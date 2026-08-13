# Decisions: novedades-modulos-edicion

Survey: **una pregunta a la vez**. Responder con letra (A/B/…).

Estado: **CLOSED** (Q1–Q10).

---

## Q1 — Modal editar (amarillo): ¿qué campos?

- **A** — Solo datos del módulo: descripción, comentario, valor ARS + checkbox `produccion` (servicios **no** se editan acá)
- **B** — Todo lo de A **más** checkboxes de servicios en el mismo modal (el modal violeta no haría falta)
- **C** — Solo descripción y valor + `produccion` (comentario solo en alta)

**Elegido: A**

---

## Q2 — Modal asociar servicios (violeta)

- **A** — Checkboxes de todos los servicios activos; premarcados los ya asociados; Aceptar reemplaza el set completo (igual que create hoy: min 1)
- **B** — Igual que A pero permite **0** servicios (“sin asociar”)
- **C** — Solo agregar (no se puede desmarcar asociados existentes desde este modal)

**Elegido: B**

---

## Q3 — API

- **A** — Reusar `PUT /novedades/modulos/{id}` para ambos modales (editar manda datos+produccion y reenvía `servicio_ids` actuales; asociar manda servicios y reenvía datos actuales)
- **B** — Separar: `PUT` solo datos (+ `produccion`); `PUT /modulos/{id}/servicios` solo asociaciones
- **C** — `PATCH` parcial genérico

**Elegido: B**

---

## Q4 — Default de `produccion` en módulos existentes y en create

- **A** — Default `true` (activos “con producción”); create UI incluye checkbox (default checked)
- **B** — Default `false`; create UI incluye checkbox (default unchecked)
- **C** — Default `true` en DB; **create** del form actual **no** muestra checkbox (solo editable en modal editar); nuevos = `true`
- **D** — Default `false` en DB; create sin checkbox; nuevos = `false` hasta editar

**Elegido: B**

---

## Q5 — Semántica de `produccion` (qué hace el flag)

- **A** — Solo metadato / filtro futuro; **no** cambia el flujo Carga ni el check externo `tiene-produccion` en este change
- **B** — En Carga, si el módulo tiene `produccion=false`, **omitir** el check externo al cargar ese módulo
- **C** — En Carga, si `produccion=false`, **bloquear** la carga de ese módulo
- **D** — Otra (describir)

**Elegido: B** — En Carga, si el módulo tiene `produccion=false`, omitir el check externo al cargar ese módulo.

---

## Q6 — ¿Se puede quitar un servicio que ya tiene asignaciones históricas de ese módulo?

- **A** — Sí, permitir (soft-delete del link; cargas históricas quedan)
- **B** — No, bloquear con error si hay asignaciones activas (no anuladas) con ese par módulo-servicio
- **C** — No, bloquear si existe cualquier asignación histórica (incl. anuladas)

**Elegido: A**

---

## Q7 — Labels de botones en la lista

- **A** — Texto: `editar` / `servicios`, estilo secundario como `fecha` en Carga
- **B** — Texto: `modificar` / `asociar`
- **C** — Iconos only (accesibles con `aria-label`)

**Elegido: A**

---

## Q8 — ¿Mostrar `produccion` en la fila de la lista (además del modal)?

- **A** — Sí, badge o texto “Producción: sí/no”
- **B** — No; solo dentro del modal editar
- **C** — Sí, solo si es `false` (aviso)

**Elegido: B**

---

## Q9 — Roles

- **A** — Igual que hoy: solo **admin** y **rrhh** editan / asocian
- **B** — También **jefe_medico**

**Elegido: A**

---

## Q10 — Branch / aislamiento

- **A** — Nueva branch desde `master` (ej. `feature/novedades-modulos-edicion`); no mezclar con `feature/tiene-produccion-force`
- **B** — Seguir en la branch actual y commitear junto

**Elegido: B**

---

## Resumen cerrado

| Q | Elegido | Resumen |
|---|---------|---------|
| Q1 | A | Modal editar: descripción, comentario, valor, `produccion` (sin servicios) |
| Q2 | B | Modal servicios: set completo; permite 0 |
| Q3 | B | API split: PUT datos vs PUT servicios |
| Q4 | B | `produccion` default `false`; checkbox en create |
| Q5 | B | Carga: si módulo `produccion=false` → omitir check externo |
| Q6 | A | Desasociar servicio siempre permitido |
| Q7 | A | Botones `editar` / `servicios` |
| Q8 | B | `produccion` no en lista; solo modal |
| Q9 | A | Solo admin/rrhh |
| Q10 | B | Seguir en branch actual |

### Interpretación default Q5 (si no se corrige)

- Solo módulo con `produccion=false` → no llama `tiene-produccion`.
- Solo novedad (sin módulo) → sí llama (como hoy).
- Ambos: si el módulo seleccionado tiene `produccion=false` → no llama; si `true` → sí llama.

---

## Notas de contexto (no son preguntas)

- Backend **ya** tiene `PUT /novedades/modulos/{id}`; la UI no lo usa.
- Asociación N:N ya existe vía `servicio_ids` en create/update.
- Este change **sí** toca el flujo Carga si Q5 ≠ A (omitir check externo cuando el módulo tiene `produccion=false`).
