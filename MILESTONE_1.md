# Hito 1 · Baselines de recuperación

## Trabajo realizado

Preparamos un corpus de **3.314 documentos sobre misiones espaciales**, procedentes de Wikipedia y de archivos de NASA y JPL. Indexamos completos los documentos de hasta 400 palabras y dividimos los más largos en fragmentos de 215 a 300 palabras, con unas 45 palabras de solapamiento. El índice contiene **19.620 unidades**, cada una con su identificador y el del documento de origen.

Aplicamos a fragmentos y consultas el mismo preprocesado con spaCy, que incluye lematización, filtrado gramatical y eliminación de palabras vacías. También aplicamos filtrado por frecuencia documental.

Seleccionamos 100 documentos al azar y un fragmento de cada uno. Generamos una consulta por fragmento y revisamos manualmente las 100 candidatas. Descartamos 17 por ambigüedad y una por copiar el texto de origen. Las **82 consultas** restantes están en `queries.jsonl` con el documento relevante y el fragmento de origen.

## Resultados

Comparamos **TF-IDF con similitud coseno** mediante Gensim y **BM25** mediante `bm25s`, variante Lucene, con `k1 = 1,5` y `b = 0,75`. Calculamos las estadísticas sobre los fragmentos y ordenamos los documentos según la puntuación de su mejor fragmento.

| Método | Recall@5 | Recall@10 | MRR@10 |
|---|---:|---:|---:|
| TF-IDF + coseno | 0,7927 | 0,8780 | 0,6759 |
| BM25 | **0,9146** | **0,9634** | **0,8813** |

## Problemas y decisiones de diseño

Evaluamos por documento porque cada consulta identifica un documento de referencia. Ambos métodos fallaron en el top 10 en dos consultas. Para Gemini 7, los dos devolvieron primero Gemini 6A, cuyo artículo describe el mismo encuentro orbital. Para Progress MS-13, los primeros resultados coincidían con partes de la consulta, como la ISS o el despliegue de satélites, pero correspondían a otras misiones.

## Siguiente paso

Implementaremos la recuperación densa del Hito 2 y la compararemos con estos baselines usando el mismo corpus, los mismos fragmentos y las mismas consultas.

## Uso de IA generativa

Usamos Llama 3.1 8B mediante Ollama para generar las consultas candidatas. El equipo revisó las consultas y decidió los descartes. Usamos Codex como apoyo para implementar y verificar la evaluación, analizar los fallos y preparar este resumen.