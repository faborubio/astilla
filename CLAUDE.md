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

## ⏭️ Estado (2026-07-22)

**Estado:** 🎉 **13 PUBLICADOS + 2 EN PAUSA (descartados por calidad)**. El motor produce shorts por
**~$0.7 c/u** (flujo híbrido: fast + stills SDXL gratis + i2v), no $3-4, PERO tiene una falencia de
calidad confirmada (ver abajo). Publicados: Anticitera v2 (**youtube.com/shorts/caRNsgvRorc**), telégrafo
(**youtube.com/shorts/YWyjv3tG4SA**), pelo/catapultas (**youtube.com/shorts/xQJHJD4XJFI**), arquero,
trepanacion, cerebro_vidrio, hormigon, quipus, lautaro, cruce_andes, chuno + **piston_fuego** y
**sismografo** (subidos por Fabián el 2026-07-22).

**⏸️ `manavai` y `pisagua` EN PAUSA (2026-07-22):** de la tanda de 4, Fabián publicó solo `piston_fuego`
y `sismografo`. **Los otros dos NO le gustaron → quedan en pausa por ahora** (no descartar el guion, sí
el render actual). Tienen `short_musica.mp4` pero no se suben. Se retoman cuando el pipeline mejore la
fidelidad visual (son justo los de referencias Rapa Nui / Guerra del Pacífico).

**🗣️ CRÍTICA DE LA AUDIENCIA (2026-07-22) — el problema #1 a resolver:** en los publicados de anoche
llegaron **comentarios con crítica constructiva sobre clips que no tienen nada que ver con lo narrado**.
Esto CONFIRMA desde afuera la deuda visual que ya veíamos internamente: LTX (t2v) deriva del contenido
del guion (etnia/época/objeto equivocado, escenas genéricas que no ilustran el mecanismo). **El flujo es
barato pero la relación imagen↔narración falla** → es la próxima pieza a arreglar del pipeline, no un
detalle cosmético. Ver [[fidelidad-visual-ltx-etnia-epoca]], [[referencias-y-i2v-para-fidelidad]].

**💰 FLUJO HÍBRIDO — la gran palanca de costo (2026-07-21/22):** de ~$3-4/short (pro, todo-video) a
**~$0.7/short**. Tres decisiones: (a) **fast por default** (no `--pro`; A/B lo probó: igual/más on-brand,
−33%, y como la API no fija semilla sacás 2 tiros por el precio de 1 pro); (b) **stills SDXL gratis en
Kaggle** para las escenas estáticas (`scripts/generar_stills_kaggle.py`, kernel `sdxl` en `ejecutor_kaggle.py`)
animadas con Ken Burns local, y LTX-video solo en las escenas con movimiento (`generar_ltx.py --video`);
(c) **i2v** (`generar_ltx.py --i2v`) para anclar el video a un still fiel cuando t2v deriva. Reparto
video/still por short en [`docs/reparto_video_still.md`](./docs/reparto_video_still.md).

**🎯 FIDELIDAD POR REFERENCIAS (2026-07-22):** para temas específicos (Rapa Nui, Guerra del Pacífico),
Fabián pasa **fotos de referencia** → Claude extrae los detalles al prompt (**Nivel 1**) + **i2v** ancla el
video a un still fiel (**Nivel 2**). Corrigió manavai (manavai reales = anillo BAJO de basalto oscuro, no
torres/vidrio) y pisagua (uniforme chileno 1879 **azul+rojo+kepí**, buques a vapor, desierto del Atacama;
adiós casco de acero/veleros). Es el fix definitivo de [[fidelidad-visual-ltx-etnia-epoca]]. Ver
[[referencias-y-i2v-para-fidelidad]].

**🖼️ DEUDA VISUAL (espera crédito):** Fabián notó que varios clips de la tanda **no son verídicos
para la época / la etnia de las personas está equivocada** (LTX mete caras europeas/anacronismos pese
a "Andean"/"Mapuche"/"Inca" en el prompt). Fix = reforzar prompt con **etnia + época explícitas +
negativos** y **regen targeted** de los clips ofensivos (no todos). Ver [[fidelidad-visual-ltx-etnia-epoca]].

**🔧 FIX de audio esta tanda:** quipus tenía una repetición de "decenas" a los 0:29 (Whisper la fusionó
en un token largo con 1.45s de pausa muerta). Se cortó del **video final** con empalme en silencio
(`trim`+`concat`, ambos extremos en silencio detectado con `silencedetect`) → $0, sin regenerar clips.
Método nuevo: para cazar repeticiones que Whisper fusiona, mirar palabras con duración anómala + `silencedetect`.

**📊 PANEL DE PRODUCCIÓN (nuevo 2026-07-21):** `docs/panel_produccion.html` (abrir con file://, sin
cuenta) = estado del pipeline por short (leído del disco) + métricas de publicados + banco. Se regenera
con `python scripts/generar_panel.py`; datos manuales en `docs/panel_datos.json`. Correrlo tras cada
avance. (El artifact de claude.ai quedó bajo la cuenta corporativo@caucorp, que Fabián no puede abrir.)

**⚠️ LECCIÓN de esta tanda (audio):** al grabar, si Fabián se traba y **repite la frase**, esa
repetición QUEDA en el audio (`limpiar_voz` no la borra). Hay que **cortarla a mano** del wav (empalme
en los silencios con `aselect='not(between(t,A,B))'`) y re-correr armar+retimeo+música (los clips LTX
se reusan, $0 extra). Por eso la nota de `guiones.md` ahora pide **pausar 1-2s antes de repetir**.
Además: si la cola se come el CTA final, re-limpiar con `--sin-recorte-final` y recortar la cola a mano.

**🔧 FIXES de pipeline esta tanda:** (a) `transcripcion_whisper.transcribir()` ya NO pasa el guion como
`initial_prompt` ni usa `vad_filter` (juntos TRUNCABAN a la mitad o ALUCINABAN el arranque; el texto
final igual sale del pase por-palabra reconciliado). (b) **Refactor folder-aware**: un short = una
carpeta `artifacts/shorts/<n>/`, scripts con `--nombre` (`scripts/rutas.py`). **Gotcha 11 muerto.**
Ver [[refactor-folder-aware-y-fix-transcripcion]].

**REPO EN GITHUB (jul 2026):** `faborubio/astilla` **privado**, remote `origin` por HTTPS (`gh`
autenticado como faborubio). `.claude/` NO se versiona (config local). `artifacts/` gitignored
(guiones `guiones.md`, wavs, mp4 quedan solo locales). Commitear/pushear cuando se pida.

**CANAL: `VESTIGIOS`** (handle `@vestigios.historia`) — nicho historia/divulgación, look museo/
documental, paleta teal+ámbar. ⚠️ NO es canal nuevo: preexistía con música IA (sin tracción) →
reconvertido. Las 595 vistas están "contaminadas" por audiencia de música, NO son señal limpia.
Los próximos 4-5 shorts REEDUCAN al algoritmo → 2-3 semanas de datos ruidosos, no sacar
conclusiones de un short individual en ese tramo. Ver [[primer-short-publicado]].

**📊 MÉTRICAS (2026-07-20, con la tanda de 4 ya publicada):** canal **23 subs (+18/28d**, casi el
doble desde los 11 de la medición anterior). Los 4 nuevos con **like-rate ~7%** (arquero 898/70,
cerebro_vidrio 778/55, trepanacion 688/36, pelo 577/41) = la señal más limpia de que el guion
funciona. 4,2K vistas / 37,9h en 28d. **⚠️ hormigón: retención 53,9%** (vs 74% del baseline) →
**tema saturado** (Fabián lo vio en varios canales); no es falla de guion. **Comentarios ~0 sigue
siendo el gap.** Primera señal (3 shorts, 74,4% retención): [[estrategia-canal-vestigios]].

**🔑 DOS CRITERIOS DE TEMA NUEVOS (2026-07-20, ver [[estrategia-canal-vestigios]] §7-8):**
(a) **chequear saturación antes de elegir tema** (el hormigón lo probó); (b) **evitar temas de odio
entre naciones** aunque den comentarios — se retiró el guion de la Guerra del Pacífico (agravio
Bolivia/mar, imán de flame) y se reemplazó por **pisagua** (misma guerra, encuadre de MECANISMO:
desembarco anfibio). Nada de superlativos falsos ("primero del mundo"). El género bélico es un
desvío: los hits siempre fueron "técnica ingeniosa", no guerra.

**ESTRATEGIA aplicada (checklist de 7 factores Hook/Retención/Duración/CTA/Constancia/Hashtags/
Suscriptores):** **títulos-pregunta** + **CTA de comentario** al cierre + **hashtags** por short, todo
en el maestro `artifacts/guiones.md`. Focos abiertos: **constancia** (grabar seguido, el factor
más frágil) y auditar el **hook a 2s** en Studio. NO perseguir foto-realismo/GPU: el moat es guion+
distribución.

**📝 BANCO DE GUIONES sin grabar (al 2026-07-20):** `lautaro`, `cruce_andes`, **`pisagua`** (Guerra
del Pacífico reencuadrada como operación anfibia) + **serie mecanismos de América**: **`chuno`**
(chuño/liofilizado de papa), **`quipus`**. **Fuente única de texto = el maestro
`artifacts/guiones.md`** (título + hashtags + guion de cada short, una sección por short); el
`shorts/<n>/guion.txt` que consume el pipeline se GENERA de ahí con
`python scripts/exportar_guion.py --nombre <n>` (solo la voz hablada) — no editar guion.txt a mano.
El guion viejo de Guerra del Pacífico se retiró a `artifacts/_legacy/shorts_retirados/guerra_pacifico/`.
Todos siguen la fórmula (gancho contraintuitivo → problema → mecanismo → tríada de 3 palabras →
cierre → CTA) sobre hechos reales.

**⚠️ `moais` EN PAUSA (saturado, chequeo 2026-07-20):** el guion existe (`artifacts/shorts/moais/`)
pero el tema "cómo caminaron los moáis" está **explotando en Shorts ahora** (shorts con el mismo
ángulo en oct-2025 … may-2026) → es el nuevo `hormigón`. NO grabar hasta que baje la ola (revisar
en ~3-6 meses). **Reemplazo elegido para la línea Isla de Pascua: `manavai`** (jardines de piedra:
cómo cultivaban en la isla volcánica pelada con corrales que rompen el viento y atrapan humedad) —
saturación en Shorts casi nula (solo prensa de conservación), mecanismo puro, on-brand. **Guion de
`manavai` ya escrito** (sección #11 del maestro `guiones.md` + título en el mismo). `pukao` (subir el
sombrero) se descartó por estar pegado al tema saturado del moái. Ver [[estrategia-canal-vestigios]] §9.

**📁 ESTRUCTURA (folder-aware desde jul 2026): un short = una carpeta `artifacts/shorts/<n>/`**
con nombres FIJOS: `voz.wav`, `guion.txt`, `prompts.json`, `segmentos.json`, `visual_job.json`,
`palabras.json`, `subs.ass`, `bed.mp4`, `clips/still_NN.png` (stills SDXL) + `clips/escena_NN.mp4`
(Ken Burns o video/i2v), `short.mp4`, `short_musica.mp4`.
Compartidos en la raíz `artifacts/`: `bd.rnnn`, `musica_lightless_dawn.mp3`, `guiones.md` (maestro:
título + hashtags + guion de todos los shorts). Lo viejo (telegrafo, pelo, anticitera, historia, hablante, luma) en `artifacts/_legacy/`.
Todos los scripts toman `--nombre <n>` y resuelven las rutas solas (`scripts/rutas.py::RutasShort`).
**Esto mató el gotcha 11 de raíz** (cada checkpoint es propio de su carpeta, imposible reusar el de
otro short).

**El circuito de producción (folder-aware, reproducible):**
1. Fabián graba el guion (mismo lugar sin ruido, 20-30cm del mic). **Si se traba: pausa 1-2s en
   silencio y repite la frase entera.** ⚠️ `limpiar_voz` NO borra repeticiones — Claude las corta a
   mano después (esa pausa clara es la que deja el corte limpio). Cae en `Documents/Grabaciones de sonido/<nombre>.m4a`.
2. **`python scripts/limpiar_voz.py --in "<...>.m4a" --nombre <n>`** → `shorts/<n>/voz.wav`.
   highpass+arnndn (`bd.rnnn`)+comp+ganancia estática a -16 LUFS (NO loudnorm 1-pasada) + recorta
   silencio inicial Y cola final (`--sin-recorte-final` la desactiva; usar si la cola se come el CTA).
2b. **`python scripts/exportar_guion.py --nombre <n>`** → genera `shorts/<n>/guion.txt` (solo la voz
   hablada) desde la sección del maestro `artifacts/guiones.md`. El guion se edita SIEMPRE en el
   maestro, nunca en guion.txt directo. (Si cambiás el texto en el maestro, re-exportá.)
3. `python -m pipeline.animado --nombre <n> --audio artifacts/shorts/<n>/voz.wav --guion
   artifacts/shorts/<n>/guion.txt --autorizacion original --evidencia "..." --estilo historico
   --modelo medium --semilla N --stub-visual` (transcribe + planifica escenas). Con `--nombre`
   escribe `segmentos.json`/`visual_job.json` DENTRO de la carpeta (ya no hay que apartar nada).
   Nota: si cambiás el audio, **borrá `shorts/<n>/segmentos.json` y `palabras.json`** para forzar
   re-transcripción (siguen siendo checkpoints, pero ahora aislados por carpeta).
4. Claude escribe los prompts pictóricos por escena EN SESIÓN → `shorts/<n>/prompts.json` (ancla de
   estilo compartida = *painterly oil painting, teal+amber, chiaroscuro, 9:16*; incluir un plano
   explainer tipo diagrama Da Vinci). **Para stills SDXL: estilo al FRENTE** (si no, SDXL deriva a foto)
   y etnia/época en afirmativo. **Tema específico/local → pedir REFERENCIAS a Fabián** y sacar los
   detalles exactos al prompt ([[referencias-y-i2v-para-fidelidad]]). Inyectar en `visual_job.json`.
4b. **Stills gratis (Kaggle SDXL, $0):** `python scripts/generar_stills_kaggle.py --nombre <n> --indices
   <estáticas>` → `clips/still_NN.png`. El negativo por defecto mata foto/etnia/anacronismo; `--negativo`
   lo override (ej. anti "torre/vidrio", anti "casco/velero", anti "todo rojo"). **Revisar por frame y
   regenerar los que fallen (gratis).**
5. **Video LTX-fast, política i2v-por-defecto (FIDELIDAD, 2026-07-22):** la audiencia criticó "clips
   que no tienen nada que ver" → causa raíz = **t2v ciego** (`--video`): LTX genera desde texto sin
   imagen de anclaje ni negative prompt, y deriva de etnia/época/objeto. **Fix = anclar todo money shot
   a un still SDXL fiel e** `**--i2v**` (LTX solo agrega movimiento, no inventa la escena):
   `python scripts/generar_ltx.py --nombre <n> --indices todas --auto --i2v "<money_shots>"` (o `--i2v
   todas`) → `clips/escena_NN.mp4` (**fast = $0.04/s**, NO `--pro`; mismo costo que t2v). Las escenas sin
   `--i2v`/`--video` = Ken Burns local $0 desde `still_NN.png`. **`--video` (t2v ciego) = solo si NO hay
   still posible** para esa escena; el script avisa si mandás t2v teniendo still disponible. Reparto por
   short: `docs/reparto_video_still.md`. Ver [[ltx-fast-vs-pro-y-hibrido-stills]], [[referencias-y-i2v-para-fidelidad]].
6. `python scripts/armar_short.py --nombre <n> --semilla N` (transcribe por palabra,
   **reconcilia con el guion-verdad**, karaoke MÍNIMO, bed, quema). Todo se resuelve de la carpeta.
7. **Retimeo alineado al contenido (GOTCHA 13):** mirar `shorts/<n>/palabras.json`, elegir 1 corte por
   clip en los límites de frase, `python scripts/retimear_bed.py --nombre <n> --cortes "a,b; b,c; ..."`.
8. Música: `[1:a]volume=0.12,afade in/out` + `amix normalize=0` + master `loudnorm=I=-16:TP=-1.5`
   → `shorts/<n>/short_musica.mp4`. Atribuir a **Kevin MacLeod (CC-BY)**.

**Próximos pasos:** → ver **`## Próxima sesión`** al final del doc (nombre estable del Método).

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
| CASO-012 | **Refactor folder-aware + tanda de 4** (arquero/trepanacion/cerebro_vidrio/hormigon): un short = una carpeta `artifacts/shorts/<n>/`, scripts con `--nombre` (`scripts/rutas.py`). Fix transcripción (vad+guion truncaba/alucinaba). Repeticiones al grabar → corte manual del wav. **Gotcha 11 muerto** | ✅ 4 shorts terminados; ver [[refactor-folder-aware-y-fix-transcripcion]] |
| CASO-013 | **Flujo híbrido barato + fidelidad (~$0.7/short)**: fast por default (no `--pro`); **stills SDXL gratis en Kaggle** (`generar_stills_kaggle.py` + kernel `sdxl`) con Ken Burns local, LTX-video solo en escenas con movimiento (`--video`); **i2v** (`--i2v`) ancla el video a un still fiel. Referencias de Fabián → prompt preciso + i2v. Tanda de 4 (piston_fuego/manavai/sismografo/pisagua) terminada | ✅ ver [[ltx-fast-vs-pro-y-hibrido-stills]], [[referencias-y-i2v-para-fidelidad]] |

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

1. **🔧 ARREGLAR LA FIDELIDAD VISUAL DEL PIPELINE (foco #1, valida crítica de audiencia).** Los
   comentarios del 2026-07-22 confirman que **los clips no ilustran lo narrado** (LTX t2v deriva de
   etnia/época/objeto/mecanismo). `manavai` y `pisagua` quedaron en pausa por esto. El flujo es barato
   pero la relación imagen↔narración es la falencia. Líneas a atacar (ver [[fidelidad-visual-ltx-etnia-epoca]],
   [[referencias-y-i2v-para-fidelidad]]): (a) **inclinar la balanza a still SDXL + i2v** (negativo real →
   controla etnia/época) y bajar el t2v puro, que es el que más deriva; (b) **reforzar el prompt** con
   etnia+época explícitas+negativos y **plano-explainer** que muestre el mecanismo (el benchmark de 8M lo
   pide); (c) **regen targeted** de los clips ofensivos, no del short entero. Definir esto ANTES de seguir
   grabando temas nuevos — no tiene sentido acumular shorts con el mismo defecto.
2. **(Fabián, cuando el pipeline mejore) Retomar `manavai` y `pisagua`** — guion y voz ya están; solo
   falta re-renderizar los clips con el flujo corregido. Título/hashtags/descripción en `artifacts/guiones.md`
   (secciones 11, 13). Activar el toggle de **"contenido alterado o sintético"** (divulgación de IA).
3. **(Fabián) Banco por grabar — NUEVA SERIE «Ingenios Olvidados» (9 guiones listos, #15-23):**
   escritos 2026-07-22 desde las **sugerencias de la IA de YouTube** (afines al algoritmo): mortero
   bizantino (clara huevo), cúpulas persas (acústica), katana+ceniza, azul maya, espejos venecianos,
   + 4 **reencuadrados** para esquivar saturación (hierro meteorítico → "cómo lo trabajaban sin fundir";
   piedra solar vikinga → "óptica de polarización", no magia; mercurio azteca → "ritual/inframundo", no
   morbo; arsénico papel chino → "conservación", no veneno). **Todos con CTA v2** (ver abajo). Descartados
   por criterio: humo herbal escita, puente levadizo, plancton polinesio. **Antes de grabar: chequear
   saturación** de cada uno en Shorts (esp. los reencuadrados). Grabar 1 cada 1-2 días (constancia).
   Banco previo: `agua_rapanui` (#14, 2ª Isla Pascua — **no pegar a manavai**), Q'eswachaka (falta guion),
   `moais` en pausa (saturado). Al grabar: **pausá 1-2s antes de repetir**; después el circuito híbrido.
   **⭐ FÓRMULA v2 (2026-07-22, fix de suscripción):** los datos muestran buena retención + like ~7% PERO
   **poca suscripción** → diagnóstico (Parte 3 del método, `docs/sistema_contenido.md` #2/#5/#7): el short se
   siente suelto y el CTA no daba razón para volver. Fix = **CTA que nombra la serie + adelanta el próximo
   short + pide suscripción** (convierte "short suelto" → "capítulo"). Molde en `artifacts/guiones.md`
   (sección "FÓRMULA v2"). Series: «Mecanismos de América» (LatAm) y «Ingenios Olvidados» (resto del mundo).
   Aplica del #15 en adelante; los 1-13 quedan con CTA viejo (no re-grabar). Ver [[formula-v2-cta-suscripcion]].
4. **Watchear métricas** de los publicados (13 con piston_fuego/sismografo). Los de 2026-07-21
   (quipus/lautaro/cruce_andes/chuno) siguen en ventana ruidosa de reeducación (no concluir de un short
   suelto). Métrica primaria = **% visto/retención** — el informe **"Rendimiento en las primeras 24h"**
   en **Modo Avanzado** da la tabla por video (**>100% = loopea, buscá eso**). Cargar en
   `docs/panel_datos.json` + regenerar panel. **Chequear saturación** antes del próximo tema.
   **Además: leer los comentarios** — ya dieron la señal más accionable (clips que no pegan).
5. **(Fabián) Branding de Vestigios:** foto de perfil (emblema de engranaje) + banner. Ocultar
   (unlisted) los videos viejos de música para limpiar la señal del canal.
6. **Deuda técnica** — en [`docs/AUDIT.md`](./docs/AUDIT.md): AUD-002 (generalizar el retimeo dentro de
   `armar_short.py`), AUD-003 (formalizar `ejecutor_ltx.py`/`generar_stills_kaggle` tras el `PuertoEjecutor`),
   AUD-004 (saldo LTX en el dashboard; la **tanda híbrida de 4 costó ~$2.7**, no ~$14 como en pro).
