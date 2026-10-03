# Proposal: Indicadores ocupación (torta sync)

## Intent

Dashboard v1 con % de ocupación de consultorios según agendas del sync mapeadas vs horario operativo real del box, en una torta global, filtrable por día/ubicación/consultorio/especialidad/médico.

## Scope

### In Scope

- Menú **Indicadores ocupación** → `/indicadores-ocupacion` (`admin`/`operador`).
- Cálculo por **un día** (default hoy):  
  - **Numerador**: suma de duración de bloques sync del día (weekday + vigencia) cuyas agendas están mapeadas a rooms incluidos; sin recorte al horario del box; filtros especialidad/médico aplican aquí.  
  - **Denominador**: suma de horas `room_operating_hours` ese weekday para rooms incluidos (ubicación/consultorio).  
  - Sin mapeo → 0% (aportan 0 al numerador; sí al denom si tienen horario).  
  - Sin horario ese día → lista “sin horario”; fuera de torta.
- UI: filtros select (ubicación, consultorio, especialidad, médico) + fecha; torta ocupado/libre con % (puede >100%); horas absolutas.
- API BFF JWT; tests de cálculo; runbook breve.

### Out of Scope

- Torta por consultorio; rankings; export.
- Usar bookings / modificar `/estadisticas` o `dashboard-estadisticas`.
- Sync desde esta pantalla; editar mapeos.
- Rango multi-día; multi-select filtros.
- Capar % a 100%.

## Approach

Nuevo endpoint (ej. `GET .../ocupacion/indicadores?date=&location_id=&room_id=&especialidad=&medico=`). Servicio une: rooms activos → horas operativas; mapeo id_agenda→room; filas sync vigentes ese weekday → horas (bloque completo). Front con recharts Pie (mismo stack que Estadística).

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/app/services/distribucion/` | New indicadores service |
| `backend/app/api/routers/distribucion.py` | New route |
| `backend/app/schemas/` | New response |
| `frontend/src/config/navigation.js` | New item |
| `frontend/src/main.jsx` | Route |
| `frontend/src/pages/` | New page |
| `backend/tests/` | New tests |
| `docs/runbook.md` | Note |

## Risks

| Risk | Mitigation |
|------|------------|
| % >100% confunde | Mostrar horas ocupadas/habilitadas |
| Denom alto con filtro médico | Copy UI: filtros esp/médico solo afectan ocupación sync |
| Solapes sync | v1 suma bloques (Q9); documentar |

## Rollback

Revert front/back deploy. Sin migración.

## Dependencies

- Snapshot sync + mapeo `0015` + `room_operating_hours` poblados.
- Survey `decisions.md`.

## Success Criteria

- [ ] Menú y ruta OK; Estadística intacta
- [ ] Torta global día con % y horas; rooms sin agenda = 0 al num
- [ ] Sin horario fuera de torta + aviso
- [ ] Filtros A1 aplicados
- [ ] Tests cálculo; runbook
