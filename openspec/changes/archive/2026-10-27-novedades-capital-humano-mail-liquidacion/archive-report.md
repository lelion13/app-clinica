# Archive Report: novedades-capital-humano-mail-liquidacion

## Change Summary
- **Change Name:** `novedades-capital-humano-mail-liquidacion`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-10-27
- **Branch (impl):** `medicos` (rev `0034_liquidacion_mail`)

## Delivered
1. Sync Integrando `MAIL` → `novedades_profesional.email`.
2. Capital Humano: envío liquidaciones por mail (período cerrado, `admin`/`rrhh`).
3. Lote + worker throttled (`MAIL_LIQUIDACION_DELAY_SECONDS`); Total general + Detalle CH; sin PDF/CC.
4. Precheck bloquea lote si falta mail; contadores + reintentar fallidos; lock tras 100% OK.
5. Tests unitarios + runbook + env examples.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: Email catálogo; Envío mail liquidación; Ciclo de vida lote. MODIFIED: Catálogo profesionales; Sync HTTP; Pantalla Capital Humano. |

## Drift check
Implementation matched delta. Stable spec catch-up on archive date.

## Verification
Implemented on `medicos`; unit tests for email/body helpers passed at apply time.
