"""Entry point: corre el pipeline end-to-end y produce un short 9:16 real.

    python -m pipeline.cli --estilo neon --semilla 1

Para la demo, la fuente es audio ORIGINAL sintetizado en local (H-6): cierra el
loop a $0 sin dependencias externas. En produccion, la fuente es el audio del
cliente con su Autorizacion; el resto del pipeline es identico.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .domain.entities import (
    Autorizacion,
    Fuente,
    Receta,
    Recorte,
    Timecode,
    TipoAutorizacion,
)
from .domain.orquestador import Orquestador
from .infrastructure.audio_demo_windows import generar_audio_demo
from .infrastructure.ensamblado_ffmpeg import EnsambladorFFmpeg
from .infrastructure.recorte_ffmpeg import extraer_recorte
from .infrastructure.subtitulos_ass import SubtituladorASS
from .infrastructure.transcripcion_whisper import TranscriptorWhisper
from .infrastructure.visual_fondo import GeneradorFondoDeterminista

RAIZ = Path(__file__).resolve().parent.parent
ARTIFACTS = RAIZ / "artifacts"


def main() -> None:
    p = argparse.ArgumentParser(description="Astilla — generar un short 9:16 (demo end-to-end).")
    p.add_argument("--estilo", default="neon", choices=["neon", "comic", "minimal", "historico"])
    p.add_argument("--semilla", type=int, default=1)
    p.add_argument("--inicio", type=float, default=0.0, help="inicio del recorte (s)")
    p.add_argument("--fin", type=float, default=0.0, help="fin del recorte (s); 0 = fuente completa")
    p.add_argument("--modelo", default="small", help="modelo faster-whisper")
    p.add_argument("--audio", default=None, help="ruta a un audio/video real (tu voz, dominio público, licenciado). Si se omite, usa el TTS de demo.")
    p.add_argument(
        "--autorizacion",
        default="original",
        choices=["original", "dominio_publico", "licencia", "cliente"],
        help="tipo de Autorizacion para --audio (el gate la exige).",
    )
    p.add_argument("--titular", default=None, help="titular del derecho (autor/cliente/sello).")
    p.add_argument("--evidencia", default=None, help="referencia del derecho (URL de licencia, contrato, 'dominio público').")
    args = p.parse_args()

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    # 1) Fuente + su Autorizacion (el gate la exige, ADR-009) ----------------
    if args.audio:
        ruta = Path(args.audio)
        if not ruta.exists():
            raise SystemExit(f"No existe el archivo: {ruta}")
        print(f"[1/6] Ingiriendo fuente real: {ruta.name}")
        fuente = Fuente.desde_archivo(id=ruta.stem[:32], titulo=ruta.stem, ruta_audio=ruta)
        if not args.evidencia:
            raise SystemExit(
                "El gate de derechos exige --evidencia (p.ej. la URL de licencia o 'dominio público')."
            )
        autorizacion = Autorizacion(
            id=f"auth-{fuente.id}",
            fuente_id=fuente.id,
            tipo=TipoAutorizacion(args.autorizacion),
            titular=args.titular or "(sin especificar)",
            evidencia=args.evidencia,
        )
    else:
        print("[1/6] Generando audio fuente (TTS nativo Windows, contenido original)...")
        audio_fuente = generar_audio_demo(ARTIFACTS / "fuente.wav")
        fuente = Fuente.desde_archivo(
            id="demo-001", titulo="Anecdota del render perdido", ruta_audio=audio_fuente
        )
        autorizacion = Autorizacion(
            id="auth-001",
            fuente_id=fuente.id,
            tipo=TipoAutorizacion.ORIGINAL,
            titular="Astilla (contenido original sintetizado en demo)",
            evidencia="Audio generado por nosotros para la demo; original, sin terceros.",
        )

    audio_fuente = fuente.ruta_audio

    # 2) Recorte operator-driven (H-4) ---------------------------------------
    from .infrastructure.ensamblado_ffmpeg import _duracion_s

    dur_fuente = _duracion_s(audio_fuente)
    fin = args.fin if args.fin > 0 else dur_fuente
    recorte = Recorte(fuente_id=fuente.id, timecode=Timecode(inicio_s=args.inicio, fin_s=fin))
    print(f"      Fuente: {dur_fuente:.1f}s · recorte: [{recorte.timecode.inicio_s:.1f}, {recorte.timecode.fin_s:.1f}]s")

    print("[2/6] Extrayendo audio del recorte...")
    audio_recorte = extraer_recorte(audio_fuente, recorte, ARTIFACTS / "recorte.wav")

    # 3) Receta versionada ---------------------------------------------------
    receta = Receta(id="rec-base", version=1, estilo=args.estilo, semilla=args.semilla)

    # 4) Cablear el orquestador con los adaptadores --------------------------
    orq = Orquestador(
        transcriptor=TranscriptorWhisper(modelo=args.modelo, idioma="es"),
        subtitulador=SubtituladorASS(),
        visualizador=GeneradorFondoDeterminista(),
        ensamblador=EnsambladorFFmpeg(),
        dir_trabajo=ARTIFACTS,
    )

    print(f"[3/6] Transcribiendo (faster-whisper '{args.modelo}', es)...")
    print("[4/6] Subtitulos ASS + [5/6] visual determinista + [6/6] ensamblado 9:16...")
    short, rastro, job = orq.generar_short(
        fuente=fuente,
        autorizacion=autorizacion,
        recorte=recorte,
        receta=receta,
        audio_recorte=audio_recorte,
    )

    print("\n=== LISTO ===")
    print(f"Job:        {job.id}  ({job.estado.value})")
    print(f"Stages:     {rastro.stages}")
    print(f"Estilo/sem: {rastro.estilo} / {rastro.semilla}  (autorizacion: {rastro.autorizacion_tipo})")
    print(f"Divulgacion IA: {rastro.divulgacion_ia}")
    print(f"Video:      {short.ruta_video}  ({short.duracion_s:.1f}s)")
    print(f"Rastro:     {ARTIFACTS / 'rastro.json'}")


if __name__ == "__main__":
    main()
