"""Flujo HABLANTE (CASO-009, arquitectura de capas): personaje audio-driven.

Capa 1 — PERSONAJE: SadTalker hace "hablar" al retrato-ancla con el audio original
-> narrator.mp4 (cabeza + cara + labios sincronizados con la voz). Es la parte que
de-riesga todo el caso: confirmar que un personaje generado por IA habla decente.

Capa 2 (ambiente, reusa los fondos de --motion) y la composicion de capas con ffmpeg
se construyen DESPUES de validar la cabeza. Este modulo solo entrega narrator.mp4.

    # validar la cabeza hablante (Kaggle T4):
    python -m pipeline.hablante --audio sources/x.wav --autorizacion dominio_publico \
        --evidencia "URL" --estilo neon --semilla 1 --prompts-llm
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .animado import ARTIFACTS, RAIZ, _fuente_y_auth
from .domain import derechos
from .domain.entities import Receta, Recorte, Timecode
from .domain.planificacion import planificar_escenas, prompt_personaje
from .infrastructure.ensamblado_ffmpeg import _duracion_s
from .infrastructure.recorte_ffmpeg import extraer_recorte
from .infrastructure.transcripcion_whisper import TranscriptorWhisper


def main() -> None:
    p = argparse.ArgumentParser(description="Astilla — flujo hablante (CASO-009, capas).")
    p.add_argument("--estilo", default="neon", choices=["neon", "comic", "minimal", "historico"])
    p.add_argument("--semilla", type=int, default=1)
    p.add_argument("--inicio", type=float, default=0.0)
    p.add_argument("--fin", type=float, default=0.0)
    p.add_argument("--modelo", default="small")
    p.add_argument("--audio", default=None)
    p.add_argument("--autorizacion", default="original",
                   choices=["original", "dominio_publico", "licencia", "cliente"])
    p.add_argument("--titular", default=None)
    p.add_argument("--evidencia", default=None)
    p.add_argument("--prompts-llm", action="store_true",
                   help="biblia de personaje por Claude para el ancla; requiere ANTHROPIC_API_KEY")
    args = p.parse_args()

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    # --- Gate + recorte + transcripcion (para describir al personaje) --------
    fuente, auth = _fuente_y_auth(args)
    derechos.verificar(fuente, auth)  # GATE (ADR-009): nada sin autorizacion
    print(f"[gate] autorizacion OK ({auth.tipo.value})")

    dur = _duracion_s(fuente.ruta_audio)
    fin = args.fin if args.fin > 0 else dur
    recorte = Recorte(fuente_id=fuente.id, timecode=Timecode(inicio_s=args.inicio, fin_s=fin))
    audio_recorte = extraer_recorte(fuente.ruta_audio, recorte, ARTIFACTS / "recorte.wav")
    receta = Receta(id="rec-habla", version=1, estilo=args.estilo, semilla=args.semilla)

    seg_path = ARTIFACTS / "segmentos.json"
    if seg_path.exists():
        from .domain.entities import SegmentoTranscrito
        segmentos = [SegmentoTranscrito(**d) for d in json.loads(seg_path.read_text(encoding="utf-8"))]
        print(f"[transcripcion] reusando checkpoint ({len(segmentos)} segmentos)")
    else:
        print("[transcripcion] faster-whisper...")
        segmentos = TranscriptorWhisper(modelo=args.modelo, idioma="es").transcribir(audio_recorte)
        seg_path.write_text(json.dumps([s.__dict__ for s in segmentos], ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Descripcion del personaje (biblia de Claude si esta, si no heuristica) ---
    biblia = ""
    if args.prompts_llm:
        try:
            from .infrastructure.prompts_claude import refinar_prompts
            biblia = refinar_prompts(planificar_escenas(segmentos, receta), receta.estilo).biblia
            (ARTIFACTS / "biblia_estilo.txt").write_text(biblia, encoding="utf-8")
            print("[prompts] biblia de personaje por Claude -> artifacts/biblia_estilo.txt")
        except Exception as e:
            print(f"[prompts] Claude no disponible ({type(e).__name__}); uso ancla heuristica")

    coherencia = {
        "ancla_prompt": prompt_personaje(segmentos, receta.estilo, biblia),
        "ancla_semilla": receta.semilla,
        # Negativo fuerte SOLO para el ancla: forzar primer plano de cara (si no,
        # SadTalker no detecta landmarks en un plano abierto).
        "ancla_negativo": ("full body, full shot, wide shot, long shot, distant, "
                           "small face, multiple people, crowd, no face, back view, "
                           "side profile, looking away, occluded face"),
    }

    # --- Capa 1: despachar talking-head a Kaggle y bajar narrator.mp4 --------
    from .infrastructure.ejecutor_kaggle import generar_talking_en_kaggle
    job_id = f"{receta.id}_v{receta.version}_s{receta.semilla}"
    narrator = generar_talking_en_kaggle(
        audio_recorte, coherencia, RAIZ / "kaggle_kernel_talking",
        ARTIFACTS / "hablante", job_id,
    )

    print("\n=== CAPA 1 LISTA (validacion talking-head) ===")
    print(f"Personaje hablando: {narrator}")
    print("Revisa que la cara se vea bien y los labios sigan la voz.")
    print("Si OK -> siguiente: generar ambiente + componer capas. Si no -> plan B Wav2Lip.")


if __name__ == "__main__":
    main()
