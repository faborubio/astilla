"""Nucleo puro del dominio. stdlib-only: sin Whisper, sin ffmpeg, sin Pydantic.

Define QUE es una fuente, una autorizacion, una receta y un short, y COMO se
compone el pipeline. El COMO concreto (transcribir, generar, ensamblar) vive en
infrastructure/ detras de los puertos de `ports.py`.
"""
