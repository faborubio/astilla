# Re-arma el bed de un short con cortes de escena ALINEADOS AL CONTENIDO y re-quema
# los subtitulos. Fix del gotcha 13: los boundaries que salen de los segmentos
# (transcritos con el guion como prompt) quedan corridos respecto del audio real.
# Aca se pasan a mano los 7 cortes derivados de palabras_<nombre>.json (timing preciso),
# uno por clip/beat. Los clips se re-ajustan con setpts (no se regeneran).
#
# Uso:
#   python scripts/retimear_bed.py --nombre pelo_catapultas \
#       --audio artifacts/voz_pelo_catapultas.wav \
#       --clips-dir artifacts/escenas_ltx \
#       --cortes "0,5.9; 5.9,14.9; 14.9,17.7; 17.7,26.3; 26.3,36.9; 36.9,41.3; 41.3,50.9"
#
# Tip: correr antes  python scripts/mostrar_palabras.py  (o mirar palabras_<nombre>.json)
# para elegir los cortes en los limites de beat.
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.domain.entities import Escena, Receta
from pipeline.infrastructure.ambiente_clips_ffmpeg import ambiente_bed_clips

ART = Path("artifacts")


def main() -> None:
    ap = argparse.ArgumentParser(description="Re-arma el bed con cortes alineados al contenido.")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--audio", required=True, type=Path)
    ap.add_argument("--clips-dir", type=Path, default=ART / "escenas_ltx")
    ap.add_argument("--cortes", required=True,
                    help='pares "ini,fin" separados por ; (uno por clip). ej "0,5.9; 5.9,14.9"')
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--estilo", default="historico")
    args = ap.parse_args()

    pares = []
    for tramo in args.cortes.split(";"):
        a, b = (x.strip() for x in tramo.split(","))
        pares.append((float(a), float(b)))

    receta = Receta(id="rec-anim", version=1, estilo=args.estilo, semilla=args.semilla)
    escenas = [Escena(indice=i, inicio_s=a, fin_s=b, texto="", prompt="", semilla=args.semilla + i)
               for i, (a, b) in enumerate(pares)]
    clips = {i: args.clips_dir / f"escena_{i:02d}.mp4" for i in range(len(escenas))}
    faltan = [i for i, p in clips.items() if not p.exists()]
    if faltan:
        sys.exit(f"faltan clips: {faltan} en {args.clips_dir}")

    bed = ART / f"bed_{args.nombre}.mp4"
    ambiente_bed_clips(clips, escenas, args.audio, receta, bed)
    print(f"[bed] re-timeado -> {bed}")
    for e in escenas:
        print(f"  esc{e.indice}: {e.inicio_s:6.2f}-{e.fin_s:6.2f}  dur {e.duracion_s:5.2f}s")

    # re-quemar los subtitulos (ruta relativa: evita el escape de C: en Windows)
    import subprocess
    salida = f"artifacts/short_{args.nombre}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(bed),
         "-vf", f"ass=artifacts/subs_{args.nombre}.ass", "-c:a", "copy", salida],
        check=True)
    print(f"OK {salida}")


if __name__ == "__main__":
    main()
