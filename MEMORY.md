# MEMORY.md — Bitácora de Astilla

> Registro cronológico de decisiones y avances. El estado actual y el "cómo correr"
> viven en [`CLAUDE.md`](./CLAUDE.md); los casos demostrables en [`docs/CASES.md`](./docs/CASES.md).

## 2026-06-29 — Del SAD a un short animado real

Punto de partida: solo existía `SAD_Astilla_repurposing.md` (arquitectura arc42, sin código).

### Sesión 1 — fundación y Fase 1
- **SAD §11.b "Revisión de halcón":** crítica de diseño con 8 hallazgos (H-1…H-8).
  Los grandes: H-1 coherencia visual mal calificada como riesgo medio (es el #1);
  H-2 GPU efímera gratis = cerro autoimpuesto (serverless/API por default);
  H-3 determinismo ⟂ hardware efímero; H-5 falta gate de QC humano; H-6 sacar TTS del MVP.
- **Fase 1 (CASO-001/002):** `pipeline/` con dominio stdlib-only + infra detrás de puertos.
  Gate de derechos → faster-whisper → subtítulos ASS → ensamblado ffmpeg 9:16 + divulgación.
  Genera `short.mp4` 1080×1920 real. Fuente de demo = TTS System.Speech de Windows (ORIGINAL).
  Tests del gate en `tests/test_derechos.py`.

### Sesión 1 (cont.) — Fase 2 animada + Kaggle
- **CASO-003:** `pipeline/animado.py` — planifica escenas desde el transcript, exporta
  `visual_job.json`, anima con Ken Burns sobre stills. Flujo de 2 fases resumible (ADR-002).
  Notebook de Colab + `docs/COLAB.md`. Bug corregido: zoompan multiplica frames.
- **Decisión del usuario:** GPU = **Kaggle gratis** (no serverless). GPU local (GTX 1050,
  3GB) es inviable para difusión — confirma H-2.
- **CASO-003b:** adaptador `ejecutor_kaggle.py` (PuertoEjecutor) — despacha kernel headless
  por API, polling, baja imágenes, ensambla. **Un comando.** Generó short con visual SD
  neón synthwave real. Gotchas resueltos: token `KGAT_` vs legacy; `runwayml/...` retirado
  de HF; **P100 sm_60 incompatible con PyTorch de Kaggle → forzar T4** (era el ERROR con
  log vacío, aislado con un kernel diagnóstico). Ver `docs/KAGGLE.md`.

### Sesión 1 (cont.) — calidad: transcript + coherencia
- **CASO-004:** (#2a) `--modelo medium` mejora notablemente la transcripción de audio real
  ruidoso vs `small` (verificado en un reel). (#1) "ancla de estilo" global en cada escena
  para coherencia sin LLM. (#2b) `prompts_claude.py` = adaptador Claude (`claude-opus-4-8`,
  structured outputs, adaptive thinking) que genera biblia de estilo + prompts coherentes;
  flag `--prompts-llm`, requiere `ANTHROPIC_API_KEY`, fallback automático al heurístico.

### Sesión 1 (cont.) — animación real
- **CASO-005:** flag `--motion {kenburns,animatediff}`. AnimateDiff (SD1.5 + motion adapter
  gratuito) en T4 genera **clips `.mp4` reales** (512×768, 16 frames/2s) por escena;
  `EnsambladorClips` loopea+concatena. Verificado: `short_animado.mp4` 1080×1920 con
  movimiento generado real. Detrás del mismo PuertoEjecutor: solo cambian kernel y ensamblador.

## Sobre derechos (postura del proyecto)

El gate (ADR-009) rechaza contenido de terceros para **publicación**. Para pruebas LOCALES
no publicadas, la decisión es humana (§3.3) y se registra honestamente en el rastro. Fuentes
limpias para testear: dominio público (LibriVox/archive.org `language:spa`) o audio propio.
No procesar reels de IG de terceros para publicar.

> ⚠️ La bitácora cronológica detallada de jul 2026 en adelante vive en las **memorias de sesión**
> (`.claude/.../memory/`, indexadas en su propio `MEMORY.md`), no acá. Este archivo guarda solo los
> hitos gruesos. Estado siempre actualizado en [`CLAUDE.md`](./CLAUDE.md).

## 2026-07-22/23 — Salto de calidad visual: pivot a ChatGPT + gates de calidad

El canal (VESTIGIOS) llegó a **14 publicados**; el mortero bizantino
(youtube.com/shorts/hm-JIzAQM_4) fue el primero de la serie «Ingenios Olvidados» con el pipeline
de calidad completo, y `piedra_solar` quedó lista para subir. Tres cambios grandes esta tanda:

1. **Generador de stills: SDXL → ChatGPT (GPT-image).** Tras la crítica pública ("ilustraciones
   deformes / algunas sin sentido") y 3-4 rondas fallidas regenerando en SDXL, generar en ChatGPT
   resolvió a la primera los 3 puntos ciegos (manos, caras, líquidos, escenas que ignoran el prompt).
   Look fijo = óleo pictórico. Flujo human-in-the-loop: Claude prepara kit de prompts en español
   (`shorts/<n>/prompts_chatgpt.md`), Fabián genera y revisa, Claude mapea por contenido. SDXL/Kaggle
   queda de respaldo. Es la decisión de "calidad sobre automatización total".

2. **Dos gates de calidad nuevos, reglas duras:** (a) **gate de revisión de stills** — Fabián revisa
   frame a frame antes de armar, Claude hace segunda pasada, comparan; (b) **gate de fuentes** — cada
   guion lleva línea `Fuente:` verificada antes de grabar (destapó que el dato del huevo del mortero,
   la ceniza de la katana y el arsénico del papel eran mitos virales de la pestaña Inspiración de
   YouTube; se reencuadraron con el mecanismo real).

3. **Fórmula v3 + banco verificado 16-33 en cola** (~1 mes de contenido) en el único `guiones.md`:
   hook-misterio, sin tríada, cierre-loop, voz propia, ~150-175 palabras + "pastilla la próxima"
   (tease separado) + guiño visual del próximo short en la última escena. Series «Ingenios Olvidados»
   (mundo) y «Mecanismos de América».

**Gotcha caro (G-16, arreglado):** `generar_ltx.py --i2v X` sin `--video` pagaba t2v ciego (~$4
quemados). Default corregido + regla: confirmar costo antes de gastar LTX (saldo ~$1). El pipeline
de imagen ya casi no usa LTX (Ken Burns local $0 + i2v solo en money shots puntuales).

## 2026-07-24 — mercurio armado con 3 i2v bajo la regla de $1 + mudanza a WSL

`mercurio_tumba` (#22) quedó **terminado y aprobado** (`short_musica.mp4`, 81.8s): 11 stills ChatGPT
en Ken Burns + 3 money shots i2v (hook túnel / charco espejo / cielo estrellado) replicando el
reparto de katana (6+4+6s = $0.96). Guiño de cierre = rollo chino → `papel` (#23).

Tres cosas nuevas de la sesión:
1. **Regla dura de presupuesto: máx $1 de LTX por short, SIEMPRE** (Fabián recargó $5 → saldo ~$4.04;
   debe rendir ~4-5 shorts más).
2. **Entorno: de Windows/PowerShell a WSL (Linux).** Venv del repo (`.venv/bin/python`), key LTX en
   `~/.ltx/api_key` (expiró justo hoy y se regeneró — un 401 súbito = sospechar key vencida).
3. **Rescate palíndromo ($0):** el i2v del cielo estrellado se arruinaba a los ~3s (drift al techo →
   bokeh). Se recortó el tramo limpio y se armó ida-vuelta con ffmpeg (trim+reverse+concat) en vez de
   regenerar. En escenas de titileo/llama la reversa es invisible. Candidato a formalizar en script.
