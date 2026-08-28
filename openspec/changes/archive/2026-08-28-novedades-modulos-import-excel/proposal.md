# Proposal: Importación masiva de módulos (Excel)

## Intent

Permitir cargar muchos módulos de una vez desde Excel en Parametrización (tab Módulos), con plantilla que ya trae los servicios existentes como desplegable, y feedback claro si falla (todo o nada).

## Scope

### In Scope

- Botón **Plantilla de importación** → descarga `.xlsx` con columnas + data validation de servicios (Sí/No para producción/SADOFE).
- Botón **Carga masiva** → sube el Excel; valida todas las filas; si hay error **no importa ninguna**; modal con fila + motivo.
- Un servicio por fila (nombre desde desplegable).
- Duplicado por descripción (activo) → error de esa fila.
- Valor vacío → 0; comentario opcional.
- Solo `admin` / `rrhh`.

### Out of Scope

- Import masivo de servicios.
- Multi-servicio por fila.
- Import parcial (commit de filas válidas si otras fallan).
- Cargas transaccionales / Limpiar cargas.

## Approach

`openpyxl`: plantilla con hoja de datos + hoja oculta/lista de servicios + DataValidation. Import: parse → validate all → commit all or none. UI en tab Módulos.

## Risks

- Matching servicio por nombre (case/espacios).
- Excel con servicios desactualizados vs DB al momento del upload.

## Success Criteria

- [ ] Plantilla descarga con dropdown de servicios activos.
- [ ] Carga masiva todo-o-nada + modal de errores por fila.
- [ ] Filas OK crean módulos asociados a 1 servicio.

## Survey

Cerrada en `decisions.md` (Q1–Q6).
