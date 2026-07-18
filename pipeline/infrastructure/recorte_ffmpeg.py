"""Extrae el audio del recorte (anecdota) de la fuente, con ffmpeg.

Operator-driven (H-4): el operador da el timecode. Los tiempos del recorte
quedan relativos a 0, de modo que los subtitulos calzan con el clip.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Recorte


def extraer_recorte(fuente_audio: Path, recorte: Recorte, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(recorte.timecode.inicio_s),
            "-to", str(recorte.timecode.fin_s),
            "-i", str(fuente_audio),
            "-ac", "1", "-ar", "16000",
            str(destino),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return destino
