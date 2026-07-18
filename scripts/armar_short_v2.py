# Ensamblado del short v2 (Anticitera, guion+voz propios) con clips LTX:
#   1) timestamps por palabra (Whisper medium, guion como verdad) -> palabras_v2.json
#   2) karaoke MINIMO (benchmark: 1 palabra, chica, blanca)      -> subs_v2.ass
#   3) bed 9:16 limpio desde clips LTX (ambiente_bed_clips)      -> bed_ltx_v2.mp4
#   4) quemar subtitulos (ruta relativa: evita el escape de C:)  -> short_v2.mp4
#
# Correr desde la raiz del repo:  python scripts/armar_short_v2.py
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.domain.entities import PalabraTranscrita, Receta, SegmentoTranscrito
from pipeline.domain.planificacion import planificar_escenas
from pipeline.infrastructure.ambiente_clips_ffmpeg import ambiente_bed_clips
from pipeline.infrastructure.subtitulos_karaoke_ass import generar_karaoke
from pipeline.infrastructure.transcripcion_whisper import TranscriptorWhisper

ART = Path("artifacts")
# Vacio = sin cartel quemado; la divulgacion de IA se declara con el toggle de YouTube
# y queda registrada en rastro.json.
DIVULGACION = ""

receta = Receta(id="rec-anim", version=1, estilo="historico", semilla=7)
segmentos = [SegmentoTranscrito(**d)
             for d in json.loads((ART / "segmentos.json").read_text(encoding="utf-8"))]
escenas = planificar_escenas(segmentos, receta)
audio = ART / "recorte.wav"

# 1) palabras con timestamp (checkpoint para no re-transcribir)
pal_path = ART / "palabras_v2.json"
if pal_path.exists():
    palabras = [PalabraTranscrita(**d) for d in json.loads(pal_path.read_text(encoding="utf-8"))]
    print(f"[palabras] reusando checkpoint ({len(palabras)})")
else:
    print("[palabras] Whisper medium por palabra (con guion)...")
    guion = (ART / "guion_historia_v2.txt").read_text(encoding="utf-8")
    palabras = TranscriptorWhisper(modelo="medium", idioma="es", guion=guion) \
        .transcribir_palabras(audio)
    pal_path.write_text(
        json.dumps([p.__dict__ for p in palabras], ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"[palabras] {len(palabras)} palabras")

# 2) karaoke minimo
generar_karaoke(palabras, receta, ART / "subs_v2.ass", DIVULGACION, minimal=True)
print("[subs] karaoke minimo -> artifacts/subs_v2.ass")

# 3) bed limpio desde los clips LTX
clips = {e.indice: ART / "escenas_ltx" / f"escena_{e.indice:02d}.mp4" for e in escenas}
faltan = [i for i, p in clips.items() if not p.exists()]
if faltan:
    sys.exit(f"faltan clips LTX para escenas: {faltan} (correr scripts/generar_ltx.py)")
ambiente_bed_clips(clips, escenas, audio, receta, ART / "bed_ltx_v2.mp4")
print("[bed] artifacts/bed_ltx_v2.mp4")

# 4) quemar karaoke sobre el bed
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", "artifacts/bed_ltx_v2.mp4",
     "-vf", "ass=artifacts/subs_v2.ass", "-c:a", "copy", "artifacts/short_v2.mp4"],
    check=True)
print("OK artifacts/short_v2.mp4")
