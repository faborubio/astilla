"""Planificacion de escenas (servicio de dominio, stdlib-only).

Convierte la transcripcion en una lista de Escena con un prompt determinista por
escena. Es donde vive parte de la 'variacion material' (H-8): cada escena tiene
su propio prompt derivado de su texto + el estilo de la receta.

Determinismo (ADR-006): semilla_escena = receta.semilla + indice. Mismo (receta,
transcripcion) -> mismas escenas y prompts.
"""
from __future__ import annotations

import re

from .entities import Escena, Receta, SegmentoTranscrito

# Prompt base por estilo. El estilo de la receta gobierna el 'look' (ADR-008).
_ESTILO_PROMPT: dict[str, str] = {
    "neon": "neon synthwave illustration, glowing rim light, dark moody atmosphere, cinematic lighting",
    "comic": "bold comic book illustration, heavy ink lines, halftone shading, dynamic composition",
    "minimal": "minimalist flat illustration, clean geometric shapes, limited elegant palette",
    # Divulgacion historica: look de documental cinematografico, no ilustracion.
    "historico": "cinematic historical photography, ancient world, dramatic volumetric light, "
                 "aged bronze and stone textures, museum documentary look, epic depth of field",
}
# Negativo base. "deformed, extra limbs" solo NO alcanza contra el defecto #1 de
# SDXL/SD: MANOS rotas (dedos fundidos/de mas/torcidos), que la audiencia notó y comentó
# ("se ven deformes", 2026-07-22). Los terminos especificos de manos SI los respeta el
# modelo. Ver [[manos-deformes-sdxl-y-fix-negativo]].
_NEGATIVO = (
    "text, watermark, signature, logo, lowres, blurry, "
    "deformed, disfigured, extra limbs, "
    "bad hands, mutated hands, malformed hands, poorly drawn hands, "
    "extra fingers, fused fingers, missing fingers, too many fingers, "
    "long fingers, twisted fingers, extra thumb, deformed hands"
)

# Stopwords ES para extraer palabras-tema sin dependencias de NLP.
_STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a",
    "y", "o", "u", "que", "en", "por", "para", "con", "sin", "su", "sus", "mi", "tu",
    "se", "lo", "le", "me", "te", "nos", "es", "era", "fue", "ser", "estar", "este",
    "esta", "esto", "ese", "esa", "eso", "como", "mas", "pero", "no", "si", "ya",
    "muy", "cuando", "donde", "porque", "iba", "voy", "vas", "va", "hay", "han",
    "he", "has", "ha", "todo", "toda", "todos", "cada", "entre", "desde", "hasta",
}

_MIN_DURACION_ESCENA_S = 4.0  # merge de segmentos cortos: menos escenas = menos render


def _palabras_tema(texto: str, maximo: int = 5) -> list[str]:
    palabras = re.findall(r"[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+", texto.lower())
    vistas: list[str] = []
    for p in palabras:
        if len(p) >= 4 and p not in _STOPWORDS and p not in vistas:
            vistas.append(p)
    # Las mas largas suelen ser las mas 'tematicas'; orden estable por longitud.
    vistas.sort(key=len, reverse=True)
    return vistas[:maximo]


def _prompt(texto: str, estilo: str, ancla: str = "") -> str:
    base = _ESTILO_PROMPT.get(estilo, _ESTILO_PROMPT["minimal"])
    temas = ", ".join(_palabras_tema(texto)) or "abstract scene"
    # La 'ancla' son temas globales del clip entero: repetirlos en cada escena da
    # coherencia mínima entre escenas (H-1) sin LLM. El adaptador Claude lo hace mejor.
    ancla_str = f"{ancla}, " if ancla else ""
    return f"{base}, {ancla_str}{temas}, vertical 9:16 composition, high detail"


def _ancla_global(segmentos: list[SegmentoTranscrito], maximo: int = 3) -> str:
    """Temas dominantes de TODO el clip; el hilo visual compartido entre escenas."""
    texto = " ".join(s.texto for s in segmentos)
    return ", ".join(_palabras_tema(texto, maximo=maximo))


def prompt_personaje(
    segmentos: list[SegmentoTranscrito], estilo: str, biblia: str = ""
) -> str:
    """Prompt del retrato-ancla del personaje recurrente (coherencia H-1, CASO-006).

    IP-Adapter / SadTalker necesitan UNA imagen de referencia con una CARA frontal
    grande y detectable; este prompt genera ese retrato (semilla fija). Se reusa para
    fijar la identidad. El personaje es ficticio (generado por IA), no una persona real.

    CRITICO: NO arrastrar temas de escena del transcript (lugar, objetos). Eso genera
    planos abiertos con la cara minuscula -> SadTalker no detecta landmarks (gotcha).
    El sujeto es solo identidad + estilo; la cara debe llenar el cuadro.
    """
    base = _ESTILO_PROMPT.get(estilo, _ESTILO_PROMPT["minimal"])
    sujeto = biblia.strip()[:140] if biblia.strip() else "a single charismatic narrator"
    return (
        f"extreme close-up headshot portrait of {sujeto}, {base}, "
        f"face fills the frame, head and shoulders only, front view, looking straight "
        f"at camera, both eyes visible, symmetric detailed face, plain background, high detail"
    )


def planificar_escenas(
    segmentos: list[SegmentoTranscrito], receta: Receta
) -> list[Escena]:
    """Agrupa segmentos cortos en escenas >= _MIN_DURACION y genera su prompt."""
    if not segmentos:
        return []

    # Greedy merge de segmentos hasta alcanzar la duracion minima de escena.
    grupos: list[list[SegmentoTranscrito]] = []
    actual: list[SegmentoTranscrito] = []
    for seg in segmentos:
        actual.append(seg)
        dur = actual[-1].fin_s - actual[0].inicio_s
        if dur >= _MIN_DURACION_ESCENA_S:
            grupos.append(actual)
            actual = []
    if actual:  # cola: pegar al ultimo grupo para no dejar una escena minuscula
        if grupos:
            grupos[-1].extend(actual)
        else:
            grupos.append(actual)

    ancla = _ancla_global(segmentos)  # hilo visual compartido (coherencia, H-1)
    escenas: list[Escena] = []
    for i, grupo in enumerate(grupos):
        texto = " ".join(s.texto for s in grupo).strip()
        escenas.append(
            Escena(
                indice=i,
                inicio_s=grupo[0].inicio_s,
                fin_s=grupo[-1].fin_s,
                texto=texto,
                prompt=_prompt(texto, receta.estilo, ancla),
                semilla=receta.semilla + i,
            )
        )
    return escenas


NEGATIVO = _NEGATIVO
