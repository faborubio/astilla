"""Bed de ambiente a partir de CLIPS de video (adaptador para Luma / video generativo).

Hermano de `ambiente_bed` (que anima stills con Ken Burns): acá el ambiente ya viene
como clips de video reales (p. ej. Luma Dream Machine). Cada clip se ajusta a la duracion
de SU escena y se concatena; el frame queda limpio (sin subs ni onda), porque el karaoke
se quema despues.

Ajuste de duracion: los clips generativos vienen de ~5s fijos y las escenas duran otra
cosa. Se estira/comprime el tiempo con setpts (ralenti cinematografico si la escena es
mas larga). Es preferible a loopear: el loop corta el movimiento y se nota.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Escena, Receta


def _duracion(p: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def ambiente_bed_clips(
    clips: dict[int, Path], escenas: list[Escena], audio: Path,
    receta: Receta, destino: Path,
) -> Path:
    """clips: {indice_escena: ruta_clip}. Devuelve el bed 9:16 con audio, sin subs."""
    from .ensamblado_ffmpeg import _duracion_s

    f = receta.formato
    w, h, fps = f.ancho, f.alto, f.fps
    tmp = destino.parent / "luma_clips"
    tmp.mkdir(parents=True, exist_ok=True)

    lineas: list[str] = []
    for e in escenas:
        src = clips.get(e.indice)
        if src is None:
            raise FileNotFoundError(f"Falta el clip de la escena {e.indice}")
        cd = _duracion(src)
        factor = e.duracion_s / cd  # >1 = ralenti (escena mas larga que el clip)
        dst = tmp / f"luma_{e.indice:02d}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(src.resolve()),
             "-vf", (f"setpts=PTS*{factor:.5f},"
                     f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                     f"crop={w}:{h},fps={fps}"),
             "-an", "-t", f"{e.duracion_s:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", str(dst.resolve())],
            check=True, capture_output=True, text=True,
        )
        lineas.append(f"file '{dst.name}'")

    (tmp / "concat.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    base = tmp / "base.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", "concat.txt", "-c", "copy", str(base.resolve())],
        check=True, capture_output=True, text=True, cwd=str(tmp),
    )

    dur = _duracion_s(audio)
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(base.resolve()),
         "-i", str(audio.resolve()), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-r", str(fps), "-t", f"{dur:.3f}", "-movflags", "+faststart",
         str(destino.resolve())],
        check=True, capture_output=True, text=True,
    )
    return destino
