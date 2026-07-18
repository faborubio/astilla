"""Adaptador de ensamblado con ffmpeg (implementa PuertoEnsamblado).

Compone el short 9:16 real: gradiente animado (fondo determinista) + onda de
audio (showwaves, animacion atada al audio real) + subtitulos ASS + divulgacion.
Se ejecuta con cwd = carpeta de salida para usar el .ass por nombre relativo y
evitar el escape de rutas con dos puntos de Windows en el filtro `subtitles`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Receta
from .visual_fondo import EspecVisualFondo


def _duracion_s(audio: Path) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(out.stdout.strip())


class EnsambladorFFmpeg:
    def ensamblar(
        self,
        audio_recorte: Path,
        spec: EspecVisualFondo,
        subtitulos_ass: Path,
        receta: Receta,
        destino: Path,
    ) -> Path:
        f = receta.formato
        dur = _duracion_s(audio_recorte)
        w, h, fps = f.ancho, f.alto, f.fps

        filtro = (
            f"gradients=s={w}x{h}:c0={spec.color_0}:c1={spec.color_1}:"
            f"x0=0:y0=0:x1={w}:y1={h}:r={fps}:d={dur:.3f}:speed=0.006[bg];"
            f"[0:a]aformat=channel_layouts=mono,"
            f"showwaves=s={w}x340:mode=cline:rate={fps}:colors={spec.color_onda}:scale=sqrt[wave];"
            f"[bg][wave]overlay=(W-w)/2:H-h-360:shortest=1[v0];"
            f"[v0]subtitles={subtitulos_ass.name}[vout]"
        )

        destino.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(audio_recorte.resolve()),
                "-filter_complex", filtro,
                "-map", "[vout]",
                "-map", "0:a",
                "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k",
                "-r", str(fps),
                "-t", f"{dur:.3f}",
                "-movflags", "+faststart",
                destino.name,
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(destino.parent),
        )
        return destino
