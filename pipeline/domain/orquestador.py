"""Orquestador del pipeline: el DAG de stages (depende solo de dominio + puertos).

Orden: GATE DE DERECHOS -> transcripcion -> subtitulos -> visual -> ensamblado.
Idempotente y resumible: si el artefacto de un stage ya existe, se reusa (ADR-002).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from . import derechos
from .entities import (
    Autorizacion,
    EstadoJob,
    EstadoStage,
    Fuente,
    Job,
    Rastro,
    Receta,
    Recorte,
    Short,
)
from .ports import PuertoEnsamblado, PuertoSubtitulos, PuertoTranscripcion, PuertoVisual

DIVULGACION_IA = "Contenido generado con IA"


class Orquestador:
    def __init__(
        self,
        transcriptor: PuertoTranscripcion,
        subtitulador: PuertoSubtitulos,
        visualizador: PuertoVisual,
        ensamblador: PuertoEnsamblado,
        dir_trabajo: Path,
    ) -> None:
        self._transcriptor = transcriptor
        self._subtitulador = subtitulador
        self._visualizador = visualizador
        self._ensamblador = ensamblador
        self._dir = dir_trabajo

    def generar_short(
        self,
        fuente: Fuente,
        autorizacion: Autorizacion,
        recorte: Recorte,
        receta: Receta,
        audio_recorte: Path,
        hoy: date | None = None,
    ) -> tuple[Short, Rastro, Job]:
        job = Job(id=self._job_id(fuente, receta), fuente_id=fuente.id, receta_id=receta.id)
        self._dir.mkdir(parents=True, exist_ok=True)

        # --- STAGE 0: GATE DE DERECHOS (precondicion dura, ADR-009) ----------
        try:
            derechos.verificar(fuente, autorizacion, hoy)
        except derechos.AutorizacionInvalida:
            job.estado = EstadoJob.RECHAZADO_DERECHOS
            raise
        job.marcar("derechos", EstadoStage.HECHO)
        job.estado = EstadoJob.EN_PROCESO

        # --- STAGE 1: transcripcion (checkpointable) -------------------------
        ruta_segmentos = self._dir / "segmentos.json"
        if ruta_segmentos.exists():
            segmentos = self._cargar_segmentos(ruta_segmentos)
        else:
            segmentos = self._transcriptor.transcribir(audio_recorte)
            self._guardar_segmentos(ruta_segmentos, segmentos)
        job.marcar("transcripcion", EstadoStage.HECHO)

        # --- STAGE 2: subtitulos --------------------------------------------
        ruta_ass = self._dir / "subtitulos.ass"
        self._subtitulador.generar(segmentos, receta, ruta_ass, DIVULGACION_IA)
        job.marcar("subtitulos", EstadoStage.HECHO)

        # --- STAGE 3: visual determinista (puerto intercambiable, H-2) -------
        spec = self._visualizador.preparar(receta)
        job.marcar("visual", EstadoStage.HECHO)

        # --- STAGE 4: ensamblado 9:16 + divulgacion (ffmpeg) ----------------
        ruta_video = self._dir / "short.mp4"
        self._ensamblador.ensamblar(audio_recorte, spec, ruta_ass, receta, ruta_video)
        job.marcar("ensamblado", EstadoStage.HECHO)

        # --- Cierre: Short en revision (gate de QC humano, H-5) --------------
        job.estado = EstadoJob.EN_REVISION
        short = Short(
            job_id=job.id, ruta_video=ruta_video, duracion_s=recorte.timecode.duracion_s
        )
        rastro = Rastro(
            job_id=job.id,
            fuente_id=fuente.id,
            fuente_sha256=fuente.sha256,
            autorizacion_id=autorizacion.id,
            autorizacion_tipo=autorizacion.tipo.value,
            receta_id=receta.id,
            receta_version=receta.version,
            semilla=receta.semilla,
            estilo=receta.estilo,
            divulgacion_ia=True,
            stages={k: v.value for k, v in job.stages.items()},
        )
        self._guardar_rastro(rastro)
        return short, rastro, job

    # ------------------------------------------------------------------ utils
    def _job_id(self, fuente: Fuente, receta: Receta) -> str:
        return f"{fuente.id}__{receta.id}_v{receta.version}_s{receta.semilla}"

    def _guardar_segmentos(self, ruta: Path, segmentos: list) -> None:
        ruta.write_text(
            json.dumps(
                [{"inicio_s": s.inicio_s, "fin_s": s.fin_s, "texto": s.texto} for s in segmentos],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _cargar_segmentos(self, ruta: Path) -> list:
        from .entities import SegmentoTranscrito

        data = json.loads(ruta.read_text(encoding="utf-8"))
        return [SegmentoTranscrito(**d) for d in data]

    def _guardar_rastro(self, rastro: Rastro) -> None:
        (self._dir / "rastro.json").write_text(
            json.dumps(rastro.__dict__, ensure_ascii=False, indent=2), encoding="utf-8"
        )
