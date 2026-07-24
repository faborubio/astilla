# Genera clips LTX (text-to-video) para escenas del visual_job de un short.
# Embrion del futuro ejecutor_ltx (PuertoEjecutor). Key: %USERPROFILE%\.ltx\api_key.
# Folder-aware (jul 2026): con --nombre lee artifacts/shorts/<n>/visual_job.json y
# escribe los clips en artifacts/shorts/<n>/clips/.
#
# POLITICA DE FIDELIDAD (2026-07-22): preferir i2v > still Ken Burns > t2v. El t2v puro es
# CIEGO (sin imagen de anclaje ni negative prompt) y deriva de etnia/epoca/objeto -> es el que
# produce los "clips que no tienen nada que ver" que critico la audiencia. Recomendado:
# generar TODOS los stills SDXL fieles (generar_stills_kaggle.py) y animar los money shots con
# --i2v (LTX solo agrega movimiento sobre un still fiel). Usar t2v solo si no hay still posible.
#
# Uso recomendado (money shots anclados a still fiel):
#       python scripts/generar_ltx.py --nombre arquero --indices todas --auto --i2v 5,6
#       (o --i2v todas para animar todas; el resto sin --i2v/--video = still+Ken Burns $0)
# Variantes:
#       python scripts/generar_ltx.py --nombre arquero --indices todas --auto --pro
#       python scripts/generar_ltx.py --job <ruta.json> --indices 0,3,7   (override)
#       --video I,J  = t2v CIEGO (evitar salvo que no exista still para esa escena)
import argparse
import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from prueba_ltx import leer_key
from rutas import RutasShort

API_URL = "https://api.ltx.video/v1/text-to-video"
I2V_API_URL = "https://api.ltx.video/v1/image-to-video"
MOVIMIENTO = "Slow cinematic camera push-in, subtle drifting particles, a single continuous shot."

STILL_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def _still_src(clips_dir: Path, i: int):
    """Imagen de la escena still, si existe (clips/still_NN.{png,jpg,...})."""
    for ext in STILL_EXTS:
        p = clips_dir / f"still_{i:02d}{ext}"
        if p.exists():
            return p
    return None


def _ken_burns(src: Path, dur: float, destino: Path,
               w: int = 1080, h: int = 1920, fps: int = 30) -> None:
    """Anima un still 9:16 con un push-in lento (Ken Burns), $0. Mismo lenguaje de
    camara que los clips LTX (MOVIMIENTO: 'slow cinematic push-in') para que la mezcla
    video+still no se note. El bed final (ambiente_bed_clips) reconforma fps/duracion."""
    dur = max(0.5, float(dur))
    frames = max(1, round(dur * fps))
    zi = 0.12 / frames  # de 1.00 a ~1.12 a lo largo de la escena
    vf = (
        f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,"
        f"crop={w * 2}:{h * 2},"
        f"zoompan=z='min(zoom+{zi:.6f},1.12)':d={frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={w}x{h}:fps={fps},setsar=1,format=yuv420p"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-vf", vf, "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", str(destino)],
        check=True,
    )


def _subir_temporal(imagen: Path) -> str:
    """Sube la imagen a litterbox (expira 1h) si la API rechaza el data URI. Devuelve la URL."""
    out = subprocess.run(
        ["curl", "-s", "-F", "reqtype=fileupload", "-F", "time=1h",
         "-F", f"fileToUpload=@{imagen}",
         "https://litterbox.catbox.moe/resources/internals/api.php"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not out.startswith("http"):
        sys.exit(f"litterbox fallo: {out!r}")
    return out


def _i2v(still: Path, prompt: str, dur: int, modelo: str, key: str, destino: Path) -> None:
    """Image-to-video: LTX anima el still (frame 0) -> ancla el contenido, el prompt guia el
    movimiento. Intenta data URI; si la API lo rechaza (400/413/422), sube a litterbox y reintenta.
    Validado en scripts/prueba_ltx_i2v.py (campo image_uri)."""
    ext = (still.suffix.lstrip(".").lower() or "png")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    b64 = base64.b64encode(still.read_bytes()).decode("ascii")
    base = {"prompt": prompt, "model": modelo, "duration": dur,
            "resolution": "1080x1920", "generate_audio": False}

    def _post(cuerpo: dict) -> bytes:
        req = urllib.request.Request(
            I2V_API_URL, data=json.dumps(cuerpo).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=600) as resp:
            return resp.read()

    try:
        datos = _post({**base, "image_uri": f"data:image/{mime};base64,{b64}"})
    except urllib.error.HTTPError as e:
        if e.code not in (400, 413, 422):
            sys.exit(f"i2v HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")
        url = _subir_temporal(still)
        try:
            datos = _post({**base, "image_uri": url})
        except urllib.error.HTTPError as e2:
            sys.exit(f"i2v HTTP {e2.code}: {e2.read().decode('utf-8', 'replace')}")
    destino.write_bytes(datos)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indices", required=True, help="ej: 0,3,7 o 'todas'")
    ap.add_argument("--duracion", type=int, default=4)
    ap.add_argument("--auto", action="store_true",
                    help="duracion por escena = ceil(fin-inicio) del visual_job (evita ralenti)")
    ap.add_argument("--pro", action="store_true")
    ap.add_argument("--nombre", default=None, help="short (def: artifacts/shorts/<n>/)")
    ap.add_argument("--job", type=Path, default=None, help="override del visual_job.json")
    ap.add_argument("--clips-dir", type=Path, default=None, help="override del destino de clips")
    ap.add_argument("--video", default=None,
                    help="indices que van a t2v CIEGO de LTX-video (PAGO); el resto de --indices se "
                         "renderiza como still+Ken Burns local ($0). Requiere clips/still_NN.png. "
                         "OMITIDO (default seguro, fix G-16): NO manda todo a video; lo que no es --i2v "
                         "va a Ken Burns SI tiene su still, y solo paga t2v la escena que NO tiene still. "
                         "Para forzar t2v teniendo still, listala explicita aca.")
    ap.add_argument("--i2v", default=None,
                    help="indices que van a IMAGE-TO-VIDEO desde clips/still_NN.png: LTX anima ese "
                         "still (ancla el contenido; ideal cuando el still es fiel y t2v deriva). "
                         "Mismo costo que t2v. Requiere el PNG. Prioridad sobre --video.")
    args = ap.parse_args()

    if not args.nombre and not args.job:
        sys.exit("pasar --nombre <short> (o --job <ruta.json>)")
    r = RutasShort(args.nombre) if args.nombre else None
    job_path = args.job or r.visual_job
    dest_dir = args.clips_dir or (r.clips if r else Path("artifacts/escenas_ltx"))

    job = json.loads(job_path.read_text(encoding="utf-8"))
    escenas = {e["indice"]: e for e in job["escenas"]}
    indices = sorted(escenas) if args.indices == "todas" else [
        int(i) for i in args.indices.split(",")]

    key = leer_key()
    modelo = "ltx-2-3-pro" if args.pro else "ltx-2-3-fast"
    # TARIFA REAL (2026-07-23): un i2v fast de 6s devolvio 402 "Required: 36 cents"
    # -> fast = $0.06/s (NO $0.04 como asumia antes; sub-estimaba y provocaba 402 a media corrida).
    # pro sin verificar: estimado 1.5x fast = $0.09/s (ajustar cuando haya dato real).
    tarifa = 0.09 if args.pro else 0.06
    import math

    def _dur_valida(beat: float) -> int:
        # la API solo acepta duraciones PARES (4,6,8,10): redondear al par >= beat
        d = math.ceil(beat)
        return min(10, max(4, d + (d % 2)))

    destino_dir = dest_dir
    destino_dir.mkdir(parents=True, exist_ok=True)

    # Particion i2v / video(t2v) / still. Prioridad: i2v > video > Ken Burns.
    # "todas" como valor de --i2v/--video selecciona todos los indices pedidos (atajo
    # de la politica i2v-por-defecto: 'anima todos los money shots desde un still fiel').
    def _sel(arg: str | None) -> set:
        if arg is None:
            return set()
        if arg.strip().lower() == "todas":
            return set(indices)
        return {int(x) for x in arg.split(",") if x.strip() != ""}

    pedidos_i = _sel(args.i2v)
    i2v_idx = [i for i in indices if i in pedidos_i]
    if args.video is None:
        # DEFAULT SEGURO (politica i2v-por-defecto, 2026-07-22): SIN --video, lo que no es
        # i2v va a Ken Burns local ($0) SI tiene su still fiel; solo va a t2v CIEGO (paga) la
        # escena que NO tiene still (unica opcion). Antes el default mandaba TODO a t2v aunque
        # hubiera stills -> pagaba de mas y tiraba la fidelidad revisada (bug detectado en
        # mortero_bizantino). Para forzar t2v teniendo still, listalo explicito en --video.
        video_idx = [i for i in indices
                     if i not in pedidos_i and _still_src(destino_dir, i) is None]
    else:
        pedidos_v = _sel(args.video)
        video_idx = [i for i in indices if i in pedidos_v and i not in pedidos_i]
    still_idx = [i for i in indices if i not in video_idx and i not in i2v_idx]

    # FIDELIDAD (2026-07-22): el t2v puro es ciego (sin imagen de anclaje ni negative
    # prompt) -> es el que deriva de etnia/epoca/objeto y produce los "clips que no tienen
    # nada que ver" que critico la audiencia. Si una escena va a t2v PERO ya existe su
    # still fiel, avisar: conviene --i2v ese indice (LTX solo agrega movimiento, no inventa).
    t2v_con_still = [i for i in video_idx if _still_src(destino_dir, i) is not None]
    if t2v_con_still:
        idxs = ",".join(str(i) for i in t2v_con_still)
        print(
            f"AVISO fidelidad: {len(t2v_con_still)} escena(s) van a t2v CIEGO teniendo "
            f"still fiel disponible ({idxs}).\n"
            f"  -> preferi anclarlas: agregalas a --i2v \"{idxs}\" (mismo costo, LTX solo "
            f"anima el still en vez de inventar la escena). Ver CLAUDE.md > fidelidad visual."
        )

    # Stills e i2v necesitan su PNG en clips/still_NN.png (Kaggle SDXL / Flux / etc.).
    faltan_png = [i for i in (still_idx + i2v_idx) if _still_src(destino_dir, i) is None]
    if faltan_png:
        sys.exit(
            "faltan imagenes (still/i2v): "
            + ", ".join(f"still_{i:02d}.png" for i in faltan_png)
            + f"\n  (ponlas en {destino_dir}/ ; formatos: {', '.join(STILL_EXTS)})"
        )

    duraciones = {
        i: (_dur_valida(escenas[i]["fin_s"] - escenas[i]["inicio_s"])
            if args.auto else args.duracion)
        for i in (video_idx + i2v_idx)
    }
    s_video = sum(duraciones[i] for i in video_idx)
    s_i2v = sum(duraciones[i] for i in i2v_idx)
    print(f">> t2v: {len(video_idx)} esc/{s_video}s  |  i2v: {len(i2v_idx)} esc/{s_i2v}s  "
          f"|  {modelo} (~${tarifa * (s_video + s_i2v):.2f})  |  "
          f"still Ken Burns: {len(still_idx)} ($0)")

    # 1) Stills primero (baratos, ya validados): still+Ken Burns -> escena_NN.mp4
    for i in still_idx:
        src = _still_src(destino_dir, i)
        beat = escenas[i]["fin_s"] - escenas[i]["inicio_s"]
        destino = destino_dir / f"escena_{i:02d}.mp4"
        _ken_burns(src, beat, destino)
        print(f"OK escena {i:02d} (still Ken Burns {beat:.1f}s) -> {destino}")

    # 1b) i2v: LTX anima el still fiel (ancla el contenido) -> escena_NN.mp4
    for i in i2v_idx:
        src = _still_src(destino_dir, i)
        destino = destino_dir / f"escena_{i:02d}.mp4"
        _i2v(src, f"{escenas[i]['prompt']} {MOVIMIENTO}", duraciones[i], modelo, key, destino)
        print(f"OK escena {i:02d} (i2v desde {src.name}, {duraciones[i]}s) -> {destino}")

    # 2) Escenas de video via LTX API
    for i in video_idx:
        destino = destino_dir / f"escena_{i:02d}.mp4"
        cuerpo = {
            "prompt": f"{escenas[i]['prompt']} {MOVIMIENTO}",
            "model": modelo,
            "duration": duraciones[i],
            "resolution": "1080x1920",
            "generate_audio": False,
        }
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(cuerpo).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                datos = resp.read()
        except urllib.error.HTTPError as e:
            sys.exit(f"escena {i}: HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")
        destino.write_bytes(datos)
        print(f"OK escena {i:02d} -> {destino} ({len(datos) / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
