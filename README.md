# Astilla — motor de repurposing a shorts verticales 9:16

Toma una **fuente larga autorizada**, recorta una anécdota y produce un **short
vertical 9:16 animado** con subtítulos y divulgación de IA. El valor no es el
contenido: es el **motor** — barato, reproducible y legal.

> Para retomar: empieza por [`CLAUDE.md`](./CLAUDE.md) (hub de contexto) y [`MEMORY.md`](./MEMORY.md) (bitácora).
> Arquitectura completa: [`SAD_Astilla_repurposing.md`](./SAD_Astilla_repurposing.md);
> la crítica de diseño en **§11.b (Revisión de halcón)**. Casos: [`docs/CASES.md`](./docs/CASES.md).

## Estado

Funcionando end-to-end (verificado con ffprobe en `docs/CASES.md`):

- **Fase 1** ($0, sin GPU): gate de derechos → Whisper → subtítulos → ensamblado 9:16.
- **Fase 2 animada**: planificación de escenas → generación visual → animación → short 9:16.
  - **Imágenes** (SD) + Ken Burns, o **AnimateDiff** (clips animados reales).
  - GPU: **Kaggle gratis** con despacho automático por API (un comando).
  - Prompts opcionales por **Claude** (biblia de estilo + coherencia).

## Requisitos
- Python 3.11+, `ffmpeg`/`ffprobe` en el PATH
- `pip install -r requirements.txt` (faster-whisper, kaggle, anthropic)
- GPU gratis: `kaggle.json` en `~/.kaggle/` (ver [`docs/KAGGLE.md`](./docs/KAGGLE.md))
- Prompts LLM (opcional): `ANTHROPIC_API_KEY`
- Fuente de demo: Windows (System.Speech). En otros SO, pasa tu propio audio con `--audio`.

## Uso

```bash
# Fase 1 — short simple ($0, sin GPU)
python -m pipeline.cli --estilo neon --semilla 1
python tests/test_derechos.py                      # gate de derechos en acción

# Fase 2 — flujo animado
python -m pipeline.animado --estilo neon --semilla 1 --stub-visual           # prueba local sin GPU
python -m pipeline.animado --kaggle --estilo neon --semilla 1                 # imágenes SD + Ken Burns (Kaggle)
python -m pipeline.animado --motion animatediff --kaggle --estilo neon        # clips animados reales (Kaggle T4)

# Con fuente real + calidad
python -m pipeline.animado --audio sources/x.wav --autorizacion dominio_publico \
    --evidencia "URL" --modelo medium --prompts-llm --motion animatediff --kaggle
```

Salida en `artifacts/`: `short.mp4` / `short_animado.mp4` + `rastro.json` (linaje completo).

## Estructura

```
pipeline/
├── domain/                 # núcleo puro (stdlib-only)
│   ├── entities.py         # Fuente, Autorizacion, Recorte, Receta, Job, Short, Rastro
│   ├── derechos.py         # gate de Autorizacion (ADR-009) — la precondición dura
│   ├── ports.py            # puertos (interfaces) de cada stage
│   └── orquestador.py      # el DAG de stages (depende solo de dominio + puertos)
│   ├── planificacion.py    # transcript → escenas + prompts (ancla de coherencia)
│   └── orquestador.py      # el DAG de stages (depende solo de dominio + puertos)
└── infrastructure/         # adaptadores (el COMO detrás de los puertos)
    ├── audio_demo_windows.py     # fuente ORIGINAL de demo (System.Speech)
    ├── transcripcion_whisper.py  # faster-whisper (small|medium)
    ├── subtitulos_ass.py
    ├── prompts_claude.py         # prompts por LLM (claude-opus-4-8)
    ├── ejecutor_kaggle.py        # PuertoEjecutor: Kaggle (imagen|animatediff)
    ├── ensamblado_ffmpeg.py      # Fase 1
    ├── ensamblado_escenas_ffmpeg.py  # Ken Burns sobre stills
    └── ensamblado_clips_ffmpeg.py    # concat de clips AnimateDiff
```
(`pipeline/cli.py` = Fase 1; `pipeline/animado.py` = Fase 2.)

## Diseño en una línea
El **dominio define qué stages y en qué orden** (el DAG) y **qué es una
autorización válida**; la **infraestructura define cómo**. Cada stage es intercambiable
detrás de su puerto: pasar de stills a video (AnimateDiff) o de local a Kaggle solo cambió
el adaptador, **sin tocar el orquestador**.
