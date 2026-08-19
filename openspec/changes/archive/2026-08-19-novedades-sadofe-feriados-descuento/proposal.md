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

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/alembic/versions/0019_*` | Create | sadofe, feriados, check tipo |
| `backend/alembic/versions/0020_*` | Create | concepto_liquidacion en servicio |
| `backend/app/models/novedades.py` | Modified | sadofe, NovedadesFeriado, NovedadTipo, concepto_liquidacion |
| `backend/app/schemas/novedades.py` | Modified | sadofe, feriados, concepto_liquidacion schemas |
| `backend/app/services/novedades/masters.py` | Modified | CRUD feriados, concepto en servicio |
| `backend/app/services/novedades/helpers.py` | Modified | novedad_valor_calculado |
| `backend/app/api/routers/novedades.py` | Modified | rutas feriados, sadofe, concepto |
| `backend/app/services/novedades/export_xls.py` | Modified | signo valor calculado |
| `frontend/src/pages/novedades/NovedadesParamPage.jsx` | Modified | tab Feriados, SADOFE, ABM Servicios modales |
| `frontend/src/pages/novedades/NovedadesCargaPage.jsx` | Modified | filtro módulos, tipo descuento |
| `backend/tests/test_novedades_sadofe_feriados.py` | Create | tests unitarios |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Bypass API: módulo/fecha sin validar backend | Med | Q4=B aceptado; documentar en design |
| Servicios existentes sin concepto | Low | NULL aceptado; se completa al editar |

## Rollback Plan

Revert del commit y `alembic downgrade 0018_modulo_produccion`. Redeploy imágenes anteriores.

## Success Criteria

- [x] Módulos se categorizan Semana/SADOFE en Param
- [x] Carga filtra combo por fecha + feriados
- [x] Horas a descontar genera valor negativo
- [x] Feriados ABM funcional (CRUD + UI)
- [x] Concepto liquidación se carga/edita en Servicios (modales)
- [x] Tests pasan (9/9)

## Decisions

Ver `decisions.md` (Q1–Q23 closed).
