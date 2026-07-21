"""Exporta la voz hablada de un short desde el archivo maestro a su guion.txt.

El maestro `artifacts/guiones.md` es la UNICA superficie que se edita a mano:
tiene, por short, titulo + hashtags + guion. El pipeline en cambio consume
`artifacts/shorts/<n>/guion.txt`, que debe ser SOLO la voz hablada (la "verdad"
que sesga a Whisper). Este script deriva ese guion.txt de la seccion del maestro,
para que nunca haya dos copias del texto desincronizadas (una sola fuente).

Uso:
    python scripts/exportar_guion.py --nombre manavai
    python scripts/exportar_guion.py --nombre todas      # exporta todas las secciones
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import ART, RutasShort  # noqa: E402

MAESTRO = ART / "guiones.md"

# Header de seccion: "## 11) NOMBRE  ->  archivo `manavai`  (notas...)"
_HEADER = re.compile(r"^#{1,6}\s.*archivo\s+`([^`]+)`")
_HASHTAGS = re.compile(r"^\*\*Hashtags:", re.IGNORECASE)
_TERMINADOR = re.compile(r"^(---\s*$|#{1,6}\s)")


def _secciones(lineas: list[str]) -> dict[str, tuple[int, int]]:
    """Mapa nombre -> (indice_header, indice_fin_exclusivo)."""
    cabeceras = [(i, m.group(1)) for i, l in enumerate(lineas)
                 if (m := _HEADER.match(l))]
    fuera = {}
    for k, (idx, nombre) in enumerate(cabeceras):
        fin = cabeceras[k + 1][0] if k + 1 < len(cabeceras) else len(lineas)
        fuera[nombre] = (idx, fin)
    return fuera


def _cuerpo(lineas: list[str], ini: int, fin: int) -> str:
    """Voz hablada: todo lo que va DESPUES de la linea de Hashtags hasta el
    terminador (--- o el proximo header), sin lineas de metadata ni blancos guia."""
    # arrancar despues de **Hashtags:**
    j = ini
    while j < fin and not _HASHTAGS.match(lineas[j]):
        j += 1
    if j == fin:
        raise ValueError("no encontre la linea **Hashtags:** en la seccion")
    cuerpo: list[str] = []
    for l in lineas[j + 1:fin]:
        if _TERMINADOR.match(l):
            break
        # ignorar notas de metadata sueltas (blockquotes o **campo:**)
        if l.lstrip().startswith(">") or re.match(r"^\*\*[^*]+:\*\*", l):
            continue
        cuerpo.append(l.rstrip())
    texto = "\n".join(cuerpo).strip()
    if not texto:
        raise ValueError("la seccion no tiene cuerpo de guion")
    return texto + "\n"


def exportar(nombre: str, secs: dict, lineas: list[str]) -> Path:
    if nombre not in secs:
        raise SystemExit(
            f"[exportar_guion] no hay seccion `archivo `{nombre}`` en {MAESTRO}. "
            f"Disponibles: {', '.join(sorted(secs))}")
    ini, fin = secs[nombre]
    texto = _cuerpo(lineas, ini, fin)
    r = RutasShort(nombre, crear=True)
    r.guion.write_text(texto, encoding="utf-8", newline="\n")
    palabras = len(texto.split())
    print(f"[exportar_guion] {nombre}: {palabras} palabras -> {r.guion}")
    return r.guion


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nombre", required=True,
                    help="nombre del short, o 'todas' para exportar todas")
    args = ap.parse_args()

    if not MAESTRO.exists():
        raise SystemExit(f"[exportar_guion] no existe el maestro {MAESTRO}")
    lineas = MAESTRO.read_text(encoding="utf-8").splitlines()
    secs = _secciones(lineas)
    if not secs:
        raise SystemExit(f"[exportar_guion] no encontre secciones en {MAESTRO}")

    objetivos = sorted(secs) if args.nombre == "todas" else [args.nombre]
    for n in objetivos:
        exportar(n, secs, lineas)


if __name__ == "__main__":
    main()
