# Design: Integración de APIs Prácticas e Internaciones en Capital Humano

## Technical Approach

Extend the existing Capital Humano synchronization flow when the user clicks **Actualizar**. The backend will perform an atomic sequence of HTTP GET requests to 3 endpoints:
1. `NOVEDADES_BONOS_RESUMEN_URL`
2. `NOVEDADES_BONOS_PRACTICAS_URL`
3. `NOVEDADES_BONOS_INTERNACIONES_URL`

If all requests succeed, the backend replaces the period snapshots in a single database transaction (`NovedadesBonoCantidad`, `NovedadesPracticaCantidad`, `NovedadesInternacionCantidad`).
The amounts are computed at calculation time (`build_capital_humano_rows`) using unit tariffs configured in `NovedadesProduccionTarifa` and added to `total_produccion`.

## Architecture Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|--------------------------|-----------|
| **Snapshot storage** | Dedicated tables `novedades_practica_cantidad` and `novedades_internacion_cantidad` | Reusing `novedades_bono_cantidad` | Prácticas and internaciones have distinct payload dimensions (`centro+servicio` vs `sucursal`) |
| **Tariff management** | Catalog options in `novedades_bono_opcion` + `novedades_produccion_tarifa` | Hardcoded values or new dedicated tariff tables | Reuses the entire existing Parametrización → Producción ABM UI and backend endpoints without duplicating code |
| **Atomic Sync** | Fetch all 3 remote APIs before database writes; single commit | Independent syncs per button / partial commits | Prevents inconsistent state and ensures all production sources are aligned to the same period |
| **Eligibility Rule** | Con módulos: todos los bonos, prácticas e internaciones. Sin módulos: bonos especiales (`DEA,DEP,CAP,CAI`), prácticas e internaciones | Apply to all professionals indiscriminately | Respects explicit business rule that practices and internaciones apply while non-special bonos (e.g. GUA) are ignored for doctors without modules |

## Data Flow

```
User clicks "Actualizar" (Capital Humano)
                 │
                 ▼
     POST /capital-humano/bonos/import {periodo_id}
                 │
                 ├──► GET NOVEDADES_BONOS_RESUMEN_URL (Bearer Token, fecha_desde/hasta)
                 ├──► GET NOVEDADES_BONOS_PRACTICAS_URL (Bearer Token, fecha_desde/hasta)
                 └──► GET NOVEDADES_BONOS_INTERNACIONES_URL (Bearer Token, fecha_desde/hasta)
                 │
            All 3 OK?
           ┌─────┴─────┐
          YES          NO ──► Raise 502/422 (Rollback, zero changes)
           │
     Atomic DB Transaction:
     - Delete & Insert NovedadesBonoCantidad
     - Delete & Insert NovedadesPracticaCantidad
     - Delete & Insert NovedadesInternacionCantidad
     - Commit DB
                 │
                 ▼
     Return summary (bonos, prácticas, internaciones)
                 │
                 ▼
     GET /capital-humano (Recalculate grid with valorized production)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/core/config.py` | Modify | Add `NOVEDADES_BONOS_PRACTICAS_URL`, `NOVEDADES_BONOS_INTERNACIONES_URL` and timeouts |
| `backend/app/models/novedades.py` | Modify | Add `NovedadesPracticaCantidad` and `NovedadesInternacionCantidad` models |
| `backend/alembic/versions/0024_practicas_internaciones.py` | Create | Alembic migration for the 2 new snapshot tables |
| `backend/app/schemas/novedades.py` | Modify | Add schemas for prácticas/internaciones responses and breakdown |
| `backend/app/services/novedades/bonos_import.py` | Modify | Add fetchers, normalizers, and atomic multi-sync logic |
| `backend/app/services/novedades/produccion_tarifas.py` | Modify | Support práctica and internación tariff options and labels |
| `backend/app/services/novedades/capital_humano.py` | Modify | Incorporate prácticas/internaciones into totals, eligibility, and detail breakdown |
| `backend/app/services/novedades/export_xls.py` | Modify | Include valorized prácticas and internaciones in XLS exports |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Modify | Display prácticas and internaciones in modal Detalle and update banner |
| `docs/runbook.md`, `.env.example`, `.env.prod.example` | Modify | Document new environment variables |

## Interfaces / Contracts

```python
class PracticaDetalleItem(BaseModel):
    centro: str
    servicio: str
    cantidad: int
    valor_unitario: int
    subtotal: int

class InternacionDetalleItem(BaseModel):
    sucursal: str
    cantidad: int
    valor_unitario: int
    subtotal: int

class BonosImportResponse(BaseModel):
    received: int
    matched: int
    solo_bonos: int
    columns: int
    ignored: int
    practicas_received: int = 0
    practicas_matched: int = 0
    internaciones_received: int = 0
    internaciones_matched: int = 0
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Multi-API fetch, normalization, and rollback on 1 failure | Mock HTTP calls in pytest |
| Unit | Eligibility rules (módulos vs special services) | Test `build_capital_humano_rows` with various professional scenarios |
| Unit | Valorization and tariff application | Test calculations when tariff is present vs missing (subtotal 0) |
| Integration | Detalle modal and XLS export | Verify returned JSON payload and generated Excel columns |

## Migration / Rollout

Alembic migration `0024_practicas_internaciones` creates the snapshot tables with indexes on `periodo_id`. No breaking data migration on existing tables.
