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

## Próximo paso sugerido

**CASO-006 (IP-Adapter / imagen de referencia)** — el cierre real de H-1: fijar una imagen
de personaje y pasarla a todas las escenas para mantener identidad entre ellas. Alternativa:
correr un AnimateDiff completo (sin límite de 12s) sobre fuente real con `--prompts-llm`.
