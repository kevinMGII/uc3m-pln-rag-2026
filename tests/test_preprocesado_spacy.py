"""Valida celdas aisladas del notebook; solo escribe en directorios temporales.

Ejecutar con el entorno del proyecto:
    .venv/Scripts/python.exe -B -m unittest discover -s tests -v
"""

import ast
import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
import re
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

try:
    import pandas as pd
    import spacy
    import wordninja
    from gensim.corpora import Dictionary
    from gensim.models.phrases import FrozenPhrases, Phrases
except ImportError:
    pd = spacy = wordninja = None


NOTEBOOK_PATH = Path(__file__).resolve().parents[1] / 'notebooks/01_preprocesado_spacy.ipynb'
NOTEBOOK = json.loads(NOTEBOOK_PATH.read_text(encoding='utf-8'))


def source(number):
    text = ''.join(NOTEBOOK['cells'][number - 1]['source'])
    return '\n'.join(text.splitlines()[1:]) if text.startswith('%%time\n') else text


def definitions(number, namespace):
    nodes = [node for node in ast.parse(source(number)).body
             if isinstance(node, ast.FunctionDef) or (
                 isinstance(node, ast.Assign) and any(
                     isinstance(target, ast.Name) and target.id.endswith('_RE')
                     for target in node.targets))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(NOTEBOOK_PATH), 'exec'), namespace)


@unittest.skipUnless(pd is not None and spacy is not None and wordninja is not None,
                     'Requiere las dependencias del entorno del proyecto')
class NotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.model = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
        except OSError as error:
            raise unittest.SkipTest('Falta el modelo en_core_web_sm') from error

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        ns = {
            'pd': pd, 'spacy': spacy, 'wordninja': wordninja,
            'Dictionary': Dictionary, 'Phrases': Phrases, 'FrozenPhrases': FrozenPhrases,
            'hashlib': hashlib, 'json': json, 'os': os, 're': re, 'Path': Path,
            'TemporaryDirectory': TemporaryDirectory, 'Counter': Counter,
            'package_version': importlib.metadata.version, 'nlp': self.model,
            'OUT_DIR': root, 'LEMMAS_CACHE': root / 'lemas_spacy.jsonl',
            'LEMMAS_META': root / 'lemas_spacy.meta.json',
            'QUERIES_PATH': root / 'queries.jsonl', 'FORCE_SPACY': False,
            'PREPROCESSING_VERSION': 1, 'display': lambda *_: None,
        }
        exec(source(9), ns)
        ns['VALID_POS'] = set(ns['CONFIG']['valid_pos'])
        ns['STOPWORDS'] = set(self.model.Defaults.stop_words) | set(ns['CONFIG']['specific_stopwords'])
        for number in (13, 15, 17, 22, 23, 37, 49):
            definitions(number, ns)
        exec(source(41), ns)
        ns['fragments_df'] = self.make_frame(8)
        self.ns = ns

    def make_frame(self, count):
        return pd.DataFrame([
            {'chunk_id': f'doc_{i // 2}__{i % 2 + 1:04d}', 'doc_id': f'doc_{i // 2}',
             'title': 'Apollo press kit', 'source': 'Prueba aislada', 'word_count': 25,
             'text': 'Apollo 11 astronauts collected lunar rocks. STS-129 delivered supplies. '
                     'The propul-\nsion system and s t a i n l e s s steel worked.'}
            for i in range(count)
        ])

    def execute(self, number):
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            exec(source(number), self.ns)
        return captured.getvalue()

    def cache(self):
        frame = self.ns['fragments_df']
        values = [['apollo', str(i)] for i in range(len(frame))]
        metadata = self.ns['make_lemma_metadata'](frame)
        self.ns['save_lemmas_cache'](frame, values, metadata)
        return values, metadata

    def prepare_pipeline(self, ngrams=True, queries=False, count=8):
        ns = self.ns
        ns['fragments_df'] = self.make_frame(count)
        ns['CONFIG'].update(use_ngrams=ngrams, ngram_min_count=1,
                            ngram_threshold=0.01, no_below=1, no_above=1.0)
        ns['lemmas'] = ns['lemmatize_texts'](ns['fragments_df'].text.tolist())
        ns['lemma_metadata'] = ns['make_lemma_metadata'](ns['fragments_df'])
        ns['save_lemmas_cache'](ns['fragments_df'], ns['lemmas'], ns['lemma_metadata'])
        self.execute(25)
        ns['D_full'] = Dictionary(ns['corpus'])
        ns['n_fragments'] = len(ns['fragments_df'])
        self.execute(35)
        self.execute(37)
        if queries:
            ns['write_jsonl'](ns['QUERIES_PATH'], [
                {'qid': 'q1', 'query': 'What did Apollo 11 astronauts collect?', 'relevant_ids': ['doc_0']},
                {'qid': 'q2', 'query': 'STS-129 supplies', 'relevant_ids': ['doc_1']},
            ])
        self.execute(47)

    def test_notebook_structure_and_all_cell_syntax(self):
        import nbformat
        from IPython.core.inputtransformer2 import TransformerManager
        nbformat.validate(nbformat.read(NOTEBOOK_PATH, as_version=4))
        self.assertEqual(len(NOTEBOOK['cells']), 50)
        self.assertIn('único fragmento', source(1))
        markdown = '\n'.join(''.join(cell['source']) for cell in NOTEBOOK['cells']
                             if cell['cell_type'] == 'markdown')
        for stale_claim in ('~530', '~1.800', '1.934', '~14.500', 'unos 5 minutos'):
            self.assertNotIn(stale_claim, markdown)
        transformer = TransformerManager()
        for number, cell in enumerate(NOTEBOOK['cells'], 1):
            if cell['cell_type'] == 'code':
                with self.subTest(cell=number):
                    compile(transformer.transform_cell(''.join(cell['source'])), f'celda_{number}', 'exec')
                    if ''.join(cell['source']).startswith('%%time\n'):
                        compile(source(number), f'cuerpo_celda_{number}', 'exec')

    def test_cache_roundtrip_and_downstream_parameters_do_not_invalidate_lemmas(self):
        values, metadata = self.cache()
        self.assertEqual(self.ns['load_lemmas_cache'](self.ns['fragments_df'], metadata)[0], values)
        self.ns['CONFIG'].update(no_below=10, ngram_threshold=30, use_ngrams=False)
        self.assertEqual(self.ns['make_lemma_metadata'](self.ns['fragments_df']), metadata)

    def test_same_ids_with_changed_text_order_or_document_invalidate_cache(self):
        self.cache()
        original = self.ns['fragments_df']
        variants = [original.copy(), original.iloc[::-1].reset_index(drop=True), original.copy()]
        variants[0].loc[0, 'text'] += ' New content.'
        variants[2].loc[0, 'doc_id'] = 'another_document'
        for frame in variants:
            with self.subTest(frame=frame.iloc[0].chunk_id):
                metadata = self.ns['make_lemma_metadata'](frame)
                values, reason = self.ns['load_lemmas_cache'](frame, metadata)
                self.assertIsNone(values)
                self.assertIn('input', reason)

    def test_parameters_versions_stopwords_and_patterns_invalidate_cache(self):
        _, metadata = self.cache()
        ns = self.ns
        changes = [
            ('parameters', patch.dict(ns['CONFIG'], {'min_token_len': 3})),
            ('implementation_version', patch.dict(ns, {'PREPROCESSING_VERSION': 2})),
            ('spacy_version', patch.object(spacy, '__version__', 'test-version')),
            ('model', patch.dict(self.model.meta, {'version': 'test-version'})),
            ('wordninja_version', patch.dict(ns, {'package_version': lambda _: 'test-version'})),
            ('cleaning_patterns', patch.dict(ns, {'URL_RE': re.compile('https?://changed')})),
        ]
        for key, change in changes:
            with self.subTest(field=key), change:
                changed = ns['make_lemma_metadata'](ns['fragments_df'])
                values, reason = self.ns['load_lemmas_cache'](self.ns['fragments_df'], changed)
                self.assertIsNone(values)
                self.assertIn(key, reason)
        with patch.dict(ns['CONFIG'], {'valid_pos': ['NOUN']}), patch.dict(ns, {'VALID_POS': {'NOUN'}}):
            changed = ns['make_lemma_metadata'](ns['fragments_df'])
            self.assertIsNone(ns['load_lemmas_cache'](ns['fragments_df'], changed)[0])
        with patch.dict(ns['CONFIG'], {'specific_stopwords': ['apollo']}), patch.dict(ns, {
            'STOPWORDS': set(self.model.Defaults.stop_words) | {'apollo'}
        }):
            changed = ns['make_lemma_metadata'](ns['fragments_df'])
            self.assertNotEqual(changed['stopwords'], metadata['stopwords'])
            self.assertIsNone(ns['load_lemmas_cache'](ns['fragments_df'], changed)[0])
        ns['CONFIG']['valid_pos'] = ['NOUN']
        with self.assertRaisesRegex(AssertionError, 'Reejecutar'):
            ns['make_lemma_metadata'](ns['fragments_df'])

    def test_legacy_cache_recomputed_then_reused_and_force_recomputes(self):
        ns = self.ns
        ns['LEMMAS_CACHE'].write_text('{"chunk_id":"old","lemmas":[]}\n', encoding='utf-8')
        calls = []
        ns['lemmatize_texts'] = lambda texts: calls.append(len(texts)) or [['new'] for _ in texts]
        self.assertIn('faltan', self.execute(23))
        self.assertEqual(calls, [8])
        self.assertIn('caché compatible', self.execute(23))
        self.assertEqual(calls, [8])
        ns['FORCE_SPACY'] = True
        self.assertIn('FORCE_SPACY', self.execute(23))
        self.assertEqual(calls, [8, 8])

    def test_corrupt_cache_and_invalid_rows_are_rejected(self):
        _, metadata = self.cache()
        ns = self.ns
        ns['LEMMAS_CACHE'].write_text('incomplete', encoding='utf-8')
        self.assertIn('huella', ns['load_lemmas_cache'](ns['fragments_df'], metadata)[1])
        for rows in ([{'chunk_id': 'wrong', 'doc_id': 'wrong', 'lemmas': []}],
                     [{'chunk_id': row.chunk_id, 'doc_id': row.doc_id, 'lemmas': 'invalid'}
                      for row in ns['fragments_df'].itertuples()]):
            with self.subTest(rows=len(rows)):
                ns['write_jsonl'](ns['LEMMAS_CACHE'], rows)
                ns['write_json'](ns['LEMMAS_META'], {
                    **metadata, 'cache_sha256': ns['sha256_file'](ns['LEMMAS_CACHE'])})
                self.assertIsNone(ns['load_lemmas_cache'](ns['fragments_df'], metadata)[0])

    def test_cache_failure_before_publication_preserves_previous_files(self):
        values, metadata = self.cache()
        ns = self.ns
        before = {path: path.read_bytes() for path in (ns['LEMMAS_CACHE'], ns['LEMMAS_META'])}
        with patch.dict(ns, {'write_jsonl': lambda *_: (_ for _ in ()).throw(OSError('interrupted'))}):
            with self.assertRaises(OSError):
                ns['save_lemmas_cache'](ns['fragments_df'], values, metadata)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        self.assertEqual(list(ns['OUT_DIR'].glob('.lemas-*')), [])

    def test_interruption_between_cache_and_metadata_is_detected(self):
        _, metadata = self.cache()
        ns = self.ns
        replace = os.replace
        def interrupted_replace(src, dst):
            if Path(dst) == ns['LEMMAS_META']:
                raise OSError('interrupted')
            return replace(src, dst)
        with patch.object(os, 'replace', side_effect=interrupted_replace):
            with self.assertRaises(OSError):
                ns['save_lemmas_cache'](ns['fragments_df'], [['different']] * 8, metadata)
        self.assertIsNone(ns['load_lemmas_cache'](ns['fragments_df'], metadata)[0])
        with ns['LEMMAS_CACHE'].open(encoding='utf-8') as stream:
            self.assertEqual(len([json.loads(line) for line in stream]), 8)

    def test_cleaning_and_explicit_empty_dictionary(self):
        ns = self.ns
        cleaned = ns['wrangle_text']('propul-\nsion STS-129 https://example.org s t a i n l e s s steel')
        self.assertIn('propulsion STS 129', cleaned)
        self.assertIn('stainless steel', cleaned)
        self.assertNotIn('https', cleaned)
        ns['D'] = Dictionary([['apollo']])
        self.assertEqual(ns['filter_by_dictionary']([['apollo']], Dictionary()), [[]])

    def test_query_pipeline_matches_documents_on_200_fragments(self):
        self.prepare_pipeline(count=200)
        self.assertGreater(len(self.ns['phrase_model'].phrasegrams), 0)
        self.assertIn('200 fragmentos', self.execute(43))
        self.assertEqual(self.ns['preprocess_queries'](
            self.ns['fragments_df'].text.tolist()), self.ns['tokens_final'])

    def test_example_falls_back_when_preferred_has_no_ocr_pattern(self):
        self.ns['fragments_df'].loc[0, 'chunk_id'] = 'doc_3221__0020'
        self.ns['fragments_df'].loc[0, 'text'] = 'A clean example.'
        self.assertIn('Ejemplo alternativo', self.execute(13))
        self.assertNotEqual(self.ns['example'].chunk_id, 'doc_3221__0020')
        self.assertTrue(self.ns['SPACED_LETTERS_RE'].search(self.ns['example'].text))

    def test_current_artifacts_roundtrip_with_queries(self):
        self.prepare_pipeline(queries=True)
        ns = self.ns
        stats, manifest = ns['save_preprocessed_outputs']()
        self.assertEqual(ns['validate_artifacts'](ns['OUT_DIR']), manifest)
        self.assertEqual(stats['n_fragments'], 8)
        self.assertEqual(stats['n_documents'], 4)
        rows = [json.loads(line) for line in (ns['OUT_DIR'] / 'fragmentos_preprocesados.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual([row['chunk_id'] for row in rows], ns['fragments_df'].chunk_id.tolist())
        self.assertEqual([row['doc_id'] for row in rows], ns['fragments_df'].doc_id.tolist())
        self.assertEqual([row['tokens'] for row in rows], ns['tokens_final'])
        query_rows = [json.loads(line) for line in (ns['OUT_DIR'] / 'consultas_preprocesadas.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual([row['qid'] for row in query_rows], ['q1', 'q2'])
        self.assertEqual([row['tokens'] for row in query_rows], ns['preprocess_queries'](ns['queries']['query'].tolist()))

    def test_optional_artifacts_from_previous_runs_are_not_reused(self):
        self.prepare_pipeline(ngrams=False)
        ns = self.ns
        for name in ('ngramas.phrases', 'consultas_preprocesadas.jsonl'):
            (ns['OUT_DIR'] / name).write_text('stale', encoding='utf-8')
        _, manifest = ns['save_preprocessed_outputs']()
        for name in ('ngramas.phrases', 'consultas_preprocesadas.jsonl'):
            self.assertNotIn(name, manifest['artifacts'])
            self.assertFalse((ns['OUT_DIR'] / name).exists())

    def test_stale_model_parameters_and_changed_queries_prevent_saving(self):
        self.prepare_pipeline(queries=True)
        ns = self.ns
        for key in ('ngram_threshold', 'no_below'):
            with self.subTest(parameter=key):
                old = ns['CONFIG'][key]
                ns['CONFIG'][key] = old + 1
                with self.assertRaises(AssertionError):
                    ns['save_preprocessed_outputs']()
                ns['CONFIG'][key] = old
        context = ns['queries_context']
        ns['queries_context'] = 'previous-pipeline'
        with self.assertRaisesRegex(AssertionError, 'consultas con el pipeline actual'):
            ns['save_preprocessed_outputs']()
        ns['queries_context'] = context
        ns['QUERIES_PATH'].write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(AssertionError, 'consultas de entrada'):
            ns['save_preprocessed_outputs']()

    def test_staging_failure_preserves_previous_artifacts(self):
        self.prepare_pipeline()
        ns = self.ns
        ns['save_preprocessed_outputs']()
        before = {path.name: path.read_bytes() for path in ns['OUT_DIR'].iterdir() if path.is_file()}
        with patch.dict(ns, {'write_jsonl': lambda *_: (_ for _ in ()).throw(OSError('interrupted'))}):
            with self.assertRaises(OSError):
                ns['save_preprocessed_outputs']()
        self.assertEqual({path.name: path.read_bytes() for path in ns['OUT_DIR'].iterdir() if path.is_file()}, before)
        ns['validate_artifacts'](ns['OUT_DIR'])

    def test_interrupted_publication_and_corrupt_artifacts_are_not_valid(self):
        self.prepare_pipeline()
        ns = self.ns
        ns['save_preprocessed_outputs']()
        replace = os.replace
        def interrupted_replace(src, dst):
            if Path(dst).name == 'diccionario.dict':
                raise OSError('interrupted')
            return replace(src, dst)
        with patch.object(os, 'replace', side_effect=interrupted_replace):
            with self.assertRaises(OSError):
                ns['save_preprocessed_outputs']()
        with self.assertRaises(FileNotFoundError):
            ns['validate_artifacts'](ns['OUT_DIR'])
        ns['save_preprocessed_outputs']()
        (ns['OUT_DIR'] / 'diccionario.dict').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'diccionario.dict'):
            ns['validate_artifacts'](ns['OUT_DIR'])


if __name__ == '__main__':
    unittest.main()
