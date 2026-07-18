# Reconcilia el GUION (verdad) con los word-timestamps de Whisper.
# Problema: con audio propio Whisper a veces alucina/dropea palabras (sobre todo
# al inicio) -> el karaoke muestra texto equivocado. Pero el guion es NUESTRO:
# las palabras correctas ya las tenemos. Aca tomamos el TEXTO del guion y el
# TIMING de Whisper donde coinciden (anclas via difflib), interpolando linealmente
# el timing de las palabras que Whisper erro. Resultado: palabras correctas del
# guion con timing plausible, sin huecos.
#
# Uso:
#   python scripts/reconciliar_palabras.py --guion artifacts/guion_telegrafo.txt \
#       --whisper artifacts/palabras_telegrafo.json --audio artifacts/voz_telegrafo.wav \
#       --out artifacts/palabras_telegrafo.json
import argparse
import json
import re
import subprocess
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


def _norm(s: str) -> str:
    """Normaliza para MATCHING: minuscula, sin acentos, solo alfanumerico."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _dur_audio(p: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def reconciliar(guion_texto: str, whisper: list[dict], dur: float) -> list[dict]:
    """Devuelve palabras {inicio_s,fin_s,texto} con TEXTO del guion y TIMING de whisper.

    whisper: lista de dicts con al menos {inicio_s, texto}. dur: duracion del audio (s).
    Las palabras del guion que matchean una de whisper toman su inicio_s (ancla);
    el resto se interpola linealmente entre anclas. Garantiza texto correcto.
    """
    guion_disp = [w for w in guion_texto.split() if _norm(w)]
    g_norm = [_norm(w) for w in guion_disp]
    whisper = [w for w in whisper if _norm(w["texto"])]
    w_norm = [_norm(w["texto"]) for w in whisper]

    anclas: dict[int, float] = {}
    sm = SequenceMatcher(a=g_norm, b=w_norm, autojunk=False)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            anclas[i + k] = whisper[j + k]["inicio_s"]

    N = len(guion_disp)
    idx_anclas = sorted(anclas)
    if not idx_anclas:
        raise ValueError("sin anclas: el guion no coincide con la transcripcion")
    primer, ultimo = idx_anclas[0], idx_anclas[-1]
    t_primer, t_ultimo = anclas[primer], anclas[ultimo]
    tiempos: list[float] = [0.0] * N
    for i in range(N):
        if i in anclas:
            tiempos[i] = anclas[i]
            continue
        prev = max((k for k in idx_anclas if k < i), default=None)
        nxt = min((k for k in idx_anclas if k > i), default=None)
        if prev is not None and nxt is not None:
            frac = (i - prev) / (nxt - prev)
            tiempos[i] = anclas[prev] + frac * (anclas[nxt] - anclas[prev])
        elif prev is None:
            tiempos[i] = t_primer * (i + 1) / (primer + 1)
        else:
            resto = N - ultimo
            tiempos[i] = t_ultimo + (dur - t_ultimo) * (i - ultimo) / max(resto, 1)

    for i in range(1, N):
        if tiempos[i] <= tiempos[i - 1]:
            tiempos[i] = tiempos[i - 1] + 0.05
    salida = []
    for i, w in enumerate(guion_disp):
        ini = round(tiempos[i], 2)
        fin = round(tiempos[i + 1], 2) if i + 1 < N else round(min(dur, ini + 0.5), 2)
        salida.append({"inicio_s": ini, "fin_s": max(fin, ini + 0.05), "texto": w})
    return salida, len(anclas), N


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--guion", required=True, type=Path)
    ap.add_argument("--whisper", required=True, type=Path, help="palabras json de Whisper")
    ap.add_argument("--audio", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    dur = _dur_audio(args.audio)
    guion_texto = args.guion.read_text(encoding="utf-8")
    wh = json.loads(args.whisper.read_text(encoding="utf-8"))
    salida, n_anclas, N = reconciliar(guion_texto, wh, dur)
    print(f"[reconciliar] guion={N} palabras · whisper={len(wh)} · anclas={n_anclas} "
          f"({100*n_anclas//max(N,1)}% del guion anclado)")
    args.out.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[reconciliar] -> {args.out} ({N} palabras del guion con timing)")
    print("   muestra:", ' '.join(w["texto"] for w in salida[:12]), "...")


if __name__ == "__main__":
    main()
