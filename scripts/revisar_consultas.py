"""Comprobaciones automáticas de las consultas y creación de queries.jsonl (Hito 1).

Lee `consultas/revision.jsonl` (un registro por candidato, con la decisión de la
revisión y la consulta que escribió el LLM con `generar_consultas.py`) y:

1. Calcula, para cada candidato, dos indicadores que ayudan a la revisión manual:
   * AMBIGÜEDAD: similitud coseno TF-IDF máxima entre el fragmento de origen y los
     fragmentos de OTROS documentos. Si es alta, el mismo texto está en otro
     documento y la consulta tendría más de una respuesta correcta.
   * COPIA: porcentaje de términos de la consulta (ya preprocesada) que están en el
     fragmento de origen, y secuencia más larga de palabras seguidas que la consulta
     comparte con el texto. El enunciado pide que la consulta no copie el texto.
2. Escribe `queries.jsonl` con las consultas aceptadas, en el formato del enunciado.
3. Escribe `consultas/comprobaciones.md` con las tablas.

Si existe `consultas/correcciones_manuales.jsonl` (candidato, consulta corregida y
motivo), esas consultas sustituyen a las del LLM y quedan listadas en el informe.

Uso (desde la raíz del repositorio):
    python scripts/revisar_consultas.py
"""

import json
import random
import sys
from pathlib import Path

import numpy as np

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_DIR / 'scripts'))
from baselines import QueryPreprocessor, TfidfRetriever, write_jsonl   # noqa: E402
from generar_consultas import longest_common_run                       # noqa: E402

REVIEW_PATH = REPO_DIR / 'consultas' / 'revision.jsonl'
CANDIDATES_PATH = REPO_DIR / 'consultas' / 'candidatos.jsonl'
REPORT_PATH = REPO_DIR / 'consultas' / 'comprobaciones.md'
CORRECTIONS_PATH = REPO_DIR / 'consultas' / 'correcciones_manuales.jsonl'   # opcional
QUERIES_PATH = REPO_DIR / 'queries.jsonl'
DUPLICATE_THRESHOLD = 0.75      # a partir de aquí consideramos que el texto está repetido en otro documento
MANUAL_SAMPLE, MANUAL_SEED = 10, 19     # consultas que se eligen al azar para la revisión manual


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def main():
    review = read_jsonl(REVIEW_PATH)
    texts = {c['chunk_id']: c['text'] for c in read_jsonl(CANDIDATES_PATH)}
    fragments = read_jsonl(REPO_DIR / 'salidas_preprocesado' / 'fragmentos_preprocesados.jsonl')
    position = {f['chunk_id']: i for i, f in enumerate(fragments)}
    doc_ids = np.array([f['doc_id'] for f in fragments])
    corpus = [f['tokens'] for f in fragments]

    preprocess = QueryPreprocessor(REPO_DIR / 'salidas_preprocesado')
    tfidf = TfidfRetriever(corpus, preprocess.dictionary)

    accepted = [r for r in review if r['decision'] == 'aceptada']
    missing = [r['candidate'] for r in accepted if not r['query'].strip()]
    if missing:
        sys.exit('Faltan consultas por generar (ejecutad antes scripts/generar_consultas.py): ' + ', '.join(missing))
    models = sorted({r.get('modelo', 'sin indicar') for r in accepted})

    # Correcciones hechas a mano en la revisión: sustituyen a la consulta del LLM, que se conserva en `query_llm`
    corrections = {c['candidate']: c for c in read_jsonl(CORRECTIONS_PATH)} if CORRECTIONS_PATH.exists() else {}
    unknown = sorted(set(corrections) - {r['candidate'] for r in accepted})
    if unknown:
        sys.exit('correcciones_manuales.jsonl tiene candidatos que no están aceptados: ' + ', '.join(unknown))
    corrected = [r for r in accepted if r['candidate'] in corrections]
    for r in corrected:
        r['query_llm'], r['query'] = r['query'], corrections[r['candidate']]['query']
    for r, tokens in zip(accepted, preprocess([r['query'] for r in accepted])):
        r['tokens'] = tokens
    for r in review:
        i = position[r['chunk_id']]
        scores = tfidf.scores(corpus[i])
        scores[doc_ids == r['doc_id']] = 0                  # solo interesan los OTROS documentos
        r['max_sim'] = float(scores.max())
        r['closest_doc'] = str(doc_ids[int(scores.argmax())])
        if r['decision'] == 'aceptada':
            source = set(corpus[i])
            r['overlap'] = sum(t in source for t in r['tokens']) / max(len(r['tokens']), 1)
            r['common_run'] = longest_common_run(r['query'], texts[r['chunk_id']])
            r['n_words'] = len(r['query'].split())

    # queries.jsonl en el formato del enunciado
    for number, r in enumerate(accepted, start=1):
        r['qid'] = f'q{number:02d}'
    write_jsonl(QUERIES_PATH, [{'qid': r['qid'], 'query': r['query'], 'relevant_ids': [r['doc_id']],
                                'source_chunk': r['chunk_id']} for r in accepted])

    lines = ['# Comprobaciones automáticas de las consultas',
             '',
             'Fichero generado por `scripts/revisar_consultas.py`. No editar a mano.',
             '',
             'Modelo que escribió las consultas (ollama): ' + ', '.join(f'`{m}`' for m in models) + '.',
             '',
             f'## Consultas aceptadas ({len(accepted)})',
             '',
             '* **Sim. otro doc.**: similitud coseno TF-IDF máxima del fragmento de origen con fragmentos de otros documentos '
             f'(a partir de {DUPLICATE_THRESHOLD} se considera texto repetido).',
             '* **Términos en el fragmento**: porcentaje de términos de la consulta preprocesada que aparecen en el fragmento de origen.',
             '* **Palabras seguidas**: secuencia más larga de palabras que la consulta comparte literalmente con el fragmento.',
             '',
             '| qid | Candidato | Documento | Fuente | Consulta | Origen | Palabras | Sim. otro doc. | Términos en el fragmento | Palabras seguidas |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for r in accepted:
        lines.append(f"| {r['qid']} | {r['candidate']} | {r['title']} (`{r['doc_id']}`) | {r['source']} | {r['query']} | {'corregida a mano' if 'query_llm' in r else 'LLM'} | {r['n_words']} | "
                     f"{r['max_sim']:.2f} | {100 * r['overlap']:.0f} % | {r['common_run']} |")
    lines += ['',
              f"Medias: {np.mean([r['n_words'] for r in accepted]):.1f} palabras por consulta, "
              f"{100 * np.mean([r['overlap'] for r in accepted]):.0f} % de términos en el fragmento, "
              f"secuencia común máxima de {max(r['common_run'] for r in accepted)} palabras.",
              '',
              f'## Consultas corregidas a mano en la revisión ({len(corrected)} de {len(accepted)})',
              '',
              'El resto son las consultas del modelo sin cambios.',
              '',
              '| qid | Consulta del LLM | Consulta corregida | Motivo |',
              '|---|---|---|---|',
              *[f"| {r['qid']} | {r['query_llm']} | {r['query']} | {corrections[r['candidate']]['motivo']} |" for r in corrected],
              '',
              f"## Candidatos descartados ({len(review) - len(accepted)})",
              '',
              '| Candidato | Documento | Fuente | Sim. otro doc. | Documento más parecido | Motivo |',
              '|---|---|---|---|---|---|']
    for r in review:
        if r['decision'] != 'aceptada':
            lines.append(f"| {r['candidate']} | {r['title']} (`{r['doc_id']}`) | {r['source']} | {r['max_sim']:.2f} | "
                         f"`{r['closest_doc']}` | {r['motivo']} |")
    sample = sorted(random.Random(MANUAL_SEED).sample(accepted, min(MANUAL_SAMPLE, len(accepted))), key=lambda r: r['qid'])
    lines += ['', f'## Material para la revisión manual ({len(sample)} consultas al azar)', '',
              'La tabla para apuntar el resultado de la revisión está en `consultas/README.md`.', '']
    for r in sample:
        excerpt = ' '.join(texts[r['chunk_id']].split())
        lines += [f"### {r['qid']} · {r['title']} (`{r['chunk_id']}`)", '', f"**Consulta:** {r['query']}", '',
                  '**Fragmento (inicio):**', '', '> ' + excerpt[:700] + ('…' if len(excerpt) > 700 else ''), '']
    REPORT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')

    print(f'{len(corrected)} consultas corregidas a mano (consultas/correcciones_manuales.jsonl)')
    print(f'{len(accepted)} consultas escritas en {QUERIES_PATH.name}; tablas en {REPORT_PATH.relative_to(REPO_DIR)}')
    print('Revisión manual:', ', '.join(r['qid'] for r in sample))
    warnings = [f"{r['qid']} ({r['candidate']})" for r in accepted
                if r['max_sim'] >= DUPLICATE_THRESHOLD or r['common_run'] >= 4 or not 8 <= r['n_words'] <= 20]
    if warnings:
        print('Revisar (texto repetido en otro documento, 4 o más palabras copiadas seguidas o longitud fuera de 8-20):',
              ', '.join(warnings))


if __name__ == '__main__':
    main()
