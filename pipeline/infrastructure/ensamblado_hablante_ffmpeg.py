"""Composicion de capas (CASO-009, capa 3): hablante sobre el ambiente.

Toma el video de AMBIENTE ya ensamblado (escenas + subtitulos + audio, lo que produce
`pipeline.animado`) y superpone el `narrator.mp4` (cabeza hablando) como un busto en la
zona superior, dejando los subtitulos visibles abajo. Un solo paso ffmpeg.

v1: el hablante va como recuadro (su propio fondo oscuro). Matting/chroma para fundirlo
con el ambiente queda como mejora (igual que subir resolucion con el enhancer).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain.entities import Escena, Receta


def ambiente_bed(
    escenas_dir: Path, escenas: list[Escena], audio: Path, receta: Receta, destino: Path
) -> Path:
    """Bed de ambiente LIMPIO: Ken Burns multi-escena + audio, SIN onda ni subs.

    El composite del hablante necesita un fondo sin subtitulos (el karaoke se agrega
    aparte) ni waveform. Reusa el zoom de EnsambladorEscenas pero deja el frame limpio.
    """
    from .ensamblado_escenas_ffmpeg import _filtro_kenburns
    from .ensamblado_ffmpeg import _duracion_s

    f = receta.formato
    w, h, fps = f.ancho, f.alto, f.fps
    clips_dir = destino.parent / "bed_clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    lineas: list[str] = []
    for e in escenas:
        img = escenas_dir / e.nombre_artefacto
        frames = max(2, round(e.duracion_s * fps))
        clip = clips_dir / f"bed_{e.indice:02d}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(img.resolve()),
             "-vf", _filtro_kenburns(e, w, h, fps, frames), "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-pix_fmt", "yuv420p", str(clip.resolve())],
            check=True, capture_output=True, text=True,
        )
        lineas.append(f"file '{clip.name}'")
    (clips_dir / "concat.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    base = clips_dir / "base.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "concat.txt",
         "-c", "copy", str(base.resolve())],
        check=True, capture_output=True, text=True, cwd=str(clips_dir),
    )
    dur = _duracion_s(audio)
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(base.resolve()), "-i", str(audio.resolve()),
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-r", str(fps),
         "-t", f"{dur:.3f}", "-movflags", "+faststart", str(destino.resolve())],
        check=True, capture_output=True, text=True,
    )
    return destino


def componer_hablante(
    ambiente: Path,
    narrator: Path,
    salida: Path,
    lado_overlay: int = 720,
    margen_top: int = 150,
) -> Path:
    """Superpone narrator (cuadrado) sobre el ambiente 9:16; audio del ambiente."""
    # narrator 256x256 -> escalado a lado_overlay y centrado en X; Y fijo arriba para
    # no tapar los subtitulos (que viven abajo en el .ass).
    filtro = (
        f"[1:v]scale={lado_overlay}:{lado_overlay}:force_original_aspect_ratio=increase,"
        f"crop={lado_overlay}:{lado_overlay}[n];"
        f"[0:v][n]overlay=(W-w)/2:{margen_top}[v]"
    )
    salida.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-i", str(ambiente), "-i", str(narrator),
         "-filter_complex", filtro,
         "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-shortest", str(salida)],
        check=True,
    )
    return salida
