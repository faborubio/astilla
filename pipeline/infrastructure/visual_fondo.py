"""Adaptador visual MVP: fondo determinista derivado de (estilo + semilla).

Implementa PuertoVisual. NO usa GPU: el 'look' sale de la receta, no de difusion.
Esta es la pieza intercambiable clave (SAD H-1/H-2): manana este puerto lo cumple
un GeneradorDiffusers (serverless por default) sin tocar el orquestador.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..domain.entities import Receta

# Paletas base por estilo: (color_0, color_1, color_onda). Hex 0xRRGGBB para ffmpeg.
_PALETAS: dict[str, list[tuple[str, str, str]]] = {
    "neon": [
        ("0x1a0b2e", "0x3b0f6f", "0x00e5ff"),
        ("0x0d1b3d", "0x4a148c", "0x18ffff"),
        ("0x2b0a3d", "0x1565c0", "0x64ffda"),
    ],
    "comic": [
        ("0x3d1500", "0xb71c1c", "0xffd54f"),
        ("0x4a1c00", "0xe65100", "0xfff176"),
        ("0x2d0a00", "0xc62828", "0xffeb3b"),
    ],
    "minimal": [
        ("0x0a0a0a", "0x2b2b2b", "0xffffff"),
        ("0x111316", "0x30363d", "0xe0e0e0"),
        ("0x0d0d12", "0x26262e", "0xf5f5f5"),
    ],
}


@dataclass(frozen=True)
class EspecVisualFondo:
    color_0: str
    color_1: str
    color_onda: str


class GeneradorFondoDeterminista:
    def preparar(self, receta: Receta) -> EspecVisualFondo:
        paletas = _PALETAS.get(receta.estilo, _PALETAS["minimal"])
        # La semilla elige la variante de paleta de forma determinista (ADR-006).
        variante = paletas[receta.semilla % len(paletas)]
        return EspecVisualFondo(color_0=variante[0], color_1=variante[1], color_onda=variante[2])
