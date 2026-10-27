# Delta Spec: novedades-capital-humano-mail-liquidacion

## ADDED Requirements

### Requirement: Email en catálogo de profesionales Novedades

Each row in `novedades_profesional` MUST support an optional **`email`** (string, max 255, nullable).

The professional HTTP sync MUST map remote field **`MAIL`** (also accept lowercase `mail`) into `email`: trim whitespace; empty or absent → store `NULL`; MUST NOT fail the sync row if `MAIL` is missing. Sync MUST refresh `email` on every successful upsert the same way as `legajo`.

List/detail API responses that expose the Novedades professional MUST include `email` when the schema already returns catalog fields (MAY remain omitted from Carga pickers that only need id/name).

Valid email for liquidación send MUST be a non-empty trimmed value that contains `@` and a domain part (basic format check). Invalid or NULL MUST count as “sin mail válido”.

#### Scenario: Sync persiste MAIL

- GIVEN respuesta Integrando con `CODPROF=007` y `MAIL=aaa@bbb.com`
- WHEN corre sync de profesionales Novedades
- THEN el catálogo MUST guardar `email=aaa@bbb.com` para ese CODPROF

#### Scenario: Sync sin MAIL

- GIVEN fila remota sin `MAIL` o con `MAIL` vacío
- WHEN corre sync
- THEN `email` MUST quedar NULL
- AND la fila MUST NOT fallar por eso

### Requirement: Envío mail liquidación desde Capital Humano

`admin` and `rrhh` MUST be able to start a **liquidación mail lot** from the Capital Humano screen when the selected period is **closed**.

The toolbar MUST show a control (e.g. **Enviar liquidaciones por mail**) that:

1. Is disabled when the period is open or no period is selected.
2. On click, runs a **precheck**: every professional in the Capital Humano grid for that period MUST have a valid `email`. If any lack a valid email, the system MUST block the entire lot (no emails sent) and MUST list the offending professionals (legajo/name at minimum).
3. If precheck passes, MUST open a confirmation modal showing the count **N** of recipients; Cancel MUST do nothing; Confirm MUST enqueue the lot and MUST NOT send all emails inside the HTTP request.

Destinatarios MUST be exactly the professionals that appear as rows in the Capital Humano listado for that period (same eligibility/population as `GET /novedades/capital-humano`). Professionals with **Total general = 0** MUST be included.

Each recipient MUST receive **one** email (To = their `email` only; no CC/BCC). Body MUST be HTML and/or plain text (no PDF attachment) and MUST include:

- Period identification
- **Importe a facturar** = **Total general** of that CH row
- Detail sections equivalent to the Capital Humano **Detalle** modal for that professional/period (cargas, producción/bonos, prácticas/internaciones as applicable, ajustes)

Sending MUST use a **lot + queued processing + throttle** over the existing app SMTP (one message at a time; configurable delay between sends). Each recipient MUST have status `pending` | `sent` | `failed`. Soft-deleted / anulado source rows follow the same rules as CH Detalle (exclude anulados).

UI on Capital Humano MUST show lot counters: enviados / pendientes / fallidos for the period’s current lot, and a **Reintentar fallidos** action when `failed` &gt; 0.

#### Scenario: Período abierto no envía

- GIVEN período open seleccionado
- WHEN mira la toolbar de Capital Humano
- THEN el control de envío MUST estar deshabilitado

#### Scenario: Falta un mail bloquea el lote

- GIVEN período cerrado y un profesional de la grilla sin `email` válido
- WHEN admin/rrhh intenta iniciar el envío
- THEN MUST bloquearse el lote
- AND MUST NOT encolarse ni enviarse ningún mail
- AND MUST listarse al menos ese profesional

#### Scenario: Confirmación con N

- GIVEN período cerrado y todos con mail válido (N=237)
- WHEN confirma el modal
- THEN MUST crearse un lote con 237 destinatarios `pending`
- AND la respuesta HTTP MUST retornar sin haber enviado los 237 SMTP en ese request

#### Scenario: Contenido del mail

- GIVEN profesional con cargas, bonos y ajustes
- WHEN se envía su mail del lote
- THEN el cuerpo MUST mostrar Total general
- AND MUST incluir el desglose equivalente a Detalle CH
- AND MUST NOT incluir PDF adjunto
- AND MUST NOT ir en copia a otros destinatarios

#### Scenario: Total cero se incluye

- GIVEN profesional en la grilla con Total general = 0 y mail válido
- WHEN se confirma el lote
- THEN MUST estar incluido y recibir mail con importe 0 y su detalle

### Requirement: Ciclo de vida del lote de mails de liquidación

For a given closed period there MUST be at most one **active** mail lot lifecycle:

- While the lot has `pending` or `failed` recipients, operators MUST be able to **retry only `failed`** (re-queue those rows to `pending` and continue throttled send). They MUST NOT start a brand-new full lot that re-sends already `sent` recipients.
- When the lot reaches **100% `sent`** (zero pending/failed), the period MUST be **locked for mail**: starting another full lot MUST be rejected. There is no exceptional re-send in this change.

Progress MUST remain visible via counters after refresh. Worker failures (SMTP errors) MUST mark the recipient `failed` without aborting the rest of the lot.

#### Scenario: Reintentar solo fallidos

- GIVEN lote con 200 `sent` y 5 `failed`
- WHEN admin pulsa Reintentar fallidos
- THEN solo esos 5 MUST volver a `pending` / reenviarse
- AND los 200 `sent` MUST NOT recibir otro mail

#### Scenario: Lote completo bloquea reenvío

- GIVEN lote del período con todos `sent`
- WHEN admin intenta iniciar envío de nuevo
- THEN MUST rechazarse
- AND MUST NOT crearse un segundo lote

#### Scenario: Un fallo no detiene el lote

- GIVEN 10 pending y el 3º SMTP falla
- WHEN el worker continúa
- THEN ese destinatario MUST quedar `failed`
- AND el resto MUST seguir procesándose

## MODIFIED Requirements

### Requirement: Catálogo de profesionales Novedades

(Previously: stored fields include NOMBRES, CODPROV, LEGAJO, es_especialista — no email.)

In addition to existing fields, the catalog MUST store optional **`email`** as defined in Requirement “Email en catálogo de profesionales Novedades”. Catalog remains sync-only (no manual email edit in Param UI in this change).

#### Scenario: Catálogo expone email tras sync

- GIVEN profesional sincronizado con MAIL
- WHEN se consulta el registro de catálogo
- THEN MUST incluir el email persistido

### Requirement: Sincronización HTTP de profesionales

(Previously: upsert refreshes name/CODPROV/legajo; no MAIL.)

In addition to existing sync behavior, each successful upsert MUST refresh **`email`** from remote **`MAIL`** (trim; empty/absent → NULL) as defined in Requirement “Email en catálogo de profesionales Novedades”.

#### Scenario: Sync actualiza email

- GIVEN profesional local con email viejo
- AND remote MAIL nuevo
- WHEN corre sync
- THEN email local MUST actualizarse al valor remoto

### Requirement: Pantalla Capital Humano

(Previously: toolbar with Actualizar, Motivo, Con novedad, exports, ajustes actions — no liquidación mail.)

In addition to existing toolbar behavior, Capital Humano MUST expose the liquidación mail controls defined in Requirements “Envío mail liquidación desde Capital Humano” and “Ciclo de vida del lote de mails de liquidación” (`admin`/`rrhh`, closed period only).

#### Scenario: Botón visible para RRHH

- GIVEN `rrhh` con período cerrado
- WHEN abre Capital Humano
- THEN MUST ver el control de envío de liquidaciones por mail
