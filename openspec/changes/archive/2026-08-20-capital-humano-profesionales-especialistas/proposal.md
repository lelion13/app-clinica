# Proposal: Capital Humano — profesionales especialistas (+20% módulos)

## Intent

Identificar especialistas vía endpoint externo, persistir el flag en el catálogo Novedades durante el sync de Parametrización, avisar códigos sin match, aplicar **+20%** al valor de **módulo** al cargarlo, y mostrar en **Detalle** de Capital Humano si el profesional es especialista.

## Scope

### In Scope

- Env `NOVEDADES_PROF_ESPECIALISTAS_URL` (+ timeout opcional); Bearer = `NOVEDADES_PROF_SYNC_TOKEN`.
- Migración `es_especialista` boolean en `novedades_profesional`.
- Tras sync de catálogo en **Parametrización**: GET especialistas → match `profesional`→`codprof` → set true/false; unmatched → modal.
- Si falla API especialistas: catálogo OK; flags previos intactos; aviso.
- Al **asignar/cargar módulo**: si especialista, `valor = valor_catálogo × 1.20` (no novedades).
- Capital Humano **Detalle**: indicar especialista.
- Docs, `.env*.example`, tests, runbook.

### Out of Scope

- Fetch especialistas en Actualizar CH o en Mis profesionales sync.
- Recalcular cargas de módulo históricas.
- +20% en novedades / bonos / ajustes.
- Excel / cierre de período.

## Approach

1. Alembic + model/schema `es_especialista`.
2. Service: fetch especialistas; integrar en sync Param; response con unmatched / warning.
3. Carga: al crear asignación de módulo, aplicar factor si flag.
4. UI Param: modal post-sync; UI CH Detalle: label especialista.
5. Specs + runbook + tests.

## Affected Areas

| Area | Impact |
|------|--------|
| models / alembic / config | New field + env |
| `prof_sync` (+ especialistas) | Modified |
| Carga módulo create | Modified |
| `NovedadesParamPage` | Modal |
| `NovedadesXlsPage` Detalle | Indicator |
| runbook / env examples | Modified |

## Risks

- Cargas viejas sin plus hasta re-cargar o ajuste manual.
- Especialistas no en catálogo no reciben flag (modal informa).

## Success Criteria

- [ ] Sync Param marca/limpia `es_especialista`.
- [ ] Modal unmatched + aviso si falla API especialistas.
- [ ] Nueva carga de módulo especialista persiste valor × 1.20.
- [ ] Detalle CH muestra especialista.
- [ ] Env documentado.
