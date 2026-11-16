"""Genera con un LLM de pesos abiertos (ollama) la consulta de cada fragmento aceptado.

Para cada candidato aceptado de `consultas/revision.jsonl` envía el fragmento a un
modelo servido por ollama y guarda la consulta en ese mismo fichero. No usa ningún
servicio de pago: solo el servidor de la UC3M o un ollama local.

Uso (desde la raíz del repositorio):

    # Servidor de la UC3M (sección 7 del enunciado). La clave es la del enunciado.
    #   PowerShell:  $env:OLLAMA_API_KEY = "<clave del enunciado>"
    #   Linux/macOS: export OLLAMA_API_KEY="<clave del enunciado>"
    python scripts/generar_consultas.py --url https://yiyuan.tsc.uc3m.es/api/generate --sin-verificar-tls

    # ollama instalado en el propio ordenador (ollama pull llama3.1:8b)
    python scripts/generar_consultas.py

Después hay que ejecutar `python scripts/revisar_consultas.py`.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_DIR / 'scripts'))
from muestrear_fragmentos import PROMPT   # noqa: E402  (el prompt está definido en un único sitio)

REVIEW_PATH = REPO_DIR / 'consultas' / 'revision.jsonl'
CANDIDATES_PATH = REPO_DIR / 'consultas' / 'candidatos.jsonl'

SYSTEM = 'You write search queries in English. Answer with the query only: one line, no quotes, no explanations.'
MIN_WORDS, MAX_WORDS = 8, 20
MAX_COMMON_RUN = 3          # nº máximo de palabras seguidas copiadas del fragmento
MAX_ATTEMPTS = 4
# Palabras de los títulos que no identifican por sí solas a una misión
GENERIC_TITLE_WORDS = {'press', 'kit', 'launch', 'mission', 'missions', 'satellite', 'project', 'spacecraft', 'module',
                       'the', 'and', 'for', 'with', 'from', 'mars', 'moon', 'lunar', 'earth', 'venus', 'jupiter',
                       'saturn', 'solar', 'space', 'star', 'one', 'first', 'region', 'imaging', 'interface',
                       'spectrograph', 'european', 'carrier', 'retrievable', 'apollo', 'progress'}


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def longest_common_run(query, text):
    """Nº de palabras de la secuencia más larga que la consulta comparte con el texto."""
    words = re.findall(r'\w+', query.lower())
    text = ' ' + ' '.join(re.findall(r'\w+', text.lower())) + ' '
    best = 0
    for start in range(len(words)):
        for end in range(start + best + 1, len(words) + 1):
            if ' ' + ' '.join(words[start:end]) + ' ' not in text:
                break
            best = end - start
    return best


def clean(answer):
    """Se queda con la primera línea con texto y le quita comillas y prefijos como 'Query:'."""
    answer = re.sub(r'<think>.*?</think>', ' ', answer, flags=re.DOTALL)      # modelos con razonamiento visible
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    if not lines:
        return ''
    line = re.sub(r'^(search\s+)?query\s*:\s*', '', lines[0], flags=re.IGNORECASE)
    return line.strip(' "\'`*').strip()


def title_names(title):
    """Palabras del título que delatan la misión: 'Sich-1' -> {'sich 1', 'sich'}.

    Solo se usa con títulos cortos (artículos de Wikipedia y press kits); los títulos
    largos de los informes técnicos son descripciones, no nombres.
    """
    title = re.sub(r'\([^)]*\)', ' ', title)                             # '(satellite)', '(1.4Mb)'...
    words = re.findall(r'[a-z0-9]+', title.lower())
    names = [w for w in words if w not in GENERIC_TITLE_WORDS]
    if not names or len(words) > 4:
        return set()
    found = {w for w in names if len(w) >= 4 and not w.isdigit()}          # 'vostok', 'gsat', 'skylab'
    if any(not w.isdigit() for w in words):
        full = ' '.join(w for w in words if w not in {'press', 'kit', 'launch', 'and', 'the'})
        if not full.isdigit():
            found.add(full)                                                # 'sich 1', 'apollo 14'
    return found


def problems(query, text, title=''):
    """Lista de motivos por los que la consulta no cumple el enunciado (vacía si está bien)."""
    found = []
    n_words = len(query.split())
    if not MIN_WORDS <= n_words <= MAX_WORDS:
        found.append(f'{n_words} palabras')
    run = longest_common_run(query, text)
    if run > MAX_COMMON_RUN:
        found.append(f'copia {run} palabras seguidas')
    normalized = ' ' + ' '.join(re.findall(r'[a-z0-9]+', query.lower())) + ' '
    used = sorted(name for name in title_names(title) if f' {name} ' in normalized)
    if used:
        found.append(f'usa el nombre "{used[-1]}"')
    return found


def ask(args, prompt, seed):
    headers = {'Content-Type': 'application/json'}
    if os.environ.get('OLLAMA_API_KEY'):
        headers['X-API-KEY'] = os.environ['OLLAMA_API_KEY']
    data = {'model': args.modelo, 'system': SYSTEM, 'prompt': prompt, 'stream': False,
            'options': {'temperature': args.temperatura, 'seed': seed, 'num_ctx': 4096}}
    response = requests.post(args.url, headers=headers, data=json.dumps(data),
                             timeout=300, verify=not args.sin_verificar_tls)
    response.raise_for_status()
    return response.json()['response']


def generate(args, text, title):
    """Pide la consulta; si no cumple (longitud, copia o nombre de la misión), lo reintenta."""
    prompt = PROMPT.replace('<fragment text>', text)
    query, found = '', ['sin respuesta']
    for attempt in range(MAX_ATTEMPTS):
        extra = '' if attempt == 0 else (f'\n\nYour previous query was rejected: "{query}". Write a different one of 8 to 20 '
                                         'words that follows ALL the rules: no names or designations, no copied '
                                         'sequences of words. Answer with the query only.')
        query = clean(ask(args, prompt + extra, args.semilla + attempt))
        found = problems(query, text, title)
        if not found:
            break
    return query, found, attempt + 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--url', default='http://localhost:11434/api/generate', help='ruta /api/generate de ollama')
    parser.add_argument('--modelo', default='llama3.1:8b')
    parser.add_argument('--temperatura', type=float, default=0.3)
    parser.add_argument('--semilla', type=int, default=2026)
    parser.add_argument('--sin-verificar-tls', action='store_true',
                        help='equivale al -k del curl del enunciado (certificado del servidor de la UC3M)')
    args = parser.parse_args()
    if args.sin_verificar_tls:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    review = read_jsonl(REVIEW_PATH)
    texts = {c['chunk_id']: c['text'] for c in read_jsonl(CANDIDATES_PATH)}
    accepted = [r for r in review if r['decision'] == 'aceptada']
    print(f'Generando {len(accepted)} consultas con {args.modelo} en {args.url}')

    for number, row in enumerate(accepted, start=1):
        try:
            query, found, attempts = generate(args, texts[row['chunk_id']], row['title'])
        except (requests.RequestException, KeyError, ValueError) as error:
            sys.exit(f'Error al llamar a ollama ({row["candidate"]}): {error}')
        row.update({'query': query, 'modelo': args.modelo, 'intentos': attempts, 'avisos': found})
        print(f'[{number:02d}/{len(accepted)}] {row["candidate"]} {row["title"][:35]:35s} -> {query}'
              + (f'   (AVISO: {", ".join(found)})' if found else ''))

    with REVIEW_PATH.open('w', encoding='utf-8', newline='\n') as f:
        for row in review:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    pending = [r['candidate'] for r in accepted if r['avisos']]
    print(f'\nConsultas guardadas en {REVIEW_PATH.relative_to(REPO_DIR)}.')
    if pending:
        print('Hay que corregir a mano en ese fichero (o descartar) estas consultas:', ', '.join(pending))
    print('Siguiente paso: python scripts/revisar_consultas.py')


if __name__ == '__main__':
    main()
