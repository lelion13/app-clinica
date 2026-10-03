# Decisions: consultorios-ui

Survey closed 2026-10-03. Change name: `consultorios-ui`. Branch: `consultorios`.

| # | Topic | Choice | Decision |
|---|--------|--------|----------|
| Q1 | Columna “nombre de consultorio” | A | Muestra el campo actual `code`; solo cambia el label en UI. No hay campo `nombre` nuevo. |
| Q2 | Ítem menú “Horarios consultorio” | A | Se elimina del menú Distribución. |
| Q3 | Ruta `/horarios-consultorio` | C | Se elimina la ruta (404). |
| Q4 | Modal Editar — campos | A | Ubicación y código (mismos que al crear). |
| Q5 | Filtro por ubicación | A | Select simple: “Todas” + una ubicación a la vez. |
| Q6 | Eliminar consultorio | A | Se mantiene acción eliminar en la fila. |
| Q7 | Aceptar / Cancelar en modales | A | Draft hasta Aceptar; Cancelar descarta y cierra sin guardar. Aplica a Agregar, Editar, Agendas y Horarios. |
| Q8 | Modal Horarios — UX | A | Misma funcionalidad que hoy (día, desde/hasta, agregar franja, lista con eliminar) en draft. |
| Q9 | Modal Agendas — UX | A | Mismo flujo (typeahead, lista, quitar, confirm mover) en draft. |
| Q10 | Confirmación al eliminar | A | `window.confirm` (o equivalente simple). |
| Q11 | Persistencia al Aceptar agendas/horarios | A | Endpoints batch transaccionales. Editar/Agregar siguen con POST/PATCH unitarios. |
| Q12 | Conflicto id_agenda en batch | A | Confirm de mover se pide durante el draft; el batch envía `confirm_move` por ítem. |
| Q13 | Detección de conflicto en draft | A | Check de solo lectura al elegir en typeahead (lookup enriquecido o equivalente); `window.confirm` y marca `confirm_move` en draft. |

## Defaults (no preguntados)

- Labels de acciones en fila: **Editar**, **Agendas**, **Horarios**.
- Roles sin cambio: `admin` / `operador`.
- Endpoints unitarios actuales de agendas/horarios se mantienen por compatibilidad; la UI nueva usa batch en Aceptar.
