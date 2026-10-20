# Implementation notes — indicadores-ocupacion-ui

Entregado 2026-10-03 → cerrado 2026-10-05. Rama: `indicadores-ocupacion-ui`.

## Qué quedó en producción (comportamiento)

### Indicadores `/indicadores-ocupacion`
- Período **Día | Mes** (`period=day|month` + `date` o `month`).
- Fórmula: horas sync **mapeadas a consultorio con horario** ÷ `room_operating_hours` del período.
- Torta donut: % ocupación al centro; horas/% dentro de segmentos; chips debajo (sin labels externos cortados).
- Top 10 especialidad y Top 10 médico: horas, **% box**, **% ocup.**

### Significado de columnas tops (Q&A producto)
- **% box** = horas del ítem ÷ `enabled_hours` (horario habilitado del box / mismo denom que la torta).
- **% ocup.** = horas del ítem ÷ `occupied_hours` (participación dentro de lo ya ocupado).
- Tops **solo** cuentan agendas con `id_agenda` mapeada a un room que entra en la torta. Lo sync sin mapear **no** entra.

### Avisos bajo la torta
- **Sin horario ese día/mes (códigos…):** consultorio sin franjas → no entra al denominador ni a la torta.
- **Con horario pero sin agenda mapeada: N:** aportan capacidad (denom) y 0 al numerador.

### Filtros compartidos (Agenda + Indicadores)
- `filter-options` / match: especialidad = solo `payload.especialidad`; médico = solo `payload.medico_responsable_equipo` (fallback `payload.medico`).
- **No** usa `especialidad_agenda` para el filtro especialidad.

### Sync Ocupación (Q8)
- Columna `medico` ← `medico_responsable_equipo` (no resto de `nombre_agenda`).
- `tipo` / `especialidad_agenda` siguen del split de `nombre_agenda`.
- Tras deploy: **Actualizar** en Ocupación para refrescar filas.

## Archivos clave
- `backend/app/services/distribucion/indicadores_ocupacion.py`
- `backend/app/services/distribucion/agenda_ocupacion.py`
- `backend/app/services/distribucion/horarios_activos.py`
- `frontend/src/pages/IndicadoresOcupacionPage.jsx`
- `docs/runbook.md`

## Tests
- `pytest tests/test_indicadores_ocupacion.py tests/test_distribucion_horarios_activos.py` → **23 passed** (2026-10-05).
- Smoke UI: validado en sesión (día/mes, torta, tops, avisos rooms).

## Fuera de alcance / próximo change (no perder)
**Idea producto (2026-10-05):** unir capacidad+programación del sistema con **ejecución real** del tablero Looker Studio  
`https://datastudio.google.com/u/0/reporting/cc363811-240f-42b1-a1c4-e4b5a3a59df8/page/p_i37pgfzr2d`  
(turnos, ausentes, etc.). Looker **no** expone API de datos del reporte; hace falta la **fuente** detrás (BigQuery / Sheets / HIS / export). Bloqueado hasta conocer fuente + primer KPI (p. ej. ausentismo vs programado). No iniciar en este change.
