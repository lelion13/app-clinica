# Proposal: novedades-sadofe-feriados-descuento

## Intent

Categorizar módulos Semana vs SADOFE, validar en Carga según fecha+feriados, ABM de feriados, tipo **Horas a descontar** (valor negativo), y en Servicios el campo opcional **concepto liquidación** (ABM en modales como Módulos).

## Scope

**In**
- Checkbox **SADOFE** en módulo (off = Semana); `produccion` no cambia
- Semana = lun–vie y no feriado; SADOFE = sáb, dom o feriado
- Combo de módulos en Carga: solo los válidos para `fecha_realizacion` (solo UI)
- Tabla feriados globales: `fecha` + `nombre`; Param tab **Feriados**; ABM admin/rrhh
- Tipo `horas_a_descontar`; valor = −(horas × valor_hora); entra en grilla/XLS/Capital Humano
- Servicios: `concepto_liquidacion` entero positivo opcional; ABM en modales (Nuevo / editar / eliminar + Esc)

**Out**
- Validación Semana/SADOFE en backend create (Q4=B)
- Feriados por servicio / recurrentes anuales
- Uso de `concepto_liquidacion` en Capital Humano (organizador de archivos importados) — change posterior
- Reusar checkbox `produccion` para SADOFE

## Approach

Migración `0019`: `sadofe`, tabla feriado, check de `tipo`. Helper de signo. UI Param + filtro Carga.
Migración `0020`: `novedades_servicio.concepto_liquidacion` nullable Integer. UI Servicios = patrón Módulos.

## Decisions

Ver `decisions.md` (Q1–Q23 closed).
