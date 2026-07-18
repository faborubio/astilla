# Prueba mínima de la API de LTX (ltx-2-3-fast) — 1 clip 9:16 de 4s (~$0.16).
# La key se lee de %USERPROFILE%\.ltx\api_key o de la env LTX_API_KEY. NUNCA va en el repo.
#
# Uso:  python scripts/prueba_ltx.py [--escena 0] [--duracion 4] [--pro]
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.ltx.video/v1/text-to-video"

ANCLA = (
    "shot on 35mm film, cinematic historical documentary, dramatic volumetric lighting, "
    "muted earthy palette with deep teal and warm amber, fine film grain, shallow depth of field, "
    "vertical 9:16 composition"
)

# Estilo del benchmark (referencia 8M): ilustración pictórica tipo Midjourney, no foto-realismo.
ANCLA_PICTORICA = (
    "painterly digital illustration in the style of a dramatic classical oil painting, visible "
    "expressive brush strokes, muted earthy palette with deep teal and warm amber, dramatic "
    "chiaroscuro lighting, epic historical illustration, vertical 9:16 composition"
)

# Escenas del guion Anticitera (mismas de artifacts/prompts_luma.md), sujeto + movimiento en un
# solo prompt porque text-to-video no separa imagen/motion como el flujo Photon.
ESCENAS = {
    0: (
        "A 1900s Greek sponge diver in a brass diving helmet and heavy canvas suit, suspended in "
        "deep blue Aegean water, sunbeams shafting down from the surface far above, silt particles "
        "suspended, the dark broken timbers of an ancient shipwreck emerging from the gloom below "
        "him. Slow camera push down following the diver as he sinks; god rays sway gently. "
        "A single continuous shot."
    ),
    2: (
        "Extreme macro of ancient corroded bronze gear wheels with fine triangular teeth, oxidized "
        "green patina, interlocking cogs, dust motes in the air, dramatic raking light glinting "
        "across the metal. Slow macro push-in as the gears rotate almost imperceptibly. "
        "A single continuous shot."
    ),
}


def leer_key() -> str:
    env = os.environ.get("LTX_API_KEY", "").strip()
    if env:
        return env
    ruta = Path.home() / ".ltx" / "api_key"
    if ruta.is_file():
        key = ruta.read_text(encoding="utf-8").strip()
        if key:
            return key
    sys.exit(
        "No hay key: crear %USERPROFILE%\\.ltx\\api_key (solo la key adentro) "
        "o definir LTX_API_KEY."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escena", type=int, default=0, choices=sorted(ESCENAS))
    ap.add_argument("--duracion", type=int, default=4)
    ap.add_argument("--pro", action="store_true", help="ltx-2-3-pro en vez de fast")
    ap.add_argument("--resolucion", default="1080x1920", help="9:16 vertical por defecto")
    ap.add_argument("--pictorico", action="store_true", help="ancla de ilustración pictórica")
    args = ap.parse_args()

    modelo = "ltx-2-3-pro" if args.pro else "ltx-2-3-fast"
    tarifa = 0.06 if args.pro else 0.04
    ancla = ANCLA_PICTORICA if args.pictorico else ANCLA
    cuerpo = {
        "prompt": f"{ESCENAS[args.escena]} {ancla}",
        "model": modelo,
        "duration": args.duracion,
        "resolution": args.resolucion,
        "generate_audio": False,
    }
    sufijo = "_pictorico" if args.pictorico else ""
    destino = Path("artifacts/prueba_ltx") / f"escena_{args.escena:02d}_{modelo}_{args.duracion}s{sufijo}.mp4"
    destino.parent.mkdir(parents=True, exist_ok=True)

    print(f">> {modelo} {args.resolucion} {args.duracion}s (~${tarifa * args.duracion:.2f})")
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {leer_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            datos = resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")

    destino.write_bytes(datos)
    print(f"OK {destino} ({len(datos) / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
