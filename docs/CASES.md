# CASES — bitácora de casos demostrables

## CASO-001 · Primer short 9:16 real, end-to-end, $0 (Fase 1)

**Fecha:** 2026-06-29 · **Estado:** ✅ verificado

### Qué demuestra
El *slice real* del SAD §11.b: de un audio autorizado sale un short vertical
9:16 con subtítulos y divulgación de IA, pasando por el gate de derechos, y con
el rastro de linaje persistido. Sin GPU, sin servicios externos, sin costo.

### Pipeline ejecutado
`gate de derechos → transcripción (Whisper) → recorte (operator-driven) →
subtítulos ASS → visual determinista → ensamblado ffmpeg + divulgación → Short + Rastro`

### Comando
```
python -m pipeline.cli --estilo neon --semilla 1
```

### Salida verificada (`ffprobe`)
| Propiedad | Valor |
|-----------|-------|
| Resolución | **1080×1920 (9:16 vertical)** |
| Códecs | h264 (video) + aac (audio) |
| FPS | 30 |
| Duración | 34.2 s |
| Tamaño | ~1.5 MB |

Artefactos en `artifacts/`: `short.mp4`, `rastro.json` (linaje: fuente sha256,
autorización, receta/versión/semilla, divulgación IA), `segmentos.json`
(transcripción), `subtitulos.ass`, `fuente.wav`, `recorte.wav`.

### Decisiones del slice (trazables a §11.b)
- **H-2** — visual = fondo determinista detrás de `PuertoVisual`; intercambiable
  por Diffusers/serverless sin tocar el orquestador.
- **H-4** — recorte operator-driven (`--inicio/--fin`).
- **H-5** — el short termina en estado `EN_REVISION` (gate de QC humano), no entregado.
- **H-6** — sin TTS en el producto; la voz es el audio original. El TTS de Windows
  solo fabrica la *fuente original* de la demo.
- **ADR-006/008** — receta versionada + semilla → paleta determinista, registrada en el rastro.
- **ADR-010** — divulgación "Contenido generado con IA" embebida en la salida.

### Calidad observada
- Transcripción `small`/es: ~98% correcta (1 error: "Desde ese día" → "Desde SDIA").
  Mejora con modelo `medium` o corrección post-VAD.
- Subtítulos grandes con borde negro, legibles; divulgación fija abajo.

## CASO-002 · El gate de derechos rechaza lo no autorizado (ADR-009)

**Estado:** ✅ verificado · `python tests/test_derechos.py`

Acepta autorización válida y vigente; **rechaza** sin evidencia, vencida, o de
otra fuente. Es la columna legal del producto: ningún render ocurre sin derechos.

## CASO-003 · Short ANIMADO por escena (Fase 2, flujo Colab)

**Fecha:** 2026-06-29 · **Estado:** ✅ local verificado (con stand-ins) · ⏳ Colab pendiente del usuario

### Qué demuestra
El stage de generación visual real detrás de `PuertoVisual`, en flujo de **2 fases
resumibles** (ADR-002): local planifica escenas y exporta el job; Colab (GPU T4
gratis) genera 1 imagen por escena con checkpoint; local anima (Ken Burns) y ensambla.

### Pipeline
`gate → transcripción → planificación de escenas (prompt+semilla por escena) →
[Colab: SD por escena, checkpoint] → ensamblado animado (Ken Burns + onda + subtítulos + divulgación)`

### Verificado localmente (`--stub-visual`, sin Colab)
- Planificación: 8 segmentos → **5 escenas** con prompts deterministas derivados
  del transcript real (ver `artifacts/visual_job.json`).
- Ensamblado animado: **`short_animado.mp4` 1080×1920, 1004 frames (~30fps), 34.2s** (ffprobe).
- Movimiento Ken Burns por escena (zoom in/out alternado), subtítulos sincronizados,
  divulgación de IA fija.

### Comandos
```bash
# Fase A — preparar el job para Colab
python -m pipeline.animado --estilo neon --semilla 1
# Probar el motor de animación localmente sin Colab
python -m pipeline.animado --estilo neon --semilla 1 --stub-visual
# Fase B — tras bajar las imágenes de Colab a artifacts/escenas/
python -m pipeline.animado --estilo neon --semilla 1 --ensamblar
```
Notebook + guía: [`colab/astilla_render.ipynb`](../colab/astilla_render.ipynb), [`docs/COLAB.md`](./COLAB.md).

### Bug encontrado y corregido
`zoompan` sobre input `-loop 1 -t` **multiplica** los frames (genera `d` frames por
cada frame del loop → ~22k frames, render de minutos). Fix: input de una sola imagen
+ `-frames:v N`. Render pasó de minutos a segundos por escena.

### Deuda visible (H-1)
La coherencia de personaje entre escenas no está resuelta: SD por escena no garantiza
el mismo sujeto. Mejora: IP-Adapter / imagen de referencia. Documentado como siguiente paso.

## CASO-003b · Generación visual REAL en Kaggle GPU (despacho automático)

**Fecha:** 2026-06-29 · **Estado:** ✅ verificado end-to-end

### Qué demuestra
El `PuertoEjecutor` cumplido por Kaggle vía API: el orquestador local **despacha,
hace polling y baja los artefactos sin handoff manual** — el diagrama del SAD
hecho realidad. Imágenes reales de Stable Diffusion, no stubs.

### Verificado
```bash
python -m pipeline.animado --kaggle --estilo neon --semilla 1
```
- Push de kernel headless (GPU **T4**) → 5 imágenes SD 512×896 generadas con
  checkpoint por escena → descarga automática → ensamblado.
- **`short_animado.mp4` 1080×1920, 34.2s, ~11.4 MB** con visual neón synthwave
  real, Ken Burns, subtítulos y divulgación de IA. Calidad publicable.

### Bugs encontrados y resueltos (ver docs/KAGGLE.md)
1. **Token `KGAT_` nuevo** no va en `kaggle.json` → usar `access_token`/env, o legacy.
2. **`runwayml/stable-diffusion-v1-5` retirado de HF** → mirror `stable-diffusion-v1-5/...`.
3. **P100 (sm_60) incompatible con el PyTorch de Kaggle (sm_70+)** → forzar
   `machine_shape: NvidiaTeslaT4`. (Era el `KernelWorkerStatus.ERROR` con log vacío.)

### Pendiente honesto
Coherencia entre escenas (H-1) sigue abierta; el transcript de audio real ruidoso
(reel) degrada los prompts (ver CASO previo) → conviene modelo `medium` + prompts por LLM.

---

## CASO-004 · Calidad de transcript (#2a) + coherencia de prompts (#1/#2b)

**Fecha:** 2026-06-29 · **Estado:** ✅ ancla heurística verificada · ⏳ LLM requiere API key

### #2a — modelo `medium` arregla la transcripción de audio real
Sobre el reel real (0-40s), `medium` vs `small`: "jamón cerrado"→"jamón **serrano**",
"Cortecía te va a hacer mi espulia"→"Con **cortesía** te voy a hacer yo". La narración
queda bien; lo que persiste mal es el grito cómico solapado (límite de cualquier ASR).
Uso: `--modelo medium` (más lento en CPU). Recomendado para fuentes reales ruidosas.

### #1 — coherencia entre escenas (sin LLM): "ancla de estilo" global
`planificacion.py` deriva los temas dominantes de TODO el clip y los inyecta en cada
escena → las escenas comparten un hilo visual en vez de ser mundos sueltos. Verificado:
las 5 escenas del demo comparten "renderizando, desconectó, diferencia". Mitiga H-1 a
nivel de prompt; no resuelve identidad exacta de personaje (eso es IP-Adapter, CASO-005).

### #2b — prompts por LLM (Claude): biblia de estilo + coherencia por construcción
`prompts_claude.py` (implementa la idea de `PuertoPromptVisual`): Claude (`claude-opus-4-8`,
structured outputs) lee el transcript y produce una **biblia de estilo** compartida
(sujeto/escenario/paleta) + un prompt por escena que la incorpora → coherencia real, no
keywords sueltas. Flag `--prompts-llm`; requiere `ANTHROPIC_API_KEY`; **fallback automático**
al heurístico si no hay key. Ataca H-1 y H-2 a la vez.

```bash
export ANTHROPIC_API_KEY=...   # o set en Windows
python -m pipeline.animado --audio sources/x.wav --autorizacion dominio_publico \
    --evidencia "URL" --modelo medium --prompts-llm --kaggle
```

---

## CASO-005 · Animación REAL generada (AnimateDiff en Kaggle T4)

**Fecha:** 2026-06-29 · **Estado:** ✅ verificado end-to-end

### Qué demuestra
Movimiento generado de verdad (no Ken Burns sobre stills): un modelo de difusión de
video gratuito corriendo en GPU gratis, detrás del mismo `PuertoEjecutor`.

### Verificado
```bash
python -m pipeline.animado --motion animatediff --kaggle --estilo neon --semilla 1 --fin 12
```
- Kernel AnimateDiff (SD 1.5 + `guoyww/animatediff-motion-adapter-v1-5-2`) en **T4**,
  `cpu_offload` + `vae_slicing`. Generó **clips `escena_XX.mp4` de 512×768, 16 frames, 2 s**.
- Ensamblado: loop de cada clip a su duración + concat + onda + subtítulos + divulgación.
- Salida: **`short_animado.mp4` 1080×1920, 12 s, ~10.5 MB** con movimiento generado real.

### Diseño (limpio detrás del puerto)
Solo cambiaron 2 piezas vs. el modo stills: el kernel produce `.mp4` (no `.png`) y el
ensamblador concatena clips (no Ken Burns). Gate, transcripción, planificación, prompts
de Claude, subtítulos y divulgación: idénticos. Flag `--motion {kenburns,animatediff}`.

### Honesto
- **Lento:** ~min/escena en T4 + descarga de pesos mayor. Sigue siendo $0.
- **Estética abstracta** a 512×768 — neón/trippy que *tolera* incoherencia entre escenas.
- **Identidad de personaje (H-1)** sigue sin resolver: AnimateDiff anima cada escena por
  separado. Cierre real = IP-Adapter / imagen de referencia (CASO-006).

---

## Próximos casos (roadmap)
- **CASO-006** — coherencia/identidad de personaje (H-1): IP-Adapter / imagen de referencia.
- **CASO-007** — reanudación tras desconexión: matar el proceso y retomar (ADR-002).
- **CASO-008** — capa MCP: "generá 3 shorts de este episodio, estilo cómic".
