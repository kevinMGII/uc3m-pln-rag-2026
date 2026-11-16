# uc3m-pln-rag-2026
Proyecto de Procesamiento de Lenguaje Natural (UC3M, 2026/27). Aplicación RAG con baselines de recuperación y evaluación reproducible.

**Aplicación:** chatbot para buscar información en documentación de misiones espaciales (NASA y otras agencias): artículos de Wikipedia, *press kits* del programa Apollo, informes técnicos de NTRS y documentos del JPL.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `corpus/corpus_misiones_espaciales_json.zip` | Corpus original: un JSON por documento, con `doc_id`, texto completo y URL de la fuente |
| `scripts/segmentar_corpus.py` | Divide los documentos en fragmentos de 300 palabras conservando `doc_id`, título y URL |
| `fragmentos_base/misiones_300.jsonl` | Fragmentos (unidad de indexación): 18.992 fragmentos de 3.314 documentos |
| `notebooks/01_preprocesado_spacy.ipynb` | Preprocesado con spaCy de fragmentos y consultas (Hito 1) |
| `preprocesado/` | Resultados del preprocesado, que usan los baselines TF-IDF y BM25 |
| `scripts/baselines.py` | Baselines de recuperación: preprocesado de consultas, TF-IDF + coseno, BM25 y ranking por documento |
| `notebooks/02_baselines_tfidf_bm25.ipynb` | Baselines TF-IDF + coseno y BM25: implementación documentada y rankings por consulta (Hito 1) |
| `resultados/` | Rankings por consulta de cada baseline (se generan cuando existe `queries.jsonl`) |

### Contenido de `preprocesado/`

| Fichero | Contenido |
|---|---|
| `fragmentos_preprocesados.jsonl` | `chunk_id`, `doc_id` y `tokens` finales de cada fragmento |
| `diccionario.dict` | Diccionario de Gensim filtrado por frecuencia documental |
| `ngramas.phrases` | Modelo de n-gramas (Gensim `Phrases` congelado), necesario para preprocesar las consultas |
| `config_preprocesado.json` | Parámetros y estadísticas del preprocesado |
| `lemas_spacy.jsonl` | Caché de los lemas de spaCy (antes de n-gramas y filtro por frecuencia) para no repetir el paso más lento |

## Instalación

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Los notebooks también se pueden ejecutar en Google Colab: copiad el repositorio a vuestro Google Drive y ajustad `REPO_DIR` en la celda de datos.

## Hito 1: baseline de recuperación

### Preprocesado (`notebooks/01_preprocesado_spacy.ipynb`)

Sigue el notebook *Text Vectorization I* de la asignatura, adaptado al corpus:

1. **Limpieza del texto:** eliminación de URLs, re-segmentación con `wordninja` del OCR con letras separadas (`b u t i s` → `but is`), unión de palabras cortadas a final de línea y separación de identificadores con guion (`STS-129` → `STS 129`).
2. **spaCy** (`en_core_web_sm`, sin `parser` ni `ner`): lematización, filtrado por categoría gramatical (`NOUN`, `VERB`, `ADJ`, `PROPN`) y eliminación de stopwords genéricas y del dominio. Se conservan números y códigos cortos (`11`, `2b`, `1969`), que distinguen misiones.
3. **N-gramas** con Gensim `Phrases` (`min_count=5`, `threshold=20`): `sts_129`, `space_station`...
4. **Filtrado por frecuencia documental** sobre fragmentos: `no_below=2`, `no_above=0.5` (vocabulario de 93.435 a 57.168 términos).
5. **Consultas:** se preprocesan con exactamente las mismas funciones, modelo de n-gramas y diccionario (`preprocess_queries`). El notebook comprueba automáticamente que el pipeline de consultas reproduce los tokens del corpus.

Para regenerar los resultados, ejecutad el notebook desde `notebooks/` (unos 5 minutos en CPU; con la caché `lemas_spacy.jsonl`, unos segundos).

### Baselines (`notebooks/02_baselines_tfidf_bm25.ipynb` y `scripts/baselines.py`)

Siguen la sección 4 del notebook *Text Vectorization I*. La unidad de indexación es el fragmento, así que el IDF y la longitud media se calculan sobre fragmentos.

1. **TF-IDF + similitud coseno:** Gensim `TfidfModel` con sus valores por defecto (`tf · log2(N/df)` y norma L2) y `SparseMatrixSimilarity`.
2. **BM25:** librería `bm25s`, variante `lucene`, con `k1 = 1.5` y `b = 0.75`:
   `score(q, d) = Σ IDF(t) · f(t,d) / (f(t,d) + k1 · (1 − b + b · |d| / avgdl))`, con `IDF(t) = ln(1 + (N − df + 0.5) / (df + 0.5))`.
3. **Consultas:** `QueryPreprocessor` aplica el mismo preprocesado, modelo de n-gramas y diccionario que a los fragmentos; el notebook comprueba que reproduce los tokens guardados del corpus.
4. **Ranking por documento:** se puntúan todos los fragmentos, cada documento recibe la puntuación de su mejor fragmento, se eliminan los repetidos y se guardan los 10 primeros.

Con `queries.jsonl` en la raíz, el notebook guarda en `resultados/` los ficheros `rankings_tfidf.jsonl` y `rankings_bm25.jsonl` (una línea por consulta, con los 10 primeros documentos en `docs` y los 10 primeros fragmentos en `chunks`) y `config_baselines.json`. Tarda unos 20 segundos.

### Estado

- [x] Corpus y fragmentación
- [x] Preprocesado de documentos y consultas con spaCy
- [ ] Consultas de evaluación (`queries.jsonl`)
- [x] Baselines TF-IDF y BM25 (falta generar los rankings con `queries.jsonl`)
- [ ] Evaluación (Recall@5, Recall@10, MRR) y `MILESTONE_1.md`
