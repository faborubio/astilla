# CLAUDE.md — Hub de contexto de Astilla

> Léeme primero. Soy el punto de entrada para retomar el proyecto en una sesión nueva.
> Fuente de verdad de arquitectura: [`SAD_Astilla_repurposing.md`](./SAD_Astilla_repurposing.md)
> (en especial **§11.b "Revisión de halcón"** — la crítica de diseño H-1…H-8).
> Bitácora cronológica: [`MEMORY.md`](./MEMORY.md) · Casos demostrables: [`docs/CASES.md`](./docs/CASES.md)
> Deuda aceptada: [`docs/AUDIT.md`](./docs/AUDIT.md) · Incidentes/gotchas: [`docs/TROUBLESHOOTING.md`](./docs/TROUBLESHOOTING.md) · Parking lot: [`IDEAS.md`](./IDEAS.md)
> Estado de producción (abrir con file://): [`docs/panel_produccion.html`](./docs/panel_produccion.html) · regenerar con `python scripts/generar_panel.py`
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

## ⏭️ Estado (2026-07-21)

**Estado:** 🎉 **10 SHORTS PUBLICADOS**. El motor produce shorts end-to-end por ~$3-4 c/u (LTX
**pro**). Publicados: Anticitera v2 (**youtube.com/shorts/caRNsgvRorc**), telégrafo
(**youtube.com/shorts/YWyjv3tG4SA**), pelo/catapultas (**youtube.com/shorts/xQJHJD4XJFI**), arquero,
trepanacion, cerebro_vidrio, hormigon + **la tanda nueva quipus / lautaro / cruce_andes** (recién
subidos 2026-07-21; sin métricas todavía). **No hay tanda terminada sin publicar.**

**⛔ SALDO LTX AGOTADO (2026-07-21, ~$0.65):** la tanda de 4 gastó ~$14.88 y el saldo se acabó a mitad
de **chuno**, que quedó **bloqueado en 3/9 clips** (los 3 guardados). Se completa SOLO con los 6 que
faltan cuando se recargue: `python scripts/generar_ltx.py --nombre chuno --indices 3,4,5,6,7,8 --auto
--pro` (~$2.6) → luego armar_short + música. Estado visible en el **panel** `docs/panel_produccion.html`.

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
`palabras.json`, `subs.ass`, `bed.mp4`, `clips/escena_NN.mp4`, `short.mp4`, `short_musica.mp4`.
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
   explainer tipo diagrama Da Vinci en la escena larga). Inyectarlos en `visual_job.json` (o re-correr
   animado con `--prompts-file`) los hornea.
5. `python scripts/generar_ltx.py --nombre <n> --indices todas --auto --pro` → clips en
   `shorts/<n>/clips/` (~$3-4 según duración del audio; cap 10s/clip; **el costo lo fija la duración
   del audio, no la cantidad de escenas**).
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
# 4) clips LTX -> shorts/<n>/clips/   (~$3-4)
python scripts/generar_ltx.py --nombre <n> --indices todas --auto --pro
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

1. **(Fabián) RECARGAR SALDO LTX** — destraba DOS cosas de una: (a) **completar chuno**
   (`generar_ltx.py --nombre chuno --indices 3,4,5,6,7,8 --auto --pro` → armar_short + música), y
   (b) **refinar los clips de etnia/época equivocada** (regen targeted, [[fidelidad-visual-ltx-etnia-epoca]]).
   Ambas están bloqueadas por saldo ($0.65). Ver panel `docs/panel_produccion.html`.
2. **(Fabián) GRABAR lo que queda del banco:** `manavai` (mecanismo Isla de Pascua, guion listo) →
   `pisagua` (último y controlado por flame, §2). `quipus`/`lautaro`/`cruce_andes` **ya publicados**;
   `moais` en pausa (saturado). Guiones (título + hashtags + **descripción** + texto) en el maestro
   `artifacts/guiones.md`; leé de ahí. Al grabar, si te trabás **pausá 1-2s antes de repetir**. Después:
   pipeline folder-aware (§Estado → circuito, arranca por `exportar_guion.py`).
3. **Watchear métricas** de los 10 publicados, sobre todo los **3 nuevos** (quipus/lautaro/cruce_andes,
   subidos 2026-07-21 → 2-3 sem de datos ruidosos por la reeducación del algoritmo, no sacar conclusiones
   de un short suelto). Métrica primaria = **% visto/retención**. Cargar los números en `docs/panel_datos.json`
   y regenerar el panel. Antes del próximo tema, **chequear saturación** (lección hormigón, §7). Gap de
   **0 comentarios**: esta tanda estrenó **comentario-semilla fijado + descripción** para atacarlo.
4. **(Fabián) Branding de Vestigios:** foto de perfil (emblema de engranaje) + banner. Ocultar
   (unlisted) los videos viejos de música para limpiar la señal del canal.
5. **Deuda técnica** — ahora numerada en [`docs/AUDIT.md`](./docs/AUDIT.md): AUD-002 (generalizar
   el retimeo dentro de `armar_short.py`), AUD-003 (formalizar `ejecutor_ltx.py` tras el
   `PuertoEjecutor`), AUD-004 (revisar saldo LTX en el dashboard; la tanda de 4 costó ~$14 pro).
