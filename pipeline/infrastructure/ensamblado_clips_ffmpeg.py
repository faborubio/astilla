"""Ensamblado de CLIPS animados (AnimateDiff) -> short 9:16 (ffmpeg).

Variante del ensamblado para movimiento real: cada escena ya es un clip corto
(~2 s, 16 frames). Se loopea para cubrir la duracion de su segmento, se recorta a
9:16, se concatenan y se compone audio + onda + subtitulos + divulgacion.
Reemplaza el motor Ken Burns (que animaba stills) sin tocar el resto del pipeline.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Escena, Receta
from .ensamblado_ffmpeg import _duracion_s


class EnsambladorClips:
    def ensamblar(
        self,
        escenas_dir: Path,
        escenas: list[Escena],
        audio_recorte: Path,
        subtitulos_ass: Path,
        receta: Receta,
        destino: Path,
    ) -> Path:
        f = receta.formato
        w, h, fps = f.ancho, f.alto, f.fps
        clips_dir = destino.parent / "escenas_clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        # 1) Loopear cada clip a la duracion de su escena + recorte 9:16.
        lista = clips_dir / "concat.txt"
        lineas: list[str] = []
        for e in escenas:
            src = escenas_dir / e.nombre_clip
            if not src.exists():
                raise FileNotFoundError(
                    f"Falta el clip de la escena {e.indice}: {src.name}. "
                    "Corre la generacion AnimateDiff en Kaggle (--motion animatediff --kaggle)."
                )
            clip = clips_dir / f"clip_{e.indice:02d}.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src.resolve()),
                    "-t", f"{e.duracion_s:.3f}",
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                           f"crop={w}:{h},fps={fps},format=yuv420p",
                    "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", str(clip.resolve()),
                ],
                check=True, capture_output=True, text=True,
            )
            lineas.append(f"file '{clip.name}'")
        lista.write_text("\n".join(lineas) + "\n", encoding="utf-8")

        # 2) Concatenar las escenas en un video base (sin audio).
        base = clips_dir / "base.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt",
             "-c", "copy", str(base.resolve())],
            check=True, capture_output=True, text=True, cwd=str(clips_dir),
        )

        # 3) Composicion final: base + onda + subtitulos + audio (divulgacion en el ASS).
        dur = _duracion_s(audio_recorte)
        filtro = (
            f"[1:a]aformat=channel_layouts=mono,showwaves=s={w}x300:mode=cline:"
            f"rate={fps}:colors=0xffffff:scale=sqrt[wave];"
            f"[0:v][wave]overlay=(W-w)/2:H-h-40:shortest=1[v1];"
            f"[v1]subtitles={subtitulos_ass.name}[vout]"
        )
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(base.resolve()),
                "-i", str(audio_recorte.resolve()),
                "-filter_complex", filtro,
                "-map", "[vout]", "-map", "1:a",
                "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-r", str(fps), "-t", f"{dur:.3f}",
                "-movflags", "+faststart", destino.name,
            ],
            check=True, capture_output=True, text=True, cwd=str(destino.parent),
        )
        return destino
