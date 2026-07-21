"""Regenera docs/panel_produccion.html (panel de produccion de VESTIGIOS).

El ESTADO del pipeline se deriva SOLO del disco (carpetas artifacts/shorts/<n>/),
asi que se actualiza solo cada vez que corres el script. Las METRICAS de los
publicados y el banco de guiones salen de docs/panel_datos.json (edicion manual,
porque vienen de YouTube Studio y no hay API).

Uso:  python scripts/generar_panel.py
"""
from __future__ import annotations

import datetime
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import SHORTS  # artifacts/shorts

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "docs" / "panel_datos.json"
SALIDA = RAIZ / "docs" / "panel_produccion.html"

ORDEN = ["grab", "voz", "escenas", "prompts", "clips", "armado", "música", "publicar"]
LBL = {"grab": "grab", "voz": "voz", "escenas": "escenas", "prompts": "prompts",
       "clips": "clips", "armado": "armado", "música": "música", "publicar": "publicar"}


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def estado_pipeline(nombre: str) -> dict:
    """Deriva el estado de un short leyendo su carpeta."""
    d = SHORTS / nombre
    voz = (d / "voz.wav").exists()
    seg = (d / "segmentos.json").exists()
    pr = (d / "prompts.json").exists()
    n_esc = 0
    vj = d / "visual_job.json"
    if vj.exists():
        try:
            n_esc = len(json.loads(vj.read_text(encoding="utf-8"))["escenas"])
        except Exception:
            n_esc = 0
    n_clips = len(list((d / "clips").glob("*.mp4"))) if (d / "clips").exists() else 0
    arm = (d / "short.mp4").exists()
    mus = (d / "short_musica.mp4").exists()
    clips_ok = n_esc > 0 and n_clips >= n_esc

    done = {"grab": voz, "voz": voz, "escenas": seg, "prompts": pr,
            "clips": clips_ok, "armado": arm, "música": mus, "publicar": False}
    cur = next((k for k in ORDEN if not done[k]), "publicar")

    if cur == "clips":
        if n_clips == 0:
            pill, txt = "pending", "En cola"
        else:
            pill, txt = "active", f"Generando {n_clips}/{n_esc}"
    elif cur == "armado":
        pill, txt = "ok", f"Clips {n_esc}/{n_esc}"
    elif cur == "música":
        pill, txt = "active", "Armado"
    elif cur == "publicar":
        pill, txt = "ok", "Listo · publicar"
    else:
        pill, txt = "pending", cur

    pct = 0 if n_esc == 0 else round(100 * min(n_clips, n_esc) / n_esc)
    return {"done": done, "cur": cur, "pill": pill, "txt": txt,
            "n_clips": n_clips, "n_esc": n_esc, "pct": pct, "clips_ok": clips_ok}


def card(nombre: str, meta: dict) -> str:
    st = estado_pipeline(nombre)
    # override honesto: un short parado por presupuesto no esta "generando"
    bloqueo = meta.get("bloqueado")
    if bloqueo and not st["clips_ok"]:
        st["pill"] = "paused"
        st["txt"] = f"Bloqueado {st['n_clips']}/{st['n_esc']}"
    pasos = []
    for k in ORDEN:
        cls = "done" if st["done"][k] else ("cur" if k == st["cur"] else "")
        pasos.append(f'<div class="step {cls}"><div class="bar"></div>'
                     f'<div class="lbl">{LBL[k]}</div></div>')
    if st["clips_ok"]:
        clips_row = f'<span class="mono">listo → {st["cur"]}</span>'
    elif bloqueo:
        clips_row = f'<span class="mono">{esc(bloqueo)}</span>'
    else:
        clips_row = f'<span class="mono">{st["n_clips"]}/{st["n_esc"]} clips</span>'
    tema = esc(meta.get("tema", ""))
    costo = esc(meta.get("costo", ""))
    return f"""      <div class="card">
        <div class="top">
          <div><h3>{esc(nombre)}</h3><div class="tema">{tema}</div></div>
          <span class="pill {st['pill']}">{esc(st['txt'])}</span>
        </div>
        <div class="steps">{''.join(pasos)}</div>
        <div class="clips"><div class="track"><div class="fill" style="width:{st['pct']}%"></div></div>
          <div class="row"><span>{st['n_esc']} escenas · {costo}</span>{clips_row}</div></div>
      </div>"""


def fila_publicado(p: dict) -> str:
    vistas = p.get("vistas_txt") or (str(p["vistas"]) if p.get("vistas") is not None else None)
    likes = p.get("likes")
    v = p.get("vistas")
    lr = (likes / v) if (likes and v) else None
    nombre = esc(p["nombre"])
    if p.get("youtube_id"):
        nombre_html = (f'<a href="https://youtube.com/shorts/{esc(p["youtube_id"])}" '
                       f'target="_blank" rel="noopener">{nombre}</a>')
    else:
        nombre_html = nombre

    vistas_td = (f'<td class="num best">{esc(vistas)}</td>' if p.get("destacado")
                 else (f'<td class="num">{esc(vistas)}</td>' if vistas
                       else '<td class="num dash">—</td>'))
    likes_td = f'<td class="num">{likes}</td>' if likes else '<td class="num dash">—</td>'
    if lr is not None:
        w = min(100, round(lr / 0.08 * 100))
        lr_td = (f'<td class="num"><span class="lr"><span class="b"><i style="width:{w}%">'
                 f'</i></span>{lr*100:.1f}%</span></td>'.replace(".", ","))
    else:
        lr_td = '<td class="num"><span class="dash">—</span></td>'

    ret = p.get("retencion")
    if ret and p.get("saturado"):
        ret_td = (f'<td class="num ret"><span class="lr"><span class="b"><i '
                  f'style="width:72%;background:var(--paused)"></i></span>{esc(ret)}</span></td>')
    elif ret:
        ret_td = f'<td class="num">{esc(ret)}</td>'
    else:
        ret_td = '<td class="num dash">—</td>'

    if p.get("saturado"):
        estado_td = '<td><span class="pill paused">Saturado</span></td>'
    elif p.get("destacado"):
        estado_td = '<td><span class="pill gold">Mejor</span></td>'
    else:
        estado_td = '<td><span class="pill ok">Publicado</span></td>'

    return (f'          <tr>\n'
            f'            <td><div class="name">{nombre_html}</div>'
            f'<div class="t">{esc(p.get("tema",""))}</div></td>\n'
            f'            {vistas_td}{likes_td}\n'
            f'            {lr_td}\n'
            f'            {ret_td}{estado_td}\n'
            f'          </tr>')


def fila_banco(b: dict) -> str:
    return (f'      <div class="brow {esc(b["clase"])}">\n'
            f'        <span class="nm">{esc(b["nombre"])}</span>\n'
            f'        <span class="ds">{esc(b["tema"])}</span>\n'
            f'        <span class="pill {esc(b["pill"])}">{esc(b["etiqueta"])}</span>\n'
            f'      </div>')


def main() -> None:
    datos = json.loads(DATOS.read_text(encoding="utf-8"))
    c = datos["canal"]
    fecha = datetime.date.today().isoformat()

    prod = datos.get("produccion", {})
    n_prod = len(prod)
    cards = "\n".join(card(n, m) for n, m in prod.items())
    filas_pub = "\n".join(fila_publicado(p) for p in datos["publicados"])
    filas_bank = "\n".join(fila_banco(b) for b in datos["banco"])
    n_pub = len(datos["publicados"])

    doc = _PLANTILLA.format(
        css=_CSS, fecha=esc(fecha),
        subs=esc(c["subs"]), subs_delta=esc(c["subs_delta"]),
        vistas=esc(c["vistas_28d"]), watch=esc(c["watch_28d"]),
        ret=esc(c["retencion_baseline"]), ret_nota=esc(c["retencion_baseline_nota"]),
        n_pub=n_pub, n_prod=n_prod,
        prod_lista=" · ".join(prod.keys()),
        cards=cards, filas_pub=filas_pub, filas_bank=filas_bank,
    )
    SALIDA.write_text(doc, encoding="utf-8")
    print(f"[panel] {n_prod} en produccion, {n_pub} publicados, {len(datos['banco'])} en banco")
    print(f"[panel] -> {SALIDA}")
    print(f"[panel] abrir: file:///{SALIDA.as_posix()}")


_CSS = r"""<style>
  :root{--bg:#10161a;--surface:#182126;--surface-2:#202d33;--border:#2f424a;--text:#e9e3d5;--muted:#94a7a8;--faint:#6d8183;--teal:#46b0a4;--amber:#e6a94a;--ok:#5ec08f;--active:#54b6d2;--pending:#8a9fa0;--paused:#d67a5f;--shadow:0 1px 0 rgba(255,255,255,.03),0 6px 22px -12px rgba(0,0,0,.6)}
  @media (prefers-color-scheme:light){:root{--bg:#e7ecea;--surface:#f8faf9;--surface-2:#eef2f1;--border:#d3ddda;--text:#17211f;--muted:#586865;--faint:#7c8a87;--teal:#2b8c82;--amber:#b0761a;--ok:#2f8f63;--active:#1f88a6;--pending:#6c7a76;--paused:#b5533a;--shadow:0 1px 0 rgba(255,255,255,.6),0 8px 20px -14px rgba(20,40,40,.35)}}
  :root[data-theme="dark"]{--bg:#10161a;--surface:#182126;--surface-2:#202d33;--border:#2f424a;--text:#e9e3d5;--muted:#94a7a8;--faint:#6d8183;--teal:#46b0a4;--amber:#e6a94a;--ok:#5ec08f;--active:#54b6d2;--pending:#8a9fa0;--paused:#d67a5f}
  :root[data-theme="light"]{--bg:#e7ecea;--surface:#f8faf9;--surface-2:#eef2f1;--border:#d3ddda;--text:#17211f;--muted:#586865;--faint:#7c8a87;--teal:#2b8c82;--amber:#b0761a;--ok:#2f8f63;--active:#1f88a6;--pending:#6c7a76;--paused:#b5533a}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1080px;margin:0 auto;padding:clamp(20px,4vw,44px) clamp(16px,3vw,28px) 64px}
  .mono{font-family:ui-monospace,"Cascadia Code",Consolas,monospace;font-variant-numeric:tabular-nums}
  header{border-bottom:1px solid var(--border);padding-bottom:22px;margin-bottom:26px}
  .eyebrow{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--teal);font-weight:600}
  h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(1.9rem,4.5vw,2.7rem);margin:.28em 0 .12em;letter-spacing:-.01em;text-wrap:balance}
  .sub{color:var(--muted);font-size:.95rem}
  .sub b{color:var(--text);font-weight:600}
  .amber-rule{height:2px;width:52px;background:var(--amber);margin-top:16px;border-radius:2px}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:26px 0 40px}
  .kpi{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:15px 16px;box-shadow:var(--shadow)}
  .kpi .n{font-family:ui-monospace,Consolas,monospace;font-variant-numeric:tabular-nums;font-size:1.7rem;font-weight:600;letter-spacing:-.02em;line-height:1.1}
  .kpi .l{font-size:.75rem;color:var(--muted);margin-top:5px}
  .kpi .d{font-size:.72rem;color:var(--faint);margin-top:2px}
  .kpi .d.up{color:var(--ok)}
  section{margin:0 0 42px}
  .shead{display:flex;align-items:baseline;gap:12px;margin-bottom:16px}
  .shead h2{font-family:Georgia,serif;font-size:1.28rem;font-weight:600;margin:0}
  .shead .count{font-size:.8rem;color:var(--faint);font-family:ui-monospace,monospace}
  .shead .rule{flex:1;height:1px;background:var(--border)}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 17px;box-shadow:var(--shadow)}
  .card .top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
  .card h3{font-size:1.02rem;margin:0;font-weight:650}
  .card .tema{font-size:.78rem;color:var(--muted);margin-top:2px}
  .pill{display:inline-flex;align-items:center;gap:6px;font-size:.72rem;font-weight:600;padding:3px 9px;border-radius:999px;border:1px solid transparent;white-space:nowrap}
  .pill::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
  .pill.ok{color:var(--ok);background:color-mix(in srgb,var(--ok) 15%,transparent);border-color:color-mix(in srgb,var(--ok) 35%,transparent)}
  .pill.active{color:var(--active);background:color-mix(in srgb,var(--active) 15%,transparent);border-color:color-mix(in srgb,var(--active) 35%,transparent)}
  .pill.pending{color:var(--pending);background:color-mix(in srgb,var(--pending) 14%,transparent);border-color:color-mix(in srgb,var(--pending) 32%,transparent)}
  .pill.paused{color:var(--paused);background:color-mix(in srgb,var(--paused) 15%,transparent);border-color:color-mix(in srgb,var(--paused) 35%,transparent)}
  .pill.gold{color:var(--amber);background:color-mix(in srgb,var(--amber) 15%,transparent);border-color:color-mix(in srgb,var(--amber) 38%,transparent)}
  .steps{display:flex;gap:5px;margin:15px 0 10px}
  .step{flex:1;text-align:center}
  .step .bar{height:5px;border-radius:3px;background:var(--surface-2);border:1px solid var(--border)}
  .step.done .bar{background:var(--teal);border-color:var(--teal)}
  .step.cur .bar{background:var(--active);border-color:var(--active)}
  .step .lbl{font-size:.6rem;color:var(--faint);margin-top:5px;letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .step.done .lbl{color:var(--muted)}
  .step.cur .lbl{color:var(--active);font-weight:600}
  .clips{margin-top:12px}
  .clips .track{height:8px;background:var(--surface-2);border:1px solid var(--border);border-radius:5px;overflow:hidden}
  .clips .fill{height:100%;background:linear-gradient(90deg,var(--teal),var(--active))}
  .clips .row{display:flex;justify-content:space-between;font-size:.74rem;color:var(--muted);margin-top:6px}
  .clips .row .mono{color:var(--text)}
  .tablewrap{overflow-x:auto;border:1px solid var(--border);border-radius:14px;box-shadow:var(--shadow)}
  table{border-collapse:collapse;width:100%;min-width:640px;background:var(--surface)}
  thead th{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;font-weight:600;padding:12px 14px;border-bottom:1px solid var(--border)}
  th.num,td.num{text-align:right;font-family:ui-monospace,Consolas,monospace;font-variant-numeric:tabular-nums}
  tbody td{padding:12px 14px;border-bottom:1px solid var(--border);font-size:.9rem}
  tbody tr:last-child td{border-bottom:none}
  tbody tr:hover{background:var(--surface-2)}
  td .name{font-weight:600}
  td .name a{color:inherit;text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--teal) 55%,transparent)}
  td .name a:hover{color:var(--teal)}
  td .t{font-size:.76rem;color:var(--faint);margin-top:1px}
  .best{color:var(--amber);font-weight:700}
  .lr{display:flex;align-items:center;gap:8px;justify-content:flex-end}
  .lr .b{width:46px;height:6px;background:var(--surface-2);border:1px solid var(--border);border-radius:4px;overflow:hidden}
  .lr .b i{display:block;height:100%;background:var(--teal)}
  .ret .b i{background:var(--amber)}
  .dash{color:var(--faint)}
  .bank{display:grid;gap:10px}
  .brow{display:flex;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:13px 16px;box-shadow:var(--shadow)}
  .brow .nm{font-weight:650;min-width:96px}
  .brow .ds{color:var(--muted);font-size:.85rem;flex:1}
  .brow.paused{border-left:3px solid var(--paused)}
  .brow.new{border-left:3px solid var(--ok)}
  .brow.next{border-left:3px solid var(--pending)}
  footer{border-top:1px solid var(--border);padding-top:18px;color:var(--faint);font-size:.78rem}
  .legend{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:10px}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .dot{width:9px;height:9px;border-radius:50%}
  a{color:var(--teal)}
</style>"""

_PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Panel de producción — VESTIGIOS</title>
{css}
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">Astilla · motor de producción</div>
    <h1>Panel de producción</h1>
    <div class="sub">Canal <b>VESTIGIOS</b> · <span class="mono">@vestigios.historia</span> · historia y divulgación · actualizado <b>{fecha}</b></div>
    <div class="amber-rule"></div>
  </header>

  <div class="kpis">
    <div class="kpi"><div class="n">{subs}</div><div class="l">Suscriptores</div><div class="d up">{subs_delta}</div></div>
    <div class="kpi"><div class="n">{vistas}</div><div class="l">Vistas · 28 d</div><div class="d">{watch}</div></div>
    <div class="kpi"><div class="n">{ret}</div><div class="l">Retención · baseline</div><div class="d">{ret_nota}</div></div>
    <div class="kpi"><div class="n">{n_pub}</div><div class="l">Publicados</div><div class="d">like-rate ~7% en la tanda nueva</div></div>
    <div class="kpi"><div class="n">{n_prod}</div><div class="l">En producción</div><div class="d">{prod_lista}</div></div>
  </div>

  <section>
    <div class="shead"><h2>En producción</h2><span class="count">{n_prod} shorts · pipeline folder-aware</span><span class="rule"></span></div>
    <div class="cards">
{cards}
    </div>
  </section>

  <section>
    <div class="shead"><h2>Publicados</h2><span class="count">{n_pub} shorts · ordenados por vistas</span><span class="rule"></span></div>
    <div class="tablewrap">
      <table>
        <thead><tr>
          <th>Short</th><th class="num">Vistas</th><th class="num">Likes</th>
          <th class="num">Like-rate</th><th class="num">Retención</th><th>Estado</th>
        </tr></thead>
        <tbody>
{filas_pub}
        </tbody>
      </table>
    </div>
    <p style="font-size:.76rem;color:var(--faint);margin:10px 2px 0">* 74,4% = retención promedio del cohorte de los 3 primeros shorts (baseline del canal), no un valor por short. Hormigón cayó a 53,9% por tema saturado — no por el guion.</p>
  </section>

  <section>
    <div class="shead"><h2>Banco de guiones</h2><span class="count">grabar en orden · chequeados por saturación</span><span class="rule"></span></div>
    <div class="bank">
{filas_bank}
    </div>
  </section>

  <footer>
    <div class="legend">
      <span><span class="dot" style="background:var(--teal)"></span>Etapa completa</span>
      <span><span class="dot" style="background:var(--active)"></span>En curso</span>
      <span><span class="dot" style="background:var(--pending)"></span>En cola / pendiente</span>
      <span><span class="dot" style="background:var(--paused)"></span>En pausa / saturado</span>
      <span><span class="dot" style="background:var(--amber)"></span>Mejor / destacado</span>
    </div>
    Pipeline: grabar → voz limpia → escenas → prompts → clips LTX → armado → música → publicar.
    Estado leído del disco; métricas desde <span class="mono">docs/panel_datos.json</span>. Métrica primaria = <b>retención</b>, no vistas absolutas.
  </footer>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    main()
