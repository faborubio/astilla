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

## CASO-006 · Coherencia de personaje (H-1): retrato-ancla + IP-Adapter

**Fecha:** 2026-07 · **Estado:** 🟡 código listo, falta validar en GPU

### Qué demuestra
El cierre real de H-1 (identidad, no solo estilo): se autogenera un **retrato-ancla**
close-up del personaje y se aplica por escena con **IP-Adapter** para mantener la misma
cara. Flag `--coherencia` (implica `--motion animatediff`).

### Detalle
`prompt_personaje` (en `planificacion.py`) fuerza primer plano de cara + negativo
anti-plano-abierto: con fuentes reales el ancla tendía a planos abiertos (figura lejana)
y SadTalker fallaba con *"can not detect the landmark"* (gotcha 9). Config: `ip_scale=0.6`.

### Pendiente honesto
Falta correrlo en GPU y **afinar `ip_scale`** (fidelidad de identidad vs. libertad de escena).

---

## CASO-009 · Personaje hablante audio-driven (arquitectura de capas)

**Fecha:** 2026-07 · **Estado:** ✅ short completo end-to-end

### Qué demuestra
Un **hablante** (talking-head) manejado por el audio (SadTalker en Kaggle) compuesto
**sobre** un ambiente generado por IA + subtítulos. No es video IA end-to-end: son capas
(`pipeline.hablante` + `animado` + `ensamblado_hablante_ffmpeg`). Salida: `short_hablante.mp4`,
y `short_hablante_pro.mp4` con matting (`matting_rembg`, u2net) + karaoke por palabra.

### Bugs resueltos
**SadTalker en Kaggle (py3.12) = campo minado** (gotcha 7): instalar deps sin pines + `numpy<2`,
parches a `animate.py`/`align_img`, correr con `cwd=/tmp/SadTalker`. Race del dataset de audio
(gotcha 10) → dataset content-addressed + poll a `ready`.

---

## CASO-010 · LTX-2.3 API — video generativo CON API, 9:16 real

**Fecha:** 2026-07 · **Estado:** ✅ verificado, short publicado

### Qué demuestra
Video generativo por API (sin GPU efímera): **t2v + i2v**, 9:16 por parámetro de resolución,
prompts pictóricos escritos por Claude en sesión. Reemplaza el paso manual de Luma (que no
tiene API en el plan consumidor). Costo: **$0.06/s pro** ($0.04 fast) → ~$3-4/short.

### Comando
```bash
python scripts/generar_ltx.py --nombre <n> --indices todas --auto --pro
```
`scripts/generar_ltx.py` (embrión del `ejecutor_ltx` detrás del `PuertoEjecutor`). Key en
`~/.ltx/api_key`. Short v2 (Anticitera) publicado con este flujo. Ver [[ltx-api-validada]].

---

## CASO-011 · Circuito de producción formalizado (tanda telégrafo/pelo)

**Fecha:** 2026-07 · **Estado:** ✅ 2 shorts terminados

### Qué demuestra
El copy-paste de ffmpeg se volvió **scripts reusables**: `limpiar_voz.py` (highpass+arnndn+
comp+ganancia estática a -16 LUFS + recorte de silencio inicial/cola), `armar_short.py`
(transcribe por palabra y **reconcilia contra el guion-verdad**, karaoke mínimo, bed, quema),
`reconciliar_palabras.py`, `retimear_bed.py` (cortes alineados al beat).

### Gotchas (11-13, ver [[produccion-tanda-telegrafo-pelo]])
Checkpoint `segmentos.json` reusado a ciegas · guion largo rompe la transcripción por palabra
(bug de `transcribir_palabras` arreglado) · cortes de escena desalineados del audio → retimeo.

---

## CASO-012 · Refactor folder-aware + tanda de 4 (Chile pendiente)

**Fecha:** 2026-07-19 · **Estado:** ✅ 4 shorts terminados (arquero, trepanacion, cerebro_vidrio, hormigon)

### Qué demuestra
**Un short = una carpeta** `artifacts/shorts/<n>/` con nombres fijos; todos los scripts toman
`--nombre` y resuelven rutas solos (`scripts/rutas.py::RutasShort`). Esto ordenó el despelote de
`artifacts/` (viejo → `_legacy/`) y **mató el gotcha 11 de raíz** (cada checkpoint es propio de su
carpeta). Salidas: `shorts/{arquero(48s),trepanacion(54s),cerebro_vidrio(63s),hormigon(48s)}/short_musica.mp4`.

### Bugs / lecciones
1. **Transcripción (`transcribir()`):** `initial_prompt`=guion-entero + `vad_filter=True` **truncaba**
   a la mitad; sin vad **alucinaba** el arranque ("Princeton en el siglo diecinueve"). Fix: ambos
   apagados (el texto final igual sale del pase por-palabra reconciliado).
2. **Audio — repeticiones al grabar:** si el locutor se traba y repite la frase, la repetición QUEDA
   en el wav (`limpiar_voz` no la borra). Se corta a mano con `aselect='not(between(t,A,B))'` empalmando
   en los silencios, y se re-arma (clips LTX se reusan, $0). `guiones.md` ahora pide pausar 1-2s
   antes de repetir. Si la cola se come el CTA → `--sin-recorte-final` + recorte manual.

Ver [[refactor-folder-aware-y-fix-transcripcion]].

---

## CASO-013 · Flujo híbrido barato + fidelidad por referencias (~$0.7/short)

**Fecha:** 2026-07-21/22 · **Estado:** ✅ 4 shorts terminados (piston_fuego, manavai, sismografo, pisagua)

### Qué demuestra
El costo por short baja de ~$3-4 (pro, todo-video) a **~$0.7** sin perder calidad, con tres palancas:
1. **fast por default** (no `--pro`): A/B mostró que `fast` ($0.04/s) sale igual o **más on-brand** que
   `pro` ($0.06/s) para el estilo painterly; y como la API **no fija semilla**, con fast sacás 2 tiros
   por el precio de 1 pro (mejor selección). −33%.
2. **Stills SDXL gratis en Kaggle** (`scripts/generar_stills_kaggle.py` + kernel `sdxl` en
   `ejecutor_kaggle.py`): las escenas estáticas se ilustran gratis y se animan con Ken Burns local; LTX
   -video paga SOLO las escenas con movimiento (`generar_ltx.py --video "i,j"`). Un short 9-esc con 2-3
   de video ≈ $0.5-1. SDXL tiene **negative_prompt real** (LTX no) → control de etnia/época/anacronismo.
3. **i2v** (`generar_ltx.py --i2v "i,j"`, endpoint `image-to-video`, campo `image_uri`): anima un still
   FIEL como frame 0 → LTX no puede re-inventar el contenido, solo agrega movimiento. Mató el casco de
   acero y los veleros que t2v metía en pisagua.

### Fidelidad por referencias (lección clave)
Para temas específicos/locales (Rapa Nui, Guerra del Pacífico) SDXL/LTX derivan a genérico. **Fabián
(chileno) pasa fotos de referencia** → Claude extrae los detalles al prompt (**Nivel 1**) + **i2v** ancla
el video (**Nivel 2**). Correcciones reales: manavai = anillo BAJO de basalto oscuro sobre pastizal sin
árboles (no torres/vidrio); pisagua = uniforme chileno 1879 **azul+rojo+kepí**, buques a vapor, desierto
del Atacama. Gotcha: repetir "red" muchas veces → SDXL pinta al soldado TODO rojo (balancear + negativo).

### Método de trabajo
Generar stills → **revisar por frame** → regenerar gratis los que fallen → recién ahí pagar el video.
Reparto video/still por short en `docs/reparto_video_still.md`. Ver [[ltx-fast-vs-pro-y-hibrido-stills]],
[[referencias-y-i2v-para-fidelidad]].

---

## CASO-014 · Pivot a ChatGPT para stills + gates de calidad (mortero/piedra_solar) ✅

**Contexto:** crítica pública en un short publicado ("mejora las ilustraciones, se ven deformes y
algunas sin sentido"). Diagnóstico: SDXL falla en 3 puntos ciegos — **manos, caras, y escenas con
relación compleja entre objetos** (SDXL pone objetos al lado; no integra "yema mezclándose EN el
mortero"). 4 rondas de regeneración en SDXL no lo resolvieron.

**Solución adoptada — stills en ChatGPT (GPT-image, Plan Plus):** generó a la primera lo que SDXL no
logró en 4 intentos. Los stills de Vestigios pasan a ChatGPT. Look fijo = **óleo pictórico** (coherente
con los 13 shorts previos; el benchmark de 8M dice que lo pictórico perdona más). Flujo: Claude escribe
un kit de prompts en español (`shorts/<n>/prompts_chatgpt.md`) con bloque de estilo + dirección
anti-puntos-ciegos (gente de espaldas/silueta, objeto como sujeto antes que acción con líquidos, "sin
texto en inglés" donde el texto sería protagonista); Fabián genera en ChatGPT y revisa; Claude mapea
cada imagen a su `still_NN.png` por CONTENIDO (los nombres de descarga no traen índice) y hace 2ª
revisión. Es human-in-the-loop: calidad sobre automatización total. SDXL/Kaggle queda de respaldo.

**Dos gates de calidad (reglas duras):**
- **Revisión de stills antes de armar** — Fabián frame a frame + Claude 2ª pasada, comparan (cada uno
  cachó defectos distintos). Regen del que falle. Ver [[revisar-stills-antes-de-armar]].
- **Fuentes antes de grabar** — cada guion lleva `Fuente:` verificada; destapó 3 mitos virales (huevo
  bizantino, ceniza de katana, arsénico del papel), reencuadrados al mecanismo real. Ver [[gate-de-fuentes-antes-de-grabar]].

**Otros:** guiño visual del próximo short en la última escena ([[guino-visual-proximo-short]]); fórmula
v3 (hook-misterio, sin tríada, cierre-loop, voz propia); fix de cola del CTA (`tpad`+`apad` ~1.3s para
que el "seguime" no se corte); bug G-16 (`--i2v` sin `--video` pagaba t2v ciego, ~$4 quemados, arreglado).
Resultado: mortero_bizantino publicado (youtube.com/shorts/hm-JIzAQM_4), piedra_solar lista para subir.
Ver [[manos-deformes-sdxl-y-fix-negativo]], [[politica-i2v-por-defecto-fidelidad]], [[confirmar-costo-ltx-antes-de-pagar]].

---

## Próximos casos (roadmap)
- **CASO-007** — reanudación tras desconexión: matar el proceso y retomar (ADR-002).
- **CASO-008** — capa MCP: "generá 3 shorts de este episodio, estilo cómic".
