# Decisions: agenda-ocupacion-dnd

Survey closed 2026-10-05. Change: `agenda-ocupacion-dnd`. Branch: `agenda-ocupacion-dnd`.

| # | Topic | Choice | Decision |
|---|--------|--------|----------|
| Q1 | Qué se mueve | A | Reasigna **toda** la agenda (`id_agenda`): todos los bloques/días de esa agenda (mismo modelo persistente que Consultorios → Agendas). |
| Q2 | Espacio disponible | C | Drop a consultorio solo si el bloque cabe en **horario operativo del box** **y** **no solapa** con otras agendas ya asignadas a ese consultorio. |
| Q3 | Movimientos | B | `Sin consultorio` ↔ consultorio **y** entre consultorios. |
| Q4 | Persistencia | A | Al soltar: guarda **al instante** (API). |
| Q5 | Robo de agenda | A | Si ya está en otro room → **modal de confirmación** (`confirm_move`) antes de persistir. |
| Q6 | Alcance validación | B | Validar **todos** los weekdays donde la agenda tiene bloques en sync; si falla uno, rechazar el move. |
| Q7 | Desasignar | B | Drop a `Sin consultorio` con **confirmación**; luego borra mapeo **sin** validar horario/solape. |
| Q8 | Eje temporal | A | Solo cambia **columna** (consultorio). Horas fijas del sync; sin drag vertical ni resize. |
| Q9 | Rechazo | B | **Modal** con motivo detallado; el bloque vuelve a su columna. |
| Q10 | Modal Agendas Consultorios | A | Se **mantiene** como está (sin las reglas nuevas de horario/solape). DnD en Agenda aplica las reglas. |

## Defaults (no preguntados)

- Roles sin cambio: `admin` / `operador`.
- Filtros actuales de Agenda ocupación se respetan (solo se puede dropear en columnas visibles; el destino debe estar en la grilla filtrada).
- Click en bloque sigue abriendo el modal de detalle (DnD no lo reemplaza).
- No cambia el sync de Ocupación ni la fórmula de Indicadores.
