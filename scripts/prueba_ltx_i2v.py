# Prueba image-to-video de LTX: anima un still existente (flujo "imagen primero").
# Intenta pasar la imagen como data URI; si la API lo rechaza, la sube a litterbox
# (host temporal, expira en 1h) y reintenta con esa URL.
#
# Uso:  python scripts/prueba_ltx_i2v.py --imagen artifacts/prueba_ltx/still_luma_buzo_916.jpg
import argparse
import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from prueba_ltx import leer_key  # misma lectura de %USERPROFILE%\.ltx\api_key

API_URL = "https://api.ltx.video/v1/image-to-video"

MOVIMIENTO = (
    "Slow camera push-in toward the diver as he drifts gently over the shipwreck; "
    "silt particles float past the lens; god rays sway; a single continuous shot."
)


def pedir(cuerpo: dict, key: str) -> bytes:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return resp.read()


def subir_temporal(imagen: Path) -> str:
    print(">> data URI rechazado; subiendo a litterbox (expira 1h)...")
    out = subprocess.run(
        [
            "curl", "-s", "-F", "reqtype=fileupload", "-F", "time=1h",
            "-F", f"fileToUpload=@{imagen}",
            "https://litterbox.catbox.moe/resources/internals/api.php",
        ],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not out.startswith("http"):
        sys.exit(f"litterbox fallo: {out!r}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--imagen", type=Path, required=True)
    ap.add_argument("--duracion", type=int, default=4)
    ap.add_argument("--pro", action="store_true")
    ap.add_argument("--resolucion", default="1080x1920")
    args = ap.parse_args()

    key = leer_key()
    modelo = "ltx-2-3-pro" if args.pro else "ltx-2-3-fast"
    tarifa = 0.06 if args.pro else 0.04
    base = {
        "prompt": MOVIMIENTO,
        "model": modelo,
        "duration": args.duracion,
        "resolution": args.resolucion,
        "generate_audio": False,
    }
    destino = Path("artifacts/prueba_ltx") / f"i2v_{args.imagen.stem}_{modelo}_{args.duracion}s.mp4"
    print(f">> {modelo} {args.resolucion} {args.duracion}s (~${tarifa * args.duracion:.2f})")

    b64 = base64.b64encode(args.imagen.read_bytes()).decode("ascii")
    try:
        datos = pedir({**base, "image_uri": f"data:image/jpeg;base64,{b64}"}, key)
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")
        if e.code not in (400, 422):
            sys.exit(f"HTTP {e.code}: {detalle}")
        print(f"   ({e.code}: {detalle[:200]})")
        url = subir_temporal(args.imagen)
        try:
            datos = pedir({**base, "image_uri": url}, key)
        except urllib.error.HTTPError as e2:
            sys.exit(f"HTTP {e2.code}: {e2.read().decode('utf-8', 'replace')}")

    destino.write_bytes(datos)
    print(f"OK {destino} ({len(datos) / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
