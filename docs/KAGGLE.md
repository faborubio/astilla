# KAGGLE — generación visual con despacho automático (PuertoEjecutor)

> A diferencia de Colab, Kaggle tiene **API** (`kaggle` CLI), así que el orquestador
> local despacha el job, hace polling y baja los artefactos **sin handoff manual**.
> Realiza el diagrama del SAD `local orquesta → remoto genera → recupera artefactos`.

## Setup de credenciales (una vez)

1. Kaggle → **Settings → API → Create Legacy API Key** → descarga `kaggle.json`
   (formato `{"username","key"}`; el token nuevo `KGAT_` va por `~/.kaggle/access_token`
   o env `KAGGLE_API_TOKEN`, pero el legacy es el más probado con el CLI).
2. Colócalo en `C:\Users\Fabian\.kaggle\kaggle.json`.
3. Requisito de Kaggle: **cuenta verificada por teléfono** (habilita API, GPU e internet).
4. `pip install kaggle` (ya en `requirements.txt`).

> 🔒 `kaggle.json` / `access_token` están en `.gitignore`. Nunca al repo, nunca al chat.

## Uso (un comando)

```bash
python -m pipeline.animado --kaggle --estilo neon --semilla 1
# o con tu audio:
python -m pipeline.animado --audio sources/x.wav --autorizacion dominio_publico \
    --evidencia "URL" --kaggle --fin 40
```

El flujo: transcribe → planifica escenas → **despacha kernel headless a Kaggle (GPU T4)**
→ polling del estado → baja `escena_*.png` a `artifacts/escenas/` → ensambla
`short_animado.mp4` (Ken Burns + subtítulos + divulgación). Todo automático.

## Modos de movimiento: `--motion`

| Modo | Qué genera Kaggle | Ensamblado local | Costo/tiempo |
|------|-------------------|------------------|--------------|
| `kenburns` (default) | 1 imagen SD por escena (`escena_XX.png`) | Ken Burns (zoom sobre still) | rápido (~seg/escena) |
| `animatediff` | 1 **clip animado** por escena (`escena_XX.mp4`, AnimateDiff) | loop + concat de clips | lento (~min/escena) + descarga mayor |

```bash
# Movimiento real generado (AnimateDiff en T4)
python -m pipeline.animado --audio sources/x.wav --autorizacion dominio_publico \
    --evidencia "URL" --motion animatediff --kaggle
```

- **AnimateDiff** = SD 1.5 + motion adapter gratuito (`guoyww/animatediff-motion-adapter-v1-5-2`).
  Corre en T4 con `enable_model_cpu_offload()` + `enable_vae_slicing()`; 16 frames @ 512×768.
- El clip dura ~2 s; el ensamblador lo **loopea** para cubrir la duración de la escena.
- `--stub-visual` no aplica a `animatediff` (no hay stub de clips); usá `--kaggle`.
- Coherencia entre escenas (H-1) **sigue abierta**: AnimateDiff anima cada escena por
  separado. La ancla de estilo + prompts de Claude ayudan; identidad exacta = IP-Adapter.

## Hallazgo crítico: P100 vs T4 (compatibilidad CUDA)

La GPU **P100 es CUDA capability sm_60**, y el PyTorch que Kaggle trae hoy **solo
soporta sm_70+**. Resultado: `torch.cuda.is_available()` da `True` pero el modelo
de difusión **falla al ejecutar** (`KernelWorkerStatus.ERROR`, sin log útil).

**Fix:** forzar T4 (sm_75) con `"machine_shape": "NvidiaTeslaT4"` en el
`kernel-metadata.json` (lo hace el adaptador automáticamente). Valores válidos:
`NvidiaTeslaT4`, `NvidiaTeslaP100`.

## Otros gotchas resueltos
- **Token nuevo `KGAT_`** no va en `kaggle.json` (rompe el parser); va en
  `~/.kaggle/access_token` o env `KAGGLE_API_TOKEN`. El CLI ≥2.x lo soporta.
- **`runwayml/stable-diffusion-v1-5`** fue retirado de HF (2024); usar el mirror
  `stable-diffusion-v1-5/stable-diffusion-v1-5`.
- **Determinismo (H-3):** P100 ≠ T4 → misma semilla, distinta imagen. Fijar una
  plataforma/GPU para reproducibilidad.

## Diagnóstico
Si un kernel falla, baja su log:
```bash
kaggle kernels output <usuario>/<slug> -p ./klog --force   # incluye <slug>.log
```
Un log de **0 bytes** ⇒ fallo de infraestructura temprano (GPU/internet/imagen),
no una excepción de Python.
