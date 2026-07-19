# Ensamblado de un short (guion+voz propios) con clips LTX ya generados.
# Version parametrizada de armar_short_v2.py (que estaba clavado al Anticitera).
# Folder-aware (jul 2026): todo vive en artifacts/shorts/<nombre>/ (ver scripts/rutas.py).
#   1) timestamps por palabra (Whisper medium, guion como verdad) -> <n>/palabras.json
#   2) karaoke MINIMO (benchmark: 1 palabra, chica, blanca)       -> <n>/subs.ass
#   3) bed 9:16 limpio desde clips LTX (ambiente_bed_clips)        -> <n>/bed.mp4
#   4) quemar subtitulos (ruta relativa: evita el escape de C:)   -> <n>/short.mp4
#
# Correr desde la raiz del repo. Con la convencion de carpeta basta el --nombre:
#   python scripts/armar_short.py --nombre telegrafo --semilla 7
# (--audio/--guion/--segmentos/--clips-dir se pueden pasar para override manual)
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
from rutas import RutasShort

# Vacio = sin cartel quemado; la divulgacion de IA se declara con el toggle de YouTube
# y queda registrada en rastro.json.
DIVULGACION = ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Arma un short desde clips LTX + voz propia.")
    ap.add_argument("--nombre", required=True, help="basename del short (ej: telegrafo)")
    ap.add_argument("--segmentos", type=Path, default=None, help="override; def <n>/segmentos.json")
    ap.add_argument("--audio", type=Path, default=None, help="override; def <n>/voz.wav")
    ap.add_argument("--guion", type=Path, default=None, help="override; def <n>/guion.txt")
    ap.add_argument("--clips-dir", type=Path, default=None, help="override; def <n>/clips")
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--estilo", default="historico")
    args = ap.parse_args()

    r = RutasShort(args.nombre)
    audio = args.audio or r.voz
    guion_path = args.guion or r.guion
    segmentos_path = args.segmentos or r.segmentos
    clips_dir = args.clips_dir or r.clips

    receta = Receta(id="rec-anim", version=1, estilo=args.estilo, semilla=args.semilla)
    segmentos = [SegmentoTranscrito(**d)
                 for d in json.loads(segmentos_path.read_text(encoding="utf-8"))]
    escenas = planificar_escenas(segmentos, receta)

    # 1) palabras con timestamp (checkpoint por short para no re-transcribir)
    pal_path = r.palabras
    if pal_path.exists():
        palabras = [PalabraTranscrita(**d) for d in json.loads(pal_path.read_text(encoding="utf-8"))]
        print(f"[palabras] reusando checkpoint {pal_path} ({len(palabras)})")
    else:
        print("[palabras] Whisper medium por palabra...")
        guion = guion_path.read_text(encoding="utf-8")
        # el pase por palabra NO usa el guion como prompt (rompe el timing, ver gotcha
        # en transcripcion_whisper.transcribir_palabras); el texto correcto se recupera
        # reconciliando con el guion-verdad abajo.
        crudas = TranscriptorWhisper(modelo="medium", idioma="es") \
            .transcribir_palabras(audio)
        dur = _dur_audio(audio)
        recon, n_anclas, N = reconciliar(
            guion, [p.__dict__ for p in crudas], dur)
        print(f"[palabras] whisper={len(crudas)} · reconciliadas al guion={N} "
              f"({100*n_anclas//max(N,1)}% anclado)")
        palabras = [PalabraTranscrita(**d) for d in recon]
        pal_path.write_text(
            json.dumps([p.__dict__ for p in palabras], ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"[palabras] -> {pal_path}")

    # 2) karaoke minimo
    subs = r.subs
    generar_karaoke(palabras, receta, subs, DIVULGACION, minimal=True)
    print(f"[subs] karaoke minimo -> {subs}")

    # 3) bed limpio desde los clips LTX
    clips = {e.indice: clips_dir / f"escena_{e.indice:02d}.mp4" for e in escenas}
    faltan = [i for i, p in clips.items() if not p.exists()]
    if faltan:
        sys.exit(f"faltan clips LTX para escenas: {faltan} (correr scripts/generar_ltx.py)")
    bed = r.bed
    ambiente_bed_clips(clips, escenas, audio, receta, bed)
    print(f"[bed] {bed}")

    # 4) quemar karaoke sobre el bed (ruta relativa: evita escape de C: en Windows)
    salida = str(r.short)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(bed),
         "-vf", f"ass={r.subs.as_posix()}", "-c:a", "copy", salida],
        check=True)
    print(f"OK {salida}")


if __name__ == "__main__":
    main()
