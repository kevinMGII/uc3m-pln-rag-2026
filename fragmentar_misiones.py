#!/usr/bin/env python3
"""
Descomprime los ZIP de misiones espaciales y genera fragmentos para indexación.

Pasos:
  1. Descomprime todos los .zip de la carpeta `datos_zip` en `datos_brutos`.
  2. Lee cada JSON de misión (se ignora indice.json).
  3. Asigna a cada documento un identificador estable (doc_0001, doc_0002, ...).
  4. Divide el texto (resumen + secciones) en fragmentos de ~300 palabras con un
     15 % de solapamiento (paso de 255 palabras). Los documentos de 300 palabras
     o menos se guardan como un único fragmento.
  5. Escribe en `fragmentos_base`:
       - fragmentos.jsonl : un fragmento por línea (doc_id, chunk_id, texto, ...)
       - documentos.jsonl : un documento por línea (doc_id, título, metadatos)
       - estadisticas.json: resumen de la fragmentación

Uso:
    python fragmentar_misiones.py
    python fragmentar_misiones.py --tamano 300 --solapamiento 0.15 --incluir-ficha

Solo usa la biblioteca estándar de Python (3.8+).
"""

import argparse
import json
import math
import statistics
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Descompresión
# ---------------------------------------------------------------------------
def descomprimir_zips(carpeta_zip: Path, carpeta_destino: Path) -> int:
    """Descomprime todos los .zip de `carpeta_zip` en `carpeta_destino`.

    Comprueba que ningún archivo del ZIP intente escribirse fuera de la carpeta
    de destino (protección contra rutas maliciosas tipo "../").
    """
    if not carpeta_zip.is_dir():
        raise FileNotFoundError(
            f"No existe la carpeta '{carpeta_zip}'.\n"
            f"Crea una carpeta llamada '{carpeta_zip.name}' junto al script y mete ahí los ZIP."
        )
    # Busca también en subcarpetas (por si los ZIP quedaron dentro de otra carpeta)
    zips = sorted(carpeta_zip.rglob("*.zip"), key=lambda p: p.name)
    if not zips:
        contenido = [p.name for p in carpeta_zip.iterdir()][:20]
        raise FileNotFoundError(
            f"No se encontraron archivos .zip en '{carpeta_zip}'.\n"
            f"Contenido actual de la carpeta: {contenido if contenido else '(vacía)'}"
        )

    carpeta_destino.mkdir(parents=True, exist_ok=True)
    destino_abs = carpeta_destino.resolve()

    for ruta_zip in zips:
        with zipfile.ZipFile(ruta_zip) as zf:
            for miembro in zf.infolist():
                ruta_final = (carpeta_destino / miembro.filename).resolve()
                if destino_abs not in ruta_final.parents and ruta_final != destino_abs:
                    raise ValueError(f"Ruta no permitida en {ruta_zip.name}: {miembro.filename}")
            zf.extractall(carpeta_destino)
        print(f"  Descomprimido: {ruta_zip.name}")
    return len(zips)


# ---------------------------------------------------------------------------
# 2. Lectura de documentos
# ---------------------------------------------------------------------------
def texto_documento(doc: dict, incluir_ficha: bool) -> str:
    """Construye el texto plano del documento: resumen + secciones (+ ficha)."""
    partes = []
    if doc.get("resumen"):
        partes.append(doc["resumen"])
    for seccion in doc.get("secciones", []):
        titulo = seccion.get("titulo", "").strip()
        texto = seccion.get("texto", "").strip()
        if titulo:
            partes.append(titulo)
        if texto:
            partes.append(texto)
    if incluir_ficha and doc.get("ficha_tecnica"):
        ficha = "\n".join(f"{k}: {v}" for k, v in doc["ficha_tecnica"].items())
        partes.append(ficha)
    return "\n".join(partes)


def cargar_documentos(carpeta_brutos: Path) -> list:
    """Devuelve la lista de (ruta_relativa, contenido_json) ordenada por ruta."""
    rutas = sorted(
        p for p in carpeta_brutos.rglob("*.json") if p.name != "indice.json"
    )
    documentos = []
    for ruta in rutas:
        with open(ruta, encoding="utf-8") as f:
            documentos.append((ruta.relative_to(carpeta_brutos).as_posix(), json.load(f)))
    return documentos


# ---------------------------------------------------------------------------
# 3. Fragmentación
# ---------------------------------------------------------------------------
def fragmentar(palabras: list, tamano: int, solapamiento: float) -> list:
    """Divide una lista de palabras en ventanas de `tamano` con solapamiento.

    Devuelve una lista de tuplas (inicio, fin) en índices de palabra.
    """
    n = len(palabras)
    if n == 0:
        return []
    if n <= tamano:
        return [(0, n)]
    paso = tamano - round(tamano * solapamiento)
    num_fragmentos = 1 + math.ceil((n - tamano) / paso)
    return [(i * paso, min(i * paso + tamano, n)) for i in range(num_fragmentos)]


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Descomprime y fragmenta las misiones espaciales.")
    parser.add_argument("--zip", default="datos_zip", help="Carpeta con los ZIP (por defecto: datos_zip)")
    parser.add_argument("--brutos", default="datos_brutos", help="Carpeta de descompresión (por defecto: datos_brutos)")
    parser.add_argument("--salida", default="fragmentos_base", help="Carpeta de salida (por defecto: fragmentos_base)")
    parser.add_argument("--tamano", type=int, default=300, help="Palabras por fragmento (por defecto: 300)")
    parser.add_argument("--solapamiento", type=float, default=0.15, help="Solapamiento entre 0 y 1 (por defecto: 0.15)")
    parser.add_argument("--incluir-ficha", action="store_true", help="Añade el texto de la ficha técnica al documento")
    args = parser.parse_args()

    if not 0 <= args.solapamiento < 1:
        parser.error("--solapamiento debe estar entre 0 y 1 (por ejemplo 0.15)")

    # Las rutas relativas se interpretan respecto a la carpeta donde está este script,
    # no respecto a la carpeta desde la que se ejecuta (p. ej., VS Code o PyCharm).
    base = Path(__file__).resolve().parent
    carpeta_zip = (base / args.zip).resolve()
    carpeta_brutos = (base / args.brutos).resolve()
    carpeta_salida = (base / args.salida).resolve()

    print(f"1) Descomprimiendo ZIP de '{carpeta_zip}' en '{carpeta_brutos}'...")
    num_zips = descomprimir_zips(carpeta_zip, carpeta_brutos)

    print("2) Leyendo documentos...")
    documentos = cargar_documentos(carpeta_brutos)
    print(f"  {len(documentos)} documentos encontrados")

    print(f"3) Fragmentando ({args.tamano} palabras, {args.solapamiento:.0%} de solapamiento)...")
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_fragmentos = carpeta_salida / "fragmentos.jsonl"
    ruta_documentos = carpeta_salida / "documentos.jsonl"

    fragmentos_por_doc = []
    palabras_por_fragmento = []
    total_fragmentos = 0

    with open(ruta_fragmentos, "w", encoding="utf-8") as f_frag, \
         open(ruta_documentos, "w", encoding="utf-8") as f_docs:
        for i, (ruta_rel, doc) in enumerate(documentos, start=1):
            doc_id = f"doc_{i:04d}"
            palabras = texto_documento(doc, args.incluir_ficha).split()
            ventanas = fragmentar(palabras, args.tamano, args.solapamiento)

            for j, (ini, fin) in enumerate(ventanas, start=1):
                fragmento = {
                    "chunk_id": f"{doc_id}_c{j:02d}",
                    "doc_id": doc_id,
                    "titulo": doc.get("titulo"),
                    "posicion": j,
                    "total_fragmentos_doc": len(ventanas),
                    "palabra_inicio": ini,
                    "palabra_fin": fin,
                    "num_palabras": fin - ini,
                    "texto": " ".join(palabras[ini:fin]),
                }
                f_frag.write(json.dumps(fragmento, ensure_ascii=False) + "\n")
                palabras_por_fragmento.append(fin - ini)

            f_docs.write(json.dumps({
                "doc_id": doc_id,
                "titulo": doc.get("titulo"),
                "archivo": ruta_rel,
                "fecha_lanzamiento": doc.get("fecha_lanzamiento"),
                "estado": doc.get("estado"),
                "tipo_mision": doc.get("tipo_mision"),
                "idioma_original": doc.get("idioma_original"),
                "url_fuente": doc.get("url_fuente"),
                "num_palabras": len(palabras),
                "num_fragmentos": len(ventanas),
            }, ensure_ascii=False) + "\n")

            fragmentos_por_doc.append(len(ventanas))
            total_fragmentos += len(ventanas)

    estadisticas = {
        "zips_descomprimidos": num_zips,
        "documentos": len(documentos),
        "fragmentos": total_fragmentos,
        "tamano_fragmento": args.tamano,
        "solapamiento": args.solapamiento,
        "paso_palabras": args.tamano - round(args.tamano * args.solapamiento),
        "incluye_ficha": args.incluir_ficha,
        "documentos_con_un_solo_fragmento": sum(1 for n in fragmentos_por_doc if n == 1),
        "max_fragmentos_por_documento": max(fragmentos_por_doc, default=0),
        "media_fragmentos_por_documento": round(statistics.mean(fragmentos_por_doc), 2) if fragmentos_por_doc else 0,
        "media_palabras_por_fragmento": round(statistics.mean(palabras_por_fragmento), 1) if palabras_por_fragmento else 0,
    }
    with open(carpeta_salida / "estadisticas.json", "w", encoding="utf-8") as f:
        json.dump(estadisticas, f, ensure_ascii=False, indent=2)

    print("Listo.")
    print(f"  Documentos: {estadisticas['documentos']}")
    print(f"  Fragmentos: {estadisticas['fragmentos']}")
    print(f"  Salida en '{carpeta_salida}': fragmentos.jsonl, documentos.jsonl, estadisticas.json")


if __name__ == "__main__":
    main()