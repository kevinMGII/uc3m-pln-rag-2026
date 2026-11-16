"""Elige al azar los fragmentos de origen de las consultas de evaluación (Hito 1).

El enunciado pide elegir fragmentos al azar y pedir a un LLM la consulta que haría
un usuario para encontrar esa información. Este script hace la primera parte de
forma reproducible y escribe los candidatos junto con el prompt que se usa.

Muestreo:
* Estratificado por fuente (ver TANDAS), para que haya consultas de todos los tipos
  de documento y no solo de Wikipedia (95 % de los documentos).
* Dentro de cada fuente se elige primero el DOCUMENTO al azar y después uno de sus
  fragmentos. Si se eligieran fragmentos directamente, casi todos saldrían de unos
  pocos PDF muy largos (un solo documento tiene 1.244 fragmentos).
* Solo se consideran fragmentos con al menos MIN_TOKENS tokens tras el preprocesado,
  para evitar tablas numéricas y OCR ilegible, de los que no se puede sacar una consulta.

Uso (desde la raíz del repositorio):
    python scripts/muestrear_fragmentos.py
"""

import json
import random
from collections import defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
FRAGMENTS_PATH = REPO_DIR / 'fragmentos_base' / 'misiones_300.jsonl'
PREPROCESSED_PATH = REPO_DIR / 'salidas_preprocesado' / 'fragmentos_preprocesados.jsonl'
OUT_PATH = REPO_DIR / 'consultas' / 'candidatos.jsonl'

MIN_TOKENS = 80
# Cada tanda es (semilla, nº de documentos por fuente). La primera tiene 40 candidatos.
# La segunda (16) se añadió porque la revisión descartó más candidatos de lo previsto
# (texto casi repetido en otros documentos, bibliografías...). No repite documentos.
TANDAS = [
    (2026, {'Wikipedia 1957–1999': 12, 'Wikipedia 2000–2025': 12, 'NTRS pilot': 6, 'JPL PDFs': 6, 'Apollo press kits': 4}),
    (2027, {'Wikipedia 1957–1999': 5, 'Wikipedia 2000–2025': 5, 'NTRS pilot': 2, 'JPL PDFs': 2, 'Apollo press kits': 2}),
]

PROMPT = """You will receive a passage from a document about a space mission. Write ONE search
query (8-20 words) that a user who does not remember the name of the mission could
type to find THIS document.

Rules:
- Do NOT write the name or designation of the mission, spacecraft, satellite, rocket or instrument.
- Include two or three specific facts from the passage (what happened, when, which
  country or agency, what it was for) so that the query could only match this document.
- Use your own words: never copy more than three consecutive words from the passage.
- Do not write vague queries such as "mission details" or "primary objectives of the mission".

Example
Passage: Mariner 10 was launched in November 1973 and used a gravity assist at Venus to reach Mercury, which it flew past three times, photographing about 45% of its surface.
Bad query: Mariner 10 mission details and objectives
Good query: first probe that used a planetary swing-by to reach the innermost planet and photograph almost half of it

Passage: <fragment text>"""


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def main():
    n_tokens = {row['chunk_id']: len(row['tokens']) for row in read_jsonl(PREPROCESSED_PATH)}
    by_source = defaultdict(lambda: defaultdict(list))      # fuente -> doc_id -> fragmentos válidos
    for fragment in read_jsonl(FRAGMENTS_PATH):
        if n_tokens[fragment['chunk_id']] >= MIN_TOKENS:
            by_source[fragment['source']][fragment['doc_id']].append(fragment)

    candidates, used = [], set()
    for seed, quotas in TANDAS:
        rng = random.Random(seed)
        for source, quota in quotas.items():
            documents = by_source[source]
            available = sorted(doc_id for doc_id in documents if doc_id not in used)
            for doc_id in rng.sample(available, quota):                 # 1º el documento...
                fragment = rng.choice(documents[doc_id])                # ...y después uno de sus fragmentos
                used.add(doc_id)
                candidates.append({key: fragment[key] for key in
                                   ('chunk_id', 'doc_id', 'title', 'source', 'url', 'word_count', 'text')})

    for number, candidate in enumerate(candidates, start=1):
        candidate['candidate'] = f'c{number:02d}'
    OUT_PATH.parent.mkdir(exist_ok=True)
    with OUT_PATH.open('w', encoding='utf-8', newline='\n') as f:
        for candidate in candidates:
            f.write(json.dumps(candidate, ensure_ascii=False) + '\n')
    print(f'{len(candidates)} candidatos escritos en {OUT_PATH.relative_to(REPO_DIR)}')
    print('\nPrompt para el LLM:\n' + PROMPT)


if __name__ == '__main__':
    main()
