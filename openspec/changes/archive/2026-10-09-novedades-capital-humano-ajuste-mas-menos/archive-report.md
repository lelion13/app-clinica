# Archive Report: novedades-capital-humano-ajuste-mas-menos

## Change Summary
- **Change Name:** `novedades-capital-humano-ajuste-mas-menos`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-10-09

## Delivered
1. Botón **Ajuste +/-** / **Anular Ajuste +/-** a la derecha de Importe a descontar; período cerrado; `admin`/`rrhh`.
2. Import Excel (headers `Legajo`, `Nombre y Apellido`, `Sector`, `Monto` con signo).
3. Lote independiente `ajuste_mas_menos_lote_id` (rev `0029_ajuste_mas_menos_lote`); coexistencia con descuento; Anular selectivo.
4. Negativos: misma waterfill + tope que Importe a descontar; positivos: misma waterfill **sin** tope.
5. Todo-o-nada + modal de errores; comentario con importe firmado.
6. Tests unitarios + runbook.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: UI Ajuste +/-; Import Excel Ajuste +/-; Reparto multi-servicio Ajuste +/-. MODIFIED: UI Importe a descontar (orden, coexistencia, Anular no toca Ajuste +/-). |

## Drift check
Implementation matched delta (service/API/UI/migration/runbook). No code/doc gap requiring changes before archive.

## Verification
Implemented (2026-10-02); documented and archived 2026-10-09. Unit tests for signed waterfill passed at implementation time.
