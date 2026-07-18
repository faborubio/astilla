# COLAB — generación visual en GPU gratis (Fase 2 / CASO-003)

> Honestidad de costo (SAD H-2/H-3): Colab gratis = $0 en dinero, pero **efímero**
> y con cold start (instalar diffusers + bajar el modelo SD ~5 min por sesión).
> El default *recomendado* en el SAD es serverless; Colab es el adaptador "$0".

## Flujo de 2 fases (resumible, ADR-002)

```
LOCAL  ──(visual_job.json)──▶  COLAB (T4 GPU)  ──(escenas.zip)──▶  LOCAL
 transcribe + planifica          genera 1 img/escena               anima + ensambla
```

### 1. Local — preparar el job
```bash
python -m pipeline.animado --audio sources/mi_audio.wav \
    --autorizacion dominio_publico --evidencia "https://archive.org/..." \
    --estilo neon --semilla 1 --fin 40
```
Genera `artifacts/visual_job.json` (prompts + semilla por escena) y para,
indicándote el siguiente paso.

### 2. Colab — generar las imágenes
1. Abre `colab/astilla_render.ipynb` en Google Colab.
2. **Runtime → Cambiar tipo de entorno → GPU (T4)**.
3. Corre las celdas; sube `artifacts/visual_job.json` cuando lo pida.
4. Render por escena con **checkpoint**: si se desconecta, re-corre y retoma.
5. Baja `escenas.zip`.

### 3. Local — ensamblar el short animado
Descomprime `escenas.zip` en `artifacts/escenas/` (debe quedar
`artifacts/escenas/escena_00.png`, ...). Luego:
```bash
python -m pipeline.animado --audio sources/mi_audio.wav \
    --autorizacion dominio_publico --evidencia "https://archive.org/..." \
    --estilo neon --semilla 1 --fin 40 --ensamblar
```
Sale `artifacts/short_animado.mp4` (9:16, Ken Burns + subtítulos + divulgación IA).

## Probar sin Colab (movimiento + composición)
```bash
python -m pipeline.animado --stub-visual
```
Genera stand-ins deterministas (gradientes, **no IA**) y ensambla, para validar
el motor de animación localmente antes de gastar una sesión de Colab.

## Notas
- Modelo: SD 1.5 (`runwayml/stable-diffusion-v1-5`), 512×896, entra holgado en T4.
- `safety_checker=None` evita imágenes negras por falsos positivos NSFW.
- La coherencia entre escenas es **limitada** (riesgo H-1): SD por escena no
  garantiza el mismo personaje. Mejora futura: IP-Adapter / imagen de referencia.
