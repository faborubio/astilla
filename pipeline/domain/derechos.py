"""Gate de derechos (ADR-009). La primera puerta del pipeline, no un disclaimer.

Es el dominio genuinamente rico del proyecto (ver SAD H-7): ningun caso de uso
de generacion se ejecuta sin una Autorizacion valida y vigente ligada a la fuente.
"""
from __future__ import annotations

from datetime import date

from .entities import Autorizacion, Fuente


class AutorizacionInvalida(Exception):
    """Se lanza cuando el gate rechaza un job. El motor NO procesa sin derechos."""


def verificar(fuente: Fuente, autorizacion: Autorizacion, hoy: date | None = None) -> None:
    """Precondicion dura. Lanza AutorizacionInvalida si el gate rechaza.

    Reglas:
      1. La autorizacion debe pertenecer a la fuente.
      2. Debe estar vigente a la fecha.
      3. Debe declarar evidencia (referencia, no contenido legal).
    """
    hoy = hoy or date.today()

    if autorizacion.fuente_id != fuente.id:
        raise AutorizacionInvalida(
            f"La autorizacion {autorizacion.id} no pertenece a la fuente {fuente.id}."
        )
    if not autorizacion.es_vigente(hoy):
        raise AutorizacionInvalida(
            f"La autorizacion {autorizacion.id} esta vencida (vigente_hasta={autorizacion.vigente_hasta})."
        )
    if not autorizacion.evidencia.strip():
        raise AutorizacionInvalida(
            f"La autorizacion {autorizacion.id} no declara evidencia del derecho."
        )
