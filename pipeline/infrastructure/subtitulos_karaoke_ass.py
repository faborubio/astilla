"""Subtitulos KARAOKE (CASO-009, pase de calidad): resaltado por palabra estilo CapCut.

A partir de palabras con timestamp (Whisper word_timestamps), agrupa en lineas cortas
y punchy y, dentro de cada linea, resalta la palabra que se esta diciendo (color + pop
de escala) mientras el resto queda en blanco. Es el look de captions actual (Submagic/
CapCut) y sube muchisimo la percepcion de calidad, $0.

El tiempo se tesela sin huecos: cada palabra se muestra hasta que arranca la siguiente,
asi la linea queda visible continua y el resaltado "salta" de palabra en palabra.
"""
from __future__ import annotations

from pathlib import Path

from ..domain.entities import PalabraTranscrita, Receta

_MAX_PALABRAS_POR_LINEA = 3   # lineas cortas: "ESA CRISIS Y"
_GAP_CORTE_S = 0.7            # un silencio largo corta la linea
_COLOR_RESALTE = "&H0000FFFF"  # amarillo (ASS = &HAABBGGRR)


def _fmt_t(segundos: float) -> str:
    cs = int(round(max(segundos, 0) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _agrupar(palabras: list[PalabraTranscrita]) -> list[list[PalabraTranscrita]]:
    """Agrupa palabras en lineas cortas; corta por tamano o por silencio largo."""
    grupos: list[list[PalabraTranscrita]] = []
    actual: list[PalabraTranscrita] = []
    for p in palabras:
        if actual and (
            len(actual) >= _MAX_PALABRAS_POR_LINEA
            or p.inicio_s - actual[-1].fin_s > _GAP_CORTE_S
        ):
            grupos.append(actual)
            actual = []
        actual.append(p)
    if actual:
        grupos.append(actual)
    return grupos


def _linea(grupo: list[PalabraTranscrita], idx_activo: int) -> str:
    partes = []
    for i, p in enumerate(grupo):
        t = p.texto.upper()
        if i == idx_activo:  # palabra activa: color + pop de escala, luego reset \r
            partes.append(f"{{\\c{_COLOR_RESALTE}\\fscx112\\fscy112}}{t}{{\\r}}")
        else:
            partes.append(t)
    return " ".join(partes)


_PLANTILLA = """[Script Info]
ScriptType: v4.00+
PlayResX: {ancho}
PlayResY: {alto}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Arial,104,&H00FFFFFF,&H00000000,&H96000000,-1,1,7,3,2,80,80,520,1
Style: KaraokeMin,Arial,58,&H00FFFFFF,&H00000000,&H96000000,-1,1,2,0,2,80,80,460,1
Style: Divulgacion,Arial,40,&H00FFFFFF,&H00000000,&H96000000,0,1,3,0,2,40,40,70,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
{eventos}
"""


def generar_karaoke(
    palabras: list[PalabraTranscrita],
    receta: Receta,
    destino: Path,
    divulgacion: str,
    minimal: bool = False,
) -> Path:
    """minimal=True: subtitulos minimos del benchmark — UNA palabra por vez, chica,
    blanca, sin resaltado (la imagen manda; el texto se subordina)."""
    eventos: list[str] = []
    fin_total = 0.0
    if minimal:
        for i, p in enumerate(palabras):
            ini = p.inicio_s
            sig = palabras[i + 1].inicio_s if i + 1 < len(palabras) else None
            # la palabra queda hasta que arranca la siguiente; en silencios largos cae sola
            fin = sig if (sig is not None and sig - p.fin_s <= _GAP_CORTE_S) else p.fin_s + 0.15
            if fin <= ini:
                fin = ini + 0.08
            fin_total = max(fin_total, fin)
            eventos.append(
                f"Dialogue: 0,{_fmt_t(ini)},{_fmt_t(fin)},KaraokeMin,0,0,0,,{p.texto.upper()}"
            )
        if divulgacion:  # vacio = sin cartel quemado (declarar via toggle de la plataforma)
            eventos.append(
                f"Dialogue: 0,{_fmt_t(0)},{_fmt_t(fin_total + 0.5)},Divulgacion,0,0,0,,{divulgacion}"
            )
        contenido = _PLANTILLA.format(
            ancho=receta.formato.ancho, alto=receta.formato.alto, eventos="\n".join(eventos)
        )
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")
        return destino

    for grupo in _agrupar(palabras):
        for i, p in enumerate(grupo):
            ini = p.inicio_s
            # se muestra hasta que arranca la siguiente palabra del grupo (sin huecos)
            fin = grupo[i + 1].inicio_s if i + 1 < len(grupo) else p.fin_s
            if fin <= ini:
                fin = ini + 0.08
            fin_total = max(fin_total, fin)
            eventos.append(
                f"Dialogue: 0,{_fmt_t(ini)},{_fmt_t(fin)},Karaoke,0,0,0,,{_linea(grupo, i)}"
            )

    eventos.append(
        f"Dialogue: 0,{_fmt_t(0)},{_fmt_t(fin_total + 0.5)},Divulgacion,0,0,0,,{divulgacion}"
    )
    contenido = _PLANTILLA.format(
        ancho=receta.formato.ancho, alto=receta.formato.alto, eventos="\n".join(eventos)
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido, encoding="utf-8")
    return destino
