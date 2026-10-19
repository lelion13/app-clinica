# Exploration: agenda-ocupacion-segun-dia

## Goal

Asignar agendas a consultorios **por día de la semana**, no solo `id_agenda` → room global. Dos puntos de entrada con reglas distintas.

## Current state

- Tabla `consulting_room_id_agenda`: PK `id_agenda` → un `room_id` (todos los días).
- Agenda ocupación DnD valida **todos** los weekdays y remapea el `id_agenda` completo.
- Consultorios → Agendas: batch replace por room (sin validación horario/solape DnD).

## Decisions (Q&A)

| Q | Decisión |
|---|----------|
| Q1 | AO = día a día (A). Consultorios = completa días pendientes (B). |
| Q2 | Desasociar en Consultorios: quita vínculos de agendas a **ese** room. |
| Q3 | Assign Consultorios: solo días aún en Sin consultorio; no pisa otros rooms. |
| Q4 | AO calendario: solo agendas con bloque ese weekday. |
| Q5 | Validación solape/horario: **solo** el weekday del calendario. |
| Q6 | Migración: fila actual → todos los weekdays sync de esa agenda en ese room. |
| Q7 | Orden columnas: numérico por código (C1…C10); sin número al final. |
| Q8 | Assign Consultorios: todo-o-nada; modal conflicto; nada si algún día falla. |
| Q9 | Sin consultorio sticky si tiene ítems; si vacía, scroll con el resto. |
| Q10 | Lista Consultorios: agenda aparece si **algún** día está en ese room. |
| Q11–12 | Full en ese room → una fila solo nombre. Parcial → una fila por día `nombre - día`. |
| Q13 | Roles sin cambio (`admin`\|`operador`). |
| Q14 | Desasociar parcial: **un día** (fila a fila). |
| Q15 | Change name = `agenda-ocupacion-segun-dia`. |

## Open technical notes (design)

- Clave mapa: `(id_agenda, weekday)` → `room_id`.
- Weekday: mismo convenio JS/backend que hours/reassign actuales.
- Auto-scroll horizontal al arrastrar cerca del borde (requisito producto).
