# Proposal: novedades-sadofe-feriados-descuento

## Intent

Categorizar módulos Semana vs SADOFE, validar en Carga según fecha+feriados, ABM de feriados globales, y un tipo de novedad **Horas a descontar** con valor negativo.

## Scope

**In**
- Checkbox **SADOFE** en módulo (off = Semana); `produccion` no cambia
- Semana = lun–vie y no feriado; SADOFE = sáb, dom o feriado
- Combo de módulos en Carga: solo los válidos para `fecha_realizacion` (solo UI)
- Tabla feriados globales: `fecha` + `nombre` obligatorio; Param tab **Feriados** (modales como Módulos); ABM admin/rrhh; listado readable para Carga
- Tipo `horas_a_descontar`; valor = −(horas × valor_hora); entra en grilla/XLS/Capital Humano
- Roles carga: admin + jefe; sola o con módulo

**Out**
- Validación Semana/SADOFE en backend create (Q4=B)
- Feriados por servicio / recurrentes anuales
- Reusar checkbox `produccion` para SADOFE

## Approach

Migración `0019`: columna `sadofe`, tabla `novedades_feriado`, ampliar check de `tipo`. Helper de signo en valor calculado. UI Param + filtro Carga.

## Decisions

Ver `decisions.md` (Q1–Q14 closed).
