"""Adaptador de prompts visuales con Claude (implementa la idea de PuertoPromptVisual).

Resuelve H-1 (coherencia) y H-2 (mejores prompts) a la vez: Claude lee el transcript
completo y produce (1) una BIBLIA DE ESTILO compartida (sujeto/personaje recurrente,
escenario, paleta) y (2) un prompt por escena que la incorpora -> coherencia por
construccion, en vez de keywords sueltas escena por escena.

Requiere ANTHROPIC_API_KEY. Si no esta, el orquestador cae al prompt heuristico.
Ver skill claude-api: claude-opus-4-8, structured outputs (output_config.format),
adaptive thinking.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from ..domain.entities import Escena

_MODELO = "claude-opus-4-8"

_SISTEMA = (
    "Eres director de arte de shorts verticales. A partir de la transcripcion de un "
    "clip, generas prompts de imagen para Stable Diffusion 1.5 que componen un short "
    "9:16 VISUALMENTE COHERENTE. Primero defines una 'biblia de estilo': el sujeto o "
    "personaje recurrente, el escenario y la paleta que deben repetirse en TODAS las "
    "escenas. Luego, para cada escena, un prompt que incorpora la biblia (mismo sujeto, "
    "misma paleta) y agrega lo especifico de esa escena. Reglas de los prompts: en "
    "INGLES, estilo SD (frases separadas por comas), concretos y visuales, sin texto ni "
    "marcas de agua, composicion vertical 9:16."
)

_SCHEMA = {
    "type": "object",
    "properties": {
        "biblia_estilo": {"type": "string"},
        "escenas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "indice": {"type": "integer"},
                    "prompt": {"type": "string"},
                },
                "required": ["indice", "prompt"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["biblia_estilo", "escenas"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ResultadoPrompts:
    biblia: str
    prompts: dict[int, str]  # indice -> prompt


def refinar_prompts(escenas: list[Escena], estilo: str) -> ResultadoPrompts:
    """Llama a Claude y devuelve biblia de estilo + prompt coherente por escena.

    Lanza si falta la API key o el SDK; el caller decide el fallback.
    """
    import anthropic  # import perezoso: solo si se usa esta ruta

    cliente = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno

    escenas_in = [{"indice": e.indice, "texto": e.texto} for e in escenas]
    user = (
        f"Estilo base del short: {estilo}.\n"
        f"Escenas (en orden, con su texto hablado):\n"
        f"{json.dumps(escenas_in, ensure_ascii=False, indent=2)}\n\n"
        f"Devuelve la biblia de estilo y un prompt por escena (mismo indice)."
    )

    resp = cliente.messages.create(
        model=_MODELO,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        system=_SISTEMA,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
    )
    texto = next(b.text for b in resp.content if b.type == "text")
    data = json.loads(texto)
    prompts = {int(e["indice"]): e["prompt"] for e in data["escenas"]}
    return ResultadoPrompts(biblia=data["biblia_estilo"], prompts=prompts)
