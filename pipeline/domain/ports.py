"""Puertos: interfaces que el dominio define y la infraestructura implementa.

El dominio dice QUE stages y en QUE orden; la infra dice COMO. Cada stage es
intercambiable (modelo local <-> API serverless) sin tocar el orquestador.
Ver SAD H-2: el PuertoEjecutor deberia tener serverless como default.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .entities import Receta, Recorte, SegmentoTranscrito


class PuertoTranscripcion(Protocol):
    """Whisper u otro: audio del recorte -> segmentos con tiempos relativos."""

    def transcribir(self, audio_recorte: Path) -> list[SegmentoTranscrito]: ...


class PuertoSubtitulos(Protocol):
    """Segmentos -> archivo de subtitulos estilizado (ASS)."""

    def generar(
        self, segmentos: list[SegmentoTranscrito], receta: Receta, destino: Path, divulgacion: str
    ) -> Path: ...


class EspecVisual(Protocol):
    """Resultado deterministico del stage visual: el 'look' derivado de la semilla."""

    color_0: str
    color_1: str
    color_onda: str


class PuertoVisual(Protocol):
    """Decide el look determinista del fondo a partir de receta+semilla.

    Implementacion MVP: fondo generado determinista ($0, sin GPU).
    Intercambiable por Diffusers/ComfyUI headless detras del mismo puerto.
    """

    def preparar(self, receta: Receta) -> EspecVisual: ...


class PuertoEnsamblado(Protocol):
    """ffmpeg: audio + visual + subtitulos + divulgacion -> mp4 9:16."""

    def ensamblar(
        self,
        audio_recorte: Path,
        spec: EspecVisual,
        subtitulos_ass: Path,
        receta: Receta,
        destino: Path,
    ) -> Path: ...
