"""Rutas por-carpeta de cada short (una carpeta = un short).

Convencion nueva (jul 2026): cada short vive en `artifacts/shorts/<nombre>/` con
nombres de archivo FIJOS dentro (voz.wav, guion.txt, segmentos.json, ...). Esto
ordena el despelote de artifacts/ raiz y de paso mata el gotcha 11 (el
`segmentos.json` compartido que se reusaba a ciegas): ahora cada checkpoint es
propio de su carpeta, imposible de confundir entre shorts.

Uso:
    from rutas import RutasShort
    r = RutasShort("arquero")
    r.voz, r.guion, r.segmentos, r.visual_job, r.palabras, r.subs, r.bed,
    r.clips (dir), r.short, r.short_musica, r.prompts
"""
from __future__ import annotations

from pathlib import Path

ART = Path("artifacts")
SHORTS = ART / "shorts"


class RutasShort:
    """Rutas estandar de un short. `crear=True` crea la carpeta (y clips/)."""

    def __init__(self, nombre: str, crear: bool = False) -> None:
        self.nombre = nombre
        self.dir = SHORTS / nombre
        if crear:
            self.clips.mkdir(parents=True, exist_ok=True)

    @property
    def voz(self) -> Path: return self.dir / "voz.wav"
    @property
    def voz_orig(self) -> Path: return self.dir / "voz_orig.wav"
    @property
    def guion(self) -> Path: return self.dir / "guion.txt"
    @property
    def prompts(self) -> Path: return self.dir / "prompts.json"
    @property
    def segmentos(self) -> Path: return self.dir / "segmentos.json"
    @property
    def visual_job(self) -> Path: return self.dir / "visual_job.json"
    @property
    def palabras(self) -> Path: return self.dir / "palabras.json"
    @property
    def subs(self) -> Path: return self.dir / "subs.ass"
    @property
    def bed(self) -> Path: return self.dir / "bed.mp4"
    @property
    def clips(self) -> Path: return self.dir / "clips"
    @property
    def short(self) -> Path: return self.dir / "short.mp4"
    @property
    def short_musica(self) -> Path: return self.dir / "short_musica.mp4"
