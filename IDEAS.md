# IDEAS — Parking lot

> Ideas fuera del alcance vigente (MANIFIESTO §2/§4). Diferir no es matar: esperan acá a que
> la **tracción** las reclame, sin presionar el backlog ni matar el timebox. Antes de mover
> una a producción, la pregunta es: **¿qué señal real la reclama hoy?**
> El foco vigente es guion + constancia + distribución (canal VESTIGIOS). No píxeles.

## Esperando tracción del canal

- **Pipeline 100% autónomo** (cron/lote con `ANTHROPIC_API_KEY` escribiendo los prompts sin
  Claude en sesión). *Reclama:* cadencia sostenida que supere lo manual (>1 short/día) o
  necesidad de producir sin operador.
- **Publicación automática a plataformas** (YouTube API, multi-plataforma TikTok/Reels).
  *Reclama:* volumen de publicación que haga doler el paso manual; hoy publicar a mano es
  además el momento de QA humano.
- **SFX por escena** (benchmark #7: música ya está, SFX no — whoosh, ambiente, impactos).
  *Reclama:* es la más barata de la lista; entra cuando un A/B o la retención sugiera que el
  sonido plano cansa. Candidata a próxima mejora de calidad.
- **Capa MCP (CASO-008):** exponer el motor como tools MCP para otros clientes/operadores.
  *Reclama:* un segundo usuario del motor que no sea esta sesión.
- **Generación premium para caras/manos/líquidos** (los 3 puntos ciegos de SDXL, ver
  [[manos-deformes-sdxl-y-fix-negativo]]). Presupuesto ~$3/short repartido por tipo: stills de
  arquitectura/objetos siguen GRATIS en SDXL Kaggle (el 70%, ya clava); solo los 2-3 planos con
  humano/líquido usan herramienta de pago. Reparto de editor: (a) **caras/personas** → imagen
  premium con mejor anatomía (Midjourney es lo que usan los canales de 8M vistas, o SDXL-API/Ideogram);
  (b) **manos** → **inpainting selectivo** (regenerar solo la mano, no la imagen entera — "vary region");
  (c) **líquidos** → ya se ven bien en movimiento con LTX i2v, el problema era el still base ambiguo →
  con still premium de base, el i2v sale bien. *Reclama:* tracción del canal + que la dirección-por-plano
  (silueta/fuera-de-cuadro/de-espaldas) deje de alcanzar. **Costo real hoy = ingeniería:** Midjourney no
  tiene API oficial (va por Discord), el inpainting necesita kernel nuevo → deuda técnica. Mientras tanto:
  **esquivar por dirección es gratis y es lo que hacen los pros** (benchmark 8M evita caras/manos de frente).

## Explícitamente descartadas salvo evidencia nueva

- **Foto-realismo / SDXL / Flux / GPU propia.** El benchmark de 8M vistas mostró que la
  ilustración pictórica **perdona más y cuesta menos**; perseguir píxeles ya quemó un tramo
  del proyecto. *Reclama:* solo datos de retención que muestren que el visual (no el guion)
  es el cuello de botella.

## Congeladas con el flujo hablante (CASO-009 en pausa)

- Enhancer **GFPGAN** · **head motion** (sin `--still`) · template de estudio
  (mic/auriculares) · feather del borde del matte · karaoke integrado end-to-end al flujo
  `hablante` · unificar `recorte.wav` entre hablante y ambiente · CASO-006 ajustar `ip_scale`
  (validar IP-Adapter en GPU). *Reclama:* que el formato talking-head vuelva al modo activo.

## Infraestructura

- **Reanudación tras desconexión (CASO-007, ADR-002).** *Reclama:* corridas largas en GPU
  remota de vuelta en el flujo activo (hoy LTX por API es corto y no la necesita).
- **Luma vía API de desarrollador** detrás del `PuertoEjecutor` (hoy Plan Plus consumidor =
  paso manual). *Reclama:* que LTX suba de precio o no alcance en calidad; hoy LTX cubre.
