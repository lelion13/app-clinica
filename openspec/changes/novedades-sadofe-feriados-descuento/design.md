# Design: novedades-sadofe-feriados-descuento

## Data

- `novedades_modulo.sadofe` BOOLEAN NOT NULL DEFAULT false (existentes = Semana).
- `novedades_feriado`: id, fecha DATE, nombre VARCHAR(200), AuditMixin. Unique active `(fecha)` WHERE `deleted_at IS NULL`.
- Alembic `0019_sadofe_feriados` revises `0018_modulo_produccion`. Drop/recreate `ck_novedades_novedad_tipo` to include `horas_a_descontar`.

## API

| Method | Path | Auth |
|--------|------|------|
| GET | `/feriados` | novedades reader (admin/rrhh/jefe) |
| POST | `/feriados` | admin/rrhh `{ fecha, nombre }` |
| PUT | `/feriados/{id}` | admin/rrhh |
| DELETE | `/feriados/{id}` | admin/rrhh soft-delete |
| GET/POST/PUT módulos | + `sadofe` | sin cambio de auth |

Create feriado: 409 si fecha activa duplicada.

## Valor novedad

`novedad_valor_calculado(tipo, horas, valor_hora)`: si tipo = `horas_a_descontar` → negativo; si no, positivo. Usar en `_novedad_response` y `export_xls._novedad_row` (Capital Humano consume esas filas).

Backend **no** valida módulo vs fecha (Q4=B). Riesgo: API bypass; aceptado.

## UI Carga

- Cargar feriados junto al resto.
- `modulosVisibles` = módulos del servicio cuyo `sadofe` coincide con el día de `fecha_realizacion` (sáb/dom/feriado ⇒ SADOFE; resto ⇒ Semana). Día con `new Date(y, m-1, d)` local.
- Si el módulo seleccionado deja de ser válido al cambiar fecha → limpiar `moduloId`.
- Combo tipo: + “Horas a descontar”; estimado con signo.

## UI Param

- Tab **Feriados** al lado de Períodos.
- Grilla + **Nuevo feriado** / editar / eliminar (modales Cancelar/Cargar|Guardar|Eliminar; Esc).
- Módulos: checkbox SADOFE junto a Producción (create + edit).

## Files

- alembic `0019_sadofe_feriados.py`
- models, schemas, masters (feriados), helpers (valor), router, export_xls
- `NovedadesParamPage.jsx`, `NovedadesCargaPage.jsx`
- tests + runbook
