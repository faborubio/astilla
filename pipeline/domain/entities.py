"""Entidades y value objects del dominio (stdlib-only).

Idioma del dominio en espanol (convencion 2.3): Fuente, Autorizacion, Recorte,
Receta, Escena, Job, Short, Rastro.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path


# --------------------------------------------------------------------------- #
# Value objects                                                               #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Timecode:
    """Recorte temporal dentro de la fuente, en segundos."""

    inicio_s: float
    fin_s: float

    def __post_init__(self) -> None:
        if self.inicio_s < 0 or self.fin_s <= self.inicio_s:
            raise ValueError(f"Timecode invalido: [{self.inicio_s}, {self.fin_s}]")

    @property
    def duracion_s(self) -> float:
        return self.fin_s - self.inicio_s


@dataclass(frozen=True)
class Formato:
    """Formato de salida. Default 9:16 vertical 1080x1920 @ 30fps."""

    ancho: int = 1080
    alto: int = 1920
    fps: int = 30

    @property
    def es_vertical(self) -> bool:
        return self.alto > self.ancho


@dataclass(frozen=True)
class Receta:
    """Estilo + formato + semilla. Unidad versionada de reproduccion (ADR-008).

    El estilo decide la paleta determinista del visual; la semilla fija toda la
    generacion. (receta, fuente, semilla) -> mismo short en el mismo entorno.
    """

    id: str
    version: int
    estilo: str  # "neon" | "comic" | "minimal"
    semilla: int
    formato: Formato = field(default_factory=Formato)


# --------------------------------------------------------------------------- #
# Autorizacion — la precondicion dura (ADR-009)                                #
# --------------------------------------------------------------------------- #
class TipoAutorizacion(str, Enum):
    CLIENTE = "cliente"
    LICENCIA = "licencia"
    DOMINIO_PUBLICO = "dominio_publico"
    ORIGINAL = "original"


@dataclass(frozen=True)
class Autorizacion:
    """PRECONDICION de ejecucion. Sin una valida y vigente, nada se procesa."""

    id: str
    fuente_id: str
    tipo: TipoAutorizacion
    titular: str
    evidencia: str  # referencia (contrato, licencia, "contenido original"), no el contenido legal
    vigente_hasta: date | None = None  # None = sin vencimiento

    def es_vigente(self, hoy: date) -> bool:
        return self.vigente_hasta is None or hoy <= self.vigente_hasta


# --------------------------------------------------------------------------- #
# Fuente y derivados                                                           #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Fuente:
    """Contenido largo as-ingested. El hash congela el snapshot (ADR-005)."""

    id: str
    titulo: str
    ruta_audio: Path
    sha256: str

    @staticmethod
    def desde_archivo(id: str, titulo: str, ruta_audio: Path) -> "Fuente":
        h = hashlib.sha256(ruta_audio.read_bytes()).hexdigest()
        return Fuente(id=id, titulo=titulo, ruta_audio=ruta_audio, sha256=h)


@dataclass(frozen=True)
class Recorte:
    """Segmento (anecdota) seleccionado de la fuente. Operator-driven (H-4)."""

    fuente_id: str
    timecode: Timecode


@dataclass(frozen=True)
class SegmentoTranscrito:
    """Tramo de texto con tiempos relativos al recorte (no a la fuente)."""

    inicio_s: float
    fin_s: float
    texto: str


@dataclass(frozen=True)
class PalabraTranscrita:
    """Palabra con timestamp propio. Base de los subtitulos karaoke (resaltado por palabra)."""

    inicio_s: float
    fin_s: float
    texto: str


@dataclass(frozen=True)
class Escena:
    """Unidad de render: prompt + tiempo + semilla. El checkpoint es por escena (ADR-002)."""

    indice: int
    inicio_s: float
    fin_s: float
    texto: str
    prompt: str
    semilla: int

    @property
    def duracion_s(self) -> float:
        return self.fin_s - self.inicio_s

    @property
    def nombre_artefacto(self) -> str:
        return f"escena_{self.indice:02d}.png"

    @property
    def nombre_clip(self) -> str:
        return f"escena_{self.indice:02d}.mp4"


# --------------------------------------------------------------------------- #
# Job / Short / Rastro                                                         #
# --------------------------------------------------------------------------- #
class EstadoStage(str, Enum):
    PENDIENTE = "pendiente"
    HECHO = "hecho"


class EstadoJob(str, Enum):
    CREADO = "creado"
    RECHAZADO_DERECHOS = "rechazado_derechos"
    EN_PROCESO = "en_proceso"
    EN_REVISION = "en_revision"  # gate de QC humano (H-5)
    COMPLETADO = "completado"


@dataclass
class Job:
    """Ejecucion del pipeline con estado por stage y checkpoints (ADR-002)."""

    id: str
    fuente_id: str
    receta_id: str
    estado: EstadoJob = EstadoJob.CREADO
    stages: dict[str, EstadoStage] = field(default_factory=dict)

    def marcar(self, stage: str, estado: EstadoStage) -> None:
        self.stages[stage] = estado

    def stage_hecho(self, stage: str) -> bool:
        return self.stages.get(stage) == EstadoStage.HECHO


@dataclass(frozen=True)
class Short:
    """Salida 9:16, artefacto inmutable."""

    job_id: str
    ruta_video: Path
    duracion_s: float


@dataclass
class Rastro:
    """Linaje del short: fuente, autorizacion, receta, semilla, divulgacion."""

    job_id: str
    fuente_id: str
    fuente_sha256: str
    autorizacion_id: str
    autorizacion_tipo: str
    receta_id: str
    receta_version: int
    semilla: int
    estilo: str
    divulgacion_ia: bool
    stages: dict[str, str] = field(default_factory=dict)
