# Proposal: Recálculo de valores + Valores Extras (Índices)

## Intent

1. Permitir a `admin`/`rrhh` **recalcular** importes persistidos de asignaciones de módulo y/o novedades de horas de un período (catálogo/`valor_hora` actual), con preview antes de aplicar — pestaña **Recálculo** en Parametrización (después de Feriados).
2. Permitir a `admin` en **Índices** consultar y exportar **Valores Extras**: cargas del período por profesional (control), con filtros, selección y PDF (chrome Clínica / app-recepcion).

## Scope

### In Scope
- Pestaña **Recálculo** (después de Feriados): período abierto/cerrado; modo horas / módulos / ambos; preview → confirm; bloqueo si no hay cambios; plus especialista como en carga; horas qty fija; excluye soft-delete; roles Param.
- Persistencia `novedades_novedad.valor` (rev `0035`) para que el recálculo de horas tenga efecto.
- Índices → botón **Valores Extras** (disabled sin período): modal con filtro (ambos / módulos / novedades / novedad extra = con observación), búsqueda nombre/legajo, grilla expandible por profesional, checkboxes + Exportar PDF (un PDF, página por profesional seleccionado).
- APIs: recalculo preview/apply; valores-extras GET + PDF POST. Roles: Recálculo `admin`/`rrhh`; Valores Extras `admin` (igual Índices).

### Out of Scope
- Recálculo filtrado por servicio/profesional; cambiar qty horas o módulo asociado; producción/bonos/ajustes CH.
- Export XLS/CSV de Valores Extras; ZIP multi-PDF.
- Histórico dedicado más allá de `updated_at`/`updated_by`.

## Approach

1. Snapshot `valor` en novedades + APIs preview/apply + tab Recálculo.
2. Agregación de cargas del período (grid rows) → modal Índices + PDF reportlab con header band compartido con recepción.

## Affected Areas

| Area | Impact |
|------|--------|
| `NovedadesParamPage` | Tab Recálculo |
| `NovedadesIndicesPage` | Valores Extras modal + PDF |
| API/services novedades | recalculo, valores_extras, valores_extras_pdf |
| Alembic `0035_novedad_valor` | Columna `valor` en novedades |
| `backend/app/assets/pdf-header-band.png` | Chrome PDF |
| `requirements.txt` | `reportlab` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Recalc en período cerrado altera liquidación ya vista | Med | Preview + confirm |
| Plus especialista mal aplicado | Med | Reusar `modulo_valor_para_profesional` |
| PDF sin header en deploy | Low | Asset en imagen; fallback navy |

## Rollback Plan

Quitar tab/endpoints/UI; valores ya recalculados no se revierten solos. Quitar botón/modal/PDF.

## Success Criteria

- [x] Tab Recálculo + preview/apply según decisiones Q1–Q9.
- [x] `0035` + valor persistido en create/grid/export.
- [x] Valores Extras (VE-Q1–Q12) + PDF selección.
- [x] Tests unitarios + runbook.
