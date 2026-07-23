# CLAUDE.md — Hub de contexto de Astilla

> Léeme primero. Soy el punto de entrada para retomar el proyecto en una sesión nueva.
> Fuente de verdad de arquitectura: [`SAD_Astilla_repurposing.md`](./SAD_Astilla_repurposing.md)
> (en especial **§11.b "Revisión de halcón"** — la crítica de diseño H-1…H-8).
> Bitácora cronológica: [`MEMORY.md`](./MEMORY.md) · Casos demostrables: [`docs/CASES.md`](./docs/CASES.md)
> Deuda aceptada: [`docs/AUDIT.md`](./docs/AUDIT.md) · Incidentes/gotchas: [`docs/TROUBLESHOOTING.md`](./docs/TROUBLESHOOTING.md) · Parking lot: [`IDEAS.md`](./IDEAS.md)
> Estado de producción (abrir con file://): [`docs/panel_produccion.html`](./docs/panel_produccion.html) · regenerar con `python scripts/generar_panel.py`
> Reparto video/still por short (plan de costos LTX): [`docs/reparto_video_still.md`](./docs/reparto_video_still.md)
> Pendientes: **`## Próxima sesión` al final de este doc** (nombre estable del Método).

## Qué es

**Astilla** = motor que convierte **audio autorizado** en **shorts verticales 9:16** con voz
original, visuales generados por IA, subtítulos y divulgación de IA. El activo es **el motor**
(barato, reproducible, legal). Regla dura: **nada se procesa sin `Autorizacion` válida**.

Hoy tiene **dos modos** (mismo pipeline, solo cambia la fuente):
1. **Repurposing** (original): fuente larga de terceros autorizada → recorte → short.
2. **Original / divulgación** (pivot jul 2026): **guion propio + voz propia** → short.
   El gate pasa como `original` → **publicable de verdad**. Es el modo activo.

---

## ⏭️ Estado (2026-07-23)

**Estado:** 🎉 **14 PUBLICADOS + 1 LISTO PARA SUBIR + 2 EN PAUSA**. El pipeline de imagen dio un salto
grande esta sesión: **el generador de stills pasó de SDXL (Kaggle, gratis pero limitado) a ChatGPT
(GPT-image, Plan Plus de Fabián)** — resuelve de raíz los 3 puntos ciegos que la audiencia venía
criticando (manos, caras, líquidos, escenas que no ilustran el guion). Publicados: Anticitera v2, telégrafo,
pelo/catapultas, arquero, trepanacion, cerebro_vidrio, hormigon, quipus, lautaro, cruce_andes, chuno,
piston_fuego, sismografo + **mortero_bizantino** (**youtube.com/shorts/hm-JIzAQM_4**, primero de la serie
«Ingenios Olvidados», 2026-07-22/23). `manavai` y `pisagua` siguen en pausa (esperan este mismo fix).

**🎨 CAMBIO DE GENERADOR: SDXL → ChatGPT (2026-07-22/23) — el fix real de fidelidad.** Tras 3-4 rondas
regenerando stills en SDXL sin resultado (manos deformes, escenas que ignoraban el prompt, diagramas
ilegibles), Fabián probó generar en ChatGPT y clavó a la primera lo que SDXL no lograba en 4 intentos
(ver el caso del still de "huevo + mortero" y los diagramas tipo Da Vinci). **Decisión: los stills de
Vestigios se generan en ChatGPT de acá en adelante**, con un kit de prompts en español por short
(`shorts/<n>/prompts_chatgpt.md`) que Claude prepara y Fabián ejecuta a mano (Plan Plus, sin API — flujo
human-in-the-loop). Look fijo = **óleo pictórico** (coherente con los 13 shorts previos). SDXL/Kaggle
queda como alternativa de respaldo, no como default. Ver [[manos-deformes-sdxl-y-fix-negativo]].

**✅ GATE DE REVISIÓN DE STILLS (regla dura, aplica siempre):** Fabián revisa CADA still frame a frame
ANTES de animar/armar — 2 preguntas: ¿bien dibujado? ¿ilustra el beat narrado? Claude hace una segunda
pasada por separado y comparan (cada uno cachó defectos que el otro no). El que falle se regenera
(gratis en Kaggle; en ChatGPT cuesta la cuota del plan pero no dinero directo). Ver [[revisar-stills-antes-de-armar]].

**💸 GOTCHA CARO DEL DÍA (G-16, ya arreglado):** `generar_ltx.py --i2v X` SIN `--video` mandaba el
resto a **t2v ciego pagado** en vez de Ken Burns gratis → quemó ~$4 del saldo LTX en clips descartados
(alguno alucinó una torre eléctrica en escena bizantina). Default arreglado: sin `--video`, lo no-i2v va
a Ken Burns SI tiene still, a t2v solo si NO tiene still. **Regla nueva: confirmar costo estimado con
Fabián antes de CUALQUIER corrida que gaste LTX.** Saldo actual: **~$1**. Ver [[confirmar-costo-ltx-antes-de-pagar]].

**📚 GATE DE FUENTES ANTES DE GRABAR (regla dura, la trajo Fabián 2026-07-22):** cada guion nuevo lleva
línea `**Fuente:**` verificada contra fuente académica ANTES de grabar; si el dato no aguanta, se
reencuadra o se bota. Lo destapó el propio mortero publicado: el dato "clara de huevo → aguanta
terremotos" es un **mito viral** de la pestaña Inspiración de YouTube (real pero inflado). Corrigió de
paso la katana (era "ceniza de volcán", mito → ahora pulido real con óxido de hierro) y el papel chino
(era "arsénico", mito → es berberina; el arsénico real era el CORRECTOR, no el tinte). Ver [[gate-de-fuentes-antes-de-grabar]].

**🎬 FÓRMULA v3 + BANCO VERIFICADO EN COLA (18 guiones, secciones 16-33 de `guiones.md`):** hook-misterio
con gap, sin tríada, voz con opinión, cierre que ABRE loop, ~150-175 palabras — más agresivo que la v2
(que solo arreglaba el CTA). Orden maestro de grabación + "pastilla la próxima" (el tease se graba
aparte y se fija al editar según calendario real). **`piedra_solar` (#21) ya está grabada y armada**,
lista para que Fabián la revise y suba — su tease apunta a la **katana** (#17, primera del banco en cola).
Series: 16-29 «Ingenios Olvidados» (mundo), 30-33 «Mecanismos de América». Todo vive en el ÚNICO
`artifacts/guiones.md` (no hay archivo separado — ver [[gate-de-fuentes-antes-de-grabar]]).

**🖼️ GUIÑO VISUAL DEL PRÓXIMO SHORT (idea de Fabián, 2026-07-22, en prueba):** la última escena de cada
short muestra la imagen del PRÓXIMO tema (no solo el audio lo nombra) — mortero cierra con un cristal
vikingo, piedra_solar cierra con una katana. Refuerza el gancho de suscripción a nivel visual, $0 extra
(es un still que ya se iba a generar). No es regla fija todavía, se evalúa short a short. Ver [[guino-visual-proximo-short]].

**📊 PANEL DE PRODUCCIÓN:** `docs/panel_produccion.html` (abrir con file://, sin cuenta) = estado del
pipeline por short + métricas + banco. Se regenera con `python scripts/generar_panel.py`; datos
manuales en `docs/panel_datos.json`. **Pendiente: no se regeneró esta sesión** — correrlo antes de la
próxima, agregando mortero_bizantino y piedra_solar.

**REPO EN GITHUB:** `faborubio/astilla` **privado**, remote `origin` por HTTPS (`gh` autenticado como
faborubio). `.claude/` NO se versiona. `artifacts/` gitignored (guiones, wavs, mp4 quedan solo locales).

**CANAL: `VESTIGIOS`** (handle `@vestigios.historia`) — nicho historia/divulgación, look museo/
documental, paleta teal+ámbar. Ver [[estrategia-canal-vestigios]], [[primer-short-publicado]].

**ESTRATEGIA vigente:** títulos-pregunta + CTA de suscripción con serie+gancho al próximo (fórmula v2/v3)
+ hashtags, todo en `artifacts/guiones.md`. Chequear saturación antes de cada tema nuevo. El moat es
guion + credibilidad (gate de fuentes) + distribución, NO foto-realismo/GPU.

**📁 ESTRUCTURA (un short = una carpeta `artifacts/shorts/<n>/`)** con nombres FIJOS: `voz.wav`,
`guion.txt`, `prompts.json` (o `prompts_chatgpt.md` para el kit en español), `segmentos.json`,
`visual_job.json`, `palabras.json`, `subs.ass`, `bed.mp4`, `clips/still_NN.png` + `clips/escena_NN.mp4`
(Ken Burns o i2v), `short.mp4`, `short_musica.mp4`. Compartidos en la raíz: `bd.rnnn`,
`musica_lightless_dawn.mp3`, `guiones.md` (maestro ÚNICO). Todos los scripts toman `--nombre <n>` y
resuelven las rutas solas (`scripts/rutas.py::RutasShort`).

**El circuito de producción (folder-aware, reproducible, actualizado con ChatGPT):**
1. Fabián graba el guion (mismo lugar sin ruido, 20-30cm del mic). **Si se traba: pausa 1-2s en
   silencio y repite la frase entera.** ⚠️ `limpiar_voz` NO borra repeticiones ni respiraciones fuertes
   — se cortan/silencian a mano después con `silencedetect`+`aselect`/`volume=enable=between(...)`
   (empalme en el hueco entre frases, sin tocar palabras). Cae en `Documents/Grabaciones de sonido/<n>.m4a`.
2. **`python scripts/limpiar_voz.py --in "<...>.m4a" --nombre <n>`** → `shorts/<n>/voz.wav`.
2b. **Ojo con guiones que tienen v2 + versión viral (A/B) en la misma sección** (G-14): `exportar_guion.py`
   toma la v2 vieja por error (corta en el primer header `###`). Si grabaste la viral, escribir
   `guion.txt` a mano con ESE texto (no correr el exportador ciegamente).
3. `python -m pipeline.animado --nombre <n> --audio ... --guion ... --autorizacion original --estilo
   historico --modelo medium --semilla N --stub-visual` (transcribe + planifica escenas).
   Si cambiaste el audio (cortes/silencios), **borrá `segmentos.json` y `palabras.json`** antes de
   re-correr para forzar re-transcripción.
4. **Storyboard + prompts en ESPAÑOL para ChatGPT** → `shorts/<n>/prompts_chatgpt.md` (bloque de estilo
   fijo: óleo pictórico, teal+amber, chiaroscuro, museo, pergamino + "sin manos/caras en primer plano" +
   dirección anti-puntos-ciegos: navegante/gente SIEMPRE de espaldas o en silueta, objetos como sujeto
   antes que acción con líquidos). Fabián genera en ChatGPT, revisa él primero, pasa las imágenes.
4b. Claude mapea cada imagen a su `still_NN.png` por CONTENIDO (los nombres de descarga de ChatGPT no
   traen el índice) y hace su propia pasada de revisión — comparar con la de Fabián antes de seguir.
5. **Clips: Ken Burns por defecto ($0), i2v solo en 1-2 money shots** (confirmando costo con Fabián
   primero — regla dura post-G-16): `python scripts/generar_ltx.py --nombre <n> --indices todas --auto
   --i2v "<money_shots>"`. Sin `--video`: lo no-i2v con still va a Ken Burns automático.
6. `python scripts/armar_short.py --nombre <n> --semilla N` (transcribe por palabra, reconcilia con el
   guion-verdad, karaoke, bed, quema).
7. **Retimeo alineado al contenido:** mirar `palabras.json`, cortes en límites de frase,
   `python scripts/retimear_bed.py --nombre <n> --cortes "a,b; b,c; ..."`.
8. **Fix de cola del CTA (nuevo, evita que se corte el "seguime"):** si el video termina justo cuando
   termina la última palabra, agregar ~1.3s: `ffmpeg -vf tpad=stop_mode=clone:stop_duration=1.3 -af
   apad=pad_dur=1.3`.
9. Música: `volume=0.12,afade in/out` + `amix normalize=0` + `loudnorm=I=-16:TP=-1.5` → `short_musica.mp4`.

**Sobre `ANTHROPIC_API_KEY`:** no bloqueante con Claude en sesión. El paso de imagen ahora es manual
(ChatGPT vía Fabián), así que el pipeline ya NO apunta a 100% autónomo en el corto plazo — es una
decisión consciente de calidad sobre automatización total.

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
| CASO-012 | **Refactor folder-aware + tanda de 4** (arquero/trepanacion/cerebro_vidrio/hormigon): un short = una carpeta `artifacts/shorts/<n>/`, scripts con `--nombre` (`scripts/rutas.py`). Fix transcripción (vad+guion truncaba/alucinaba). Repeticiones al grabar → corte manual del wav. **Gotcha 11 muerto** | ✅ 4 shorts terminados; ver [[refactor-folder-aware-y-fix-transcripcion]] |
| CASO-013 | **Flujo híbrido barato + fidelidad (~$0.7/short)**: fast por default (no `--pro`); **stills SDXL gratis en Kaggle** (`generar_stills_kaggle.py` + kernel `sdxl`) con Ken Burns local, LTX-video solo en escenas con movimiento (`--video`); **i2v** (`--i2v`) ancla el video a un still fiel. Referencias de Fabián → prompt preciso + i2v. Tanda de 4 (piston_fuego/manavai/sismografo/pisagua) terminada | ✅ ver [[ltx-fast-vs-pro-y-hibrido-stills]], [[referencias-y-i2v-para-fidelidad]] |
| CASO-014 | **Pivot a ChatGPT para stills + gates de calidad**: SDXL fallaba en manos/caras/líquidos/escenas complejas → **stills en ChatGPT** (GPT-image, óleo pictórico, kit `prompts_chatgpt.md`, human-in-the-loop). Gate de revisión de stills (Fabián + Claude) + **gate de fuentes** (cada guion con `Fuente:` verificada; cazó 3 mitos virales). Guiño visual del próximo short, fórmula v3, fix de cola del CTA. mortero publicado + piedra_solar lista | ✅ ver [[manos-deformes-sdxl-y-fix-negativo]], [[gate-de-fuentes-antes-de-grabar]], [[revisar-stills-antes-de-armar]] |

**LUMA (H-2 concretado, jul 2026):** `ambiente_clips_ffmpeg.ambiente_bed_clips` = adaptador de
ambiente por CLIPS de video (hermano de `ambiente_bed`/Ken Burns). Ajusta clips de ~5s al beat de
cada escena con `setpts` (ralentí cinematográfico > loop). Resultado: `short_historia_luma.mp4`.
**A/B decisivo: Luma >> SD1.5** (comparar con `short_historia_sd.mp4`). Gotchas de Luma: el
**aspect ratio es setting del UI**, NO del prompt (pedir 9:16 en el texto no sirve → salen 16:9);
prompts en plural ("close-up **shots**") producen artefacto de **tríptico** (costura vertical) →
usar "a single continuous shot"; Plan Plus = consumidor, **sin API** → paso manual (para automatizar
tras el `PuertoEjecutor` hace falta API de desarrollador). Flujo recomendado: **imagen primero**
(Photon, iterar barato) → luego image-to-video. Ancla de estilo compartida en las N escenas = H-1
resuelto (ver `artifacts/_legacy/prompts_luma.md`).

**MODO ORIGINAL (pivot a divulgación, jul 2026):** el motor ya servía sin tocar orquestador ni gate.
Agregado: estilo `historico` (look documental) · `--guion guion.txt` (el guion propio es la VERDAD:
sesga a Whisper vía `initial_prompt` → deja de adivinar nombres propios, solo resuelve timing) ·
`--prompts-file prompts.json` (override del operador por escena, H-4). Con guion+voz propios el
gate pasa como `original` → **publicable de verdad**. Ver `artifacts/_legacy/short_historia_sd.mp4`.
Aprendizaje: el heurístico de prompts elige palabras LARGAS (abstractas: "cuatrocientos",
"encontraron"), inútiles como prompt visual → para divulgación hace falta `--prompts-llm` (Claude)
o el override. SD1.5 brilla en macro de textura y falla en gente/escala (ahí entra Luma).

**Pase de calidad (en curso):** ✅ matting del hablante (`matting_rembg`, u2net) · ✅ subtítulos
karaoke por palabra estilo CapCut (`subtitulos_karaoke_ass` + `transcribir_palabras`).
Resultado: `short_hablante_pro.mp4`. Las mejoras pendientes del hablante (SDXL/Flux, GFPGAN,
head motion, template de estudio, feather del matte, karaoke end-to-end) quedaron **congeladas
con el flujo** → parqueadas en [`IDEAS.md`](./IDEAS.md) (AUD-007).

**Pendiente (roadmap):** diferido al parking lot [`IDEAS.md`](./IDEAS.md) — reanudación
(CASO-007/ADR-002), capa MCP (CASO-008), pipeline autónomo, publicación automática, SFX,
mejoras hablante. Nada de eso entra sin tracción que lo reclame.

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

### MODO ORIGINAL — el flujo activo (divulgación/historia), folder-aware

> El circuito paso a paso (con gotchas) está arriba en **§Estado → "El circuito de producción"**.
> Todo vive en `artifacts/shorts/<n>/` y los scripts toman `--nombre`. End-to-end de un short:

```bash
# 1) limpiar voz grabada -> shorts/<n>/voz.wav
python scripts/limpiar_voz.py --in "Documents/Grabaciones de sonido/<n>.m4a" --nombre <n>
# 1b) exportar guion.txt (voz hablada) desde el maestro artifacts/guiones.md
python scripts/exportar_guion.py --nombre <n>
# 2) transcribir + planificar (segmentos.json + visual_job.json en la carpeta)
python -m pipeline.animado --nombre <n> --audio artifacts/shorts/<n>/voz.wav \
    --guion artifacts/shorts/<n>/guion.txt --autorizacion original \
    --evidencia "Guion y voz propios (contenido original)" --estilo historico \
    --modelo medium --semilla N --stub-visual
# 3) Claude escribe shorts/<n>/prompts.json e inyecta en visual_job.json
# 4) clips LTX -> shorts/<n>/clips/   (fast por default, $0.04/s; NO usar --pro)
#    FIDELIDAD (2026-07-22): generá TODOS los stills SDXL fieles primero y animá los money
#    shots con --i2v (LTX solo agrega movimiento sobre un still fiel, NO inventa la escena).
#    El t2v ciego (--video) es el que produce "clips que no tienen nada que ver" (crítica de
#    la audiencia) -> usalo solo si no hay still posible para esa escena.
python scripts/generar_ltx.py --nombre <n> --indices todas --auto --i2v <money_shots>
#    el resto (sin --i2v/--video) = still+Ken Burns local ($0). Necesita clips/still_NN.png.
# 5) armar (palabras + karaoke + bed + quema) -> shorts/<n>/short.mp4
python scripts/armar_short.py --nombre <n> --semilla N
# 6) retimeo alineado al contenido (mirar shorts/<n>/palabras.json)
python scripts/retimear_bed.py --nombre <n> --cortes "0,a; a,b; ..."
# 7) música -> shorts/<n>/short_musica.mp4  (afade + amix normalize=0 + loudnorm -16)
```
> El `ass=` de armar/retimear usa **ruta relativa** (`shorts/<n>/subs.ass`): evita el escape de `C:` en Windows.

Salidas por short en `artifacts/shorts/<n>/` (gitignored): `short.mp4` / `short_musica.mp4` + los
intermedios. `rastro.json` (linaje: sha256, autorización, receta/semilla, divulgación) lo emite el
modo demo/kaggle en la raíz.

## Entorno y credenciales

- **Windows + PowerShell**; Python 3.11 (`C:\Python311`). `ffmpeg`/`ffprobe` en PATH.
- `pip install -r requirements.txt` (faster-whisper, kaggle, anthropic).
- **Kaggle:** `kaggle.json` legacy en `C:\Users\Fabian\.kaggle\kaggle.json` (usuario
  `fabianskeinerrubio`). Requiere verificación por teléfono. Ver [`docs/KAGGLE.md`](./docs/KAGGLE.md).
- **Prompts LLM:** definir `ANTHROPIC_API_KEY` (si falta, cae al heurístico). `claude-opus-4-8`.
- 🔒 Credenciales en `.gitignore` (`kaggle.json`, `access_token`, `.kaggle/`). Nunca al repo/chat.

## Gotchas e incidentes (NO repetir)

**Movidos a [`docs/TROUBLESHOOTING.md`](./docs/TROUBLESHOOTING.md)** — gotchas G-1…G-13 +
incidentes por área (Kaggle/GPU, transcripción, grabación, música, Windows, Luma), en formato
síntoma → causa → fix. Los tres que más muerden en el flujo activo:
- **Si cambia el audio de un short, borrar `shorts/<n>/segmentos.json` y `palabras.json`**
  (checkpoints reusables; G-11/AUD-005).
- **Al grabar: pausa 1-2s en silencio antes de repetir una frase** — la repetición queda en el
  wav y se corta a mano.
- **Kaggle: forzar T4** (`machine_shape: NvidiaTeslaT4`); la P100 muere con log vacío (G-1).

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

---

## Próxima sesión

> Pendientes en orden de valor. **(Fabián)** = espera acción o decisión del autor.

1. **(Fabián) SUBIR `piedra_solar`** — está terminada y aprobada (`shorts/piedra_solar/short_musica.mp4`,
   79s, 100% stills ChatGPT, guiño de katana al cierre). Solo falta que Fabián la revise una vez más y la
   suba. Título/hashtags/descripción en `guiones.md` #21 (versión viral grabada). Toggle **"contenido
   alterado o sintético"** (divulgación de IA). ⚠️ Su tease dice "ceniza de volcán" (dato viejo); el short
   #17 katana ya lo corrigió a óxido — es solo el tease, menor, pero tenerlo presente.
2. **(Fabián) GRABAR `katana` (#17, primera del banco en cola)** — el tease de piedra_solar apunta a ella.
   Guion viral + `Fuente:` verificada ya en `guiones.md` #17 (ángulo REAL: pulido *togi* + nugui de óxido
   de hierro, NO la ceniza-mito). Después el circuito: limpiar voz → transcribir → **kit de prompts ChatGPT**
   (`prompts_chatgpt.md`, óleo pictórico, guiño al próximo tema = mercurio #22) → Fabián genera en ChatGPT
   y revisa → Claude mapea + segunda revisión → Ken Burns + armar. **Confirmar costo antes de tocar LTX.**
3. **(Fabián) Banco 16-33 verificado en cola (~1 mes de contenido)** en `guiones.md`: orden maestro de
   grabación (katana → mercurio → papel → cihuang → cúpulas → azul maya → espejos → hierro → arroz →
   cadena americana). **Regla dura antes de grabar cualquiera: su línea `Fuente:` ya está chequeada**
   (gate de fuentes, [[gate-de-fuentes-antes-de-grabar]]). Chequear saturación del tema en Shorts igual.
   Grabar 1 cada 1-2 días (constancia = el factor más frágil). **Pausá 1-2s antes de repetir** al grabar.
4. **(Fabián, cuando quiera) Retomar `manavai` y `pisagua`** — ahora que los stills se hacen en ChatGPT,
   se pueden re-renderizar bien (era el fix que esperaban). Guion y voz ya están (guiones.md 11, 13).
5. **Watchear métricas** de los publicados (14 con mortero). Métrica primaria = **% visto/retención**
   (informe "Rendimiento en las primeras 24h", Modo Avanzado; **>100% = loopea**). El mortero es el
   primer short con el pipeline de calidad completo (ChatGPT + v3 + guiño) → su retención/suscripción es
   la señal a mirar. **Leer comentarios** (dieron la señal más accionable). ⚠️ **Regenerar el panel**
   (`generar_panel.py`) — no se corrió esta sesión; agregar mortero + piedra_solar a `panel_datos.json`.
6. **(Fabián) Branding de Vestigios:** foto de perfil (emblema de engranaje) + banner. Ocultar (unlisted)
   los videos viejos de música para limpiar la señal del canal.
7. **Deuda técnica** — en [`docs/AUDIT.md`](./docs/AUDIT.md): AUD-002 (generalizar el retimeo dentro de
   `armar_short.py`), + nuevos: formalizar el flujo ChatGPT (kit de prompts → mapeo por contenido) y el
   fix de cola del CTA (pasos 8) dentro de los scripts en vez de a mano. Distribución multi-plataforma y
   research dummy-account siguen en [`IDEAS.md`](./IDEAS.md).
