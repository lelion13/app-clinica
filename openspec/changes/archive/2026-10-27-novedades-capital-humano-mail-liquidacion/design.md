# Design: novedades-capital-humano-mail-liquidacion

## Architecture

1. **Sync**: `prof_sync` maps Integrando `MAIL` → `novedades_profesional.email` (nullable).
2. **Lot tables**: one lote per `periodo_id`; destinatarios with status `pending|sent|failed`.
3. **API** (`admin`/`rrhh`, closed period):
   - `GET .../mail-liquidacion/status?periodo_id=`
   - `POST .../mail-liquidacion` — precheck mails → create lote → start worker
   - `POST .../mail-liquidacion/retry-failed`
4. **Worker**: daemon thread + `SessionLocal`; throttle via `MAIL_LIQUIDACION_DELAY_SECONDS` (default 3); in-process set avoids duplicate workers per lote.
5. **Mail body**: plain text (+ optional HTML alternate) built from CH row + grilla cargas + ajustes; Total general; no PDF; signature via existing `email_service`.
6. **UI**: Capital Humano toolbar — button, confirm modal (N), missing-email modal, counters + retry.

## Data

- `novedades_profesional.email` VARCHAR(255) NULL
- `novedades_liquidacion_mail_lote` (periodo_id UNIQUE)
- `novedades_liquidacion_mail_item` (lote_id, professional_id, email snapshot, total_general, status, error, sent_at)
