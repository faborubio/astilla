"""Adaptador de transcripcion con faster-whisper (implementa PuertoTranscripcion).

Local, CPU, $0. Intercambiable por una API detras del mismo puerto (ADR-003).
"""
from __future__ import annotations

from pathlib import Path

from ..domain.entities import PalabraTranscrita, SegmentoTranscrito


class TranscriptorWhisper:
    def __init__(
        self, modelo: str = "small", idioma: str = "es", guion: str = ""
    ) -> None:
        self._nombre_modelo = modelo
        self._idioma = idioma
        # MODO ORIGINAL: si el guion es NUESTRO, no hay que adivinarlo. Pasarlo como
        # initial_prompt sesga el decoder hacia las palabras correctas (sobre todo
        # nombres propios: "Anticitera" y no "Anticidera"). Whisper solo aporta timing.
        self._guion = guion.strip()
        self._modelo = None  # carga perezosa: descarga pesada solo si se usa

    def _cargar(self):
        if self._modelo is None:
            from faster_whisper import WhisperModel

            # int8 en CPU: rapido y suficiente para subtitulos.
            self._modelo = WhisperModel(self._nombre_modelo, device="cpu", compute_type="int8")
        return self._modelo

    def transcribir(self, audio_recorte: Path) -> list[SegmentoTranscrito]:
        modelo = self._cargar()
        segmentos_raw, _info = modelo.transcribe(
            str(audio_recorte),
            language=self._idioma,
            beam_size=5,
            vad_filter=True,  # corta silencios: subtitulos mas limpios
            initial_prompt=self._guion or None,
        )
        return [
            SegmentoTranscrito(
                inicio_s=round(s.start, 3),
                fin_s=round(s.end, 3),
                texto=s.text.strip(),
            )
            for s in segmentos_raw
            if s.text.strip()
        ]

    def transcribir_palabras(self, audio_recorte: Path) -> list[PalabraTranscrita]:
        """Como transcribir() pero con timestamp por palabra (subtitulos karaoke).

        GOTCHA (jul 2026): a diferencia de transcribir(), aca NO se pasa el guion
        como initial_prompt. Con word_timestamps=True un initial_prompt largo (el
        guion entero, ~130 palabras) ROMPE la alineacion por palabra: dropea los
        primeros ~20s de audio y alucina texto (llega a decodificar en ingles).
        Sin el prompt largo, la transcripcion por palabra arranca en t=0 y sale
        limpia. La correccion del texto (nombres propios) NO se pierde: el llamador
        reconcilia estas palabras con el guion-verdad (ver scripts/reconciliar_palabras.py),
        que toma el TEXTO del guion y el TIMING de aca. temperature=0 -> determinista.
        """
        modelo = self._cargar()
        segmentos_raw, _info = modelo.transcribe(
            str(audio_recorte),
            language=self._idioma,
            beam_size=5,
            vad_filter=True,
            word_timestamps=True,  # habilita w.start/w.end por palabra
            temperature=0,
            initial_prompt=None,   # ver GOTCHA arriba: el guion largo rompe el timing
        )
        palabras: list[PalabraTranscrita] = []
        for s in segmentos_raw:
            for w in (s.words or []):
                t = w.word.strip()
                if t:
                    palabras.append(
                        PalabraTranscrita(inicio_s=round(w.start, 3),
                                          fin_s=round(w.end, 3), texto=t)
                    )
        return palabras
