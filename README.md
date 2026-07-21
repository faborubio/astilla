# Astilla — motor de shorts de divulgación 9:16 con visuales IA

Astilla convierte **audio autorizado** en **shorts verticales 9:16 listos para publicar**:
voz original, visuales generados por IA con estilo pictórico consistente, subtítulos por
palabra, música y divulgación de IA. El activo no es ningún video suelto: es el **motor** —
barato, reproducible (un short = una carpeta + una semilla) y legal (**nada se procesa sin
una `Autorizacion` válida**).

## Resultados medidos (jul 2026)

- **7 shorts producidos end-to-end, 3 publicados** en el canal de historia
  [VESTIGIOS](https://youtube.com/@vestigios.historia):
  [Anticitera](https://youtube.com/shorts/caRNsgvRorc) ·
  [el telégrafo antiguo](https://youtube.com/shorts/YWyjv3tG4SA) ·
  [pelo y catapultas](https://youtube.com/shorts/xQJHJD4XJFI).
- **Retención ~74%** en la primera señal limpia de métricas — la métrica primaria del
  proyecto (las vistas absolutas no son comparables entre shorts de distinta edad).
- **Costo ~$3–4 por short** de 48–63 s (video generativo LTX-2.3 por API, $0.04–0.06/s; el
  costo lo fija la duración del audio, no la cantidad de escenas). **Sin GPU propia.**

## Dos modos, un mismo pipeline

1. **Original / divulgación** (modo activo): guion propio + voz propia → el gate de derechos
   clasifica `original` → publicable de verdad.
2. **Repurposing**: fuente larga de terceros **con autorización verificable** → recorte → short.

La regla dura es la misma (ADR-009): el gate de `Autorizacion` es una **precondición** del
pipeline, no un aviso. Rechaza contenido de terceros sin permiso y deja rastro de linaje
(`rastro.json`: sha256, autorización, receta/semilla, divulgación de IA).

## Cómo se produce un short (modo original)

1. **Grabación** de la voz sobre un guion propio (~110 palabras, estructura probada contra un
   benchmark real de 8M de vistas).
2. `scripts/limpiar_voz.py` — denoise (RNNoise) + compresión + ganancia estática a −16 LUFS.
3. `pipeline.animado` — transcripción (faster-whisper `medium`) + planificación de escenas.
4. **Prompts pictóricos por escena** con un ancla de estilo compartida (*painterly oil
   painting, teal+amber, chiaroscuro*) — así las N escenas parecen del mismo mundo.
5. `scripts/generar_ltx.py` — clips de video generativo (LTX-2.3 API, 9:16 nativo).
6. `scripts/armar_short.py` — timestamps por palabra **reconciliados contra el guion-verdad**
   (difflib), subtítulos karaoke mínimos, bed de clips y quemado.
7. `scripts/retimear_bed.py` — cortes de escena re-alineados a límites de frase (la imagen
   cambia cuando el relato cambia).
8. **Música** (CC-BY, atribuida) + master `loudnorm I=-16:TP=-1.5` → `short_musica.mp4`.

Todo es *folder-aware*: un short vive entero en `artifacts/shorts/<nombre>/` con nombres de
archivo fijos; cada script recibe `--nombre` y resuelve sus rutas (`scripts/rutas.py`).

## Arquitectura (Clean Architecture-lite)

```
pipeline/
├── domain/            # núcleo puro, stdlib-only: entidades, gate de derechos,
│                      # planificación de escenas, puertos, orquestador (DAG de stages)
└── infrastructure/    # adaptadores: Whisper, ffmpeg, Kaggle, LTX, subtítulos, matting…
```

**El dominio dice QUÉ** (qué stages, en qué orden, qué es una autorización válida); **la
infraestructura dice CÓMO**. La prueba de que los puertos funcionan: el proveedor visual
cambió **cuatro veces** — stills SD + Ken Burns → AnimateDiff (Kaggle T4) → Luma → LTX-2.3
API — **sin tocar el orquestador**; solo se cambió el adaptador.

## Decisiones que guían el diseño

- **El moat es el guion, no la GPU.** El análisis de un short de referencia con 8M de vistas
  mostró que el 80% es escritura (claim visceral → mecanismo → compresión memorable) y que la
  **ilustración pictórica supera al foto-realismo** (perdona defectos y cuesta menos). El
  proyecto abandonó la carrera de píxeles a propósito.
- **La imagen manda, el texto se subordina**: subtítulos mínimos de una palabra, sin karaoke
  gigante.
- **Legalidad como precondición**, no como parche: gate de derechos + divulgación de IA +
  música con atribución (Kevin MacLeod, CC-BY) + linaje completo por short.

## Uso rápido

```bash
# Demo Fase 1 ($0, sin GPU, TTS de Windows) + gate de derechos
python -m pipeline.cli --estilo neon --semilla 1
python tests/test_derechos.py

# Modo original end-to-end (el flujo activo; ver CLAUDE.md para el circuito completo)
python scripts/limpiar_voz.py --in "<grabacion>.m4a" --nombre <n>
python -m pipeline.animado --nombre <n> --audio artifacts/shorts/<n>/voz.wav \
    --guion artifacts/shorts/<n>/guion.txt --autorizacion original \
    --evidencia "Guion y voz propios" --estilo historico --modelo medium --stub-visual
python scripts/generar_ltx.py --nombre <n> --indices todas --auto --pro
python scripts/armar_short.py --nombre <n> --semilla 1
```

## Requisitos

- Python 3.11+, `ffmpeg`/`ffprobe` en el PATH, `pip install -r requirements.txt`.
- LTX API key (video generativo, de pago por segundo) · opcional: `kaggle.json` (GPU gratis
  para los modos SD/AnimateDiff/SadTalker, ver [`docs/KAGGLE.md`](./docs/KAGGLE.md)) ·
  opcional: `ANTHROPIC_API_KEY` (prompts por LLM sin operador).

## Documentación

| Documento | Responde a |
|---|---|
| [`SAD_Astilla_repurposing.md`](./SAD_Astilla_repurposing.md) | ¿Cómo está diseñado y por qué? (fuente de verdad; §11.b = crítica de diseño) |
| [`CLAUDE.md`](./CLAUDE.md) | ¿Cómo retomo el proyecto en 5 minutos? (termina en `## Próxima sesión`) |
| [`docs/CASES.md`](./docs/CASES.md) | ¿Qué casos quedaron demostrados? |
| [`docs/AUDIT.md`](./docs/AUDIT.md) | ¿Qué deuda acepté y cómo se paga? (AUD-NNN) |
| [`docs/TROUBLESHOOTING.md`](./docs/TROUBLESHOOTING.md) | ¿Qué falló y cómo se arregló? (gotchas G-1…G-13 + incidentes) |
| [`IDEAS.md`](./IDEAS.md) | ¿Qué ideas esperan tracción? (parking lot) |
| [`MEMORY.md`](./MEMORY.md) | Bitácora cronológica |
