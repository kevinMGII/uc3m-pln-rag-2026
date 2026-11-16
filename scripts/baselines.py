"""Baselines de recuperación dispersa del Hito 1: TF-IDF + similitud coseno y BM25.

Sigue la sección 4 del notebook *Text Vectorization I* (Gensim para TF-IDF, bm25s
para BM25), adaptada a nuestro corpus:

* La unidad de indexación es el FRAGMENTO, así que el IDF y la longitud media se
  calculan sobre fragmentos (nota del enunciado del Hito 1).
* El ranking final es de DOCUMENTOS: cada documento recibe la puntuación de su
  mejor fragmento y se eliminan los repetidos antes de quedarse con los K primeros.
* Las consultas se preprocesan con los mismos pasos, el mismo modelo de n-gramas y
  el mismo diccionario que los fragmentos (notebook 01_preprocesado_spacy).

Uso típico (desde un notebook o desde otro script):

    from baselines import QueryPreprocessor, TfidfRetriever, BM25Retriever, rank_documents
"""

import json
import re
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# 1. Preprocesado de consultas (mismas funciones que notebooks/01_preprocesado_spacy)
# ---------------------------------------------------------------------------

# Estas expresiones regulares son copia literal de las del notebook 01. Si allí se
# cambian, hay que cambiarlas aquí e incrementar PREPROCESSING_VERSION en el notebook.
# La comprobación `check_consistency` detecta cualquier diferencia entre ambos.
SPACED_LETTERS_RE = re.compile(r'\b(?:[A-Za-z] ){2,}[A-Za-z]\b')
URL_RE = re.compile(r'https?://\S+|www\.\S+')
HYPHEN_BREAK_RE = re.compile(r'(\w)-[ \t]*\n\s*(\w)')
ID_SEPARATOR_RE = re.compile(r'(?<=[A-Za-z0-9])[-/](?=[A-Za-z0-9])')
WHITESPACE_RE = re.compile(r'\s+')


class QueryPreprocessor:
    """Texto bruto -> tokens, igual que se hizo con los fragmentos del corpus.

    Carga de `preprocesado/` la configuración, el modelo de n-gramas y el
    diccionario que generó el notebook 01, para no repetir ningún parámetro aquí.
    """

    def __init__(self, preprocessed_dir):
        # Se importan aquí para que el resto del módulo no dependa de spaCy.
        import spacy
        import wordninja
        from gensim.corpora import Dictionary
        from gensim.models.phrases import FrozenPhrases

        preprocessed_dir = Path(preprocessed_dir)
        with open(preprocessed_dir / 'config_preprocesado.json', encoding='utf-8') as f:
            self.config = json.load(f)['config']

        self._wordninja = wordninja
        self.nlp = spacy.load(self.config['spacy_model'], disable=['parser', 'ner'])
        self.valid_pos = set(self.config['valid_pos'])
        self.stopwords = set(self.nlp.Defaults.stop_words) | set(self.config['specific_stopwords'])
        self.dictionary = Dictionary.load(str(preprocessed_dir / 'diccionario.dict'))
        self.phrase_model = None
        if self.config['use_ngrams']:
            self.phrase_model = FrozenPhrases.load(str(preprocessed_dir / 'ngramas.phrases'))

    def _fix_spaced_letters(self, match):
        joined = match.group(0).replace(' ', '')
        return ' '.join(self._wordninja.split(joined)) if self.config['ocr_resegment'] else joined

    def wrangle_text(self, text):
        text = URL_RE.sub(' ', text)
        text = HYPHEN_BREAK_RE.sub(r'\1\2', text)
        text = SPACED_LETTERS_RE.sub(self._fix_spaced_letters, text)
        text = ID_SEPARATOR_RE.sub(' ', text)
        return WHITESPACE_RE.sub(' ', text).strip()

    def normalize_token(self, tk):
        # Devuelve la forma normalizada del token, o None si hay que descartarlo
        text = tk.lower_
        if self.config['keep_identifiers'] and text.isalnum() and any(c.isdigit() for c in text):
            return text if len(text) <= self.config['max_identifier_len'] else None
        if not tk.is_alpha or tk.pos_ not in self.valid_pos:
            return None
        lemma = tk.lemma_.lower()
        if len(lemma) < self.config['min_token_len'] or not lemma.isalpha():
            return None
        if lemma in self.stopwords or tk.lower_ in self.stopwords:
            return None
        return lemma

    def __call__(self, texts, batch_size=128):
        """Lista de textos -> lista de listas de tokens (spaCy -> n-gramas -> diccionario)."""
        cleaned = (self.wrangle_text(t) for t in texts)
        token_lists = [[t for t in map(self.normalize_token, doc) if t]
                       for doc in self.nlp.pipe(cleaned, batch_size=batch_size)]
        if self.phrase_model is not None:
            token_lists = [self.phrase_model[tokens] for tokens in token_lists]
        vocab = self.dictionary.token2id
        return [[t for t in tokens if t in vocab] for tokens in token_lists]


def check_consistency(preprocess, raw_texts, expected_tokens):
    """Comprueba que `preprocess` reproduce los tokens guardados del corpus.

    Devuelve las posiciones que NO coinciden (lista vacía si todo va bien).
    """
    recomputed = preprocess(list(raw_texts))
    return [i for i, (new, old) in enumerate(zip(recomputed, expected_tokens, strict=True)) if new != old]


# ---------------------------------------------------------------------------
# 2. Recuperadores: puntúan TODOS los fragmentos para una consulta ya tokenizada
# ---------------------------------------------------------------------------

class TfidfRetriever:
    """TF-IDF de Gensim + similitud coseno (Text Vectorization I, sección 4.2).

    Peso de un término en un fragmento: tf * log2(N / df), con el vector normalizado
    a norma 1 (valores por defecto de `TfidfModel`). N y df se miden sobre fragmentos.
    Como los vectores tienen norma 1, el coseno es un producto escalar.
    """

    def __init__(self, corpus_tokens, dictionary):
        from gensim.models import TfidfModel
        from gensim.similarities import SparseMatrixSimilarity

        self.dictionary = dictionary
        corpus_bow = [dictionary.doc2bow(tokens) for tokens in corpus_tokens]
        self.model = TfidfModel(corpus_bow)
        self.index = SparseMatrixSimilarity(self.model[corpus_bow], num_features=len(dictionary))

    def scores(self, query_tokens):
        """Similitud coseno de la consulta con cada fragmento (vector de tamaño N)."""
        query_tfidf = self.model[self.dictionary.doc2bow(query_tokens)]   # mismo diccionario y modelo que el corpus
        return np.asarray(self.index[query_tfidf], dtype=np.float64)


class BM25Retriever:
    """BM25 con la librería bm25s (Text Vectorization I, sección 4.3).

    Variante `lucene` (la de bm25s por defecto, la misma que usan Lucene y
    Elasticsearch):

        score(q, d) = sum_{t en q} IDF(t) * f(t,d) / (f(t,d) + k1 * (1 - b + b * |d| / avgdl))
        IDF(t)      = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))

    Respecto a la fórmula de las diapositivas, omite el factor constante (k1 + 1)
    del numerador (no cambia el orden del ranking) y su IDF nunca es negativo.
    N, df, |d| y avgdl se miden sobre fragmentos.
    """

    def __init__(self, corpus_tokens, k1=1.5, b=0.75, method='lucene'):
        import bm25s

        self.k1, self.b, self.method = k1, b, method
        self.model = bm25s.BM25(k1=k1, b=b, method=method)
        self.model.index(corpus_tokens, show_progress=False)
        self._vocab = self.model.vocab_dict

    def scores(self, query_tokens):
        """Puntuación BM25 de la consulta con cada fragmento (vector de tamaño N)."""
        # Un término repetido en la consulta suma dos veces, como en el notebook.
        known = [t for t in query_tokens if t in self._vocab]
        if not known:
            return np.zeros(self.model.scores['num_docs'], dtype=np.float64)
        return np.asarray(self.model.get_scores(known), dtype=np.float64)


# ---------------------------------------------------------------------------
# 3. De puntuaciones por fragmento a rankings
# ---------------------------------------------------------------------------

def rank_chunks(scores, chunk_ids, doc_ids, k=10):
    """Los k fragmentos con mayor puntuación (solo los que puntúan más que 0)."""
    order = np.argsort(-scores, kind='stable')[:k]      # 'stable': empates en el orden del corpus
    return [{'rank': rank, 'chunk_id': chunk_ids[i], 'doc_id': doc_ids[i], 'score': round(float(scores[i]), 6)}
            for rank, i in enumerate(order, start=1) if scores[i] > 0]


def rank_documents(scores, chunk_ids, doc_ids, k=10):
    """Ranking a nivel de documento, como pide el enunciado del Hito 1:

    1. se puntúan los fragmentos,
    2. cada documento recibe la puntuación de su mejor fragmento,
    3. se eliminan los documentos repetidos,
    4. se devuelven los k primeros.

    Un fragmento con puntuación 0 no comparte ningún término con la consulta, así
    que no cuenta como recuperado (la lista puede tener menos de k documentos).
    """
    ranking, seen = [], set()
    for i in np.argsort(-scores, kind='stable'):        # fragmentos de mayor a menor puntuación
        if scores[i] <= 0 or len(ranking) == k:
            break
        if doc_ids[i] in seen:                          # ya está: lo representaba un fragmento mejor
            continue
        seen.add(doc_ids[i])
        ranking.append({'rank': len(ranking) + 1, 'doc_id': doc_ids[i],
                        'score': round(float(scores[i]), 6), 'best_chunk': chunk_ids[i]})
    return ranking


def build_rankings(retriever, queries, chunk_ids, doc_ids, k=10):
    """Un registro por consulta con su ranking de documentos y de fragmentos.

    `queries` es una lista de diccionarios con `qid`, `query` y `tokens`.
    """
    records = []
    for q in queries:
        scores = retriever.scores(q['tokens'])
        records.append({
            'qid': q['qid'], 'query': q['query'], 'tokens': q['tokens'],
            'docs': rank_documents(scores, chunk_ids, doc_ids, k),
            'chunks': rank_chunks(scores, chunk_ids, doc_ids, k),
        })
    return records


def write_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
