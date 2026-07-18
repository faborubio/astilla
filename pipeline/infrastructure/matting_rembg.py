"""Matting del hablante (CASO-009, pase de calidad): rembg saca el fondo del narrator.

Quita el fondo (oscuro/portrait) de la cabeza hablante para que se FUNDA con el ambiente
en vez de quedar como recuadro PiP. Local, $0 (CPU, onnxruntime). Modelo u2net_human_seg
(segmentacion de personas). Salida .mov con canal alpha (qtrle) -> ffmpeg lo compone con
transparencia sobre el fondo (el mismo `componer_hablante` ya respeta el alpha).
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def mattear_narrator(
    narrator: Path, salida: Path, fps: int = 25, modelo: str = "u2net_human_seg"
) -> Path:
    import imageio.v3 as iio
    from rembg import new_session, remove

    sesion = new_session(modelo)
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        n = 0
        for i, frame in enumerate(iio.imiter(narrator, plugin="pyav")):
            rgba = remove(frame, session=sesion)  # ndarray RGBA (fondo -> alpha 0)
            iio.imwrite(tdp / f"f_{i:05d}.png", rgba)
            n = i + 1
        salida.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
             "-i", str(tdp / "f_%05d.png"),
             "-c:v", "qtrle", "-pix_fmt", "argb", str(salida)],
            check=True,
        )
    print(f"[matting] {n} frames sin fondo -> {salida}")
    return salida
