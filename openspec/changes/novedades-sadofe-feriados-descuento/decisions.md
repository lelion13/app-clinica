# Decisions: novedades-sadofe-feriados-descuento

Survey: **una pregunta a la vez**. Responder con letra (A/B/…).

Estado: **CLOSED** (Q1–Q14).

---

## Q1 — Semana / SADOFE en el módulo: ¿cómo se modela?

Hoy el módulo ya tiene checkbox **Producción** (otro concepto: omitir check externo).

- **A** — Un solo campo enum `tipo_dia`: `semana` | `sadofe` (obligatorio; exactamente uno)
- **B** — Dos checkboxes independientes `semana` y `sadofe` (¿ambos / ninguno? → ver Q2 si elegís B)
- **C** — Un checkbox “SADOFE”; si está off = Semana (default Semana)
- **D** — Reemplazar/reusar el checkbox `produccion` actual para esto (no recomendado: ya tiene otra semántica)

**Elegido: C** — Checkbox SADOFE; off = Semana. `produccion` se mantiene aparte.

---

## Q2 — (si aplica) Combinaciones Semana/SADOFE

- **A** — Exactamente uno obligatorio
- **B** — Al menos uno; pueden ambos (válido cualquier día)
- **C** — Pueden ambos false (sin restricción de día al cargar)

**Elegido: N/A** (Q1=C implica mutuamente excluyentes vía un solo checkbox)

---

## Q3 — ¿Qué días acepta cada tipo?

- **A** — Semana = lun–vie **y no** feriado; SADOFE = sáb, dom **o** feriado (tabla Feriados)
- **B** — Semana = lun–vie (ignora feriados); SADOFE = sáb/dom solamente (feriados no cambian nada)
- **C** — Semana = lun–vie; SADOFE = sáb/dom; feriado en día de semana → **ambos** válidos
- **D** — Otra (describir)

**Elegido: A** — Semana = lun–vie sin feriado; SADOFE = sáb/dom o feriado.

---

## Q4 — Validación módulo vs fecha: ¿dónde y cuándo?

- **A** — UI al elegir módulo / cambiar fecha + backend en create/update asignación (rechazo 422)
- **B** — Solo UI (aviso; backend no valida)
- **C** — Solo backend

**Elegido: B** — Solo UI.

---

## Q5 — Si el módulo no corresponde a la fecha

- **A** — Bloquear: no se puede cargar ese módulo ese día (mensaje claro)
- **B** — Advertir pero permitir continuar
- **C** — Filtrar el combo de módulos: solo mostrar los válidos para esa fecha

**Elegido: C** — Filtrar combo de módulos según fecha.

---

## Q6 — Tipo novedad “Horas a descontar”

- **A** — Nuevo valor enum `horas_a_descontar` (label “Horas a descontar”); valor_calculado = `-(horas × valor_hora)`
- **B** — Mismo enum pero flag/signo aparte
- **C** — Otra (describir)

**Elegido: A** — Enum `horas_a_descontar`; valor = −(horas × valor_hora).

---

## Q7 — “Horas a descontar”: ¿quién y con qué?

- **A** — Igual que otras novedades: admin + jefe_medico; puede ir sola o junto con módulo en el mismo submit
- **B** — Solo jefe_medico (admin no)
- **C** — No se puede combinar con módulo en el mismo submit (solo novedad)

**Elegido: A** — Admin + jefe; sola o con módulo.

---

## Q8 — Totales Capital Humano / XLS / grillas

- **A** — El valor negativo entra en sumas/export igual (resta al total del profesional)
- **B** — Se muestra en detalle pero **no** resta en agregados de Capital Humano
- **C** — Otra (describir)

**Elegido: A** — El negativo entra en sumas/export (resta al profesional).

---

## Q9 — Feriados: datos del registro

- **A** — Solo `fecha` (date) + `nombre`/`descripcion` opcional
- **B** — `fecha` + `nombre` obligatorio
- **C** — `fecha` + nombre + flag “repite todos los años” (solo mes/día)
- **D** — Otra

**Elegido: B** — `fecha` + `nombre` obligatorio.

---

## Q10 — Feriados: alcance

- **A** — Globales a toda la clínica (una tabla)
- **B** — Por servicio
- **C** — Globales + opcionales por servicio

**Elegido: A** — Globales a toda la clínica.

---

## Q11 — Feriados: roles ABM

- **A** — Solo admin/rrhh (como Param Módulos/Períodos)
- **B** — También jefe_medico (solo lectura o escritura)

**Elegido: A** — Solo admin/rrhh.

---

## Q12 — Feriados UI (confirmado parcialmente por pedido)

Pedido base: tab **Feriados** al lado de Períodos; grilla; **Nuevo feriado** modal; editar/eliminar como Módulos.

- **A** — Exactamente ese patrón (modales Nuevo / editar / confirmar delete + Esc)
- **B** — Igual pero sin modal de delete (delete directo)
- **C** — Otra diferencia

**Elegido: A** — Tab Feriados; Nuevo feriado; editar/eliminar como Módulos (modales + Esc).

---

## Q13 — Default Semana/SADOFE en módulos existentes

- **A** — Migrar todos a `semana`
- **B** — Migrar todos a `sadofe`
- **C** — Exigir elegir al editar; create exige elegir; existentes quedan en un default explícito (decir cuál)
- **D** — Según `produccion` actual (mapear de alguna forma — describir)

**Elegido: A** — Existentes migran a Semana (SADOFE off).

---

## Q14 — Branch

- **A** — Nueva branch desde `master` (recomendado; VPS ya tiene lo anterior)
- **B** — Seguir en `feature/tiene-produccion-force`

**Elegido: B** — Seguir en `feature/tiene-produccion-force`.

---

## Resumen cerrado

| Q | Elegido | Resumen |
|---|---------|---------|
| Q1 | C | Checkbox SADOFE; off = Semana; `produccion` aparte |
| Q2 | N/A | Un solo checkbox |
| Q3 | A | Semana = lun–vie sin feriado; SADOFE = sáb/dom o feriado |
| Q4 | B | Validación solo UI |
| Q5 | C | Filtrar combo de módulos según fecha |
| Q6 | A | Tipo `horas_a_descontar`; valor = −(horas × valor_hora) |
| Q7 | A | Admin + jefe; sola o con módulo |
| Q8 | A | El negativo entra en sumas/export |
| Q9 | B | Feriado: fecha + nombre obligatorio |
| Q10 | A | Feriados globales |
| Q11 | A | ABM feriados: admin/rrhh |
| Q12 | A | Tab Feriados; modales como Módulos |
| Q13 | A | Existentes = Semana |
| Q14 | B | Branch actual |

---

## Notas

- SADOFE = sábado, domingo y feriado (definición de negocio a cerrar en Q3).
- `produccion` existente **no** es Semana/SADOFE salvo Q1=D.
- Q4=B: validación solo UI — documentar riesgo de bypass API en design.
