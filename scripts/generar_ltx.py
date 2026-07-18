# Genera clips LTX (text-to-video) para escenas del visual_job.json vigente.
# Embrion del futuro ejecutor_ltx (PuertoEjecutor). Key: %USERPROFILE%\.ltx\api_key.
#
# Uso:  python scripts/generar_ltx.py --indices 0,3,7 [--duracion 4] [--pro]
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from prueba_ltx import leer_key

API_URL = "https://api.ltx.video/v1/text-to-video"
MOVIMIENTO = "Slow cinematic camera push-in, subtle drifting particles, a single continuous shot."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indices", required=True, help="ej: 0,3,7 o 'todas'")
    ap.add_argument("--duracion", type=int, default=4)
    ap.add_argument("--auto", action="store_true",
                    help="duracion por escena = ceil(fin-inicio) del visual_job (evita ralenti)")
    ap.add_argument("--pro", action="store_true")
    ap.add_argument("--job", type=Path, default=Path("artifacts/visual_job.json"))
    args = ap.parse_args()

    job = json.loads(args.job.read_text(encoding="utf-8"))
    escenas = {e["indice"]: e for e in job["escenas"]}
    indices = sorted(escenas) if args.indices == "todas" else [
        int(i) for i in args.indices.split(",")]

    key = leer_key()
    modelo = "ltx-2-3-pro" if args.pro else "ltx-2-3-fast"
    tarifa = 0.06 if args.pro else 0.04
    import math

    def _dur_valida(beat: float) -> int:
        # la API solo acepta duraciones PARES (4,6,8,10): redondear al par >= beat
        d = math.ceil(beat)
        return min(10, max(4, d + (d % 2)))

    duraciones = {
        i: (_dur_valida(escenas[i]["fin_s"] - escenas[i]["inicio_s"])
            if args.auto else args.duracion)
        for i in indices
    }
    destino_dir = Path("artifacts/escenas_ltx")
    destino_dir.mkdir(parents=True, exist_ok=True)
    total_s = sum(duraciones.values())
    print(f">> {len(indices)} escenas, {total_s}s total, {modelo} (~${tarifa * total_s:.2f})")

    for i in indices:
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
