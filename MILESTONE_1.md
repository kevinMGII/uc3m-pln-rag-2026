# Hito 1: Baseline de recuperación

**Aplicación:** chatbot sobre documentación de misiones espaciales - **Notebook:** `hito1.ipynb` - **Commit evaluado:** `<completar>`

## Qué se ha hecho

- **Corpus:** 3.314 documentos en inglés (3.157 artículos de Wikipedia, 85 PDF del NTRS, 63 del JPL y 9 *press kits* del Apolo), cada uno con `doc_id`, título, URL y texto.
- **Unidad de indexación: el fragmento.** Los documentos de hasta 400 palabras se indexan completos y los demás se dividen en fragmentos de 215-300 palabras con un solapamiento de 45 (15 %). El resultado son 19.620 fragmentos con `doc_id` e identificador propio (`doc_0123__0007`). IDF y longitud media se calculan sobre fragmentos.
- **Preprocesado con spaCy** (`en_core_web_sm`): limpieza (URLs, guiones de fin de línea, identificadores como STS-129 y letras separadas por el OCR), lematización, filtrado por categoría gramatical (NOUN, VERB, ADJ, PROPN), stopwords generales y de dominio, n-gramas con `Phrases` y filtrado por frecuencia documental (93.549 -> 57.422 términos). Las consultas pasan por la misma función.
- **Consultas:** muestreo **aleatorio** y reproducible (semilla 2026) de 100 documentos y de un fragmento al azar de cada uno. `llama3.1:8b` escribe para cada fragmento una consulta *known-item*, sin nombrar la misión ni copiar frases. Si la consulta contiene el título, se vuelve a generar.
- **Revisión manual:** las 100 consultas se repartieron entre los 4 miembros del equipo, 25 por persona, y cada uno revisó manualmente 10 de sus 25 consultas, seleccionadas mediante una ruleta aleatoria (40 en total). Se descartaron 18 (16 por contener un dato erróneo, 1 ambigua y 1 trivial), con el motivo anotado en el notebook. Quedan **82 consultas** en `queries.jsonl`, con `relevant_ids` y `source_chunk`.
- **Baselines:** TF-IDF de Gensim (tf·log₂(N/df) y similitud coseno) y BM25 con `bm25s` (variante Lucene, k1 = 1,5 y b = 0,75). Cada documento recibe la puntuación de su mejor fragmento y se eliminan los repetidos antes de quedarse con el top 10.

## Resultados (82 consultas, evaluación por documento)

| Método | Recall@5 | Recall@10 | MRR@10 |
| --- | --- | --- | --- |
| TF-IDF | 0,793 | 0,878 | 0,676 |
| BM25 | **0,915** | **0,963** | **0,881** |

BM25 supera a TF-IDF en todas las métricas, y la ventaja es mayor con K = 5. Con ese corte, BM25 es el único que acierta en 11 consultas y TF-IDF en 1 (McNemar exacto, p = 0,006); con K = 10, son 8 frente a 1 (p = 0,04). Los dos métodos fallan a la vez en 6 consultas con K = 5 y en 2 con K = 10.

## Problemas encontrados y decisiones de diseño

- **Documentos muy heterogéneos:** van de decenas de palabras a un libro que da 1.244 fragmentos. Por eso fragmentamos con un tamaño casi constante y puntuamos cada documento por su mejor fragmento. El OCR de los PDF antiguos separa las letras, y lo reconstruimos con `wordninja`.
- **Errores del LLM:** 18 de las 40 consultas revisadas se descartaron, casi siempre porque alteraban un dato del fragmento (una fecha o la causa de un fallo). Las 60 no revisadas pueden contener errores parecidos.
- **Fallos comunes:** hay dos causas. (1) Documentos casi equivalentes o consultas poco específicas (Gemini 6A y 7, Kosmos 2434-2436, naves Progress MS), que cuentan como fallo porque cada consulta tiene un solo documento relevante. (2) Desajustes de vocabulario (*Guiana Space Centre* / *Kourou*), agravados porque los n-gramas sustituyen a los unigramas.
- **Sesgo del muestreo:** como se muestrean documentos, 95 de las 100 consultas salen de Wikipedia, aunque los PDF suman el 48 % de los fragmentos.
- **MRR:** se calcula sobre el top 10 (MRR@10).

## Uso de herramientas de IA generativa

- **llama3.1:8b** (servidor ollama de la UC3M): generación de las 100 consultas de evaluación, revisadas después por el equipo como se describe arriba.
- **Claude Opus 5.5 (Anthropic):** apoyo en la extracción de los documentos del corpus, en la revisión del código del notebook y en el ajuste del preprocesado de los notebooks de clase a las características y particularidades de nuestro dominio específico. El equipo ha revisado y validado el código y los resultados.
- - **GPT 6.1 Sol (OpenAI):** utilizado en la extracción de los documentos del corpus, así como la extracción de los fragmentos debido al volumen de los mismos. Además, esta utilización ha estado supervisada en todo momento por el equipo.
