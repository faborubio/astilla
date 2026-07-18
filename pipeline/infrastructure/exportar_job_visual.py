"""Exporta el job visual que consume el notebook headless de Colab.

Es el 'contrato' entre la orquestacion local y el ejecutor remoto (PuertoEjecutor):
local decide QUE escenas y con que prompt/semilla; Colab solo ejecuta el render.
Resumible: el notebook salta escenas cuya imagen ya existe (ADR-002).
"""
from __future__ import annotations

import json
from pathlib import Path

from ..domain.entities import Escena, Receta
from ..domain.planificacion import NEGATIVO

# Parametros de generacion pensados para T4 16GB (Colab free) con SD 1.5.
# Nota: runwayml/stable-diffusion-v1-5 fue retirado de HF (2024); usamos el mirror.
_GEN = {"width": 512, "height": 896, "steps": 25, "guidance": 7.5, "modelo": "stable-diffusion-v1-5/stable-diffusion-v1-5"}


def exportar_job_visual(
    escenas: list[Escena],
    receta: Receta,
    destino: Path,
    motion: str = "imagen",
    coherencia: dict | None = None,
) -> Path:
    # motion="imagen" -> escena_XX.png (stills + Ken Burns)
    # motion="animatediff" -> escena_XX.mp4 (clip animado por escena)
    # coherencia (CASO-006): {"ip_adapter": bool, "ancla_prompt": str,
    #   "ancla_semilla": int, "ip_scale": float}. El kernel genera el retrato-ancla
    #   y lo aplica a cada escena via IP-Adapter (misma identidad, H-1).
    def archivo(e: Escena) -> str:
        return e.nombre_clip if motion == "animatediff" else e.nombre_artefacto

    job = {
        "job_id": f"{receta.id}_v{receta.version}_s{receta.semilla}",
        "estilo": receta.estilo,
        "motion": motion,
        "negativo": NEGATIVO,
        "generacion": _GEN,
        "coherencia": coherencia,
        "escenas": [
            {
                "indice": e.indice,
                "archivo": archivo(e),
                "prompt": e.prompt,
                "semilla": e.semilla,
                "inicio_s": round(e.inicio_s, 3),
                "fin_s": round(e.fin_s, 3),
            }
            for e in escenas
        ],
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino
