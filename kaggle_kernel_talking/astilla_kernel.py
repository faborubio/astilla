import os, json, subprocess, sys, glob, shutil, traceback
out_dir = "/kaggle/working"
os.makedirs(out_dir, exist_ok=True)

# Captura de errores propia: Kaggle a veces devuelve log vacio en kernels script con
# error -> escribimos progreso y traceback a archivos del working para NO quedar ciegos.
def log(msg):
    print(msg, flush=True)
    with open(os.path.join(out_dir, "run.log"), "a") as f:
        f.write(str(msg) + "\n")

def pip(pkgs):
    log("pip install: " + " ".join(pkgs))
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + pkgs,
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("PIP FALLO:\n" + (r.stdout[-1500:] + r.stderr[-1500:]))
        raise RuntimeError("pip install fallo: " + " ".join(pkgs))

try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "diffusers", "transformers", "accelerate"], check=True)
    import torch
    from diffusers import StableDiffusionPipeline

    JOB = json.loads(r"""{"job_id": "rec-habla_v1_s1", "negativo": "text, watermark, logo, lowres, blurry, deformed, extra limbs", "generacion": {"modelo": "stable-diffusion-v1-5/stable-diffusion-v1-5"}, "coherencia": {"ancla_prompt": "extreme close-up headshot portrait of a single charismatic narrator, neon synthwave illustration, glowing rim light, dark moody atmosphere, cinematic lighting, face fills the frame, head and shoulders only, front view, looking straight at camera, both eyes visible, symmetric detailed face, plain background, high detail", "ancla_semilla": 1, "ancla_negativo": "full body, full shot, wide shot, long shot, distant, small face, multiple people, crowd, no face, back view, side profile, looking away, occluded face"}, "audio_path": "/kaggle/input/astilla-audio-rec-habla-v1-s1-4bb748a3/recorte.wav"}""")
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
        "try:\n    from src.utils.face_enhancer import enhancer_generator_with_len, enhancer_list\nexcept Exception:\n    enhancer_generator_with_len = enhancer_list = None")
    open(_ap, "w").write(_s)
    log("patch: import del enhancer hecho opcional")

    # SadTalker usa aliases de numpy removidos en 1.24+ (np.float/int/bool). Los
    # reemplazamos en su codigo por los tipos reales (fix que el propio numpy marca
    # como seguro). \b evita tocar np.float32/np.int64 ya correctos.
    import re as _re
    for _root, _, _files in os.walk(os.path.join(ST, "src")):
        for _fn in _files:
            if _fn.endswith(".py"):
                _fp = os.path.join(_root, _fn)
                _t = open(_fp).read()
                _u = _re.sub(r"np\.float\b", "np.float64", _t)
                _u = _re.sub(r"np\.int\b", "np.int64", _u)
                _u = _re.sub(r"np\.bool\b", "np.bool_", _u)
                _u = _re.sub(r"np\.object\b", "object", _u)
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
    log("INFERENCE STDOUT:\n" + r.stdout[-3000:])
    log("INFERENCE STDERR:\n" + r.stderr[-3000:])
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
