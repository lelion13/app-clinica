# Archive Report: novedades-servicio-especialista-plus

## Change Summary
- **Change Name:** `novedades-servicio-especialista-plus`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-10-02

## Delivered
1. Migration `0028_servicio_especialista`: servicio boolean `especialista` (default OFF).
2. Parametrización: checkbox **Especialista** en ABM servicios (independiente de Activo).
3. Alta de módulo: +20% solo si `es_especialista` **y** `servicio.especialista`; edición no reaplica plus.
4. Capital Humano Detalle Cargas: columna **Plus esp.** (Sí si valor ≈ catálogo × 1.20); sin columna en Excel.
5. Ajuste UI Detalle: tabla Cargas con scroll (modal overflow) para no romper layout.
6. Script ops `backend/scripts/recalc_especialista_plus.py` (dry-run, `--apply`, `--csv`, `--ids`).
7. Tests + runbook.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: Flag Especialista en servicio; Plus esp. en Detalle CH. MODIFIED: Servicios y módulos (campo `especialista`); Plus 20% (gate profesional + servicio, reglas de edición); Detalle unificado (cross-ref Plus esp.). |

## Verification
Implementado y validado en uso (2026-10). Usuario confirmó comportamiento en carga y Detalle.

## Ops notes (prod)
- Período Septiembre 2026 (`periodo_id=3`): dry-run del script mostró 14 filas candidatas; se aplicó **corrección puntual SQL** solo en 5 asignaciones CMG GUARDIA PISO (legajo 3875) que tenían plus erróneo con servicio sin flag — ids 1706, 1833, 1893, 1769, 1958 → `valor=319600`. No se realinearon filas UTIA vía recalc masivo.
- Para recalc acotado post-deploy: `recalc_especialista_plus.py --ids …`.
