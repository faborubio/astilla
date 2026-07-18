"""Genera una fuente de audio ORIGINAL para la demo, con el TTS nativo de Windows.

No es el stage de voz del producto (en el MVP la voz es el audio original del
cliente, H-6). Es solo material original nuestro para cerrar el loop end-to-end
a $0 y sin dependencias externas: lo sintetizamos -> es contenido ORIGINAL ->
encaja en el gate como TipoAutorizacion.ORIGINAL y se divulga como IA.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

# Guion de demo (~25 s hablados). Una "anecdota" autocontenida.
GUION_DEMO = (
    "Te voy a contar como casi pierdo un proyecto entero por no guardar mi trabajo. "
    "Estaba renderizando un video en una maquina prestada, en la nube, gratis. "
    "Llevaba dos horas. Y justo cuando iba por la ultima escena, la sesion se desconecto. "
    "Todo se borro. Desde ese dia, cada escena que genero queda guardada al instante. "
    "Si se cae, retomo donde iba. Esa es toda la diferencia entre algo gratis y algo usable."
)

_PS_SCRIPT = """
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = -1
$synth.SetOutputToWaveFile('{salida}')
$synth.Speak(@'
{texto}
'@)
$synth.Dispose()
"""


def generar_audio_demo(destino: Path, texto: str = GUION_DEMO) -> Path:
    """Sintetiza un WAV con System.Speech y lo normaliza a 16kHz mono PCM."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    crudo = destino.with_name("fuente_cruda.wav")

    script = _PS_SCRIPT.format(salida=str(crudo).replace("\\", "\\\\"), texto=texto)
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=True,
        capture_output=True,
        text=True,
    )

    # Normalizar a 16 kHz mono PCM: formato amable para Whisper y ffmpeg.
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(crudo), "-ac", "1", "-ar", "16000", str(destino)],
        check=True,
        capture_output=True,
        text=True,
    )
    crudo.unlink(missing_ok=True)
    return destino
