"""Adaptador Kaggle del PuertoEjecutor (SAD H-2): despacho headless por API.

Realiza el diagrama del SAD `local orquesta -> remoto genera -> recupera artefactos`
de forma automatica (lo que Colab no permite): genera un kernel script con el job
embebido, lo sube y corre con GPU, hace polling del estado y baja las imagenes.

Resiliencia (ADR-002): el kernel saltea escenas cuya imagen ya exista en su working.
Determinismo (H-3): el resultado depende de la GPU de Kaggle (P100); no comparable
pixel a pixel con otra plataforma. Quedarse en una sola.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

# Plantilla del kernel de IMAGEN (1 PNG por escena, stills -> Ken Burns local).
_KERNEL_IMAGEN = '''\
import os, json, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "diffusers", "transformers", "accelerate"], check=True)
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

JOB = json.loads(r"""{job_json}""")
g = JOB["generacion"]
out_dir = "/kaggle/working"
os.makedirs(out_dir, exist_ok=True)
print("job", JOB["job_id"], "| escenas:", len(JOB["escenas"]), "| estilo:", JOB["estilo"])

pipe = StableDiffusionPipeline.from_pretrained(
    g["modelo"], torch_dtype=torch.float16, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("cuda")

for esc in JOB["escenas"]:
    dst = os.path.join(out_dir, esc["archivo"])
    if os.path.exists(dst):
        print("checkpoint, salto", esc["archivo"]); continue
    gen = torch.Generator("cuda").manual_seed(int(esc["semilla"]))
    img = pipe(esc["prompt"], negative_prompt=JOB["negativo"],
               width=g["width"], height=g["height"],
               num_inference_steps=g["steps"], guidance_scale=g["guidance"],
               generator=gen).images[0]
    img.save(dst)
    print("ok", esc["archivo"], "::", esc["prompt"][:60])
print("LISTO: todas las escenas generadas")
'''


# Plantilla del kernel de ANIMACION real (1 clip mp4 por escena, AnimateDiff).
# AnimateDiff = SD 1.5 + motion adapter gratuito; corre en T4 con cpu-offload + vae slicing.
# Coherencia de personaje (CASO-006, H-1): si JOB["coherencia"].ip_adapter, el kernel
# genera UN retrato-ancla del personaje (semilla fija) y lo aplica con IP-Adapter a
# cada escena -> misma identidad en todo el short, sin entrenar nada. Resumible: si
# ancla.png ya existe en el working, lo reusa (ADR-002).
_KERNEL_ANIMATEDIFF = '''\
import os, json, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "diffusers", "transformers", "accelerate",
                "imageio", "imageio-ffmpeg"], check=True)
import torch
from diffusers import (AnimateDiffPipeline, MotionAdapter, DDIMScheduler,
                       StableDiffusionPipeline)
from diffusers.utils import export_to_video
from PIL import Image

JOB = json.loads(r"""{job_json}""")
g = JOB["generacion"]
base = g["modelo"]
coh = JOB.get("coherencia") or {{}}
usar_ip = bool(coh.get("ip_adapter"))
out_dir = "/kaggle/working"
os.makedirs(out_dir, exist_ok=True)
W, H, FRAMES, FPS, STEPS = 512, 768, 16, 8, 25
print("animatediff", JOB["job_id"], "| escenas:", len(JOB["escenas"]), "| ip_adapter:", usar_ip)

# --- 1) Retrato-ancla del personaje (coherencia H-1, solo si ip_adapter) ---------
ancla_img = None
if usar_ip:
    ancla_path = os.path.join(out_dir, "ancla.png")
    if os.path.exists(ancla_path):
        print("checkpoint, reuso ancla.png")
    else:
        sd = StableDiffusionPipeline.from_pretrained(
            base, torch_dtype=torch.float16, safety_checker=None).to("cuda")
        gen = torch.Generator("cuda").manual_seed(int(coh["ancla_semilla"]))
        retrato = sd(coh["ancla_prompt"], negative_prompt=JOB["negativo"],
                     width=512, height=512, num_inference_steps=30, guidance_scale=7.5,
                     generator=gen).images[0]
        retrato.save(ancla_path)
        print("ok ancla.png ::", coh["ancla_prompt"][:60])
        del sd; torch.cuda.empty_cache()
    ancla_img = Image.open(ancla_path).convert("RGB")

# --- 2) AnimateDiff (+ IP-Adapter para fijar la identidad) -----------------------
adapter = MotionAdapter.from_pretrained(
    "guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)
pipe = AnimateDiffPipeline.from_pretrained(base, motion_adapter=adapter, torch_dtype=torch.float16)
pipe.scheduler = DDIMScheduler.from_pretrained(
    base, subfolder="scheduler", clip_sample=False,
    beta_schedule="linear", timestep_spacing="linspace", steps_offset=1)
if usar_ip:
    # IP-Adapter "plus" (SD1.5): transferencia fuerte del sujeto desde la imagen ancla.
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models",
                         weight_name="ip-adapter-plus_sd15.bin")
    pipe.set_ip_adapter_scale(float(coh.get("ip_scale", 0.6)))
pipe.enable_vae_slicing()
pipe.enable_model_cpu_offload()  # ajusta a la VRAM de la T4 (no usar .to('cuda') con esto)

for esc in JOB["escenas"]:
    dst = os.path.join(out_dir, esc["archivo"])  # escena_XX.mp4
    if os.path.exists(dst):
        print("checkpoint, salto", esc["archivo"]); continue
    gen = torch.Generator("cpu").manual_seed(int(esc["semilla"]))
    kw = dict(prompt=esc["prompt"], negative_prompt=JOB["negativo"],
              num_frames=FRAMES, height=H, width=W,
              guidance_scale=7.5, num_inference_steps=STEPS, generator=gen)
    if usar_ip:
        kw["ip_adapter_image"] = ancla_img  # misma cara en cada escena
    out = pipe(**kw)
    export_to_video(out.frames[0], dst, fps=FPS)
    print("ok", esc["archivo"], "::", esc["prompt"][:60])
print("LISTO: clips animados generados")
'''

# Plantilla del kernel SDXL (1 PNG por escena-still -> Ken Burns local, hibrido --video).
# SDXL base 1.0 entra comodo en la T4 (fp16, ~7GB); estable y rapido (~15-25s/img).
# Ventaja clave para la fidelidad de etnia/epoca: negative_prompt REAL (a diferencia de
# LTX y de FLUX-schnell) -> se empuja "european/caucasian face, modern clothing" al negativo.
# Los PNG se nombran still_NN.png: el flag --video de generar_ltx.py los busca ahi.
_KERNEL_SDXL = '''\
import os, json, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U",
                "diffusers", "transformers", "accelerate", "safetensors"], check=True)
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

JOB = json.loads(r"""{job_json}""")
g = JOB["generacion"]
out_dir = "/kaggle/working"
os.makedirs(out_dir, exist_ok=True)
print("sdxl", JOB["job_id"], "| escenas:", len(JOB["escenas"]), "| neg:", JOB["negativo"][:60])

pipe = StableDiffusionXLPipeline.from_pretrained(
    g["modelo"], torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_vae_slicing()
pipe = pipe.to("cuda")

for esc in JOB["escenas"]:
    dst = os.path.join(out_dir, esc["archivo"])
    if os.path.exists(dst):
        print("checkpoint, salto", esc["archivo"]); continue
    gen = torch.Generator("cuda").manual_seed(int(esc["semilla"]))
    img = pipe(esc["prompt"], negative_prompt=JOB["negativo"],
               width=g["width"], height=g["height"],
               num_inference_steps=g["steps"], guidance_scale=g["guidance"],
               generator=gen).images[0]
    img.save(dst)
    print("ok", esc["archivo"], "::", esc["prompt"][:60])
print("LISTO: stills SDXL generados")
'''


_TEMPLATES = {"imagen": _KERNEL_IMAGEN, "animatediff": _KERNEL_ANIMATEDIFF, "sdxl": _KERNEL_SDXL}
_PATRON = {"animatediff": "escena_*.mp4", "imagen": "escena_*.png", "sdxl": "still_*.png"}


def _slug(texto: str) -> str:
    s = re.sub(r"[^a-z0-9-]", "-", texto.lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:45] or "astilla-render"


def _usuario_kaggle() -> str:
    p = Path.home() / ".kaggle" / "kaggle.json"
    return json.loads(p.read_text(encoding="utf-8"))["username"]


def _push_y_esperar(kid: str, dir_kernel: Path, timeout_s: int, intervalo_s: int) -> None:
    """Sube el kernel, dispara la GPU y hace polling hasta complete/error/timeout."""
    print(f"[kaggle] despachando kernel {kid} (GPU)...")
    r = subprocess.run(
        ["kaggle", "kernels", "push", "-p", str(dir_kernel)], capture_output=True, text=True
    )
    print("[kaggle]", r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        raise RuntimeError(f"push fallo: {r.stderr.strip()}")
    t0 = time.time()
    while True:
        s = subprocess.run(
            ["kaggle", "kernels", "status", kid], capture_output=True, text=True
        )
        estado = (s.stdout + s.stderr).lower()
        if "complete" in estado:
            print("[kaggle] estado: complete"); return
        if "error" in estado:
            raise RuntimeError(f"kernel con error: {s.stdout.strip() or s.stderr.strip()}")
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"timeout tras {timeout_s}s esperando el kernel")
        print(f"[kaggle] ... {s.stdout.strip() or 'queued/running'} ({int(time.time()-t0)}s)")
        time.sleep(intervalo_s)


def _bajar_output(kid: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    o = subprocess.run(
        ["kaggle", "kernels", "output", kid, "-p", str(dest), "--force"],
        capture_output=True, text=True,
    )
    print("[kaggle]", o.stdout.strip() or o.stderr.strip())


def generar_en_kaggle(
    visual_job: Path,
    escenas_dir: Path,
    dir_kernel: Path,
    motion: str = "imagen",
    timeout_s: int = 2400,
    intervalo_s: int = 25,
) -> None:
    job = json.loads(visual_job.read_text(encoding="utf-8"))
    plantilla = _TEMPLATES.get(motion, _KERNEL_IMAGEN)
    usuario = _usuario_kaggle()
    slug = _slug(f"astilla-{motion}-{job['job_id']}")
    kid = f"{usuario}/{slug}"
    patron = _PATRON.get(motion, "escena_*.png")

    # 1) Armar el kernel (script + metadata) con el job embebido.
    dir_kernel.mkdir(parents=True, exist_ok=True)
    (dir_kernel / "astilla_kernel.py").write_text(
        plantilla.format(job_json=json.dumps(job)), encoding="utf-8"
    )
    (dir_kernel / "kernel-metadata.json").write_text(
        json.dumps(
            {
                "id": kid,
                "title": slug,
                "code_file": "astilla_kernel.py",
                "language": "python",
                "kernel_type": "script",
                "is_private": True,
                "enable_gpu": True,
                # T4 (sm_75): la P100 (sm_60) NO es compatible con el PyTorch
                # actual de Kaggle (solo sm_70+). Forzar T4 evita el CUDA error.
                "machine_shape": "NvidiaTeslaT4",
                "enable_internet": True,
                "dataset_sources": [],
                "competition_sources": [],
                "kernel_sources": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # 2-3) Push + polling hasta complete.
    _push_y_esperar(kid, dir_kernel, timeout_s, intervalo_s)

    # 4) Bajar artefactos (las imagenes de escena) a escenas_dir.
    _bajar_output(kid, escenas_dir)
    artefactos = sorted(escenas_dir.glob(patron))
    print(f"[kaggle] artefactos recuperados ({patron}): {len(artefactos)}")
    if not artefactos:
        raise RuntimeError("el kernel completo pero no se bajaron artefactos de escena")


# --------------------------------------------------------------------------- #
# CASO-009: talking-head audio-driven (SadTalker). Capa de personaje.          #
# --------------------------------------------------------------------------- #
# El retrato-ancla "habla" con el audio original -> cabeza+cara+labios sync.
# v0 de validacion (riesgo: SadTalker espera caras realistas; sobre ilustracion
# puede no detectar la cara). Plan B si pelea: Wav2Lip (solo labios).
_KERNEL_TALKING = '''\
import os, json, subprocess, sys, glob, shutil, traceback
out_dir = "/kaggle/working"
os.makedirs(out_dir, exist_ok=True)

# Captura de errores propia: Kaggle a veces devuelve log vacio en kernels script con
# error -> escribimos progreso y traceback a archivos del working para NO quedar ciegos.
def log(msg):
    print(msg, flush=True)
    with open(os.path.join(out_dir, "run.log"), "a") as f:
        f.write(str(msg) + "\\n")

def pip(pkgs):
    log("pip install: " + " ".join(pkgs))
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + pkgs,
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("PIP FALLO:\\n" + (r.stdout[-1500:] + r.stderr[-1500:]))
        raise RuntimeError("pip install fallo: " + " ".join(pkgs))

try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "diffusers", "transformers", "accelerate"], check=True)
    import torch
    from diffusers import StableDiffusionPipeline

    JOB = json.loads(r"""{job_json}""")
    g = JOB["generacion"]
    coh = JOB["coherencia"]
    audio = JOB["audio_path"]          # /kaggle/input/<dataset>/recorte.wav
    if not os.path.exists(audio):      # fallback robusto si Kaggle monta otra ruta
        cand = glob.glob("/kaggle/input/**/recorte.wav", recursive=True)
        if cand:
            audio = cand[0]
    _sz = os.path.getsize(audio) if os.path.exists(audio) else -1
    log("talking-head " + JOB["job_id"] + " | audio: " + audio + " | bytes: " + str(_sz))

    # 1) Retrato-ancla del personaje (cara frontal para que SadTalker la detecte).
    ancla_path = os.path.join(out_dir, "ancla.png")
    if not os.path.exists(ancla_path):
        sd = StableDiffusionPipeline.from_pretrained(
            g["modelo"], torch_dtype=torch.float16, safety_checker=None).to("cuda")
        gen = torch.Generator("cuda").manual_seed(int(coh["ancla_semilla"]))
        neg = coh.get("ancla_negativo") or JOB["negativo"]
        img = sd(coh["ancla_prompt"], negative_prompt=neg,
                 width=512, height=512, num_inference_steps=30, guidance_scale=7.5,
                 generator=gen).images[0]
        img.save(ancla_path)
        del sd; torch.cuda.empty_cache()
    log("ok ancla.png")

    # 2) SadTalker: audio + retrato -> cabeza hablando (audio-driven).
    # Repo + checkpoints (~1GB) van a /tmp, FUERA de /kaggle/working: asi el output
    # del kernel queda chico (solo narrator.mp4 + logs) -> descargas instantaneas.
    ST = "/tmp/SadTalker"
    if not os.path.isdir(ST):
        subprocess.run(["git", "clone", "-q",
                        "https://github.com/OpenTalker/SadTalker", ST], check=True)
    # animate.py importa el enhancer (gfpgan/basicsr) a nivel de modulo aunque no se use,
    # y el dir local gfpgan/ (pesos que baja download_models.sh) ensombrece al paquete.
    # Como NO usamos enhancer, hacemos ese import opcional -> evita todo el pozo
    # basicsr/functional_tensor sin perder nada de la ruta core.
    _ap = os.path.join(ST, "src/facerender/animate.py")
    _s = open(_ap).read()
    _s = _s.replace(
        "from src.utils.face_enhancer import enhancer_generator_with_len, enhancer_list",
        "try:\\n    from src.utils.face_enhancer import enhancer_generator_with_len, enhancer_list\\nexcept Exception:\\n    enhancer_generator_with_len = enhancer_list = None")
    open(_ap, "w").write(_s)
    log("patch: import del enhancer hecho opcional")

    # SadTalker usa aliases de numpy removidos en 1.24+ (np.float/int/bool). Los
    # reemplazamos en su codigo por los tipos reales (fix que el propio numpy marca
    # como seguro). \\b evita tocar np.float32/np.int64 ya correctos.
    import re as _re
    for _root, _, _files in os.walk(os.path.join(ST, "src")):
        for _fn in _files:
            if _fn.endswith(".py"):
                _fp = os.path.join(_root, _fn)
                _t = open(_fp).read()
                _u = _re.sub(r"np\\.float\\b", "np.float64", _t)
                _u = _re.sub(r"np\\.int\\b", "np.int64", _u)
                _u = _re.sub(r"np\\.bool\\b", "np.bool_", _u)
                _u = _re.sub(r"np\\.object\\b", "object", _u)
                if _u != _t:
                    open(_fp, "w").write(_u)
    log("patch: aliases np.float/int/bool actualizados")

    # numpy 1.24+ ya no crea arrays de listas inhomogeneas (escalar + sub-array).
    # En align_img, t[0]/t[1]/s pueden venir como arrays de 1 elem -> forzamos escalar.
    _pp = os.path.join(ST, "src/face3d/util/preprocess.py")
    _p = open(_pp).read()
    _p = _p.replace(
        "trans_params = np.array([w0, h0, s, t[0], t[1]])",
        "trans_params = np.array([w0, h0, float(s), float(t[0]), float(t[1])])")
    open(_pp, "w").write(_p)
    log("patch: align_img trans_params a escalares")
    log("instalando deps de SadTalker (curado, sin pines rotos ni enhancer)...")
    # Kaggle = Python 3.12: los pines de requirements.txt (numpy==1.23.4, scikit-image
    # ==0.19.3...) no compilan. Instalamos sin pines y SIN el stack del enhancer
    # (basicsr/gfpgan/gradio, que no usamos). facexlib SI: lo usa el cropper (ruta core).
    # numpy<2: el codigo de SadTalker usa np.VisibleDeprecationWarning / np.float (1.x);
    # numpy 2.0 los removio. 1.26.4 tiene wheels para 3.12 y conserva esa API.
    pip(["numpy<2", "face_alignment", "imageio", "imageio-ffmpeg", "librosa", "numba",
         "resampy", "pydub", "scipy", "kornia", "tqdm", "yacs", "pyyaml", "joblib",
         "scikit-image", "facexlib", "av", "safetensors"])
    log("descargando checkpoints...")
    subprocess.run(["bash", "scripts/download_models.sh"], cwd=ST, check=True)
    res = os.path.join(out_dir, "sadtalker_out")
    log("inferencia SadTalker (sin enhancer, preprocess crop)...")
    # Sin --enhancer gfpgan: evita basicsr/functional_tensor (error #1 en torchvision
    # moderno). --preprocess crop = modo mas robusto. La calidad de cara se mejora luego.
    # inference.py usa imports relativos (src/) -> cwd=SadTalker, rutas absolutas.
    # Capturamos su salida SIEMPRE: asi sabemos si falla por no detectar la cara
    # (ilustracion) o por un choque de deps en runtime.
    r = subprocess.run([sys.executable, "inference.py",
                        "--driven_audio", audio, "--source_image", os.path.abspath(ancla_path),
                        "--result_dir", res, "--still", "--preprocess", "crop"],
                       cwd=ST, capture_output=True, text=True)
    log("INFERENCE STDOUT:\\n" + r.stdout[-3000:])
    log("INFERENCE STDERR:\\n" + r.stderr[-3000:])
    if r.returncode != 0:
        raise RuntimeError("inference.py fallo (ver run.log)")
    mp4s = sorted(glob.glob(os.path.join(res, "**", "*.mp4"), recursive=True))
    assert mp4s, "SadTalker no produjo mp4"
    shutil.copy(mp4s[-1], os.path.join(out_dir, "narrator.mp4"))
    log("LISTO: narrator.mp4 :: " + os.path.basename(mp4s[-1]))
except Exception:
    tb = traceback.format_exc()
    with open(os.path.join(out_dir, "error.txt"), "w") as f:
        f.write(tb)
    print(tb, flush=True)
    raise
'''


def _subir_audio_dataset(audio: Path, dslug: str, usuario: str) -> str:
    """Sube recorte.wav como dataset privado (transporte de input a Kaggle).

    El kernel push embebe solo el script JSON; los binarios (audio) viajan como
    dataset. Crea la primera vez, versiona si ya existe. Devuelve 'usuario/slug'.
    """
    import shutil
    import tempfile

    ref = f"{usuario}/{dslug}"
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        shutil.copy(audio, tdp / "recorte.wav")
        (tdp / "dataset-metadata.json").write_text(
            json.dumps({"title": dslug, "id": ref,
                        "licenses": [{"name": "CC0-1.0"}]}),
            encoding="utf-8",
        )
        # Sin --dir-mode zip: sube el wav como archivo suelto -> en runtime queda en
        # /kaggle/input/<slug>/recorte.wav (zip lo montaba distinto -> FileNotFound).
        c = subprocess.run(
            ["kaggle", "datasets", "create", "-p", str(tdp)],
            capture_output=True, text=True,
        )
        salida = (c.stdout + c.stderr).lower()
        if c.returncode != 0 and "already exists" in salida:
            print("[kaggle] dataset existe -> versiono")
            subprocess.run(
                ["kaggle", "datasets", "version", "-p", str(tdp), "-m", "update"],
                check=True, capture_output=True, text=True,
            )
        elif c.returncode != 0:
            raise RuntimeError(f"create dataset fallo: {c.stderr.strip()}")

        # Esperar a que la version quede 'ready' antes de que el kernel la use
        # (si no, el kernel puede agarrar una version anterior -> audio equivocado).
        import time
        for _ in range(36):  # ~180s
            st = subprocess.run(
                ["kaggle", "datasets", "status", ref], capture_output=True, text=True
            )
            estado = (st.stdout + st.stderr).lower()
            if "ready" in estado:
                break
            if "error" in estado:
                raise RuntimeError(f"dataset en error: {st.stdout.strip() or st.stderr.strip()}")
            time.sleep(5)
        else:
            print("[kaggle] aviso: el dataset no confirmo 'ready'; sigo igual")
        print(f"[kaggle] dataset audio listo: {ref}")
    return ref


def generar_talking_en_kaggle(
    audio: Path,
    coherencia: dict,
    dir_kernel: Path,
    salida_dir: Path,
    job_id: str,
    timeout_s: int = 3600,
    intervalo_s: int = 30,
) -> Path:
    """Despacha el kernel talking-head a Kaggle y baja narrator.mp4."""
    from ..domain.planificacion import NEGATIVO
    from .exportar_job_visual import _GEN

    import hashlib

    usuario = _usuario_kaggle()
    # Dataset content-addressed: el hash del audio en el slug evita el race de versiones
    # de Kaggle (que el kernel agarre una version vieja del wav). Audio distinto = dataset
    # distinto; mismo audio = mismo dataset (idempotente).
    h = hashlib.sha256(audio.read_bytes()).hexdigest()[:8]
    dslug = _slug(f"astilla-audio-{job_id}-{h}")
    ref_audio = _subir_audio_dataset(audio, dslug, usuario)

    job = {
        "job_id": job_id,
        "negativo": NEGATIVO,
        "generacion": {"modelo": _GEN["modelo"]},
        "coherencia": coherencia,
        "audio_path": f"/kaggle/input/{dslug}/recorte.wav",
    }
    slug = _slug(f"astilla-talking-{job_id}")
    kid = f"{usuario}/{slug}"

    dir_kernel.mkdir(parents=True, exist_ok=True)
    (dir_kernel / "astilla_kernel.py").write_text(
        _KERNEL_TALKING.format(job_json=json.dumps(job)), encoding="utf-8"
    )
    (dir_kernel / "kernel-metadata.json").write_text(
        json.dumps(
            {
                "id": kid,
                "title": slug,
                "code_file": "astilla_kernel.py",
                "language": "python",
                "kernel_type": "script",
                "is_private": True,
                "enable_gpu": True,
                "machine_shape": "NvidiaTeslaT4",
                "enable_internet": True,
                "dataset_sources": [ref_audio],  # el wav viaja como dataset
                "competition_sources": [],
                "kernel_sources": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    _push_y_esperar(kid, dir_kernel, timeout_s, intervalo_s)
    _bajar_output(kid, salida_dir)
    narrator = salida_dir / "narrator.mp4"
    if not narrator.exists():
        raise RuntimeError("el kernel completo pero no se bajo narrator.mp4")
    print(f"[kaggle] narrator.mp4 recuperado -> {narrator}")
    return narrator
