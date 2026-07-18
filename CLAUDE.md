# CLAUDE.md — Hub de contexto de Astilla

> Léeme primero. Soy el punto de entrada para retomar el proyecto en una sesión nueva.
> Fuente de verdad de arquitectura: [`SAD_Astilla_repurposing.md`](./SAD_Astilla_repurposing.md)
> (en especial **§11.b "Revisión de halcón"** — la crítica de diseño H-1…H-8).
> Bitácora cronológica: [`MEMORY.md`](./MEMORY.md) · Casos demostrables: [`docs/CASES.md`](./docs/CASES.md)

## Qué es

**Astilla** = motor que convierte **audio autorizado** en **shorts verticales 9:16** con voz
original, visuales generados por IA, subtítulos y divulgación de IA. El activo es **el motor**
(barato, reproducible, legal). Regla dura: **nada se procesa sin `Autorizacion` válida**.

Hoy tiene **dos modos** (mismo pipeline, solo cambia la fuente):
1. **Repurposing** (original): fuente larga de terceros autorizada → recorte → short.
2. **Original / divulgación** (pivot jul 2026): **guion propio + voz propia** → short.
   El gate pasa como `original` → **publicable de verdad**. Es el modo activo.

---

## ⏭️ RETOMAR ACÁ (2026-07-18)

**Estado:** 🎉 **3 SHORTS PUBLICADOS.** El motor produce shorts end-to-end por ~$3 c/u (LTX **pro**).
Publicados: Anticitera v2 (**youtube.com/shorts/caRNsgvRorc**, día 1: 595 vistas contaminadas),
telégrafo (**youtube.com/shorts/YWyjv3tG4SA**) y pelo/catapultas (**youtube.com/shorts/xQJHJD4XJFI**).
Archivos: `artifacts/short_telegrafo_musica.mp4` (51s) y `short_pelo_catapultas_musica.mp4` (46s),
cada uno con versión solo-voz `short_<n>.mp4`. El circuito quedó **formalizado en scripts reusables**
(ya no es copy-paste de ffmpeg). Ver [[produccion-tanda-telegrafo-pelo]] para gotchas 11-13.

**CANAL: `VESTIGIOS`** (handle `@vestigios.historia`) — nicho historia/divulgación, look museo/
documental, paleta teal+ámbar. ⚠️ NO es canal nuevo: preexistía con música IA (sin tracción) →
reconvertido. Las 595 vistas están "contaminadas" por audiencia de música, NO son señal limpia.
Los próximos 4-5 shorts REEDUCAN al algoritmo → 2-3 semanas de datos ruidosos, no sacar
conclusiones de un short individual en ese tramo. Ver [[primer-short-publicado]].

**El circuito de producción (formalizado en scripts jul 2026, reproducible):**
1. Fabián graba el guion (mismo lugar sin ruido, 20-30cm del mic, si se traba repite la frase sin
   cortar). Cae en `Documents/Grabaciones de sonido/<nombre>.m4a`.
2. **`python scripts/limpiar_voz.py --in <...>.m4a --out artifacts/voz_<n>.wav`** — highpass+arnndn
   (`bd.rnnn`)+comp+ganancia estática a -16 LUFS (NO loudnorm 1-pasada) + recorta silencio inicial
   Y cola final (silencio + click de detener grabación; `--sin-recorte-final` lo desactiva).
3. `python -m pipeline.animado --audio artifacts/voz_<n>.wav --guion artifacts/guion_<n>.txt
   --autorizacion original --estilo historico --modelo medium --semilla N --stub-visual` (transcribe
   + planifica 7 escenas). ⚠️ **GOTCHA 11:** aparta `artifacts/segmentos.json` viejo antes (reuso ciego);
   resguardá `segmentos_<n>.json` / `visual_job_<n>.json`.
4. Claude escribe los prompts pictóricos por escena EN SESIÓN → `artifacts/prompts_<n>.json` (ancla de
   estilo compartida = *painterly oil painting, teal+amber, chiaroscuro, 9:16*; incluir un plano
   explainer tipo diagrama Da Vinci en la escena larga). Re-correr animado con `--prompts-file` los hornea.
5. Preservar clips del short anterior (`mv artifacts/escenas_ltx/escena_*.mp4 artifacts/escenas_ltx_<prev>/`)
   y `python scripts/generar_ltx.py --indices todas --auto --pro` (clips LTX, ~$3; cap 10s/clip).
6. `python scripts/armar_short.py --nombre <n> --segmentos artifacts/segmentos_<n>.json
   --audio artifacts/voz_<n>.wav --guion artifacts/guion_<n>.txt --semilla N` (transcribe por palabra,
   **reconcilia con el guion-verdad**, karaoke MÍNIMO, bed, quema).
7. **Retimeo alineado al contenido (GOTCHA 13):** mirar `palabras_<n>.json`, elegir 7 cortes en los
   límites de beat, `python scripts/retimear_bed.py --nombre <n> --audio <...> --cortes "a,b; b,c; ..."`.
8. Música: `[musica]volume=0.12,afade in/out` + `amix normalize=0` + master `loudnorm=I=-16:TP=-1.5`
   → `short_<n>_musica.mp4`. Atribuir a **Kevin MacLeod (CC-BY)**.

**Próximos pasos:**
1. **Seguir grabando** en orden: **arquero → trepanacion → cerebro_vidrio → hormigon**.
   Cadencia: 1 short cada 1-2 días (cuello de botella = grabar la voz, no el pipeline).
2. **Watchear métricas** de los 3 publicados (señal aún ruidosa por la reeducación del algoritmo).
3. **Branding de Vestigios:** foto de perfil (emblema de engranaje) + banner. Ocultar (unlisted) los
   videos viejos de música para limpiar la señal del canal.
4. **Deuda técnica:** (a) generalizar el retimeo (paso 7) dentro de `armar_short.py`; (b) formalizar
   `ejecutor_ltx.py` detrás del `PuertoEjecutor` (hoy `scripts/generar_ltx.py`); (c) content-address
   los checkpoints (`segmentos.json`) para matar el gotcha 11 de raíz.

**Sobre `ANTHROPIC_API_KEY`:** ya NO es bloqueante con Claude en sesión (escribe los prompts como
`--prompts-file`). Solo haría falta para correr el pipeline 100% autónomo (cron/lote sin nadie).

---

## Estado actual (implementado y verificado)

| Caso | Qué | Estado |
|------|-----|--------|
| CASO-001 | Fase 1: gate → Whisper → subtítulos → ensamblado 9:16 (`pipeline.cli`) | ✅ |
| CASO-002 | Gate de derechos rechaza no autorizado (`tests/test_derechos.py`) | ✅ |
| CASO-003 | Fase 2 animada: planificación de escenas + Ken Burns sobre stills | ✅ |
| CASO-003b | Generación visual real en **Kaggle GPU** (despacho por API, `--kaggle`) | ✅ |
| CASO-004 | Transcript `medium` + coherencia (ancla global + prompts por Claude) | ✅ (LLM requiere key) |
| CASO-005 | **AnimateDiff**: clips animados reales en Kaggle T4 (`--motion animatediff`) | ✅ |
| CASO-006 | **Coherencia de personaje** (H-1): retrato-ancla + IP-Adapter por escena (`--coherencia`) | 🟡 código listo, falta validar en GPU |
| CASO-009 | **Personaje hablante** (capas): hablante audio-driven (SadTalker) compuesto sobre ambiente IA + subs (`pipeline.hablante` + `animado` + `ensamblado_hablante_ffmpeg`) | ✅ short completo end-to-end (`short_hablante.mp4`) |
| CASO-010 | **LTX-2.3 API** (video generativo CON API, $0.04/s): t2v + i2v, 9:16 por parámetro, prompts pictóricos por Claude en sesión. Short v2 publicado | ✅ `scripts/generar_ltx.py` + `armar_short_v2.py`; ver [[ltx-api-validada]] |
| CASO-011 | **Circuito de producción formalizado** (tanda telégrafo/pelo): `limpiar_voz.py`, `armar_short.py` (parametrizado, reconcilia guion↔timing), `reconciliar_palabras.py`, `retimear_bed.py`. Bug de `transcribir_palabras` arreglado. 2 shorts terminados | ✅ ver [[produccion-tanda-telegrafo-pelo]] (gotchas 11-13) |

**LUMA (H-2 concretado, jul 2026):** `ambiente_clips_ffmpeg.ambiente_bed_clips` = adaptador de
ambiente por CLIPS de video (hermano de `ambiente_bed`/Ken Burns). Ajusta clips de ~5s al beat de
cada escena con `setpts` (ralentí cinematográfico > loop). Resultado: `short_historia_luma.mp4`.
**A/B decisivo: Luma >> SD1.5** (comparar con `short_historia_sd.mp4`). Gotchas de Luma: el
**aspect ratio es setting del UI**, NO del prompt (pedir 9:16 en el texto no sirve → salen 16:9);
prompts en plural ("close-up **shots**") producen artefacto de **tríptico** (costura vertical) →
usar "a single continuous shot"; Plan Plus = consumidor, **sin API** → paso manual (para automatizar
tras el `PuertoEjecutor` hace falta API de desarrollador). Flujo recomendado: **imagen primero**
(Photon, iterar barato) → luego image-to-video. Ancla de estilo compartida en las N escenas = H-1
resuelto (ver `artifacts/prompts_luma.md`).

**MODO ORIGINAL (pivot a divulgación, jul 2026):** el motor ya servía sin tocar orquestador ni gate.
Agregado: estilo `historico` (look documental) · `--guion guion.txt` (el guion propio es la VERDAD:
sesga a Whisper vía `initial_prompt` → deja de adivinar nombres propios, solo resuelve timing) ·
`--prompts-file prompts.json` (override del operador por escena, H-4). Con guion+voz propios el
gate pasa como `original` → **publicable de verdad**. Ver `artifacts/short_historia_sd.mp4`.
Aprendizaje: el heurístico de prompts elige palabras LARGAS (abstractas: "cuatrocientos",
"encontraron"), inútiles como prompt visual → para divulgación hace falta `--prompts-llm` (Claude)
o el override. SD1.5 brilla en macro de textura y falla en gente/escala (ahí entra Luma).

**Pase de calidad (en curso):** ✅ matting del hablante (`matting_rembg`, u2net) · ✅ subtítulos
karaoke por palabra estilo CapCut (`subtitulos_karaoke_ass` + `transcribir_palabras`).
Resultado: `short_hablante_pro.mp4`. Pendiente: personaje **SDXL/Flux** hi-res (hoy SD1.5 256²),
template de estudio (mic/auriculares), enhancer GFPGAN, head motion (sin `--still`), afinar
borde del matte (feather), integrar karaoke al flujo `hablante` end-to-end (hoy es paso aparte).

**Pendiente (roadmap):** unificar `recorte.wav` entre hablante y ambiente · CASO-006 ajustar
`ip_scale` · CASO-007 reanudación tras desconexión (ADR-002) · CASO-008 capa MCP.

## Arquitectura (Clean Architecture-lite)

```
pipeline/
├── domain/                 # núcleo puro, stdlib-only (sin Whisper/ffmpeg/anthropic)
│   ├── entities.py         # Fuente, Autorizacion, Recorte, Escena, Receta, Job, Short, Rastro
│   ├── derechos.py         # GATE de Autorizacion (ADR-009) — precondición dura
│   ├── planificacion.py    # transcript → escenas + prompts; estilos (neon|comic|minimal|historico)
│   │                       # + prompt_personaje (ancla close-up, gotcha 9)
│   ├── ports.py            # puertos (interfaces) de cada stage
│   └── orquestador.py      # DAG de stages (Fase 1)
└── infrastructure/         # adaptadores (el COMO detrás de los puertos)
    ├── audio_demo_windows.py     # fuente ORIGINAL de demo (System.Speech)
    ├── recorte_ffmpeg.py
    ├── transcripcion_whisper.py  # faster-whisper (small|medium) + guion= (initial_prompt)
    │                             # + transcribir_palabras() → timestamps por palabra
    ├── subtitulos_ass.py             # subs estáticos (Fase 1)
    ├── subtitulos_karaoke_ass.py     # karaoke por palabra (⚠️ hoy muy grande/amarillo, achicar)
    ├── exportar_job_visual.py    # visual_job.json para el ejecutor remoto
    ├── prompts_claude.py         # prompts por LLM (claude-opus-4-8) — requiere API key
    ├── visual_fondo.py / stub_visual.py   # fondos/stand-ins deterministas ($0, sin GPU)
    ├── ejecutor_kaggle.py        # PuertoEjecutor: Kaggle (imagen|animatediff|talking/SadTalker)
    ├── matting_rembg.py          # quita el fondo del hablante (u2net) → .mov con alpha
    ├── ensamblado_ffmpeg.py      # Fase 1 (fondo+onda+subs)
    ├── ensamblado_escenas_ffmpeg.py  # Ken Burns sobre stills (CON onda+subs)
    ├── ensamblado_clips_ffmpeg.py    # concat de clips AnimateDiff
    ├── ensamblado_hablante_ffmpeg.py # ambiente_bed (Ken Burns LIMPIO) + componer_hablante
    └── ambiente_clips_ffmpeg.py      # ambiente_bed_clips: bed desde CLIPS (Luma), ajusta al beat
pipeline/cli.py        # Fase 1 (un short simple)
pipeline/animado.py    # Fase 2 / modo original (--guion, --prompts-file, --estilo historico)
pipeline/hablante.py   # CASO-009 capa 1: talking-head audio-driven (SadTalker en Kaggle)
```

**Nota:** `ambiente_bed` (Ken Burns) y `ambiente_bed_clips` (Luma) son **hermanos intercambiables**:
producen el mismo bed 9:16 limpio (sin subs ni onda) y el karaoke se quema después. Ese es el
punto de extensión para cualquier proveedor de visuales.

**Idea fuerza:** el dominio dice QUÉ stages y en qué orden + QUÉ es una autorización válida;
la infra dice CÓMO. Cada stage es intercambiable detrás de su puerto — por eso pasar de
stills a video (AnimateDiff) o de local a Kaggle solo cambió el adaptador, no el orquestador.

## Cómo correr

```bash
# Fase 1 — short simple (demo con TTS original de Windows)
python -m pipeline.cli --estilo neon --semilla 1

# Gate de derechos en acción
python tests/test_derechos.py

# Fase 2 — flujo animado. Modos:
python -m pipeline.animado --estilo neon --semilla 1 --stub-visual          # prueba local sin GPU
python -m pipeline.animado --kaggle --estilo neon --semilla 1                # imágenes SD en Kaggle + Ken Burns
python -m pipeline.animado --motion animatediff --kaggle --estilo neon --semilla 1  # clips animados reales
python -m pipeline.animado --motion animatediff --coherencia --prompts-llm --kaggle --estilo neon --semilla 1  # + misma cara en todas las escenas (CASO-006)

# Con fuente real + mejoras de calidad:
python -m pipeline.animado --audio sources/x.wav --autorizacion dominio_publico \
    --evidencia "URL" --modelo medium --prompts-llm --motion animatediff --kaggle
```

### MODO ORIGINAL — el flujo activo (divulgación/historia)

```bash
# 1) Limpiar la voz grabada (paso-alto + denoise + compresión + loudness broadcast)
ffmpeg -y -i "artifacts/guion_historia/mi_voz.m4a" \
  -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a pcm_s16le -ar 16000 -ac 1 artifacts/guion_historia.wav

# 2) ⚠️ CORTAR EL SILENCIO INICIAL (había 5.4s → mata la retención en shorts)
ffmpeg -i artifacts/guion_historia.wav -af "silencedetect=noise=-35dB:d=0.4" -f null -   # detectar
ffmpeg -y -ss <inicio_voz> -to <fin_voz> -i artifacts/guion_historia.wav -c:a pcm_s16le artifacts/guion_trim.wav
# los tiempos de segmentos.json se pueden DESPLAZAR matemáticamente (-offset) en vez de re-transcribir

# 3) Pipeline: gate original + guion como verdad + prompts del operador
python -m pipeline.animado --audio artifacts/guion_trim.wav \
    --guion artifacts/guion_historia.txt --prompts-file artifacts/prompts_historia.json \
    --autorizacion original --evidencia "Guion y voz propios (contenido original)" \
    --estilo historico --modelo medium --semilla 7 --kaggle

# 4) Bed limpio (sin subs) + karaoke + quemar
#    - con stills SD:  ambiente_bed(escenas_dir, escenas, audio, receta, dest)
#    - con clips Luma: ambiente_bed_clips({indice: Path(clip)}, escenas, audio, receta, dest)
ffmpeg -y -i artifacts/bed_luma.mp4 -vf "ass=artifacts/subs_trim.ass" -c:a copy artifacts/short_final.mp4
```
> El `ass=` usa **ruta relativa** corriendo desde la raíz del repo: evita el escape de `C:` en Windows.

Salidas en `artifacts/` (gitignored): `short*.mp4` + `rastro.json` (linaje: sha256, autorización,
receta/semilla, divulgación) + `visual_job.json`.

## Entorno y credenciales

- **Windows + PowerShell**; Python 3.11 (`C:\Python311`). `ffmpeg`/`ffprobe` en PATH.
- `pip install -r requirements.txt` (faster-whisper, kaggle, anthropic).
- **Kaggle:** `kaggle.json` legacy en `C:\Users\Fabian\.kaggle\kaggle.json` (usuario
  `fabianskeinerrubio`). Requiere verificación por teléfono. Ver [`docs/KAGGLE.md`](./docs/KAGGLE.md).
- **Prompts LLM:** definir `ANTHROPIC_API_KEY` (si falta, cae al heurístico). `claude-opus-4-8`.
- 🔒 Credenciales en `.gitignore` (`kaggle.json`, `access_token`, `.kaggle/`). Nunca al repo/chat.

## Gotchas aprendidos (NO repetir)

1. **Kaggle GPU: forzar T4.** La P100 es CUDA sm_60 e **incompatible con el PyTorch de
   Kaggle (sm_70+)** → kernel ERROR con log vacío. Se fuerza `machine_shape: NvidiaTeslaT4`.
2. **Modelo SD:** `runwayml/stable-diffusion-v1-5` fue retirado de HF → usar mirror
   `stable-diffusion-v1-5/stable-diffusion-v1-5`.
3. **Token Kaggle nuevo `KGAT_`** va en `~/.kaggle/access_token` o env `KAGGLE_API_TOKEN`,
   NO en `kaggle.json` (rompe el parser). El legacy `{username,key}` es lo más probado.
4. **ffmpeg zoompan con `-loop 1 -t`** multiplica frames (explosión) → usar input único
   + `-frames:v N`.
5. **Output de procesos en background está bufferizado** — para ver el estado de un kernel
   Kaggle, consultar `kaggle kernels status <user>/<slug>` directo, no el stdout local.
6. **Derechos:** rechazar reels de IG de terceros para publicación (gate ADR-009). Para
   prueba LOCAL no publicada se registró el uso honestamente. Fuentes limpias: dominio
   público (LibriVox/archive.org `language:spa`) o audio propio.
7. **SadTalker en Kaggle (Python 3.12) = campo minado.** Su `requirements.txt` no instala
   (pines viejos). Recetа que funciona (ver `ejecutor_kaggle._KERNEL_TALKING`): instalar
   deps **sin pines** + `numpy<2`; **NO** usar `-r requirements.txt`. Parches al código
   clonado: (a) import del enhancer (`gfpgan`) hecho opcional en `animate.py` — el dir
   local `gfpgan/` de pesos ensombrece al paquete; (b) aliases `np.float/int/bool` →
   tipos reales (removidos en numpy 1.24, y no hay numpy con esos aliases + wheels 3.12);
   (c) `align_img`: `np.array([...,t[0],t[1]])` → `float(...)` (arrays inhomogéneos).
   Correr `inference.py` con `cwd=/tmp/SadTalker` (imports relativos) y clonar/checkpoints
   en `/tmp` (NO en `/kaggle/working`, si no el output pesa ~1GB).
8. **`kaggle datasets create --dir-mode zip`** monta el dataset distinto en runtime →
   `FileNotFoundError`. Subir sin `--dir-mode` (archivo suelto en `/kaggle/input/<slug>/`).
9. **El ancla (retrato del personaje) NO debe arrastrar temas de escena del transcript.**
   Con fuentes reales eso genera planos abiertos (figura lejana) y SadTalker falla:
   `can not detect the landmark from source image`. `prompt_personaje` fuerza primer
   plano de cara + negativo anti-plano-abierto (`ancla_negativo`). Verificado con audio real.
10. **Race del dataset de audio en Kaggle:** subir nueva versión y despachar el kernel al
    toque hace que agarre la versión ANTERIOR del wav (audio equivocado, mismo nombre).
    Fix: dataset **content-addressed** (hash del wav en el slug) + poll `kaggle datasets
    status` hasta `ready` antes del push. Síntoma: narrator con duración del audio viejo.

## 🎯 Benchmark: qué hace funcionar a un short de divulgación (jul 2026)

Analizado sobre una referencia real con **8M de vistas** (medicina romana / extracción de flechas).
**Es el hallazgo más importante del proyecto hasta ahora** y contradice el rumbo técnico previo:

1. **El guion es el 80%.** Estructura ganadora: *claim visceral corto* ("Arrancar una flecha te
   mataba") → *problema con anatomía concreta* → *mecanismo explicado* → *revelaciones escalonadas*
   → **compresión memorable** ("Tres pasos. Herramienta, vino, miel.") → *cierre con imagen humana*.
   ~110 palabras. **CERO relleno y CERO auto-bombo** (nunca dice "esto te va a volar la cabeza";
   entrega y deja que impacte). El **título es una pregunta** con brecha de curiosidad.
2. **Tema > producción.** Visceral + mecánico + contraintuitivo. Un "dato curioso" no compite.
3. **Ilustración pictórica > foto-realismo.** Sus visuales son stills tipo Midjourney, **más
   baratos que video generativo**. El estilo pictórico **perdona** (sin valle inquietante, sin
   manos deformes). Perseguir foto-realismo fue el eje equivocado.
4. **Subtítulos mínimos:** una palabra, chica, blanca, sin resaltado. **La imagen manda, el texto
   se subordina.** Nuestro karaoke amarillo grande compite con la imagen.
5. **Plano explainer** (tríptico/diagrama) para explicar el mecanismo en un cuadro. Barato y claro.
6. **Dirección de prompt**: detalles intencionales (un frasco rotulado "MEL"), no lo primero que sale.
7. **Música y SFX** siempre presentes. Nuestro short está mudo.

**Implicancia estratégica:** el moat es **la escritura y el criterio**, no la GPU. Esto ya estaba
anticipado al decidir el pivot ("el moat se mueve a la calidad del guion") y aun así se ignoró un
tramo persiguiendo píxeles. No repetir.

## Hallazgos de producto (de la crítica §11.b)

- **H-1 (coherencia visual) = riesgo #1**, no "medio". Mitigado a nivel de prompt (ancla
  global + biblia de estilo de Claude); identidad exacta de personaje sigue abierta (IP-Adapter).
  En Luma se resuelve con un **ancla de estilo compartida** en todos los prompts (funcionó).
- **H-2:** GPU efímera gratis es cerro autoimpuesto; Kaggle gana a Colab por su API (despacho
  automático). El `PuertoEjecutor` lo abstrae.
- **#2a:** Whisper `small` se degrada con audio real ruidoso (música/voces solapadas);
  `medium` lo arregla en la narración (más lento en CPU).
