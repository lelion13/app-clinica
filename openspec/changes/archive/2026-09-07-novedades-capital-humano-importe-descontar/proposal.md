# Proposal: novedades-capital-humano-importe-descontar

## Intent

Permitir a Capital Humano importar un Excel de descuentos por legajo (período cerrado), creando ajustes negativos como **Agregar importe**, con anulación del lote importado y validación todo-o-nada.

## Scope

### In Scope
- Botón **Importe a descontar** (antes de Descargar liquidación); con lote activo → **Anular descuento**.
- Excel columnas exactas: `Legajo`, `Nombre y Apellido`, `Sector`, `Monto`.
- Import `admin`/`rrhh`, solo período **cerrado**; re-import exige anular antes.
- Importe = `-abs(Monto)`; comentario = `Legajo - Nombre - Sector - MontoNeg` (truncado 500).
- Waterfill multi-servicio (mayor cargas primero; resto tras cargas al último servicio); tope cargas+producción; solo-prod → 1 ajuste sin servicio.
- Todo-o-nada; modal centrado con **todos** los errores (legajo inválido/duplicado, monto 0, tope/total negativo, etc.).
- Marca de lote en ajustes para Anular selectivo.
- Alinear liquidación para respetar `servicio_id` de estos ajustes (si aplica).

### Out of Scope
- Cambiar UX de Agregar importe manual.
- Validar Nombre/Sector contra catálogo.
- Plantilla descargable (no pedida).
- Import en período abierto.

## Approach

1. Migración: `descuento_lote_id` (nullable UUID) en `novedades_ajuste_capital`.
2. Service: parse openpyxl → validar todas las filas contra grilla CH → waterfill → commit lote; anular soft-delete por `periodo_id`+lote.
3. API: import multipart, anular, estado “tiene descuento”.
4. UI: botón toggle + file picker + modal errores.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/app/models/novedades.py` + Alembic | Modified/New |
| `backend/app/services/novedades/` (import + CH) | New/Modified |
| `backend/app/api/routers/novedades.py` | Modified |
| `frontend/.../NovedadesXlsPage.jsx` | Modified |
| `liquidacion_export.py` | Modified (servicio_id) |
| `docs/runbook.md` | Modified |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Liquidación ignora waterfill | Med | Mapear ajuste→concepto por `servicio_id` |
| Comentario truncado | Low | Documentar; aceptar |
| Empate de servicios | Low | Aceptado (Q23) |

## Rollback Plan

Revertir migración/código; soft-deleted ajustes del lote no se recrean solos. Anular en UI limpia el lote activo.

## Dependencies

- Grilla CH + producción valorizada (existente).
- Modelo ajustes + soft-delete AuditMixin.

## Success Criteria

- [ ] Import cerrado crea ajustes negativos por legajo/servicio según waterfill.
- [ ] Error cualquiera → 0 filas impactadas + modal con todos los casos.
- [ ] Anular quita solo el lote; botón vuelve a Importe a descontar.
- [ ] Manual Agregar importe intacto.
