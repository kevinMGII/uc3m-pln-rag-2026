"""Pruebas de segmentación y escritura, sin dependencias externas.

Ejecutar desde la raíz: python -B -m unittest discover -s tests -v
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from scripts.segmentar_corpus import WORD, read_documents, segment, write_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "segmentar_corpus.py"


def make_document(word_count, doc_id="doc_prueba"):
    separators = (" ", ",\t", ".\n\n", " — ", ";\r\n")
    text = " \n«" + "".join(
        f"palabra{i}{separators[i % len(separators)]}" for i in range(word_count)
    ) + "»\n "
    return {
        "doc_id": doc_id,
        "title": "Misión de prueba",
        "source": "Fuente de prueba",
        "url": "https://example.org/mision",
        "text": text,
        "word_count": word_count,
        "language": "es",
        "original_format": "html",
        "revision_url": "https://example.org/revision/123",
        "revision_id": 123,
        "attribution": "Autores",
        "license": "CC BY-SA 4.0",
        "license_url": "https://example.org/licencia",
        "extra": {"etiquetas": ["espacio", "misión"], "revisado": None},
    }


def write_fixture(directory, documents):
    """Escribe el formato de índice plano que utiliza el corpus original."""
    index = []
    for i, document in enumerate(documents):
        filename = f"documentos/{i}.json"
        path = directory / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        index.append({"doc_id": document["doc_id"], "file": filename})
    (directory / "indice.json").write_text(json.dumps(index), encoding="utf-8")


class SegmentTests(unittest.TestCase):
    def assert_document_chunks(self, document, chunks):
        """Comprueba cobertura, límites, texto, metadatos, páginas e identificadores."""
        text = document["text"]
        words = list(WORD.finditer(text))
        word_count = len(words)
        starts = {word.start(): i for i, word in enumerate(words)}
        metadata = {
            key: value for key, value in document.items()
            if key not in ("text", "word_count", "page_offsets")
        }
        self.assertTrue(chunks, document["doc_id"])
        self.assertEqual(chunks[0]["char_start"], 0)
        self.assertEqual(chunks[-1]["char_end"], len(text))
        self.assertEqual(len({chunk["chunk_id"] for chunk in chunks}), len(chunks))
        if word_count <= 400:
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0]["text"], text)

        previous = None
        previous_word_end = None
        reconstructed = ""
        for number, chunk in enumerate(chunks, start=1):
            start, end = chunk["char_start"], chunk["char_end"]
            self.assertLessEqual(0, start)
            self.assertLessEqual(start, end)
            self.assertLessEqual(end, len(text))
            self.assertEqual(chunk["text"], text[start:end])
            self.assertEqual(chunk["word_count"], len(WORD.findall(chunk["text"])))
            self.assertEqual(chunk["chunk_id"], f"{document['doc_id']}__{number:04d}")
            self.assertEqual(chunk["chunk_index"], number)
            self.assertEqual({key: chunk[key] for key in metadata}, metadata)
            if word_count > 400:
                self.assertGreaterEqual(chunk["word_count"], 200)
                self.assertLessEqual(chunk["word_count"], 400)

            pages = [
                page["page"] for page in document.get("page_offsets", [])
                if max(start, page["start"]) < min(end, page["end"])
            ]
            if pages:
                self.assertEqual(chunk["pages"], pages)
            else:
                self.assertNotIn("pages", chunk)

            word_start = 0 if start == 0 else starts[start]
            word_end = word_count if end == len(text) else starts[end]
            self.assertEqual(chunk["word_count"], word_end - word_start)
            if previous is not None:
                self.assertGreater(start, previous["char_start"])
                self.assertGreater(end, previous["char_end"])
                self.assertLessEqual(start, previous["char_end"])
                self.assertEqual(previous_word_end - word_start, 45)
                overlap_end = previous["char_end"] - start
                self.assertEqual(chunk["text"][:overlap_end], text[start:previous["char_end"]])
                reconstructed += chunk["text"][overlap_end:]
            else:
                reconstructed = chunk["text"]
            previous = chunk
            previous_word_end = word_end
        self.assertEqual(reconstructed, text)

    def test_short_documents_are_preserved_whole(self):
        for word_count in (0, 1, 28, 199, 200, 299, 300, 301, 399, 400):
            with self.subTest(words=word_count):
                document = make_document(word_count)
                self.assert_document_chunks(document, list(segment(document)))

    def test_empty_and_nonlexical_text_are_preserved(self):
        for text in ("", " \t\r\n", "…!? — 🚀"):
            with self.subTest(text=text):
                document = {**make_document(0), "text": text}
                self.assert_document_chunks(document, list(segment(document)))

    def test_all_lengths_and_repeated_tail_boundaries(self):
        # Barre todos los restos posibles durante varios saltos de 255 palabras.
        for word_count in range(401, 2501):
            with self.subTest(words=word_count):
                document = make_document(word_count)
                self.assert_document_chunks(document, list(segment(document)))

    def test_tail_is_kept_absorbed_or_balanced(self):
        expected_sizes = {
            401: [223, 223],
            402: [224, 223],
            454: [250, 249],
            455: [300, 200],
            500: [300, 245],
            554: [300, 299],
            555: [300, 300],
            556: [300, 301],
            655: [300, 400],
            656: [300, 223, 223],
            709: [300, 250, 249],
            710: [300, 300, 200],
            809: [300, 300, 299],
        }
        for word_count, expected in expected_sizes.items():
            with self.subTest(words=word_count):
                chunks = list(segment(make_document(word_count)))
                self.assertEqual([chunk["word_count"] for chunk in chunks], expected)

    def test_large_document_has_no_redundant_ranges(self):
        document = make_document(10000)
        self.assert_document_chunks(document, list(segment(document)))

    def test_unicode_punctuation_and_original_spacing(self):
        document = make_document(0)
        document["text"] = " \r\n«" + (
            "Órbita lunar; l’exploration, don't, co-operación…\t🚀\n\n" * 101
        ) + "»\t\n"
        document["word_count"] = -1  # El recuento se calcula a partir del texto.
        self.assert_document_chunks(document, list(segment(document)))

    def test_metadata_and_pages_across_chunk_boundaries(self):
        document = make_document(809)
        words = list(WORD.finditer(document["text"]))
        boundaries = (0, words[270].start(), words[550].start(), len(document["text"]))
        document.update({
            "original_format": "pdf",
            "total_pages": 3,
            "pages_with_text": 3,
            "download_url": "https://example.org/mision.pdf",
            "page_offsets": [
                {"page": i + 1, "start": start, "end": end}
                for i, (start, end) in enumerate(zip(boundaries, boundaries[1:]))
            ],
        })
        chunks = list(segment(document))
        self.assert_document_chunks(document, chunks)
        self.assertEqual([chunk["pages"] for chunk in chunks], [[1, 2], [1, 2, 3], [2, 3]])

    def test_pages_touching_boundary_are_not_included(self):
        document = make_document(455)
        words = list(WORD.finditer(document["text"]))
        boundary = words[300].start()
        document["page_offsets"] = [
            {"page": 1, "start": 0, "end": boundary},
            {"page": 2, "start": boundary, "end": len(document["text"])},
        ]
        chunks = list(segment(document))
        self.assert_document_chunks(document, chunks)
        self.assertEqual(chunks[0]["pages"], [1])
        self.assertEqual(chunks[1]["pages"], [1, 2])

    def test_exact_argument_no_longer_discards_content(self):
        for word_count in (0, 28, 299, 400, 401, 556):
            with self.subTest(words=word_count):
                document = make_document(word_count)
                self.assertEqual(list(segment(document, True)), list(segment(document, False)))

    def test_identifiers_are_unique_across_documents(self):
        ids = []
        for doc_id, size in (("doc_1", 28), ("doc_2", 401), ("doc_3", 809)):
            document = make_document(size, doc_id)
            chunks = list(segment(document))
            self.assert_document_chunks(document, chunks)
            ids.extend(chunk["chunk_id"] for chunk in chunks)
        self.assertEqual(len(ids), len(set(ids)))


class WriteChunksTests(unittest.TestCase):
    def test_directory_and_zip_produce_identical_jsonl_and_totals(self):
        documents = [make_document(n, f"doc_{i}") for i, n in enumerate((28, 401, 809))]
        expected = [chunk for doc in documents for chunk in segment(doc)]
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            corpus = root / "corpus"
            write_fixture(corpus, documents)
            archive = root / "corpus.zip"
            with ZipFile(archive, "w") as zipped:
                for path in corpus.rglob("*.json"):
                    zipped.write(path, path.relative_to(corpus).as_posix())
            for source in (corpus, archive):
                with self.subTest(source=source):
                    output = root / f"{source.name}.jsonl"
                    totals = write_chunks(source, output)
                    self.assertEqual(totals, (3, 6, 4, 0))
                    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
                    self.assertEqual(rows, expected)

    def test_existing_output_is_not_overwritten(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "existing.jsonl"
            output.write_bytes(b"contenido previo\n")
            with self.assertRaises(FileExistsError):
                write_chunks(root / "missing.zip", output)
            self.assertEqual(output.read_bytes(), b"contenido previo\n")

    def test_duplicate_and_inconsistent_ids_leave_no_partial_output(self):
        for inconsistent in (False, True):
            with self.subTest(inconsistent=inconsistent), TemporaryDirectory() as temporary:
                root = Path(temporary)
                corpus = root / "corpus"
                write_fixture(corpus, [make_document(28), make_document(401)])
                if inconsistent:
                    index_path = corpus / "indice.json"
                    index = json.loads(index_path.read_text(encoding="utf-8"))
                    index[0]["doc_id"] = "otro_id"
                    index_path.write_text(json.dumps(index), encoding="utf-8")
                output = root / "salida.jsonl"
                with self.assertRaisesRegex(ValueError, "Identificador duplicado o inconsistente"):
                    write_chunks(corpus, output)
                self.assertFalse(output.exists())
                self.assertEqual(list(root.glob("*.tmp")), [])

    def test_cli_exactos_warns_and_preserves_all_documents(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            corpus = root / "corpus"
            write_fixture(corpus, [make_document(28, "corto"), make_document(556, "largo")])
            normal = root / "normal.jsonl"
            compatible = root / "exactos.jsonl"
            for output, flags in ((normal, []), (compatible, ["--exactos"])):
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), str(corpus), str(output), *flags],
                    capture_output=True, text=True, encoding="utf-8",
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("2 documentos | 3 fragmentos", result.stdout)
                self.assertIn("1 fragmentos de menos de 300 palabras", result.stdout)
                if flags:
                    self.assertIn("--exactos está obsoleto", result.stderr)
                else:
                    self.assertEqual(result.stderr, "")
            self.assertEqual(normal.read_bytes(), compatible.read_bytes())

    def test_legacy_index_by_decade_is_still_readable(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = {
                "id": "mision_1", "titulo": "Misión", "fuente": "Fuente",
                "url_fuente": "https://example.org/mision", "resumen": " Resumen. ",
                "secciones": [{"titulo": "Sección", "texto": "Texto.\n"}],
            }
            (root / "indice.json").write_text(json.dumps({
                "misiones": [{"id": "mision_1", "archivo": "mision.json"}]
            }), encoding="utf-8")
            (root / "mision.json").write_text(json.dumps(source), encoding="utf-8")
            documents = list(read_documents(root))
            self.assertEqual(len(documents), 1)
            doc_id, document = documents[0]
            self.assertEqual(doc_id, document["doc_id"])
            self.assertEqual(document["text"], " Resumen. \n\nSección\nTexto.\n")
            self.assertEqual(list(segment(document))[0]["text"], document["text"])


if __name__ == "__main__":
    unittest.main()
