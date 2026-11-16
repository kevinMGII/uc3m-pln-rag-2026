# Consultas de evaluación (Hito 1)

Issue #3: *[03] Crear y revisar las consultas de evaluación*. El resultado es `queries.jsonl`, en la raíz del repositorio, con las consultas de tipo *known-item* (una por candidato aceptado: 35 si no se descarta ninguna más) en el formato del enunciado:

```json
{"qid": "q01", "query": "...", "relevant_ids": ["doc_1838"], "source_chunk": "doc_1838__0009"}
```

`relevant_ids` es el documento del que sale la consulta y `source_chunk` el fragmento de origen.

## Ficheros

| Fichero | Contenido |
|---|---|
| `scripts/muestrear_fragmentos.py` | Elige al azar los fragmentos candidatos y contiene el prompt |
| `consultas/candidatos.jsonl` | Los 56 fragmentos candidatos, con su texto |
| `scripts/generar_consultas.py` | Pide a un modelo de ollama la consulta de cada fragmento aceptado |
| `consultas/revision.jsonl` | Por candidato: decisión (aceptada o descartada), motivo, consulta, modelo que la escribió y avisos |
| `consultas/correcciones_manuales.jsonl` | Consultas reescritas a mano en la revisión, con el motivo; sustituyen a las del LLM |
| `scripts/revisar_consultas.py` | Comprobaciones automáticas; genera `queries.jsonl` y `comprobaciones.md` |
| `consultas/comprobaciones.md` | Tablas con las comprobaciones de las consultas, los descartes y el material para la revisión manual |

Para regenerarlo todo desde la raíz del repositorio:

```bash
python scripts/muestrear_fragmentos.py
python scripts/generar_consultas.py --url https://yiyuan.tsc.uc3m.es/api/generate --sin-verificar-tls   # con OLLAMA_API_KEY definida
python scripts/revisar_consultas.py
```

## Cómo se han creado

1. **Fragmentos al azar.** El muestreo es reproducible (semillas en el script) y estratificado por fuente, para que haya consultas de todos los tipos de documento y no solo de Wikipedia. Dentro de cada fuente se elige primero el documento y después uno de sus fragmentos: si se eligieran fragmentos directamente, casi todos saldrían de unos pocos PDF muy largos. Solo se consideran fragmentos con al menos 80 tokens tras el preprocesado. Hubo dos tandas: 40 candidatos y, como la revisión descartó más de lo previsto, 16 más.
2. **Revisión y descarte de fragmentos.** Antes de generar nada se revisaron los 56 fragmentos y se descartaron 21 por ser ambiguos o no tener contenido útil (motivo de cada uno en `comprobaciones.md`):

   | Motivo | Candidatos |
   |---|---|
   | El mismo texto aparece casi igual en otro documento (similitud coseno TF-IDF de 0,75 o más con un fragmento de otro documento): fichas de satélites de una misma serie, o *press kits* de lanzamiento y de llegada de la misma misión | 10 |
   | Texto compartido con otros documentos de la misma serie, aunque por debajo del umbral (fichas de plantilla, secciones comunes de los *press kits* de Apollo, dos versiones del mismo artículo) | 8 |
   | El fragmento es solo bibliografía o una lista de nombres | 3 |

   Esta selección depende solo del fragmento, no de la consulta ni de los resultados de los baselines.
3. **Consulta escrita por un LLM de pesos abiertos.** `generar_consultas.py` envía cada fragmento aceptado a un modelo servido con **ollama** (por defecto `llama3.1:8b`, en el servidor de la UC3M o en local) con este prompt, adaptado del notebook *Text Vectorization I* (se le añadieron reglas más estrictas y un ejemplo porque, con el prompt original, el modelo usaba el nombre de la misión o escribía consultas demasiado vagas):

   ```
   You will receive a passage from a document about a space mission. Write ONE search
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

   Passage: <fragment text>
   ```

   Las consultas están en inglés, el idioma del corpus. Se usa temperatura 0,3 y semilla fija. Si la respuesta no tiene entre 8 y 20 palabras, copia más de 3 palabras seguidas del fragmento o contiene el nombre de la misión que aparece en el título del documento, se vuelve a pedir (hasta 4 intentos); si sigue sin cumplir, queda marcada con un aviso para corregirla o descartarla a mano. El modelo usado queda anotado en `revision.jsonl` y en `comprobaciones.md`.
4. **Corrección manual.** Al revisar las consultas del modelo, las que copiaban texto, usaban el nombre de la misión, eran ambiguas o contenían un dato incorrecto se reescribieron a mano en `correcciones_manuales.jsonl`. La consulta original del modelo se conserva en `revision.jsonl`, y `comprobaciones.md` lista cada corrección con su motivo.
5. **Comprobación de que no se copia el texto.** `revisar_consultas.py` mide, para cada consulta, qué porcentaje de sus términos (tras el preprocesado) está en el fragmento de origen y cuántas palabras seguidas comparte con él. Los valores están en `comprobaciones.md`.

## Reparto por fuente

| Fuente | Documentos en el corpus | Candidatos | Aceptados |
|---|---|---|---|
| Wikipedia 1957–1999 | 1.563 | 17 | 9 |
| Wikipedia 2000–2025 | 1.594 | 17 | 15 |
| NTRS pilot | 85 | 8 | 4 |
| JPL PDFs | 63 | 8 | 4 |
| Apollo press kits | 9 | 6 | 3 |
| **Total** | 3.314 | 56 | 35 |

## Limitaciones conocidas

* Como avisa el notebook de la asignatura, otros documentos pueden ser también relevantes para una consulta, pero cuentan como error. En este corpus es frecuente: hay muchos satélites de una misma serie con artículos casi iguales.
* Los fragmentos de los *press kits* de Apollo tienen OCR con letras separadas, así que sus consultas comparten pocos términos con el texto y son un caso difícil para los métodos dispersos.
* El muestreo estratificado da más peso a los PDF (11 de 35 fragmentos aceptados) del que tienen en el corpus (157 de 3.314 documentos).

## Revisión manual del equipo

El enunciado pide revisar a mano al menos 10 consultas. `revisar_consultas.py` elige 10 al azar y deja al final de `comprobaciones.md` cada consulta junto al inicio de su fragmento. Para cada una hay que comprobar tres cosas: que el documento responde a la consulta, que la consulta no copia frases del texto y que no es trivial ni ambigua. Si una consulta no vale, se corrige o se marca como `descartada` en `revision.jsonl` (con su motivo) y se vuelve a ejecutar `revisar_consultas.py`.

**Pendiente de rellenar por una persona del equipo.**

| qid | Responde | No copia | Ni trivial ni ambigua | Revisado por | Comentario |
|---|---|---|---|---|---|
| q03 |  |  |  |  |  |
| q05 |  |  |  |  |  |
| q08 |  |  |  |  |  |
| q10 |  |  |  |  |  |
| q12 |  |  |  |  |  |
| q13 |  |  |  |  |  |
| q17 |  |  |  |  |  |
| q19 |  |  |  |  |  |
| q32 |  |  |  |  |  |
| q34 |  |  |  |  |  |
