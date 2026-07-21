# TROUBLESHOOTING — ¿Qué falló y cómo se arregló?

> Registro de incidentes y gotchas de Astilla (MANIFIESTO §2: cada falla resuelta se anota acá;
> las graves, con su mini-postmortem). La numeración **G-1…G-13** conserva el orden histórico de
> los "gotchas" porque otros docs y las memorias los citan por número.
> Formato: **síntoma → causa → fix**.

---

## Gotchas numerados (G-1…G-13)

### G-1 · Kaggle: kernel ERROR con log vacío
- **Síntoma:** el kernel falla de inmediato, sin log.
- **Causa:** asignó una **P100** (CUDA sm_60), incompatible con el PyTorch de Kaggle (sm_70+).
- **Fix:** forzar `machine_shape: NvidiaTeslaT4` en el metadata del kernel.

### G-2 · Modelo SD1.5 retirado de Hugging Face
- **Síntoma:** `runwayml/stable-diffusion-v1-5` no descarga.
- **Fix:** usar el mirror `stable-diffusion-v1-5/stable-diffusion-v1-5`.

### G-3 · Token Kaggle nuevo `KGAT_` rompe el parser
- **Síntoma:** la CLI de Kaggle falla al leer credenciales.
- **Causa:** el token nuevo `KGAT_` NO va en `kaggle.json` (rompe el parser `{username,key}`).
- **Fix:** ponerlo en `~/.kaggle/access_token` o env `KAGGLE_API_TOKEN`. El legacy
  `kaggle.json` `{username,key}` es lo más probado.

### G-4 · ffmpeg zoompan: explosión de frames
- **Síntoma:** `-loop 1 -t` con `zoompan` multiplica frames (archivo gigante / cuelgue).
- **Fix:** input único + `-frames:v N`.

### G-5 · Estado de kernels Kaggle en background
- **Síntoma:** el stdout local no muestra el progreso (está bufferizado).
- **Fix:** consultar `kaggle kernels status <user>/<slug>` directo.

### G-6 · Derechos: reels de terceros
- **Regla:** rechazar reels de IG de terceros para publicación (gate ADR-009). Para prueba
  LOCAL no publicada se registró el uso honestamente. Fuentes limpias: dominio público
  (LibriVox/archive.org `language:spa`) o audio propio.

### G-7 · SadTalker en Kaggle (Python 3.12) = campo minado
- **Síntoma:** su `requirements.txt` no instala (pines viejos); errores de numpy y de imports.
- **Fix** (receta completa en `ejecutor_kaggle._KERNEL_TALKING`):
  instalar deps **sin pines** + `numpy<2`; **NO** usar `-r requirements.txt`. Parches al clon:
  (a) import del enhancer (`gfpgan`) opcional en `animate.py` — el dir local `gfpgan/` de pesos
  ensombrece al paquete; (b) aliases `np.float/int/bool` → tipos reales (removidos en numpy
  1.24); (c) `align_img`: `np.array([...,t[0],t[1]])` → `float(...)` (arrays inhomogéneos).
  Correr `inference.py` con `cwd=/tmp/SadTalker` (imports relativos) y clonar/checkpoints en
  `/tmp` (NO en `/kaggle/working`, si no el output pesa ~1GB).

### G-8 · `kaggle datasets create --dir-mode zip`
- **Síntoma:** `FileNotFoundError` en runtime (el dataset se monta distinto).
- **Fix:** subir sin `--dir-mode` (archivo suelto en `/kaggle/input/<slug>/`).

### G-9 · El ancla de personaje no debe arrastrar temas de escena
- **Síntoma:** con fuentes reales salen planos abiertos (figura lejana) y SadTalker falla:
  `can not detect the landmark from source image`.
- **Fix:** `prompt_personaje` fuerza primer plano de cara + negativo anti-plano-abierto
  (`ancla_negativo`). Verificado con audio real.

### G-10 · Race del dataset de audio en Kaggle
- **Síntoma:** narrator con la duración del audio VIEJO (el kernel agarró la versión anterior
  del wav, mismo nombre).
- **Fix:** dataset **content-addressed** (hash del wav en el slug) + poll
  `kaggle datasets status` hasta `ready` antes del push del kernel.

### G-11 · Checkpoint de transcript ciego — ✅ MUERTO (jul 2026)
- **Síntoma:** `pipeline.animado` reusaba `artifacts/segmentos.json` para CUALQUIER audio
  nuevo → planificaba escenas del guion anterior; dos shorts en paralelo colisionaban.
- **Fix definitivo:** refactor **folder-aware** (un short = una carpeta
  `artifacts/shorts/<n>/`, checkpoints propios de cada carpeta). Resto residual: si cambia el
  audio de un short, borrar a mano `shorts/<n>/segmentos.json` y `palabras.json`
  (ver AUD-005 en `AUDIT.md`).

### G-12 · Guion largo como `initial_prompt` rompe la transcripción por palabra
- **Síntoma:** con `word_timestamps=True`, pasar el guion entero (~130 palabras) dropea los
  primeros ~20s y alucina (decodifica hasta en inglés, "However").
- **Fix:** en `transcribir_palabras`: `initial_prompt=None` + `temperature=0`. El texto
  correcto se recupera **reconciliando** con el guion-verdad (`reconciliar_palabras.py`).

### G-13 · Cortes de escena desalineados del audio
- **Síntoma:** los boundaries de escena (derivados de segmentos) quedan corridos unos
  segundos respecto de lo que se dice.
- **Fix:** re-derivar cortes CONTINUOS desde `shorts/<n>/palabras.json` (1 corte por clip en
  límites de frase) y reconstruir el bed con `scripts/retimear_bed.py --cortes "a,b; b,c; …"`
  (los clips se re-ajustan con `setpts`, no se regeneran). Generalizarlo es AUD-002.

---

## Incidentes por área

### Transcripción · nivel-segmento truncaba o alucinaba (jul 2026)
- **Síntoma:** según el audio, `transcribir()` (a) TRUNCA a la mitad, o (b) alucina los
  primeros ~18s en una línea ("Princeton en el siglo diecinueve").
- **Causa:** guion entero como `initial_prompt` + `vad_filter=True` — el decoder "completa"
  el prompt y corta al primer silencio del VAD; sin vad, alucina el arranque.
- **Fix:** **ambos apagados** (`initial_prompt=None`, `vad_filter=False`) → cobertura total y
  sin alucinar. No pierde nada: el texto final sale del pase por-palabra reconciliado (G-12).

### Grabación · las repeticiones quedan en el wav
- **Síntoma:** si el narrador se traba y repite la frase, la repetición QUEDA en el audio —
  `limpiar_voz` limpia ruido/silencios pero NO borra repeticiones. Los 4 audios de la tanda
  jul 2026 las tenían.
- **Fix:** cortar a mano el wav: ubicar la repetición con transcripción por-palabra +
  `silencedetect`, empalmar en los silencios con
  `ffmpeg -af "aselect='not(between(t,A,B))',asetpts=N/SR/TB"`, re-correr
  armar+retimeo+música (los clips LTX se reusan, $0 extra).
- **Prevención:** al grabar, **pausar 1-2s en silencio antes de repetir la frase entera**
  (esa pausa deja el corte limpio). Anotado en el maestro `artifacts/guiones.md`.

### Grabación · el recorte de cola se come el CTA final
- **Síntoma:** `limpiar_voz` recorta la cola (silencio + click de detener grabación) y a
  veces se lleva el final del CTA.
- **Fix:** re-limpiar con `--sin-recorte-final` y recortar la cola a mano.

### Música · el master clippeaba a +0 dBTP
- **Síntoma:** sin master, el pico de la mezcla voz+música se va a +0 dBTP (clip audible).
- **Fix (mezcla validada):** `[musica]volume=0.12,afade in 1.2s,afade out 2.5s` +
  `amix normalize=0` + master `loudnorm=I=-16:TP=-1.5`. Atribuir a Kevin MacLeod (CC-BY).

### Windows · escape de `C:` en el filtro `ass=`
- **Síntoma:** ffmpeg no parsea la ruta absoluta de los subtítulos (`C:\…`) en `ass=`.
- **Fix:** usar **ruta relativa** (`shorts/<n>/subs.ass`) corriendo desde `artifacts/`.

### Luma (paso manual, proveedor legado)
- El **aspect ratio es setting del UI**, NO del prompt: pedir 9:16 en el texto no sirve
  (salen 16:9).
- Prompts en plural ("close-up **shots**") producen artefacto de **tríptico** (costura
  vertical) → usar "a single continuous shot".
- Plan Plus = consumidor, **sin API** → no automatizable tras el `PuertoEjecutor` (hoy lo
  cubre LTX; ver `IDEAS.md`).
- Flujo recomendado: **imagen primero** (Photon, iterar barato) → luego image-to-video.
