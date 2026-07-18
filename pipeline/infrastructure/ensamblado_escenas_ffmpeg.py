"""Ensamblado animado: imagenes de escena -> short 9:16 con movimiento (ffmpeg).

Anima cada still generado con efecto Ken Burns (zoom/pan), concatena las escenas
en el tiempo de su segmento, y compone audio + onda + subtitulos + divulgacion.
Es la 'animacion' real de Fase 2 sobre stills (CASO-003); cuando exista video
diffusion (AnimateDiff), reemplaza este motor de movimiento sin tocar el dominio.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Escena, Receta
from .ensamblado_ffmpeg import _duracion_s

# Movimiento Ken Burns: zoom in / zoom out alternado por escena (variacion, H-8).
_ZOOM_MAX = 1.30
_ZOOM_INC = 0.0011


def _filtro_kenburns(escena: Escena, w: int, h: int, fps: int, frames: int) -> str:
    # Render a resolucion de salida directamente (sin supersample 2x: era el cuello
    # de botella en CPU). El zoom suave evita el shake clasico de zoompan.
    if escena.indice % 2 == 0:  # zoom in
        z = f"min(zoom+{_ZOOM_INC},{_ZOOM_MAX})"
    else:  # zoom out (arranca acercado y se aleja)
        z = f"if(eq(on,0),{_ZOOM_MAX},max(zoom-{_ZOOM_INC},1.001))"
    return (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
        f"zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s={w}x{h}:fps={fps},format=yuv420p"
    )


class EnsambladorEscenas:
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

        # 1) Un clip Ken Burns por escena, en su duracion.
        lista = clips_dir / "concat.txt"
        lineas: list[str] = []
        for e in escenas:
            img = escenas_dir / e.nombre_artefacto
            if not img.exists():
                raise FileNotFoundError(
                    f"Falta la imagen de la escena {e.indice}: {img.name}. "
                    "Corre primero el notebook de Colab (ver COLAB.md) o usa --stub-visual."
                )
            frames = max(2, round(e.duracion_s * fps))
            clip = clips_dir / f"clip_{e.indice:02d}.mp4"
            # Una sola imagen de entrada (-loop 1) + zoompan d=frames + corte por
            # -frames:v: evita que zoompan multiplique frames por cada frame del loop.
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loop", "1",
                    "-i", str(img.resolve()),
                    "-vf", _filtro_kenburns(e, w, h, fps, frames),
                    "-frames:v", str(frames), "-an",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p",
                    str(clip.resolve()),
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
                "-movflags", "+faststart",
                destino.name,
            ],
            check=True, capture_output=True, text=True, cwd=str(destino.parent),
        )
        return destino
