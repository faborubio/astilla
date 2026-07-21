# AUDIT — Deuda aceptada (AUD-NNN)

> Todo trade-off aceptado tiene su entrada (MANIFIESTO §3, regla 2): deuda sin AUD es
> **deuda invisible**. Cada una lleva por qué se aceptó y cómo/cuándo se paga.
> Estados: 🔴 abierta · 🟡 mitigada · ✅ pagada.

| ID | Deuda / trade-off | Por qué se aceptó | Plan de pago | Estado |
|---|---|---|---|---|
| AUD-001 | Checkpoint de transcript compartido entre shorts (`segmentos.json` global, gotcha 11): reusaba a ciegas el transcript de otro audio | Velocidad en la primera tanda; un solo short a la vez | Refactor folder-aware (jul 2026): un short = una carpeta, checkpoints aislados | ✅ pagada 2026-07 |
| AUD-002 | Retimeo alineado al contenido (paso 7) es un script aparte y manual (`retimear_bed.py` + elegir cortes a ojo en `palabras.json`) | Funcionó en la primera tanda y el criterio de corte (límites de frase) aún es humano | Integrar a `armar_short.py` con auto-propuesta de cortes cuando la cadencia lo haga doler (>2 shorts/semana) | 🔴 abierta |
| AUD-003 | LTX vive en `scripts/generar_ltx.py`, fuera del `PuertoEjecutor` (no hay `ejecutor_ltx.py`) | El script funciona y el puerto formal no bloquea producir | Formalizar `ejecutor_ltx.py` detrás del puerto al tocar de nuevo la capa de ejecución | 🔴 abierta |
| AUD-004 | Sin control programático de saldo LTX (no exponen endpoint de balance) | Limitación del proveedor, no nuestra | Revisar el dashboard a mano tras cada tanda (referencia: tanda de 4 ≈ $14 pro) | 🟡 mitigada |
| AUD-005 | Checkpoints `segmentos.json`/`palabras.json` no son content-addressed: si cambia el audio del short hay que borrarlos a mano | El refactor folder-aware ya aisló el radio de daño a la propia carpeta | Hashear el wav en el checkpoint si vuelve a morder | 🟡 mitigada |
| AUD-006 | Repeticiones al grabar se cortan a mano del wav (empalme ffmpeg en silencios) | El protocolo de grabación (pausa 1-2s antes de repetir) hace el corte barato y confiable | Automatizar detección (por-palabra duplicada + silencedetect) solo si la serie Chile lo vuelve frecuente | 🟡 mitigada |
| AUD-007 | Flujo `hablante` congelado con deuda propia: karaoke como paso aparte, personaje SD1.5 256², matte sin feather, sin head motion | El pivot a divulgación dejó al talking-head fuera del modo activo | Pagar solo si el formato hablante revive (las mejoras están en `IDEAS.md`) | 🟡 mitigada |

**Retro del método:** al cerrar una fase/tanda, si un atajo nuevo quedó sin fila acá, eso es un
fallo del ritmo (DoD paso 3), no solo del código.
