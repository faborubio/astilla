#!/usr/bin/env python
"""Limpia una voz grabada (m4a/wav) y la deja lista para el pipeline.

Formaliza el flujo manual de CLAUDE.md (§RETOMAR paso 2). Cadena buena:
    highpass=80 -> arnndn (denoise RNN) -> acompressor -> volume(NdB) -> alimiter
NO usa loudnorm de 1 pasada (sube el ruido en las pausas). En vez de eso:
mide el loudness integrado y aplica una GANANCIA ESTATICA (volume) para llegar
al target -> no bombea el piso de ruido. Ademas recorta automaticamente el
silencio INICIAL (mata la retencion en shorts) y la cola FINAL (silencio +
el click de 'detener grabacion'). Desactivable con --sin-recorte-final.

Uso:
    python scripts/limpiar_voz.py --in artifacts/guion_historia/telegrafo.m4a \
        --out artifacts/voz_telegrafo.wav

    # Ver los tiempos detectados sin escribir nada:
    python scripts/limpiar_voz.py --in ... --out ... --dry-run

Correr SIEMPRE desde la raiz del repo (el modelo arnndn se referencia relativo
para evitar el escape de 'C:' en Windows).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MODELO_RNNN = "artifacts/bd.rnnn"       # relativo a la raiz del repo (Windows-safe)
TARGET_LUFS = -16.0                       # broadcast para shorts
LIMITE_TP = -1.5                          # techo (dBTP) del limiter
UMBRAL_SILENCIO = "-35dB"                # coincide con CLAUDE.md
DUR_SILENCIO = 0.4                         # s de silencio para contar como pausa
COLA_PALABRA = 0.15                       # s de aire que dejamos antes de la 1a palabra
COLA_FINAL = 0.20                         # s de aire que dejamos despues de la ultima palabra
MIN_VOZ = 0.30                            # tramos con voz mas cortos que esto = blip (p.ej. el click)


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def medir_loudness(path: Path) -> float:
    """Loudness integrado (LUFS) via el analisis de loudnorm (solo lectura)."""
    cp = _run([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-af", "loudnorm=print_format=json", "-f", "null", "-",
    ])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", cp.stderr, re.S)
    if not m:
        print("  ! no pude medir loudness, asumo -23 LUFS", file=sys.stderr)
        return -23.0
    return float(json.loads(m.group(0))["input_i"])


def duracion(path: Path) -> float:
    """Duracion en segundos via ffprobe."""
    cp = _run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ])
    try:
        return float(cp.stdout.strip())
    except ValueError:
        return 0.0


def detectar_fin_voz(path: Path, dur_total: float) -> float | None:
    """Segundo donde termina la ultima palabra real (antes del silencio final y el
    click de 'detener grabacion'). Devuelve None si no hay cola muerta que recortar.

    Reconstruye los tramos con voz (complemento de los silencios) y descarta los
    blips mas cortos que MIN_VOZ (el click es un pico brevisimo), quedandose con el
    fin del ultimo tramo hablado de verdad.
    """
    cp = _run([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-af", f"silencedetect=noise={UMBRAL_SILENCIO}:d={DUR_SILENCIO}",
        "-f", "null", "-",
    ])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", cp.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", cp.stderr)]
    if not starts:
        return None

    prev_end = 0.0
    voiced: list[tuple[float, float]] = []
    for i, s in enumerate(starts):
        voiced.append((prev_end, s))
        prev_end = ends[i] if i < len(ends) else dur_total
    if prev_end < dur_total:
        voiced.append((prev_end, dur_total))

    fin_voz = None
    for ini, fin in voiced:
        if fin - ini >= MIN_VOZ:
            fin_voz = fin
    if fin_voz is None or dur_total - fin_voz < 0.2:
        return None  # la voz llega hasta el final: no hay silencio/click que sacar
    return min(dur_total, fin_voz + COLA_FINAL)


def detectar_inicio_voz(path: Path) -> float:
    """Segundo donde termina el silencio inicial (0.0 si arranca hablando)."""
    cp = _run([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-af", f"silencedetect=noise={UMBRAL_SILENCIO}:d={DUR_SILENCIO}",
        "-f", "null", "-",
    ])
    # Si el PRIMER evento es un silence_start en ~0, el video arranca en silencio;
    # su silence_end nos dice cuando entra la voz.
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", cp.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", cp.stderr)]
    if starts and starts[0] < 0.3 and ends:
        return max(0.0, ends[0] - COLA_PALABRA)
    return 0.0


def cadena_limpieza(gain_db: float) -> str:
    return (
        "highpass=f=80,"
        f"arnndn=m={MODELO_RNNN},"
        "acompressor=threshold=-18dB:ratio=3:attack=5:release=50,"
        f"volume={gain_db:.2f}dB,"
        f"alimiter=limit={LIMITE_TP}dB"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="entrada", required=True, type=Path)
    ap.add_argument("--out", dest="salida", type=Path, default=None,
                    help="destino .wav (override); con --nombre def artifacts/shorts/<n>/voz.wav")
    ap.add_argument("--nombre", default=None,
                    help="short: escribe a artifacts/shorts/<n>/voz.wav")
    ap.add_argument("--target", type=float, default=TARGET_LUFS, help="LUFS objetivo (def -16)")
    ap.add_argument("--sin-recorte-final", action="store_true",
                    help="NO recortar la cola (silencio final + click de detener grabacion)")
    ap.add_argument("--dry-run", action="store_true", help="solo reporta tiempos/loudness")
    args = ap.parse_args()

    if args.salida is None:
        if not args.nombre:
            print("ERROR: pasar --out <ruta.wav> o --nombre <short>", file=sys.stderr)
            return 2
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from rutas import RutasShort
        args.salida = RutasShort(args.nombre, crear=True).voz

    if not args.entrada.exists():
        print(f"ERROR: no existe {args.entrada}", file=sys.stderr)
        return 2
    if not Path(MODELO_RNNN).exists():
        print(f"ERROR: falta el modelo {MODELO_RNNN} (correr desde la raiz del repo)", file=sys.stderr)
        return 2

    print(f"[1/4] Denoise preliminar para medir loudness limpio...")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "pre.wav"
        cp = _run([
            "ffmpeg", "-y", "-hide_banner", "-i", str(args.entrada),
            "-af", f"highpass=f=80,arnndn=m={MODELO_RNNN}",
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(tmp),
        ])
        if not tmp.exists():
            print(cp.stderr[-1500:], file=sys.stderr)
            return 1

        lufs = medir_loudness(tmp)
        inicio = detectar_inicio_voz(tmp)
        dur_total = duracion(tmp)
        fin = None if args.sin_recorte_final else detectar_fin_voz(tmp, dur_total)

    gain = args.target - lufs
    print(f"[2/4] Loudness medido: {lufs:.1f} LUFS  ->  ganancia {gain:+.1f} dB (target {args.target})")
    print(f"[3/4] Voz entra en: {inicio:.2f}s  (se recorta el silencio inicial)")
    if fin is not None:
        print(f"      Voz termina en: {fin:.2f}s de {dur_total:.2f}s  "
              f"(se recorta {dur_total - fin:.2f}s de cola: silencio final + click)")
    else:
        print(f"      Sin recorte de cola (no se detecto silencio/click al final).")

    if args.dry_run:
        print("[dry-run] no escribo nada.")
        return 0

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    in_args: list[str] = []
    if inicio > 0.05:
        in_args += ["-ss", f"{inicio:.3f}"]
    if fin is not None:
        in_args += ["-t", f"{fin - inicio:.3f}"]
    print(f"[4/4] Escribiendo {args.salida} ...")
    cp = _run([
        "ffmpeg", "-y", "-hide_banner", *in_args, "-i", str(args.entrada),
        "-af", cadena_limpieza(gain),
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(args.salida),
    ])
    if not args.salida.exists():
        print(cp.stderr[-1500:], file=sys.stderr)
        return 1

    print(f"OK -> {args.salida}")
    print("     Siguiente: python -m pipeline.animado --audio "
          f"{args.salida} --guion <guion.txt> --prompts-file <p.json> "
          "--autorizacion original --estilo historico --modelo medium --stub-visual")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
