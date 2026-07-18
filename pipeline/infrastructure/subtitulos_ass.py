"""Adaptador de subtitulos: segmentos -> archivo ASS estilizado (implementa PuertoSubtitulos).

Captions verticales grandes, estilo short, mas una linea fija de divulgacion de IA
abajo (la divulgacion va embebida en el subtitulo: evita drawtext + rutas de fuente
con dos puntos en Windows). Ver SAD H-6 / ADR-010.
"""
from __future__ import annotations

from pathlib import Path

from ..domain.entities import Receta, SegmentoTranscrito

_MAX_PALABRAS_POR_CAPTION = 6


def _fmt_t(segundos: float) -> str:
    """Segundos -> H:MM:SS.cc (centisegundos), formato de tiempo ASS."""
    cs = int(round(segundos * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _trocear(seg: SegmentoTranscrito) -> list[SegmentoTranscrito]:
    """Parte un segmento en captions de <= N palabras, repartiendo el tiempo."""
    palabras = seg.texto.split()
    if len(palabras) <= _MAX_PALABRAS_POR_CAPTION:
        return [seg]

    trozos: list[SegmentoTranscrito] = []
    total = len(palabras)
    dur = seg.fin_s - seg.inicio_s
    for i in range(0, total, _MAX_PALABRAS_POR_CAPTION):
        grupo = palabras[i : i + _MAX_PALABRAS_POR_CAPTION]
        ini = seg.inicio_s + dur * (i / total)
        fin = seg.inicio_s + dur * (min(i + _MAX_PALABRAS_POR_CAPTION, total) / total)
        trozos.append(SegmentoTranscrito(inicio_s=ini, fin_s=fin, texto=" ".join(grupo)))
    return trozos


_PLANTILLA = """[Script Info]
ScriptType: v4.00+
PlayResX: {ancho}
PlayResY: {alto}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,96,&H00FFFFFF,&H00000000,&H64000000,-1,1,6,2,2,80,80,540,1
Style: Divulgacion,Arial,40,&H00FFFFFF,&H00000000,&H96000000,0,1,3,0,2,40,40,70,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
{eventos}
"""


class SubtituladorASS:
    def generar(
        self,
        segmentos: list[SegmentoTranscrito],
        receta: Receta,
        destino: Path,
        divulgacion: str,
    ) -> Path:
        eventos: list[str] = []
        fin_total = 0.0
        for seg in segmentos:
            for trozo in _trocear(seg):
                fin_total = max(fin_total, trozo.fin_s)
                texto = trozo.texto.replace("\n", " ").strip()
                eventos.append(
                    f"Dialogue: 0,{_fmt_t(trozo.inicio_s)},{_fmt_t(trozo.fin_s)},"
                    f"Caption,0,0,0,,{texto}"
                )

        # Linea fija de divulgacion de IA durante todo el clip (ADR-010).
        eventos.append(
            f"Dialogue: 0,{_fmt_t(0)},{_fmt_t(fin_total + 0.5)},Divulgacion,0,0,0,,{divulgacion}"
        )

        contenido = _PLANTILLA.format(
            ancho=receta.formato.ancho,
            alto=receta.formato.alto,
            eventos="\n".join(eventos),
        )
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")
        return destino
