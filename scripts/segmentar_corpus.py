"""Segmenta el corpus de misiones espaciales sin dependencias externas."""

import argparse
import json
import re
from contextlib import nullcontext
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZipFile


WORDS_PER_CHUNK = 300
MIN_WORDS_PER_CHUNK = 200
MAX_WORDS_PER_CHUNK = 400
OVERLAP_WORDS = 45  # 15 % del tamaño objetivo.
WORD = re.compile(r"\b\w+(?:[’'-]\w+)*\b")


def read_json(corpus, filename):
    """Lee una entrada del ZIP o del directorio extraído."""
    relative_path = PurePosixPath(filename)
    if relative_path.is_absolute() or ".." in relative_path.parts or "\\" in filename:
        raise ValueError(f"Ruta de entrada inválida: {filename}")
    if isinstance(corpus, ZipFile):
        with corpus.open(filename) as entry:
            return json.load(entry)
    with (corpus / relative_path).open(encoding="utf-8") as entry:
        return json.load(entry)


def read_documents(corpus):
    """Acepta el ZIP del corpus o los datos brutos organizados por décadas."""
    index = read_json(corpus, "indice.json")
    if isinstance(index, list):
        for row in index:
            yield row["doc_id"], read_json(corpus, row["file"])
        return

    for row in index["misiones"]:
        source = read_json(corpus, row["archivo"])
        blocks = [source.get("resumen") or ""]
        blocks.extend(
            "\n".join(value for value in (section.get("titulo"), section.get("texto")) if value)
            for section in source.get("secciones", [])
        )
        yield row["id"], {
            "doc_id": source["id"],
            "title": source["titulo"],
            "source": source["fuente"],
            "url": source["url_fuente"],
            "text": "\n\n".join(block for block in blocks if block.strip()),
        }


def word_ranges(word_count):
    """Devuelve intervalos de palabras con solapamiento y sin restos pequeños."""
    if word_count <= MAX_WORDS_PER_CHUNK:
        return [(0, word_count)]

    ranges = []
    start = 0
    while word_count - start > WORDS_PER_CHUNK:
        ranges.append((start, start + WORDS_PER_CHUNK))
        start += WORDS_PER_CHUNK - OVERLAP_WORDS

    if word_count - start >= MIN_WORDS_PER_CHUNK:
        ranges.append((start, word_count))
    else:
        # Absorber el resto evita añadir un fragmento casi redundante.
        previous_start, _ = ranges.pop()
        if word_count - previous_start <= MAX_WORDS_PER_CHUNK:
            ranges.append((previous_start, word_count))
        else:
            # Repartir el último tramo en dos, conservando 45 palabras comunes.
            middle = previous_start + (
                word_count - previous_start + OVERLAP_WORDS + 1
            ) // 2
            ranges.extend([
                (previous_start, middle),
                (middle - OVERLAP_WORDS, word_count),
            ])
    return ranges


def segment(document):
    """Conserva texto y metadatos; omite documentos sin palabras reconocibles."""
    text = document["text"]
    words = list(WORD.finditer(text))
    if not words:
        return
    # Los tamaños son del fragmento; el mapa de páginas se proyecta más abajo.
    provenance = {
        key: value for key, value in document.items()
        if key not in ("text", "word_count", "page_offsets")
    }

    for number, (offset, next_offset) in enumerate(word_ranges(len(words)), start=1):
        # Cut at the next word so punctuation and paragraph breaks are preserved.
        start = 0 if offset == 0 else words[offset].start()
        end = words[next_offset].start() if next_offset < len(words) else len(text)
        chunk = {
            **provenance,
            "chunk_id": f"{document['doc_id']}__{number:04d}",
            "chunk_index": number,
            "word_count": next_offset - offset,
            "char_start": start,
            "char_end": end,
            "text": text[start:end],
        }
        pages = [
            page["page"]
            for page in document.get("page_offsets", [])
            if max(start, page["start"]) < min(end, page["end"])
        ]
        if pages:
            chunk["pages"] = pages
        yield chunk


def write_chunks(corpus_path, output_path):
    """Escribe JSONL y publica el resultado solo tras procesar el índice completo."""
    if output_path.exists():
        raise FileExistsError(f"La salida ya existe: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    container = (
        nullcontext(corpus_path) if corpus_path.is_dir() else ZipFile(corpus_path)
    )
    document_ids = set()
    total_chunks = 0
    short_chunks = 0
    documents_without_chunks = 0
    temporary_path = None

    try:
        with container as corpus, NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            dir=output_path.parent, suffix=".tmp", delete=False,
        ) as output:
            temporary_path = Path(output.name)
            for expected_id, document in read_documents(corpus):
                doc_id = document["doc_id"]
                if doc_id != expected_id or doc_id in document_ids:
                    raise ValueError(f"Identificador duplicado o inconsistente: {doc_id}")
                document_ids.add(doc_id)

                previous_total = total_chunks
                for chunk in segment(document):
                    output.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                    total_chunks += 1
                    short_chunks += chunk["word_count"] < WORDS_PER_CHUNK
                documents_without_chunks += total_chunks == previous_total

        if output_path.exists():
            raise FileExistsError(f"La salida ya existe: {output_path}")
        temporary_path.rename(output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return len(document_ids), total_chunks, short_chunks, documents_without_chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path, help="ZIP o carpeta con indice.json")
    parser.add_argument("salida", type=Path, help="Ruta de salida .jsonl")
    args = parser.parse_args()
    try:
        docs, chunks, short, empty = write_chunks(args.corpus, args.salida)
    except (OSError, BadZipFile, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Error al segmentar el corpus: {error}\n")
    print(f"{docs} documentos | {chunks} fragmentos | {short} fragmentos de menos de 300 palabras")
    if empty:
        print(f"{empty} documentos no produjeron ningún fragmento.")
    print(f"Salida: {args.salida.resolve()}")


if __name__ == "__main__":
    main()
