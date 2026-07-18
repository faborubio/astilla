"""Prueba del gate de derechos (ADR-009): la precondicion dura del producto.

Ejecutable sin pytest:  python tests/test_derechos.py
Demuestra que el motor NO procesa sin Autorizacion valida, vigente y de la fuente.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.domain import derechos
from pipeline.domain.entities import Autorizacion, Fuente, TipoAutorizacion

HOY = date(2026, 6, 29)


def _fuente() -> Fuente:
    return Fuente(id="f1", titulo="t", ruta_audio=Path("x.wav"), sha256="abc")


def _ok(msg: str) -> None:
    print(f"  PASS · {msg}")


def caso_acepta_autorizacion_valida() -> None:
    auth = Autorizacion("a1", "f1", TipoAutorizacion.CLIENTE, "Cliente X", "contrato-2026")
    derechos.verificar(_fuente(), auth, HOY)  # no debe lanzar
    _ok("acepta autorizacion valida y vigente")


def caso_rechaza_sin_evidencia() -> None:
    auth = Autorizacion("a1", "f1", TipoAutorizacion.CLIENTE, "Cliente X", "   ")
    try:
        derechos.verificar(_fuente(), auth, HOY)
    except derechos.AutorizacionInvalida:
        _ok("rechaza autorizacion sin evidencia")
        return
    raise AssertionError("deberia haber rechazado: sin evidencia")


def caso_rechaza_vencida() -> None:
    auth = Autorizacion("a1", "f1", TipoAutorizacion.LICENCIA, "Sello", "lic-123", vigente_hasta=date(2025, 1, 1))
    try:
        derechos.verificar(_fuente(), auth, HOY)
    except derechos.AutorizacionInvalida:
        _ok("rechaza autorizacion vencida")
        return
    raise AssertionError("deberia haber rechazado: vencida")


def caso_rechaza_fuente_ajena() -> None:
    auth = Autorizacion("a1", "OTRA-fuente", TipoAutorizacion.CLIENTE, "Cliente X", "contrato")
    try:
        derechos.verificar(_fuente(), auth, HOY)
    except derechos.AutorizacionInvalida:
        _ok("rechaza autorizacion de otra fuente")
        return
    raise AssertionError("deberia haber rechazado: fuente ajena")


if __name__ == "__main__":
    print("Gate de derechos (ADR-009):")
    caso_acepta_autorizacion_valida()
    caso_rechaza_sin_evidencia()
    caso_rechaza_vencida()
    caso_rechaza_fuente_ajena()
    print("OK — el motor solo procesa contenido autorizado.")
