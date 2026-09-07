# Decisions: novedades-carga-novedad-extra

## Survey (closed)

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Sin tildar / tildado | Sin tildar = hoy (skip check, POST directo). Tildado = modal force **sin** API externo |
| Q2 | No permitir horas | **A** — ocultar/deshabilitar bloque novedad; solo carga **módulo** vía force |
| Q3 | Persistencia | Solo `motivo_sin_produccion` / `observacion_sin_produccion` (sin flag nuevo) |
| Q4 | Visibilidad | Opcional, default off; solo si módulo `produccion=false`; al cambiar a prod=true → ocultar y limpiar check |
| Q5 | Modal | Mismo force-load actual (texto, motivos, Cancelar/Cargar) |
| Q6 | Datos novedad al tildar | Se **limpian** tipo/horas al tildar |

## Derived rules

- Roles: mismos de Carga create (`admin` / `jefe_medico`).
- No cambia Parametrización ni Capital Humano.
- Backend create endpoints unchanged (siguen aceptando motivo/obs opcionales).
