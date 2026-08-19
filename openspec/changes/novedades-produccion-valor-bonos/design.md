# Design: novedades-produccion-valor-bonos

## Technical Approach

Separar **hechos** (cantidades importadas por período) de **precios** (tarifas maestras en Param). La valorización es un join en tiempo de lectura entre snapshot de bonos y catálogo de tarifas; no se persiste subtotal por profesional/período.

## Architecture Decisions

### Decision: FK a `novedades_bono_opcion` vs copiar 4 strings
**Choice**: FK `opcion_id` UNIQUE + denormalizar 4 campos en respuesta API desde la opción.
**Alternatives considered**: tabla con unique `(centro, servicio, semana, horario)` sin FK.
**Rationale**: Q9 exige selector desde opciones detectadas; evita drift de strings y reutiliza unicidad existente.

### Decision: Valorización en lectura, no en import
**Choice**: calcular subtotales al listar Capital Humano / exportar XLS.
**Alternatives considered**: persistir `monto_bonos` al importar.
**Rationale**: cambiar tarifa en Param debe reflejarse sin re-import; snapshot solo guarda cantidades.

### Decision: Dos columnas por opción
**Choice**: extender lista `columns` con entradas `kind: "cantidad" | "subtotal"` enlazadas por `opcion_key`.
**Alternatives considered**: solo columna total bonos.
**Rationale**: Q4 explícito; desglose auditable.

### Decision: Sin tarifa → subtotal 0 + banner
**Choice**: no bloquear; flag `opciones_sin_tarifa: list[str]` (keys) en grid response.
**Rationale**: Q5 + Q11.

## Data Model

```text
novedades_produccion_tarifa
  id              PK
  opcion_id       FK → novedades_bono_opcion.id  UNIQUE NOT NULL
  valor_unitario  INTEGER NOT NULL  (≥ 0)
  + AuditMixin (created_at, updated_at, deleted_at, created_by, updated_by)
```

Índice: unique parcial en `opcion_id` WHERE `deleted_at IS NULL` (o unique simple si soft-delete no permite re-alta misma opción — preferir unique en `opcion_id` y hard semantics: delete soft, create rechaza si existe activa).

## Data Flow

```text
1. Import bonos → upsert novedades_bono_opcion + novedades_bono_cantidad
2. Param Producción → CRUD novedades_produccion_tarifa (admin/rrhh)
3. GET capital-humano:
   a. load_bonos_snapshot → columns (opciones del período)
   b. load tarifas activas → map key → valor_unitario
   c. por fila/prof: cantidad desde snapshot; subtotal = qty × valor (0 si missing)
   d. monto_total = cargas + ajustes + sum(subtotales)
   e. opciones_sin_tarifa = column keys del período sin entrada en map
4. Export XLS: mismos datos que grid
```

## API Contracts (nuevo / modificado)

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/novedades/produccion-tarifas` | admin, rrhh | Lista tarifas con 4 campos + valor |
| POST | `/novedades/produccion-tarifas` | admin, rrhh | Alta: `opcion_id`, `valor_unitario` |
| PUT | `/novedades/produccion-tarifas/{id}` | admin, rrhh | Editar solo `valor_unitario` |
| DELETE | `/novedades/produccion-tarifas/{id}` | admin, rrhh | Soft-delete |
| GET | `/novedades/bono-opciones` | admin, rrhh | Opciones para selector (excluir ya tarifadas en create) |

### Schema extensions

```python
class BonoColumnaResponse:
    key: str           # ej. "CMG|CAP|LUNES|DIA" o "CMG|CAP|LUNES|DIA|subtotal"
    label: str
    centro, servicio, semana, horario: str
    kind: Literal["cantidad", "subtotal"] = "cantidad"
    opcion_key: str    # key base de la opción (sin sufijo)

class CapitalHumanoRowResponse:
    ...
    bonos: dict[str, int]              # cantidades por opcion_key
    bonos_subtotales: dict[str, int]   # subtotales por opcion_key
    monto_bonos: int                   # suma subtotales (conveniencia)

class CapitalHumanoGridResponse:
    columns: list[BonoColumnaResponse]
    rows: list[CapitalHumanoRowResponse]
    opciones_sin_tarifa: list[str] = []  # opcion_keys del período sin tarifa
```

`monto_total` pasa a ser Decimal/int según convención existente: cargas + ajustes + monto_bonos.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/novedades.py` | Modify | `NovedadesProduccionTarifa` |
| `backend/alembic/versions/0021_produccion_tarifa.py` | Add | Migración |
| `backend/app/schemas/novedades.py` | Modify | Schemas tarifa + grid |
| `backend/app/services/novedades/produccion_tarifas.py` | Add | CRUD + helpers |
| `backend/app/services/novedades/capital_humano.py` | Modify | Valorización + exports |
| `backend/app/api/routers/novedades.py` | Modify | Rutas |
| `frontend/.../NovedadesParamPage.jsx` | Modify | Tab Producción |
| `frontend/.../NovedadesXlsPage.jsx` | Modify | Columnas + banner |
| `backend/tests/test_produccion_tarifas.py` | Add | Tests |
| `backend/tests/test_bonos_import.py` | Modify | Tests valorización CH |
| `docs/runbook.md` | Modify | Tab + fórmula |

## Frontend — Tab Producción

- Insertar tab `{ id: "produccion", label: "Producción" }` **después** de Módulos.
- Help text: “Tarifas para valorizar bonos importados. No confundir con el flag Producción del módulo.”
- Grilla filas: label legible de opción (4 campos) + `valor_unitario` + botones editar/eliminar.
- Modal **Nueva producción**: `<select>` opciones desde `GET /bono-opciones?sin_tarifa=1`; input entero valor; Cancelar/Cargar; Esc cierra.
- Modal editar: solo `valor_unitario`.
- Modal eliminar: confirmación con resumen opción + valor.

## Frontend — Capital Humano

- Renderizar columnas en orden: por cada opción, columna cantidad luego subtotal (headers derivados de `label` + sufijo).
- Banner amarillo/info si `opciones_sin_tarifa.length > 0`: “Hay opciones de bonos sin tarifa en Producción. Los subtotales se muestran en 0.”
- Actualizar texto ayuda con nueva fórmula de total.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | CRUD tarifa, unique opcion_id | pytest service |
| Unit | subtotal = qty × valor; 0 sin tarifa | pytest capital_humano |
| Unit | monto_total incluye bonos | pytest |
| Integration | 403 jefe_medico en rutas tarifa | pytest router |
| Export | XLS con subtotales | pytest bytes/headers |

## Migration / Rollout

1. Deploy backend + `alembic upgrade head`.
2. Deploy frontend.
3. Cargar tarifas en Param antes de confiar en totales (banner guía hasta completar).

## Open Questions

- [ ] ¿Archivar `capital-humano-bonos-servicios-especiales` en paralelo o después de este change?
- [ ] v2: listado “opciones sin tarifa” también en tab Producción (fuera de scope v1).
