# Reparto VIDEO / STILL por short (plan de pre-producción para exprimir el saldo LTX)

> **Objetivo:** pagar LTX-video (fast, $0.04/s) SOLO en las escenas donde el movimiento vende el
> mecanismo; el resto = **stills SDXL gratis en Kaggle** (`scripts/generar_stills_kaggle.py`) animados
> con Ken Burns local (`generar_ltx.py --video "..."`). Ver [[ltx-fast-vs-pro-y-hibrido-stills]].
>
> ⚠️ Los **índices reales de escena salen del `visual_job.json`** (se genera al grabar+transcribir, paso 3
> del pipeline). Acá el reparto es por **beat del guion**; al grabar, mapeás beat→índice mirando el
> `visual_job.json` y pasás esos índices a `--video`. Las duraciones son estimadas (fast redondea a par, mín 4s).

## Resumen (con $5 alcanzan LOS 5, sobra margen)

| Short | Escenas video | ~seg video | ~costo | Nota |
|-------|---------------|-----------|--------|------|
| manavai | 1 | 8 | **$0.32** | casi todo estructura/diagrama = still |
| pisagua | 3 | ~28 | **$1.12** | acción anfibia justifica más video |
| piston_fuego | 2 | 14 | **$0.56** | los 2 money shots: golpe + fogonazo |
| sismografo | 2 | 16 | **$0.64** | péndulo inclina + bolita cae |
| agua_rapanui | 1 | 8 | **$0.32** | solo el agua brotando |
| **TOTAL** | | | **≈ $2.96** | vs ~$14 si fuera todo video |

→ **Los 5 shorts entran en ~$3**, quedan ~$2 de colchón para regens. La regla: mín escenas de video,
las más largas posibles (el redondeo a par desperdicia menos).

---

## manavai — `¿Cómo cultivaban en una isla sin ríos ni buena tierra?`
| Beat | Contenido | V/S | Por qué |
|------|-----------|-----|---------|
| 1 | Isla barrida por el viento | 🎬 VIDEO | el viento sacudiendo las plantas vende la hostilidad |
| 2 | Peñón volcánico, sol que raja la tierra | 🖼️ still | paisaje estático |
| 3 | Corrales redondos de roca (manavai) | 🖼️ still | estructura, sin movimiento |
| 4 | Roca porosa chupa/devuelve humedad | 🖼️ still | **diagrama explainer** (corte tipo Da Vinci) |
| 5 | Las piedras guardan el calor | 🖼️ still | — |
| 6 | Tríada "Cortar. Atrapar. Abrigar." | 🖼️ still | tríptico |
| 7 | Camote/taro/plátano creciendo adentro | 🖼️ still | (opcional 🎬 si querés vida vegetal, +$0.28) |
| 8 | CTA | 🖼️ still | — |

**Video: 1 escena (~8s) = $0.32.**

## pisagua — `¿Cómo se mete un ejército en una playa defendida sin que lo masacren?`
| Beat | Contenido | V/S | Por qué |
|------|-----------|-----|---------|
| 1 | Playa defendida desde los cerros | 🖼️ still | establishing dramático |
| 2 | Geometría: botes lentos vs trincheras | 🖼️ still | **diagrama táctico** |
| 3 | Barcos bombardean las alturas | 🎬 VIDEO | cañonazos + humo = movimiento |
| 4 | Tropa remando entre olas bajo fuego | 🎬 VIDEO | **money shot**, olas + remo |
| 5 | Trepan el cerro a tomar la trinchera | 🎬 VIDEO | avance cuesta arriba |
| 6 | Operación anfibia coordinada | 🖼️ still | — |
| 7 | Tríada "Cañón. Remo. Cima." | 🖼️ still | tríptico |
| 8 | Cierre + CTA | 🖼️ still | — |

**Video: 3 escenas (~28s) = $1.12.** (El más caro del lote — la acción lo pide.)

## piston_fuego — `¿Cómo hacían fuego en un segundo, sin chispa ni fricción?`
| Beat | Contenido | V/S | Por qué |
|------|-----------|-----|---------|
| 1 | Frotar dos palos, minutos de sudor | 🖼️ still | contraste; el payoff es el pistón |
| 2 | El tubo presentado | 🖼️ still | objeto |
| 3 | Tubo + émbolo sellado (macro) | 🖼️ still | macro del objeto |
| 4 | La yesca en la punta | 🖼️ still | macro |
| 5 | El émbolo baja de un golpe seco | 🎬 VIDEO | **money shot**: el golpe |
| 6 | La yesca se enciende sola | 🎬 VIDEO | **money shot**: el fogonazo |
| 7 | Tríada "Comprimir. Calentar. Encender." | 🖼️ still | tríptico |
| 8 | Principio del diésel + CTA | 🖼️ still | **diagrama** pistón/diésel |

**Video: 2 escenas (~14s) = $0.56.**

## sismografo — `¿Cómo sabían de qué lado venía un terremoto hace 2000 años?`
| Beat | Contenido | V/S | Por qué |
|------|-----------|-----|---------|
| 1 | Corte lejano, temblor que no se siente | 🖼️ still | establishing |
| 2 | La vasija de bronce (hero shot) | 🖼️ still | objeto ornamentado |
| 3 | Ocho dragones con bolitas, ocho sapos | 🖼️ still | detalle |
| 4 | El péndulo interno, quieto | 🖼️ still | **diagrama de corte** |
| 5 | El péndulo se inclina, empuja la palanca | 🎬 VIDEO | el mecanismo en movimiento |
| 6 | La bolita cae en la boca del sapo | 🎬 VIDEO | **money shot**: la caída |
| 7 | Tríada "Temblar. Inclinar. Caer." | 🖼️ still | tríptico |
| 8 | El mensajero confirma + CTA | 🖼️ still | — |

**Video: 2 escenas (~16s) = $0.64.**

## agua_rapanui — `¿De dónde sacaban agua para beber en una isla sin un solo río?`
| Beat | Contenido | V/S | Por qué |
|------|-----------|-----|---------|
| 1 | Isla sin ríos, la roca se traga la lluvia | 🖼️ still | (opcional 🎬 si querés lluvia) |
| 2 | El agua corre bajo tierra hasta la orilla | 🖼️ still | **diagrama de corte** (filtración) |
| 3 | El agua dulce brota en la orilla | 🎬 VIDEO | **money shot**: agua brotando |
| 4 | Los rapanui la juntan en bajamar | 🖼️ still | — |
| 5 | Tríada "Filtrar. Brotar. Beber." | 🖼️ still | tríptico |
| 6 | Los moáis marcan los manantiales | 🖼️ still | revelación (moáis en la costa) |
| 7 | CTA | 🖼️ still | — |

**Video: 1 escena (~8s) = $0.32.**

---

## Cómo aplicarlo al grabar (por short)
1. Grabás → `exportar_guion.py` → `pipeline.animado ... --stub-visual` (genera `visual_job.json`).
2. Abrís `visual_job.json`, mapeás los beats 🎬 de acá a sus **índices reales** de escena.
3. Escribís los prompts (Claude en sesión) — **para stills, estilo al FRENTE** (evita la deriva foto).
4. Stills gratis: `python scripts/generar_stills_kaggle.py --nombre <n> --indices <los still>`.
5. Video pago: `python scripts/generar_ltx.py --nombre <n> --indices todas --auto --video <los 🎬>`.
6. Sigue igual: `armar_short.py` → retimeo → música.
