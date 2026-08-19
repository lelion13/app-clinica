# Tasks: novedades-sadofe-feriados-descuento

## 1. Backend

- [x] 1.1 Alembic `0019_sadofe_feriados`: `sadofe`, tabla feriado, check tipo
- [x] 1.2 Models + schemas módulo `sadofe` + feriado + tipo `horas_a_descontar`
- [x] 1.3 CRUD feriados (list/create/update/delete; unique fecha activa)
- [x] 1.4 `novedad_valor_calculado` en response + XLS
- [x] 1.5 Tests: signo, unique feriado, default sadofe
- [x] 1.6 Alembic `0020_servicio_concepto_liquidacion`: columna nullable Integer
- [x] 1.7 Model/schema/CRUD servicio: `concepto_liquidacion` (0/`None` → NULL)
- [x] 1.8 Tests: 0→NULL, positivo, negativo 422, repetible

## 2. Frontend Param

- [x] 2.1 Checkbox SADOFE en create/edit módulo
- [x] 2.2 Tab Feriados: grilla + Nuevo / editar / eliminar (modales + Esc)
- [x] 2.3 Servicios: Nuevo servicio / editar / eliminar (modales + Esc); campo concepto; quitar valor hora inline

## 3. Frontend Carga

- [x] 3.1 Tipo Horas a descontar + estimado negativo
- [x] 3.2 Filtrar módulos por fecha + feriados; limpiar si deja de valer

## 4. Docs

- [x] 4.1 Runbook + marcar tasks (SADOFE/feriados/descuento)
- [x] 4.2 Runbook: concepto liquidación + ABM Servicios; marcar 1.6–1.8 / 2.3 / 4.2
