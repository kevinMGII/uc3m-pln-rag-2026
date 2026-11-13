"""Segmenta el corpus de misiones espaciales sin dependencias externas."""

import argparse
import json
import re
from contextlib import nullcontext
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZipFile


WORDS_PER_CHUNK = 300
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


def segment(document, exact):
    """Agrupa palabras consecutivas y conserva el texto original del intervalo."""
    text = document["text"]
    words = list(WORD.finditer(text))
    provenance = {
        key: document[key] for key in ("doc_id", "title", "source", "url")
    }
    if document.get("revision_url"):
        provenance["revision_url"] = document["revision_url"]

    for offset in range(0, len(words), WORDS_PER_CHUNK):
        group = words[offset : offset + WORDS_PER_CHUNK]
        if exact and len(group) < WORDS_PER_CHUNK:
            break

        number = offset // WORDS_PER_CHUNK + 1
        # Cut at the next word so punctuation and paragraph breaks are preserved.
        start = 0 if offset == 0 else group[0].start()
        next_offset = offset + len(group)
        end = words[next_offset].start() if next_offset < len(words) else len(text)
        chunk = {
            **provenance,
            "chunk_id": f"{document['doc_id']}__{number:04d}",
            "chunk_index": number,
            "word_count": len(group),
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


def write_chunks(corpus_path, output_path, exact=False):
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
                for chunk in segment(document, exact):
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
    parser.add_argument(
        "--exactos", action="store_true",
        help="Descarta el último fragmento si tiene menos de 300 palabras",
    )
    args = parser.parse_args()
    try:
        docs, chunks, short, empty = write_chunks(args.corpus, args.salida, args.exactos)
    except (OSError, BadZipFile, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Error al segmentar el corpus: {error}\n")
    print(f"{docs} documentos | {chunks} fragmentos | {short} finales cortos")
    if empty:
        print(f"{empty} documentos no produjeron ningún fragmento.")
    print(f"Salida: {args.salida.resolve()}")


if __name__ == "__main__":
    main()
