"""Flujo animado (CASO-003, Fase 2): generacion visual por escena via Colab.

Dos fases resumibles (ADR-002):
  Fase A (local): gate -> transcripcion -> planificar escenas -> exportar visual_job.json.
                  Si faltan las imagenes, imprime instrucciones de Colab y para.
  Fase B (local): con las imagenes de escena presentes -> ensamblado animado.

    # 1) preparar el job (transcribe + planifica + exporta el spec para Colab)
    python -m pipeline.animado --audio fuente.wav --autorizacion dominio_publico --evidencia "URL"

    # 2) (en Colab) correr el notebook con visual_job.json -> bajar escenas/ aqui

    # 3) ensamblar el short animado (o probar ya con stand-ins)
    python -m pipeline.animado --audio fuente.wav --autorizacion dominio_publico --evidencia "URL" --ensamblar
    python -m pipeline.animado --stub-visual   # prueba local sin Colab
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .domain import derechos
from .domain.entities import (
    Autorizacion,
    Fuente,
    Receta,
    Recorte,
    Timecode,
    TipoAutorizacion,
)
from .domain.orquestador import DIVULGACION_IA
from .domain.planificacion import planificar_escenas
from .infrastructure.audio_demo_windows import generar_audio_demo
from .infrastructure.ensamblado_escenas_ffmpeg import EnsambladorEscenas
from .infrastructure.ensamblado_ffmpeg import _duracion_s
from .infrastructure.exportar_job_visual import exportar_job_visual
from .infrastructure.recorte_ffmpeg import extraer_recorte
from .infrastructure.stub_visual import generar_stubs
from .infrastructure.subtitulos_ass import SubtituladorASS
from .infrastructure.transcripcion_whisper import TranscriptorWhisper

RAIZ = Path(__file__).resolve().parent.parent
ARTIFACTS = RAIZ / "artifacts"
ESCENAS_DIR = ARTIFACTS / "escenas"


def _fuente_y_auth(args) -> tuple[Fuente, Autorizacion]:
    if args.audio:
        ruta = Path(args.audio)
        if not ruta.exists():
            raise SystemExit(f"No existe el archivo: {ruta}")
        fuente = Fuente.desde_archivo(id=ruta.stem[:32], titulo=ruta.stem, ruta_audio=ruta)
        if not args.evidencia:
            raise SystemExit("El gate exige --evidencia (URL de licencia, contrato o 'dominio publico').")
        auth = Autorizacion(
            id=f"auth-{fuente.id}", fuente_id=fuente.id,
            tipo=TipoAutorizacion(args.autorizacion),
            titular=args.titular or "(sin especificar)", evidencia=args.evidencia,
        )
    else:
        audio = generar_audio_demo(ARTIFACTS / "fuente.wav")
        fuente = Fuente.desde_archivo(id="demo-001", titulo="Anecdota del render perdido", ruta_audio=audio)
        auth = Autorizacion(
            id="auth-001", fuente_id=fuente.id, tipo=TipoAutorizacion.ORIGINAL,
            titular="Astilla (demo, original)", evidencia="Audio original sintetizado para la demo.",
        )
    return fuente, auth


def main() -> None:
    p = argparse.ArgumentParser(description="Astilla — flujo animado (Fase 2, Colab).")
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
    p.add_argument("--guion", default=None,
                   help="MODO ORIGINAL: .txt con el guion propio. Es la verdad de referencia: "
                        "sesga a Whisper hacia las palabras correctas (nombres propios) y este "
                        "solo resuelve el timing. Solo aplica si el contenido es tuyo.")
    p.add_argument("--prompts-file", default=None,
                   help="JSON {indice: prompt} para fijar a mano el prompt visual de cada escena "
                        "(override del operador, H-4). Gana sobre el heuristico y sobre --prompts-llm. "
                        "Util cuando el heuristico elige palabras abstractas y no visuales.")
    p.add_argument("--ensamblar", action="store_true", help="ensamblar con las imagenes ya generadas")
    p.add_argument("--stub-visual", action="store_true", help="generar stand-ins locales y ensamblar (sin Colab/Kaggle)")
    p.add_argument("--kaggle", action="store_true", help="despachar la generacion a Kaggle (GPU), esperar y ensamblar")
    p.add_argument("--prompts-llm", action="store_true", help="refinar prompts con Claude (biblia de estilo + coherencia, H-1/H-2); requiere ANTHROPIC_API_KEY")
    p.add_argument("--motion", default="kenburns", choices=["kenburns", "animatediff"],
                   help="kenburns = stills animados (rapido); animatediff = clips animados reales (Kaggle GPU)")
    p.add_argument("--coherencia", action="store_true",
                   help="ancla de personaje via IP-Adapter (misma cara en todas las escenas, H-1/CASO-006); solo con --motion animatediff")
    args = p.parse_args()

    if args.coherencia and args.motion != "animatediff":
        raise SystemExit("--coherencia requiere --motion animatediff (IP-Adapter sobre los clips).")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    # --- Fase A: gate + transcripcion + planificacion -----------------------
    fuente, auth = _fuente_y_auth(args)
    derechos.verificar(fuente, auth)  # GATE (ADR-009): nada sin autorizacion
    print(f"[gate] autorizacion OK ({auth.tipo.value})")

    dur_fuente = _duracion_s(fuente.ruta_audio)
    fin = args.fin if args.fin > 0 else dur_fuente
    recorte = Recorte(fuente_id=fuente.id, timecode=Timecode(inicio_s=args.inicio, fin_s=fin))
    audio_recorte = extraer_recorte(fuente.ruta_audio, recorte, ARTIFACTS / "recorte.wav")
    receta = Receta(id="rec-anim", version=1, estilo=args.estilo, semilla=args.semilla)

    seg_path = ARTIFACTS / "segmentos.json"
    if seg_path.exists():
        from .domain.entities import SegmentoTranscrito
        segmentos = [SegmentoTranscrito(**d) for d in json.loads(seg_path.read_text(encoding="utf-8"))]
        print(f"[transcripcion] reusando checkpoint ({len(segmentos)} segmentos)")
    else:
        guion_txt = Path(args.guion).read_text(encoding="utf-8") if args.guion else ""
        if guion_txt:
            print("[transcripcion] faster-whisper + guion propio (modo original)...")
        else:
            print("[transcripcion] faster-whisper...")
        segmentos = TranscriptorWhisper(
            modelo=args.modelo, idioma="es", guion=guion_txt
        ).transcribir(audio_recorte)
        seg_path.write_text(json.dumps([s.__dict__ for s in segmentos], ensure_ascii=False, indent=2), encoding="utf-8")

    escenas = planificar_escenas(segmentos, receta)

    # Refinar prompts con Claude (biblia de estilo + coherencia, H-1/H-2) -------
    biblia = ""
    if args.prompts_llm:
        import dataclasses
        try:
            from .infrastructure.prompts_claude import refinar_prompts

            res = refinar_prompts(escenas, receta.estilo)
            escenas = [
                dataclasses.replace(e, prompt=res.prompts.get(e.indice, e.prompt))
                for e in escenas
            ]
            biblia = res.biblia  # descripcion del personaje recurrente -> ancla IP-Adapter
            (ARTIFACTS / "biblia_estilo.txt").write_text(res.biblia, encoding="utf-8")
            print(f"[prompts] refinados por Claude · biblia -> artifacts/biblia_estilo.txt")
        except Exception as e:  # sin API key / sin red / error -> fallback heuristico
            print(f"[prompts] Claude no disponible ({type(e).__name__}); uso prompts heuristicos")

    # Override del operador (H-4): prompts visuales fijados a mano. Ultima palabra.
    if args.prompts_file:
        import dataclasses
        fijos = {int(k): v for k, v in json.loads(
            Path(args.prompts_file).read_text(encoding="utf-8")).items()}
        escenas = [
            dataclasses.replace(e, prompt=fijos[e.indice]) if e.indice in fijos else e
            for e in escenas
        ]
        print(f"[prompts] override del operador: {len(fijos)} escenas fijadas a mano")

    motion_modo = "animatediff" if args.motion == "animatediff" else "imagen"

    # Coherencia de personaje (CASO-006, H-1): retrato-ancla + IP-Adapter por escena.
    coherencia = None
    if args.coherencia:  # validado arriba: implica motion_modo == "animatediff"
        from .domain.planificacion import prompt_personaje
        coherencia = {
            "ip_adapter": True,
            "ancla_prompt": prompt_personaje(segmentos, receta.estilo, biblia),
            "ancla_semilla": receta.semilla,
            "ip_scale": 0.6,
        }
        print(f"[coherencia] IP-Adapter ON · retrato-ancla del personaje (semilla {receta.semilla})")

    exportar_job_visual(escenas, receta, ARTIFACTS / "visual_job.json",
                        motion=motion_modo, coherencia=coherencia)
    print(f"[planificacion] {len(escenas)} escenas ({args.motion}) -> artifacts/visual_job.json")

    SubtituladorASS().generar(segmentos, receta, ARTIFACTS / "subtitulos.ass", DIVULGACION_IA)

    def artefacto(e):  # nombre segun el modo de movimiento
        return e.nombre_clip if motion_modo == "animatediff" else e.nombre_artefacto

    # --- Fase B: obtener artefactos de escena ------------------------------
    if args.stub_visual:
        if motion_modo == "animatediff":
            raise SystemExit("--stub-visual solo aplica a --motion kenburns. Para animatediff usa --kaggle.")
        print("[visual] generando stand-ins locales (NO es IA; prueba de movimiento)...")
        generar_stubs(escenas, receta, ESCENAS_DIR)
    elif args.kaggle:
        from .infrastructure.ejecutor_kaggle import generar_en_kaggle
        generar_en_kaggle(ARTIFACTS / "visual_job.json", ESCENAS_DIR, RAIZ / "kaggle_kernel", motion=motion_modo)

    faltan = [e.indice for e in escenas if not (ESCENAS_DIR / artefacto(e)).exists()]
    if not args.ensamblar and not args.stub_visual and not args.kaggle:
        print("\n=== Fase A lista. Siguiente paso: generar visuales ===")
        print(f"  Kaggle (auto):  re-corre agregando  --kaggle  (modo {args.motion})")
        print(f"  Colab (manual): sube artifacts/visual_job.json al notebook (ver COLAB.md),")
        print(f"                  baja los artefactos a {ESCENAS_DIR}\\ y re-corre con --ensamblar.")
        if motion_modo == "imagen":
            print(f"  Prueba local:   --stub-visual  (movimiento sin IA)")
        return
    if faltan:
        raise SystemExit(f"Faltan artefactos de escena {faltan}. Corre Kaggle (--kaggle) o usa --stub-visual (kenburns).")

    if motion_modo == "animatediff":
        from .infrastructure.ensamblado_clips_ffmpeg import EnsambladorClips
        print("[ensamblado] concatenando clips animados + subtitulos + divulgacion...")
        ensamblador = EnsambladorClips()
    else:
        print("[ensamblado] animando stills (Ken Burns) + subtitulos + divulgacion...")
        ensamblador = EnsambladorEscenas()
    destino = ensamblador.ensamblar(
        ESCENAS_DIR, escenas, audio_recorte, ARTIFACTS / "subtitulos.ass", receta, ARTIFACTS / "short_animado.mp4"
    )
    print("\n=== LISTO ===")
    print(f"Escenas:  {len(escenas)}  (estilo {receta.estilo}, semilla {receta.semilla})")
    print(f"Video:    {destino}  ({recorte.timecode.duracion_s:.1f}s, 9:16)")
    print(f"Divulgacion IA: {DIVULGACION_IA}")


if __name__ == "__main__":
    main()
