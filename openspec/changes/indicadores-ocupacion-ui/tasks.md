# Tasks: indicadores-ocupacion-ui

## Phase 1: Backend — filtros compartidos

- [x] 1.1 `list_filter_options`: especialidad solo `payload.especialidad`; medico solo `payload.medico`
- [x] 1.2 Match payload-only en `list_agenda_events` (especialidad/medico)
- [x] 1.3 Match payload-only en `compute_indicadores`
- [x] 1.4 Tests filter-options + match (Indicadores y/o agenda)

## Phase 2: Backend — período y tops

- [x] 2.1 Schemas: `period`, `month`, `IndicadoresTopItem`, `top_especialidad`, `top_medico`
- [x] 2.2 Router: query `period`, `date`, `month`
- [x] 2.3 `compute_indicadores` modo month (suma days)
- [x] 2.4 Calcular tops 10 (horas, percent_box, percent_occupied; Sin especialidad/médico)
- [x] 2.5 Tests day regression + month sum + tops

## Phase 3: Frontend Indicadores

- [x] 3.1 Control Día \| Mes + date/month inputs
- [x] 3.2 Wire API params period/date/month
- [x] 3.3 Torta: labels/leyenda con horas y %
- [x] 3.4 Panel tops especialidad y médico (al costado / stack mobile)
- [x] 3.5 Textos ayuda y empty states (sin hours, sin tops)

## Phase 4: Docs y verificación

- [x] 4.1 Nota `docs/runbook.md` (filtros payload; día/mes; tops; impacto Agenda)
- [x] 4.2 Correr tests backend tocados
- [ ] 4.3 Smoke UI: filtros, día/mes, torta, tops
