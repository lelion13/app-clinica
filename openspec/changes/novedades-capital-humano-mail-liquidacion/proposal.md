# Proposal: Envío mail liquidación Capital Humano

## Intent

Permitir a `admin`/`rrhh` enviar, desde **Capital Humano**, un correo por profesional con el **Total general** y el mismo desglose del modal Detalle, cuando el período está cerrado — sin disparar un blast SMTP que dispare spam/rate-limit (~200+ mails).

## Scope

### In Scope
- Columna `email` en `novedades_profesional` + mapeo sync Integrando campo **`MAIL`**.
- Botón en Capital Humano (período cerrado): modal con N destinatarios → encolar lote.
- Un mail por profesional del listado CH (misma población que la grilla), cuerpo HTML/texto con Total general + detalle Detalle CH; sin PDF; sin CC/BCC.
- Incluir profesionales con Total = 0.
- Validación: si falta algún mail válido → bloquear todo el lote.
- Lote + worker + throttle sobre SMTP existente; estados por destinatario; UI con contadores + reintentar solo `failed`.
- Si el lote terminó 100% OK → no se puede volver a enviar ese período.

### Out of Scope
- PDF / adjuntos.
- ESP externo (SendGrid/SES/etc.).
- Reenvío completo tras lote OK.
- Preview del cuerpo del mail.
- Copia a RRHH/admin.
- Envío con período abierto.

## Approach

1. Extender sync + modelo con `email` (nullable hasta que Integrando lo provea).
2. Al confirmar: snapshot de destinatarios del CH del período → filas de lote (`pending|sent|failed`).
3. Worker/procesamiento asíncrono con throttle (intervalo configurable por env) usando `email_service` actual.
4. Endpoints: crear lote (precheck mails), status contadores, retry failed.
5. UI en `NovedadesXlsPage` (Capital Humano): botón, modal, contadores, reintentar.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `novedades_profesional` + `prof_sync` | Modified | Campo `email` + sync |
| `email_service` / nuevo service lote | Modified/New | Envío throttled + plantilla liquidación |
| API Capital Humano | New | Lote / status / retry |
| `NovedadesXlsPage.jsx` | Modified | Botón + modal + contadores |
| Alembic | New | Columna email + tablas de lote |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Rate-limit / spam SMTP | Med | Throttle + un destinatario por mensaje + SPF/DKIM del dominio |
| Integrando sin mail aún | Med | Columna nullable; precheck bloquea lote; sync listo cuando confirmen JSON |
| Request HTTP largo | Low | Encolar y devolver; worker aparte del request |
| Reenvío accidental | Low | Período bloqueado tras lote 100% OK; solo retry failed |

## Rollback Plan

- Feature flag o quitar botón + endpoints.
- Revert migración (drop tablas lote / columna email) si no hay dependencia en prod.
- Mails ya enviados no se “deshacen”; documentar en runbook.

## Dependencies

- API Integrando (`NOVEDADES_PROF_SYNC_URL`) expone `MAIL` por profesional (confirmado).
- SMTP configurado (`SMTP_*`) y reputación del dominio (SPF/DKIM/DMARC operativos).

## Success Criteria

- [ ] Con período cerrado, `admin`/`rrhh` encola un lote tras modal con N.
- [ ] Sin mail válido en algún profesional del listado → 422/bloqueo, cero envíos.
- [ ] Cada profesional recibe un mail con Total general + desglose Detalle CH.
- [ ] Contadores reflejan pending/sent/failed; retry solo failed.
- [ ] Lote 100% OK → no se puede iniciar otro lote para ese período.
- [ ] Sync persiste `email` cuando Integrando lo envía.
