"""Imagenes stand-in por escena para probar el ensamblado animado sin Colab.

NO es generacion por IA: son gradientes deterministas, uno por escena, con la
paleta del estilo. Sirven para validar HOY el movimiento + la composicion; el
notebook de Colab los reemplaza por las imagenes reales de Diffusers (mismo path).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Escena, Receta
from .visual_fondo import _PALETAS


def generar_stubs(escenas: list[Escena], receta: Receta, escenas_dir: Path) -> None:
    escenas_dir.mkdir(parents=True, exist_ok=True)
    paletas = _PALETAS.get(receta.estilo, _PALETAS["minimal"])
    w, h = 512, 896
    for e in escenas:
        c0, c1, _onda = paletas[e.semilla % len(paletas)]
        salida = escenas_dir / e.nombre_artefacto
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"gradients=s={w}x{h}:c0={c0}:c1={c1}:x0=0:y0=0:x1={w}:y1={h}:d=1:r=1",
                "-frames:v", "1", str(salida.resolve()),
            ],
            check=True, capture_output=True, text=True,
        )
