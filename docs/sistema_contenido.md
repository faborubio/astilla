# Sistema de contenido — destilado de los 4 videos + nichos de shorts

> **Origen y estatus (leer primero):** este documento es material de *referencia externa*, no
> doctrina de Astilla. Viene destilado de 4 videos de YouTube (2 de shorts, 2 de automation
> faceless) que son **funnels de venta** (Skool, coaching, la herramienta afiliada "Viralit").
> Las cifras de "$40k/mes" son prueba social de marketing → ignorar. Lo que sí vale es el
> **método** y el **stack técnico**, que es lo que queda acá.
>
> **Cómo encaja con lo que ya sabemos:** buena parte de esto ya está en el proyecto (guion es el
> 80% — ver benchmark de 8M vistas en `CLAUDE.md`; hook contraintuitivo + título-pregunta + CTA;
> chequeo de saturación + ángulo > nicho). Lo tratamos como **segunda fuente independiente que
> valida el método**. Lo genuinamente nuevo para Astilla está marcado abajo con **[NUEVO]** y
> parqueado en [`../IDEAS.md`](../IDEAS.md): distribución multi-plataforma, research con dummy
> account, y la veta LatAm/Chile como ventaja consciente.
>
> **Recordatorio de prioridad (Parte 5):** esto NO es un proyecto nuevo (ya existen
> `vestigios.historia` y Astilla), pero el objetivo #1 sigue siendo la pega remota. Tratarlo como
> experimento acotado y batcheado, no como segundo trabajo.

---

## PARTE 1 — Lo que sirve (sin pitch)

### 1.1 El stack de producción (idéntico en los 3 videos de contenido)

Este es el núcleo reutilizable y lo más importante para Astilla, porque es el pipeline
que podés codificar:

```
Guion (ChatGPT)  →  Voz (ElevenLabs)  →  Edición (CapCut)  →  Publicar
```

- **Guion**: ChatGPT. Nunca usar el primer output crudo — se genera, se revisa, se ajusta.
- **Voz**: ElevenLabs. Detalles finos que salen en los videos: velocidad ~1.14, sacar
  comas que meten pausas largas, probar voces hasta que suene humano (no robótico).
- **Edición**: CapCut (gratis o barato). Junta clips/imágenes de stock sin copyright +
  subtítulos con IA. Regla: **mostrar siempre algo relacionado a lo que se narra**.

Para Astilla, esto es literalmente el diagrama de flujo del pipeline: cada caja es un
paso automatizable (o semi-automatizable con human-in-the-loop en la revisión de guion).
**Diferencia clave de Astilla:** usamos **voz propia** (no ElevenLabs) → el gate pasa como
`original` y resuelve de raíz el requisito transformativo del §1.4.

### 1.2 Los 3 estilos de edición de shorts (video 1)

| Estilo | Cómo funciona | Clave | Dificultad |
|---|---|---|---|
| **Streamer clipping** | Recortás momentos de un streamer, facecam arriba + gameplay abajo (9:16), título masivo | **Volumen brutal** (~10/día); la mayoría hace 10-30k pero un outlier explota | Baja, pero requiere volumen |
| **AI commentary** | Clip de TikTok/stock + guion + voz IA + edición | **El guion es el rey**, no el clip. Retención = plata | Alta (no apto para principiantes) |
| **Ranking** | Varios clips de un tema, lista numerada con voz over | Voz over lo vuelve **transformativo** (evita strike) | Baja (el más fácil) |

Para `vestigios.historia`, el estilo natural es una mezcla de **AI commentary + ranking**:
guion histórico + voz + clips/imágenes de stock/dominio público. Nada de clipping de streamers.

### 1.3 Técnicas de edición que suben retención (video 1)

- **Hook con contradicción absurda** en el primer segundo: "el arma más peligrosa...
  pero hecha de globos inofensivos". Para historia: "el imperio más poderoso del
  mundo... cayó por un error de contabilidad".
- **Zoom con keyframes + easing** (`Alt+K` → cubic ease en scale/X/Y) para movimiento suave.
- **Efectos de sonido en cada transición** (whoosh, camera shutter, "ding" a -7 no reventado,
  vine boom, XP de Minecraft en momentos clave).
- **Música trending sincronizada al beat drop** con marcadores en el momento pico.
- **Subtítulos** con font custom, stroke grueso, animación tipo "color bounce". CapCut Pro
  los autogenera.
- **CTA al final** en forma de pregunta ("¿lo intentarías?" — para historia: "¿sabías esto?"
  o "¿qué habrías hecho?") para provocar comentarios.

### 1.4 El requisito transformativo (crítico para no comerte un strike)

Bajar un clip ajeno y resubirlo = reused content = canal muerto. Para que YouTube lo cuente
como **transformativo**: voz over propia + edición + reordenamiento. En historia tenés ventaja:
mucho material es **dominio público** (grabados, mapas, pinturas, footage de archivo), así que
el riesgo de copyright es menor, pero igual necesitás el guion/voz propio para diferenciarte.

### 1.5 Criterios de nicho (videos 3 y 4 — aplican también a shorts)

Un nicho/canal de referencia es potencial si cumple:

1. **Más visitas que suscriptores** en sus videos — valida que la gente entra por el
   **tema**, no por el creador. (El criterio más importante y el más reutilizable.)
2. Canales chicos (los videos dicen máx ~100-250k subs) — señal de nicho joven, no saturado.
3. Ningún gigante dominando ni montones de canales fracasando.
4. Nicho relativamente nuevo (<6 meses idealmente).
5. **Monetizable / RPM decente** (para largo importa mucho; para shorts el fondo de shorts
   paga distinto, pero el volumen de visitas manda).
6. Que puedas hacer **mejor contenido** que el competidor (aunque sea solo mejor guion).

### 1.6 Métodos de descubrimiento (el oro de los videos 3 y 4)

- **Niche transfer method**: agarrar un formato probado y moverlo a otro mercado/tema.
  Ejemplo canónico: "cómo vivían en la época medieval" → cavernícolas → piratas → sin techo.
- **Topic transfer method**: un topic viral en un nicho → llevado a otro. "por qué no
  sobrevivirías 24h en la época medieval" → en la Edad de Piedra → en la Roma antigua.
- **Transfer de idioma EN → ES**: lo que ya explotó en el mercado inglés (el más grande y
  competido), replicarlo en español (menos competido). **Copiar, MODIFICAR y pegar** —
  nunca copy-paste literal.
- **Outliers**: videos que multiplicaron sus visitas normales (canal que suele hacer 100k
  y un video hizo 3M) = señal de idea viral, independiente del tamaño del canal.
- **Regla de supply/demand por topic**: buscá el tema en el buscador; si ya se hizo >3 veces
  y no tenés un ángulo distinto, cambiá de topic.
- **Doblar la apuesta (80/20)**: cuando algo funciona, hacé 80% de eso y 20% de tests nuevos.
  No reinventes la rueda.

### 1.7 Packaging: título + miniatura ANTES del contenido (video 4)

- El packaging (título + miniatura) se decide **antes** de producir el video, porque es lo
  primero que ve el usuario. En shorts la "miniatura" pesa menos, pero **el hook visual del
  primer frame + el título/texto en pantalla es tu packaging**.
- Miniatura llama la atención → título convierte esa atención en visualización.
- Título: traducir/adaptar uno que ya funcionó cambiando detalles ("2.000 € en 5 días" →
  "4.000 en 7"). Misma idea, reajuste chico.

### 1.8 Lo que es puro pitch (ignorar)

- "Book a call with me" / comunidades de Skool / coaching de $X.
- Las cifras de ingresos como promesa (son marketing).
- La herramienta "Viralit" con link de descuento: **es un afiliado**. Hace research de
  nichos/outliers, sí, pero no es imprescindible — se replica gratis con el método de la
  dummy account + búsqueda manual + VidIQ free (ver Parte 2).

---

## PARTE 2 — Cómo encontrar nichos de shorts (aterrizado a `vestigios.historia`)

### 2.1 Método general (5 pasos, sin herramientas de pago)   **[NUEVO para Astilla]**

1. **Cuenta "dummy"**: una cuenta nueva/incógnito que uses SOLO para research. Entrenás el
   algoritmo dándole play, like y subscribe únicamente a **shorts de historia faceless**.
   Media hora de eso y tu home se llena de canales del nicho que ni conocías.
2. **Filtrá por "más visitas que subs"**: cuando aparezcan canales, mirá la relación. Canal
   con 15-50k subs y shorts de 500k-3M views = señal fuerte. VidIQ (plan free) te muestra
   los números.
3. **Cazá outliers**: shorts que hicieron mucho más que el promedio de su canal.
4. **Transfer EN → ES**: buscá qué explota en **history shorts en inglés** y adaptalo al
   español (mercado menos competido). No traducción literal — reversioná guion y ángulo.
5. **Validá el topic**: buscá ese topic exacto en español; si ya hay 3+ versiones sin ángulo
   nuevo, buscá otro o dale un giro (localización, ranking, contradicción).

### 2.2 Sub-nichos y ángulos DENTRO de historia (para vestigios.historia)

Historia es amplia; el juego es encontrar el **ángulo/formato** menos saturado en español.
Ideas ordenadas de "formato probado" a "más de nicho":

> ⚠️ **Matiz crítico (video de "los 9 que el algoritmo odia"):** en un canal NUEVO, los temas
> globales como "así vivían en la antigua Roma" están saturados — miles de videos de canales
> más grandes y antiguos. YouTube no te va a empujar a vos por sobre ellos. Regla de oro:
> **el nicho no te diferencia, te diferencia el ÁNGULO.** Los formatos de abajo son la base,
> pero cada uno necesita un giro específico + promesa. No "así vivían en la antigua Roma",
> sino "el hábito de higiene romano que hoy te daría asco" o "por qué un romano promedio te
> ganaría en una pelea". Mismo tema, ángulo nuevo, promesa concreta.
>
> **En Astilla esto ya es criterio activo:** chequeo de saturación antes de elegir tema (el
> hormigón lo probó; `moais` en pausa por saturado). Ver `CLAUDE.md` → estrategia de canal.

**Formatos probados (transfer del inglés — SIEMPRE con ángulo, ver matiz de arriba):**
- **"Cómo vivían los X"** — vida cotidiana de romanos, egipcios, vikingos, mayas, incas.
  Base del niche transfer, pero de bajo impacto sin un ángulo/detalle específico encima.
- **"No sobrevivirías 24h en X"** — Roma antigua, la peste negra, las trincheras, Tenochtitlán.
- **Muertes absurdas / brutales de la historia** — figuras que murieron de formas ridículas.
- **Últimas palabras / últimos días de X** — Napoleón, César, reyes, etc.
- **Mitos históricos desmentidos** — "lo que te enseñaron mal sobre...".
- **Inventos/tecnología antigua** que parecen imposibles para su época.
  *(← este es el filón que ya funciona en Vestigios: "técnica ingeniosa", mecanismo puro.)*
- **Comparaciones** — Roma vs Grecia, samurái vs caballero, imperio vs imperio.

**Ángulos menos competidos (donde podés diferenciarte):**
- **Historia oscura/censurada** — hechos incómodos que no salen en el colegio.
- **Mapas que cambian** — fronteras/imperios a lo largo del tiempo (footage de mapas anima muy bien).
- **Misterios sin resolver** — desapariciones, artefactos, civilizaciones perdidas.
- **Historia de Latinoamérica y Chile** — ESTE es tu ángulo diferencial. El nicho hispano de
  historia está menos saturado que el anglo, y la historia latinoamericana/chilena
  (precolombina, colonial, independencias, Guerra del Pacífico, etc.) tiene poca oferta en
  formato shorts de calidad. Tu raíz en Maule y el interés por lo local te da una voz
  auténtica que un canal genérico traducido del inglés no tiene.

> Sugerencia concreta: mantené `vestigios.historia` con formatos probados para volumen y
> retención, pero reservá 20% para la veta **historia local/latinoamericana** — ahí está el
> hueco de mercado real y tu ventaja injusta. **[NUEVO como decisión consciente]**
> ⚠️ Nota Astilla: tu banco actual (lautaro, cruce_andes, pisagua, chuno, quipus, manavai,
> Q'eswachaka) ya es casi todo veta LatAm — el 80/20 quizás esté invertido. Tenerlo consciente.

### 2.3 Plantilla de guion para history short (basada en video 1)

```
[0-2s]  HOOK con contradicción o dato absurdo. Texto grande en pantalla.
        "El imperio más rico de la historia quebró por culpa de la pimienta."
[2-6s]  Contexto mínimo: quién/cuándo/dónde. Nada de intro larga.
[6-20s] Desarrollo en beats cortos. Un dato por corte. Zoom + SFX en cada uno.
        Imagen/mapa/grabado de dominio público relacionado a CADA frase.
[final] CTA-pregunta: "¿Sabías esto?" / "¿Qué imperio quieres que cuente?"
```
> Astilla ya usa una fórmula equivalente y más afinada (gancho contraintuitivo → problema →
> mecanismo → tríada de 3 palabras → cierre → CTA) en `artifacts/guiones.md`.

### 2.4 Research práctico paso a paso (una tarde)   **[NUEVO para Astilla]**

1. Dummy account → entrená el feed con history shorts (30 min).
2. Anotá 10-15 canales con **más views que subs**.
3. Por cada uno, saca sus 3 shorts más vistos (outliers) → tenés 30-45 ideas validadas.
4. Cruzá con el buscador en español: ¿ya está hecho? ¿con qué ángulo? → filtrá los saturados.
5. De los que quedan, priorizá los que podés localizar/mejorar (ángulo Chile/LatAm o mejor guion).
6. Armá un backlog de 15-20 topics y batcheálos: guiones (ChatGPT) → voces (ElevenLabs) →
   edición (CapCut). En una jornada podés dejar listos varios.

---

## PARTE 3 — Los 9 que el algoritmo odia (checklist)

> Fuente: video en español de un creador con 14 años en YouTube. Es el más sólido de todos
> (poco pitch — solo un "validador de nicho" por WhatsApp al final, ignorable). Usalo como
> checklist antes de subir cada tanda.

1. **Caos de temas (aún dentro del nicho).** No basta con "hacer historia". Saltar de Roma a
   los mayas a la WWII confunde al algoritmo: distinto avatar → no hacen click → cae el CTR →
   deja de empujarte y arranca de cero cada video. **Acción:** elegí UN micro-nicho, quemalo
   antes de rotar. (Para vos: misterios, o historia oscura, o tu veta LatAm/Chile.)

2. **Falta de personalidad en faceless.** YouTube se está cargando las "copias de copias".
   **Acción:** un tráiler de 30-60s en la home con tu voz/opinión, y apariciones/anotaciones
   puntuales. No hace falta cara en cada video. Tu raíz Maule/LatAm es justo la personalidad
   que un canal traducido no tiene.

3. **Videos vagos / temas globales sin ángulo.** "Así vivían en la antigua Roma" = saturado.
   **El nicho no te diferencia, te diferencia el ángulo.** (Ver el matiz crítico en §2.2.)

4. **Aprender tarde.** Subir 30-40 videos "por constancia" antes de mirar datos. Hoy se premia
   **testear rápido**: con 3-4 videos ya hay señal. **Acción (con tus ~11):** abrí
   YouTube Studio → CTR (>5% ok, abajo hay margen) y retención (debajo de 40% hay margen). Si
   tenés buen CTR + retención pero pocas visitas → problema de guion / audiencia no cualificada.

5. **Bajo impacto de sesión.** A YouTube le importa si la persona **se queda en la plataforma**
   al terminar tu video. **Acción:** pantallas finales encadenando a un video TUYO relacionado
   (no cualquiera — conectado con lo que acaban de ver). Esa cadena es oro.

6. **Canales sin confianza.** Cuenta nueva = YouTube no se fía. **Acción:** calentala ~5 días
   comportándote como humano (consumí el nicho, like, cerrar/abrir sesión) antes del 1er video.
   ⚠️ Si alguien te vende "dispositivos" o pagar para subir el trust score = estafa. Lo real es gratis.

7. **Hooks débiles.** Un hook es débil cuando cuestiona una creencia que la audiencia **no
   tiene**. El formato "por qué no consigues X como crees" pega cuando la gente ya se lo
   cuestiona; el truco es llevarlo a temas donde NO se lo cuestionan ("la forma en que fríes
   los huevos está mal"). **El hook es una promesa, no solo llamar la atención.**

8. **Packaging irrelevante.** Título + miniatura le hablan al **deseo del avatar**, no a la
   herramienta. (Canal de golf con logo de GPT en la miniatura = al golfista le da igual la IA.)
   **Acción:** vendé lo que van a aprender/sentir, no el "hecho con IA".

9. **Señales engañosas (la más importante).** YouTube ahora **analiza el video de verdad**:
   procesa audio, arma la transcripción, lee la miniatura, entiende de qué va como un humano.
   Los trucos de mismatch título/contenido están muertos. **Hacé bien el trabajo = te recompensa.**
   Corolario tranquilizador: si no tenés visitas, casi siempre es el contenido, no "mala suerte".

---

## PARTE 4 — Distribución multi-plataforma (reutilizar tus shorts)   **[NUEVO para Astilla]**

> El hueco más grande hoy: Astilla publica solo en YouTube. Esto es un candidato claro a
> módulo futuro del pipeline (salida multi-plataforma vía APIs). Parqueado en `IDEAS.md` —
> no entra sin tracción que lo reclame.

Lógica base de 2026: **creá una vez, publicá en todas.** Los creadores que reutilizan
bien postean 5-7 videos/semana repartidos entre plataformas produciendo solo 2-3
originales. Postear a una sola plataforma = dejar dos tercios de tu audiencia sin tocar.

Dos particularidades de `vestigios.historia` que cambian la prioridad:

- **Contenido evergreen** (la historia no depende de trends) → favorece plataformas con
  **búsqueda / descubrimiento perenne** por sobre las de tendencias. Un short de historia
  te puede dar views por meses o años.
- **Audiencia hispana (España + LatAm)** → en LatAm **Facebook sigue siendo gigante** y
  concentra justo el público que consume historia (25-45+). Es tu pick sorpresa.

### 4.1 Plataformas ordenadas por fit

**Prioridad alta:**
- **TikTok** — la más grande del formato (~1.600M usuarios/mes), disponible sin problema
  en Chile/LatAm. Favorece sonidos en tendencia y energía casual, pero tiene buscador
  propio → tu contenido evergreen se descubre por search, no solo por feed.
- **Instagram Reels** — +2.000M usuarios, la alternativa más directa a TikTok y la mayor
  audiencia integrada fuera de él. Premia lo visual pulido. Fuerte para descubrimiento.

**Prioridad media (según tiempo):**
- **Facebook Reels** — la plataforma más subestimada para audiencias sobre 30, y en LatAm
  sigue siendo enorme. Para historia es oro y casi nadie la trabaja. Mismos reels, cero
  esfuerzo extra.
- **Pinterest** (video / Idea Pins) — evergreen y searchable puro. La gente busca temas
  históricos ahí y los pines siguen trayendo tráfico meses después.

**Opcionales (cross-post gratis, poco esfuerzo):**
- **X / Threads / Bluesky** — hook punchy y alcance extra. No es el hábitat natural de la
  historia evergreen, pero cross-postear no cuesta nada.
- **Snapchat Spotlight / Kwai** — pagan, pero público más joven (Snap) u otro segmento
  LatAm (Kwai). Dejar para después.

### 4.2 Dos tips prácticos que importan más de lo que parece

1. **Nunca subas el mismo archivo con marca de agua.** Si subís a IG/Facebook un video con
   el logo de TikTok (o viceversa), el algoritmo lo penaliza por ser de otra plataforma.
   Exportá desde CapCut **sin marca de agua** y reutilizá ese master limpio en todas.
   Ideal: ajustar hook/caption por plataforma; el clip base puede ser el mismo.
   *(Astilla ya exporta master limpio — `short_musica.mp4` — así que esto sale gratis.)*
2. **Usá un scheduler** (Metricool, Buffer o similar) para programar el mismo short a varias
   plataformas de una. Es justo lo que Astilla debería cubrir: la salida multi-plataforma
   puede ser un módulo del pipeline vía APIs en vez de pagar un SaaS.

### 4.3 Recomendación honesta (no te disperses)

Con ~11 shorts y en plena búsqueda de pega, **no abras 8 plataformas.** El costo real no es
subir el video, es responder comentarios y sostener presencia en cada una. Objetivo acotado:

> **YouTube (donde ya estás) + TikTok + Instagram Reels + Facebook Reels**, las cuatro con el
> mismo master limpio, batcheadas y programadas en una sentada semanal. Cubre la mayor parte
> del alcance hispano con esfuerzo casi plano. Cuando alguna despegue, ahí metés energía.

Y ojo: con ~11 videos estás lejísimos de los umbrales de monetización de cualquier plataforma.
Ahora esto es para **construir audiencia y descubrir dónde pega tu contenido**, no para plata.

### 4.4 Horarios para publicar (bonus)

El timing importa **menos en shorts** que en long-form: el feed los distribuye por días/
semanas, así que un short a mala hora igual puede pegar. Igual, publicar cuando tu audiencia
está activa le da mejores señales en la primera hora. Ventanas generales 2026 (en **hora
local de tu audiencia**, no la tuya): almuerzo entre semana **12-3 PM**, tardes/noche
**6-9 PM**, mañanas de finde **9 AM-12 PM**. Días fuertes: **miércoles a viernes**; domingo
flojo. Pero **la consistencia le gana a la hora exacta.**

Tu complicación real: audiencia repartida en varios husos (España + LatAm). Solución:
1. **Elegí una región primaria** (si tu tracción viene de México, optimizá a hora de México,
   NO a tu hora de Constitución).
2. **Dejá que tus datos manden**: YouTube Studio → Analytics → **Audiencia** → "cuándo tus
   espectadores están en YouTube". Esa es TU ventana real. Con pocos videos aún no hay data;
   arrancá con las ventanas de arriba y afiná tras ~20 videos.

---

## PARTE 5 — Cómo encaja esto con Astilla y tu realidad

- **Astilla** = el pipeline codificado de la Parte 1.1. Lo que estos videos dan gratis es
  el **flujo de referencia** y los **detalles de tuning** (velocidad de voz, SFX, requisito
  transformativo). No inventar el pipeline: copiar el que ya funciona y automatizar los pasos.
- **`vestigios.historia`** = el caso de uso real para probar el pipeline con contenido propio.
- **Verdad incómoda:** estás en búsqueda activa de pega remota con una restricción autoimpuesta
  de no abrir proyectos nuevos durante los 90 días, y tu patrón conocido es abrir más rápido de
  lo que cerrás. Esto **no es un proyecto nuevo** (ya tenés vestigios.historia y Astilla scoped),
  así que está bien — PERO tratalo como un experimento acotado y batcheado, no como un segundo
  trabajo que te come las horas de postular. Si empieza a comerse el tiempo del job search, ese
  es el momento de pausarlo, no de escalarlo. El objetivo #1 sigue siendo la pega de 3-8x tu
  ingreso actual; esto es secundario hasta que eso esté cerrado.
