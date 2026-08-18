# Design: novedades-sadofe-feriados-descuento

## Data

- `novedades_modulo.sadofe` BOOLEAN NOT NULL DEFAULT false (existentes = Semana).
- `novedades_feriado`: id, fecha DATE, nombre VARCHAR(200), AuditMixin. Unique active `(fecha)` WHERE `deleted_at IS NULL`.
- Alembic `0019_sadofe_feriados` revises `0018_modulo_produccion`. Drop/recreate `ck_novedades_novedad_tipo` to include `horas_a_descontar`.
- `novedades_servicio.concepto_liquidacion` INTEGER NULL. Alembic `0020_servicio_concepto_liquidacion` revises `0019`. No unique. Existing rows stay NULL.

## API

| Method | Path | Auth |
|--------|------|------|
| GET | `/feriados` | novedades reader (admin/rrhh/jefe) |
| POST | `/feriados` | admin/rrhh `{ fecha, nombre }` |
| PUT | `/feriados/{id}` | admin/rrhh |
| DELETE | `/feriados/{id}` | admin/rrhh soft-delete |
| GET/POST/PUT módulos | + `sadofe` | sin cambio de auth |
| GET/POST/PUT servicios | + `concepto_liquidacion` | sin cambio de auth |

Create feriado: 409 si fecha activa duplicada.

Pydantic: `concepto_liquidacion: int | None`; `0` y `None` → `NULL`; negativo → 422.

## Valor novedad

`novedad_valor_calculado(tipo, horas, valor_hora)`: si tipo = `horas_a_descontar` → negativo; si no, positivo. Usar en `_novedad_response` y `export_xls._novedad_row`.

Backend **no** valida módulo vs fecha (Q4=B). Riesgo: API bypass; aceptado.

Capital Humano **no** consume `concepto_liquidacion` en este change (Q19=E).

## UI Carga

- Cargar feriados junto al resto.
- `modulosVisibles` = módulos del servicio cuyo `sadofe` coincide con el día de `fecha_realizacion`.
- Si el módulo seleccionado deja de ser válido al cambiar fecha → limpiar `moduloId`.
- Combo tipo: + “Horas a descontar”; estimado con signo.

## UI Param

- Tab **Feriados** al lado de Períodos; modales como Módulos.
- Módulos: checkbox SADOFE junto a Producción.
- Servicios: botón **Nuevo servicio**; grilla `#id · nombre · activo` + concepto (`—` si NULL) + valor hora texto; editar/eliminar modales; Esc. Alta siempre `activo=true`. Edit incluye checkbox Activo. Sin edición inline de valor hora.

## Files

- alembic `0019_sadofe_feriados.py`, `0020_servicio_concepto_liquidacion.py`
- models, schemas, masters, helpers, router, export_xls
- `NovedadesParamPage.jsx`, `NovedadesCargaPage.jsx`
- tests + runbook
