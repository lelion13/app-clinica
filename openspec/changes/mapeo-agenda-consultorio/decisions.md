# Decisions — mapeo-agenda-consultorio

**Estado:** SURVEY CLOSED  
**Change:** `mapeo-agenda-consultorio`  
**Branch:** `feature/ocupacion`

| # | Tema | Decisión |
|---|------|----------|
| Q1 | Dónde se mantiene el mapeo | **B** — En ficha del consultorio |
| Q2 | id_agenda ya en otro consultorio | **B** — Moverlo con confirmación |
| Q3 | Alta de id_agenda | **D** — Combobox: médico → agendas sync → guarda `id_agenda` |
| Q4 | Sync sin mapeo en grilla | **B** — Columna **"Sin consultorio"** |
| Q5 | Roles | **A** — admin + operador |
| Q6 | Texto opción combo | **A** — `id_agenda — nombre_agenda` |
| Q7 | Alcance | **B** — mapeo + grilla planilla en Agenda ocupación |

## Modelo
- `id_agenda` (sync) → `consulting_rooms` (N:1), UNIQUE en mapeo
- Fuente typeahead: snapshot `ocupacion_horario_activo`
