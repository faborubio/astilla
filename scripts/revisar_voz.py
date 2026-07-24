#!/usr/bin/env python
"""Revisa voz.wav en busca de REPETICIONES y STUTTERS antes de armar.

Nace de la odisea 2026-07-23 (mercurio/papel/cihuang): la transcripcion por
SEGMENTOS esconde repeticiones cuando el hueco entre tomas es <0.4s o hay una tos
(Whisper las fusiona en un segmento largo). Peor: un tartamudeo pegado ("y las
paredes del tunel... y las paredes del tunel estaban") Whisper lo transcribe como
UNA palabra estirada (ej. "tunel" durando 3.4s), asi que ni el detector de
repeticiones exactas lo ve. Dos deteccciones complementarias + el OIDO de Fabian:

  1) REPETICIONES: >=3 palabras identicas pegadas en el timeline de palabras.
  2) STUTTERS: palabras con duracion anormal (>1.1s) = toma repetida fusionada.
     (Ojo: numeros largos "seiscientos setenta y cinco" y pausas antes de una
     conjuncion tambien disparan -> confirmar la zona con silencedetect + oido.)

Para CORTAR: usar los SILENCIOS ACUSTICOS (silencedetect), NO los timestamps de
palabra de Whisper, que en la zona del stutter son basura. Verificar SIEMPRE
despues de cortar (re-correr esto). El gate final es el oido de Fabian.

Uso:
    python scripts/revisar_voz.py --nombre mercurio_tumba papel_veneno cihuang
    python scripts/revisar_voz.py artifacts/shorts/x/voz.wav
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

from faster_whisper import WhisperModel

STUTTER_THRESH = 1.1  # una palabra normal dura <1s


def _norm(w: str) -> str:
    return re.sub(r"[^\wáéíóúñü]", "", w.lower())


def revisar(model: WhisperModel, wav: Path) -> None:
    segs, _ = model.transcribe(str(wav), language="es", word_timestamps=True,
                               vad_filter=True,
                               vad_parameters=dict(min_silence_duration_ms=150))
    words = [(w.word.strip(), w.start, w.end)
             for s in segs for w in (s.words or [])]
    nm = [_norm(w) for (w, _, _) in words]
    n = len(words)
    print(f"\n===== {wav}  ({n} palabras) =====")

    # 1) repeticiones exactas (>=3 palabras pegadas)
    reps, i = [], 0
    while i < n:
        best = 0
        for k in range(min(18, (n - i) // 2), 2, -1):
            if nm[i:i + k] == nm[i + k:i + 2 * k] and all(nm[i:i + k]):
                best = k
                break
        if best >= 3:
            reps.append((words[i][1], words[i + best][1],
                         " ".join(w for (w, _, _) in words[i:i + best])))
            i += best
        else:
            i += 1
    if reps:
        for (t0, t1, ph) in reps:
            print(f"  REPETICION  toma1@{t0:6.2f} -> toma2@{t1:6.2f}  "
                  f"cortar [{t0:.2f}->{t1:.2f}]  \"{ph}\"")
    else:
        print("  repeticiones exactas (>=3 palabras): ninguna")

    # 2) stutters (palabras estiradas)
    stut = [(a, b, b - a, w) for (w, a, b) in words if b - a > STUTTER_THRESH]
    if stut:
        for (a, b, d, w) in stut:
            print(f"  STUTTER?    {a:6.2f}-{b:6.2f} ({d:.2f}s)  '{w}'  "
                  f"<- revisar zona con silencedetect (puede ser numero/pausa)")
    else:
        print("  stutters (palabras >1.1s): ninguno")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombre", nargs="*", default=[],
                    help="shorts: revisa artifacts/shorts/<n>/voz.wav")
    ap.add_argument("wavs", nargs="*", type=Path, help="rutas .wav directas")
    args = ap.parse_args()

    rutas = list(args.wavs)
    for n in args.nombre:
        rutas.append(Path(f"artifacts/shorts/{n}/voz.wav"))
    if not rutas:
        print("pasar --nombre <short...> o rutas .wav", file=sys.stderr)
        return 2

    model = WhisperModel("medium", device="cpu", compute_type="int8")
    for r in rutas:
        if not r.exists():
            print(f"  ! no existe {r}", file=sys.stderr)
            continue
        revisar(model, r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
