# Ensamblado de un short (guion+voz propios) con clips LTX ya generados.
# Version parametrizada de armar_short_v2.py (que estaba clavado al Anticitera).
#   1) timestamps por palabra (Whisper medium, guion como verdad) -> palabras_<nombre>.json
#   2) karaoke MINIMO (benchmark: 1 palabra, chica, blanca)       -> subs_<nombre>.ass
#   3) bed 9:16 limpio desde clips LTX (ambiente_bed_clips)        -> bed_<nombre>.mp4
#   4) quemar subtitulos (ruta relativa: evita el escape de C:)   -> short_<nombre>.mp4
#
# Correr desde la raiz del repo, ej:
#   python scripts/armar_short.py --nombre telegrafo \
#       --segmentos artifacts/segmentos_telegrafo.json \
#       --audio artifacts/voz_telegrafo.wav \
#       --guion artifacts/guion_telegrafo.txt
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ para reconciliar_palabras

from pipeline.domain.entities import PalabraTranscrita, Receta, SegmentoTranscrito
from pipeline.domain.planificacion import planificar_escenas
from pipeline.infrastructure.ambiente_clips_ffmpeg import ambiente_bed_clips
from pipeline.infrastructure.subtitulos_karaoke_ass import generar_karaoke
from pipeline.infrastructure.transcripcion_whisper import TranscriptorWhisper
from reconciliar_palabras import _dur_audio, reconciliar

ART = Path("artifacts")
# Vacio = sin cartel quemado; la divulgacion de IA se declara con el toggle de YouTube
# y queda registrada en rastro.json.
DIVULGACION = ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Arma un short desde clips LTX + voz propia.")
    ap.add_argument("--nombre", required=True, help="basename del short (ej: telegrafo)")
    ap.add_argument("--segmentos", required=True, type=Path, help="segmentos.json del guion")
    ap.add_argument("--audio", required=True, type=Path, help="voz limpia .wav")
    ap.add_argument("--guion", required=True, type=Path, help=".txt del guion (verdad para Whisper)")
    ap.add_argument("--clips-dir", type=Path, default=ART / "escenas_ltx")
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--estilo", default="historico")
    args = ap.parse_args()

    receta = Receta(id="rec-anim", version=1, estilo=args.estilo, semilla=args.semilla)
    segmentos = [SegmentoTranscrito(**d)
                 for d in json.loads(args.segmentos.read_text(encoding="utf-8"))]
    escenas = planificar_escenas(segmentos, receta)

    # 1) palabras con timestamp (checkpoint por short para no re-transcribir)
    pal_path = ART / f"palabras_{args.nombre}.json"
    if pal_path.exists():
        palabras = [PalabraTranscrita(**d) for d in json.loads(pal_path.read_text(encoding="utf-8"))]
        print(f"[palabras] reusando checkpoint {pal_path.name} ({len(palabras)})")
    else:
        print("[palabras] Whisper medium por palabra...")
        guion = args.guion.read_text(encoding="utf-8")
        # el pase por palabra NO usa el guion como prompt (rompe el timing, ver gotcha
        # en transcripcion_whisper.transcribir_palabras); el texto correcto se recupera
        # reconciliando con el guion-verdad abajo.
        crudas = TranscriptorWhisper(modelo="medium", idioma="es") \
            .transcribir_palabras(args.audio)
        dur = _dur_audio(args.audio)
        recon, n_anclas, N = reconciliar(
            guion, [p.__dict__ for p in crudas], dur)
        print(f"[palabras] whisper={len(crudas)} · reconciliadas al guion={N} "
              f"({100*n_anclas//max(N,1)}% anclado)")
        palabras = [PalabraTranscrita(**d) for d in recon]
        pal_path.write_text(
            json.dumps([p.__dict__ for p in palabras], ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"[palabras] -> {pal_path.name}")

    # 2) karaoke minimo
    subs = ART / f"subs_{args.nombre}.ass"
    generar_karaoke(palabras, receta, subs, DIVULGACION, minimal=True)
    print(f"[subs] karaoke minimo -> {subs}")

    # 3) bed limpio desde los clips LTX
    clips = {e.indice: args.clips_dir / f"escena_{e.indice:02d}.mp4" for e in escenas}
    faltan = [i for i, p in clips.items() if not p.exists()]
    if faltan:
        sys.exit(f"faltan clips LTX para escenas: {faltan} (correr scripts/generar_ltx.py)")
    bed = ART / f"bed_{args.nombre}.mp4"
    ambiente_bed_clips(clips, escenas, args.audio, receta, bed)
    print(f"[bed] {bed}")

    # 4) quemar karaoke sobre el bed (ruta relativa: evita escape de C: en Windows)
    salida = f"artifacts/short_{args.nombre}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(bed),
         "-vf", f"ass=artifacts/subs_{args.nombre}.ass", "-c:a", "copy", salida],
        check=True)
    print(f"OK {salida}")


if __name__ == "__main__":
    main()
