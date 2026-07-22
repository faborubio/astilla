# Genera los STILLS de las escenas-still de un short en Kaggle (SDXL, GPU T4 gratis, $0).
# Hermano de generar_ltx.py para el flujo HIBRIDO: las escenas que NO van a LTX-video
# (ver el flag --video de generar_ltx.py) se ilustran como stills y luego el propio
# generar_ltx.py las anima con Ken Burns local. Este script solo produce los PNG.
#
# Despacho headless via el PuertoEjecutor (pipeline/infrastructure/ejecutor_kaggle.py,
# kernel "sdxl"): sube el job, corre en T4, baja los PNG a artifacts/shorts/<n>/clips/.
# Ventaja de SDXL para fidelidad de etnia/epoca: negative_prompt REAL (LTX/FLUX-schnell
# no tienen) -> se empuja "european/caucasian face, modern clothing" al negativo.
#
# Uso:  python scripts/generar_stills_kaggle.py --nombre chuno --indices 3,5,6,8
#       (los prompts salen de shorts/<n>/prompts.json; salida -> clips/still_NN.png)
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ para rutas

from pipeline.domain.planificacion import NEGATIVO
from pipeline.infrastructure.ejecutor_kaggle import generar_en_kaggle
from rutas import RutasShort

# Negativo por defecto: el base + los killers de etnia/epoca/estilo que SDXL SI respeta.
# "photorealistic photo/sepia" empuja hacia el look painterly on-brand; el resto blinda
# contra el anacronismo que LTX metia (caras europeas, ropa moderna). Ver
# [[fidelidad-visual-ltx-etnia-epoca]]. Se puede reemplazar entero con --negativo.
# Recipe validado (2026-07-21): los killers de FOTO al frente fuerzan el look painterly
# on-brand (SDXL base deriva a foto si el positivo esta cargado); + killers de etnia/epoca
# que SDXL SI respeta; + "signature" (SDXL mete firmas falsas). El otro 50% del fix es la
# ESTRUCTURA del prompt positivo: estilo al FRENTE. Ver [[ltx-fast-vs-pro-y-hibrido-stills]].
NEG_ETNIA = ("photograph, photo, realistic, photorealistic, dslr, film still, sepia, "
             "european face, caucasian, white person, modern clothing, signature, "
             "anime, cartoon, 3d render")

# GUIA DE COMPOSICION ANTI-DEFORMIDAD (2026-07-22, tras la critica de la audiencia sobre
# manos deformes). El negative de manos ayuda pero NO es infalible; la mejor defensa es
# COMPONER el plano para no exponer manos/dedos cuando no son el foco:
#   - Preferir planos que NO muestren manos completas: el OBJETO en primer plano, la accion
#     sugerida, siluetas, manos cortadas por el encuadre o en sombra/contraluz.
#   - Si la mano ES el foco (ej. sostener el pistón), pedir "a single hand, seen from the side,
#     partly in shadow" y pensar en generar 2-3 semillas y quedarse con la mejor (es $0).
#   - Cero grupos de personas en plano medio (multiplican caras/manos rotas). Multitud = lejana,
#     de espaldas o en silueta.
# El validador de abajo AVISA cuando un prompt entra en zona de riesgo (pide manos/dedos/gente
# de cerca) para que revises ESE still con lupa. No bloquea: solo marca.
_RIESGO_MANOS = ("hand", "hands", "finger", "fingers", "fist", "grip", "gripping",
                 "holding", "grasp", "palm", "thumb")
_RIESGO_GENTE = ("face", "faces", "crowd", "people", "soldiers", "men", "group of",
                 "portrait")


def _tiene(termino: str, texto: str) -> bool:
    """Match por palabra completa (evita 'men' dentro de 'docuMENtary', etc.)."""
    return re.search(rf"\b{re.escape(termino)}\b", texto) is not None


def _avisos_riesgo(indice: int, prompt: str) -> list[str]:
    """Marca patrones que suelen salir deformes en SDXL, para revisar ese still con lupa."""
    p = prompt.lower()
    avisos = []
    hits_m = sorted({t for t in _RIESGO_MANOS if _tiene(t, p)})
    hits_g = sorted({t for t in _RIESGO_GENTE if _tiene(t, p)})
    if hits_m:
        avisos.append(f"  esc {indice:02d}: pide MANOS ({', '.join(hits_m)}) -> revisá dedos; "
                      f"si no son el foco, reformulá a objeto/silueta/mano en sombra")
    if hits_g:
        avisos.append(f"  esc {indice:02d}: pide GENTE de cerca ({', '.join(hits_g)}) -> "
                      f"revisá caras; multitud mejor lejana/de espaldas")
    return avisos


def main() -> None:
    ap = argparse.ArgumentParser(description="Genera stills SDXL de un short en Kaggle (T4).")
    ap.add_argument("--nombre", required=True, help="short (artifacts/shorts/<n>/)")
    ap.add_argument("--indices", required=True,
                    help="escenas-still a generar, ej '3,5,6,8' (deben estar en prompts.json)")
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--modelo", default="stabilityai/stable-diffusion-xl-base-1.0")
    ap.add_argument("--wh", default="832x1216", help="ancho x alto (SDXL nativo cercano a 9:16)")
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--guidance", type=float, default=7.0)
    ap.add_argument("--negativo", default=None,
                    help="override COMPLETO del negativo (por def: base + killers de etnia)")
    ap.add_argument("--prompts-file", type=Path, default=None,
                    help="override del prompts.json (mismo formato {indice: prompt}); util para "
                         "probar la convencion de prompt sin pisar el prompts.json del short")
    ap.add_argument("--timeout", type=int, default=2400, help="segundos de espera del kernel")
    args = ap.parse_args()

    r = RutasShort(args.nombre, crear=True)
    fuente_prompts = args.prompts_file or r.prompts
    if not fuente_prompts.exists():
        sys.exit(f"falta {fuente_prompts} (los prompts pictoricos por escena)")
    prompts = json.loads(fuente_prompts.read_text(encoding="utf-8"))

    indices = [int(x) for x in args.indices.split(",") if x.strip() != ""]
    faltan = [i for i in indices if str(i) not in prompts]
    if faltan:
        sys.exit(f"prompts.json no tiene las escenas: {faltan}")

    w, h = (int(x) for x in args.wh.lower().split("x"))
    negativo = args.negativo or f"{NEGATIVO}, {NEG_ETNIA}"

    # Aviso de zonas de riesgo (manos/gente de cerca) ANTES de gastar la corrida: te dice
    # cuales stills mirar con lupa al bajarlos (regenerarlos es $0 en Kaggle). Ver guia arriba.
    avisos = [a for i in indices for a in _avisos_riesgo(i, prompts[str(i)])]
    if avisos:
        print(">> ZONAS DE RIESGO DE DEFORMIDAD (revisá estos stills con lupa; regen = $0):")
        print("\n".join(avisos))

    job = {
        "job_id": f"stills-{args.nombre}",
        "estilo": "historico",
        "negativo": negativo,
        "generacion": {"modelo": args.modelo, "width": w, "height": h,
                       "steps": args.steps, "guidance": args.guidance},
        "escenas": [
            {"indice": i, "archivo": f"still_{i:02d}.png",
             "prompt": prompts[str(i)], "semilla": args.semilla + i}
            for i in indices
        ],
    }
    job_path = r.dir / "stills_job.json"
    job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f">> {len(indices)} stills SDXL @ {w}x{h}, {args.steps} pasos (Kaggle T4, $0)")
    print(f"   negativo: {negativo}")
    print(f"   -> {r.clips}/still_NN.png")
    generar_en_kaggle(
        visual_job=job_path,
        escenas_dir=r.clips,
        dir_kernel=r.dir / "_kernel_stills",
        motion="sdxl",
        timeout_s=args.timeout,
    )
    hechos = sorted(r.clips.glob("still_*.png"))
    print(f"OK stills en {r.clips}: {[p.name for p in hechos]}")


if __name__ == "__main__":
    main()
