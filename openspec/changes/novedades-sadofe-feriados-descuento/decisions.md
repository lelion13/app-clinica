# Decisions: novedades-sadofe-feriados-descuento

Survey: **una pregunta a la vez**. Responder con letra (A/B/…).

Estado: **CLOSED** — Q1–Q14 original + addendum Q15–Q23 (`concepto_liquidacion`).

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
| Q15 | A | Entero positivo, sin decimales |
| Q16 | B | Opcional; vacío = `NULL` |
| Q17 | A | Se puede repetir |
| Q18 | C | ABM Servicios en modales como Módulos |
| Q19 | E | Capital Humano más adelante; este change solo persiste el campo |
| Q20 | B | Vacío o `0` = `NULL` |
| Q21 | A | Sin tope extra; valor ≥ 1 |
| Q22 | A | Grilla actual + concepto; `NULL` = “—” |
| Q23 | B | Activo solo en editar; alta siempre activo |

---

## Notas

- SADOFE = sábado, domingo y feriado (definición de negocio a cerrar en Q3).
- `produccion` existente **no** es Semana/SADOFE salvo Q1=D.
- Q4=B: validación solo UI — documentar riesgo de bypass API en design.

---

## Addendum — `concepto_liquidacion` en Servicios

Campo numérico en Parametrización → Servicios, cargable al crear o editar.

### Q15 — Tipo de número

- **A** — Entero positivo (ej. `101`, `205`) — sin decimales
- **B** — Entero (puede ser negativo)
- **C** — Decimal con 2 decimales (como `valor_hora`)
- **D** — Otro

**Elegido: A** — Entero positivo, sin decimales.

### Q16 — ¿Es obligatorio?

- **A** — Obligatorio al crear y al editar (no se puede guardar sin valor ≥ 1)
- **B** — Opcional: se puede dejar vacío (en BD queda `NULL`)
- **C** — Obligatorio al crear; existentes pueden quedar vacíos hasta editarlos
- **D** — Otro

**Elegido: B** — Opcional; vacío = `NULL`.

### Q17 — Unicidad

- **A** — Se puede repetir (sin unicidad)
- **B** — Único entre servicios activos
- **C** — Único entre todos los servicios
- **D** — Único solo cuando tiene valor (varios `NULL` sí)

**Elegido: A** — Se puede repetir; sin constraint unique.

### Q18 — UI de alta / edición de Servicios

Hoy: formulario inline + `valor_hora` editable en la grilla; delete directo. No hay modal de editar.

- **A** — Input en el alta + input en cada fila (blur como valor hora)
- **B** — Input en el alta; botón editar con modal (nombre, valor hora, concepto, activo)
- **C** — Alta y edición en modales como Módulos/Feriados: **Nuevo servicio** + editar/eliminar con confirmación + Esc
- **D** — Otro

**Elegido: C** (pedido D: “puede ser C; igual que módulos”) — Grilla de servicios; botón **Nuevo servicio**; crear/editar/eliminar por modal (Cancelar/Guardar o Cargar; delete con confirmación; Esc cancela). `concepto_liquidacion` va en crear y editar. `valor_hora` deja de editarse inline.

### Q19 — Uso de `concepto_liquidacion` además de Parametrización

- **A** — Solo Parametrización (API + grilla); no XLS ni Capital Humano en este change
- **B** — También columna en el XLS
- **C** — Visible en Carga / grillas de novedades
- **D** — A + B
- **E** — Otro

**Elegido: E** — Se va a usar en **Capital Humano** como organizador de los archivos que se importen desde ahí. **Ese uso se define más adelante** (fuera del alcance de implementación de este change). En este change: persistir el campo en Servicios y exponerlo en el ABM.

### Q20 — Vacío vs `0`

- **A** — Vacío = `NULL`; `0` inválido
- **B** — Vacío o `0` = `NULL` (“sin concepto”)
- **C** — Vacío = `NULL`; `0` es un concepto válido
- **D** — Otro

**Elegido: B** — Vacío o `0` se persisten como `NULL`.

### Q21 — Tope numérico

- **A** — Sin tope especial: entero ≥ 1 (límite de `Integer`)
- **B** — Hasta 9999
- **C** — Hasta 999999
- **D** — Otro

**Elegido: A** — Sin tope extra; si hay valor, entero ≥ 1.

### Q22 — Grilla de Servicios

- **A** — Layout actual (`#id · nombre · activo`) más **Concepto liquidación** (`NULL` → vacío o “—”)
- **B** — Filas tipo Módulos: id, nombre, valor hora, concepto, activo
- **C** — Como A, vacío = “Sin concepto”
- **D** — Otro

**Elegido: A** — Misma fila que hoy + concepto; `NULL` se muestra como “—”.

### Q23 — Campo `activo` en modales

- **A** — Checkbox Activo en crear y editar (default ON al crear)
- **B** — Solo en editar; el alta siempre queda activo
- **C** — No se toca `activo` en este change
- **D** — Otro

**Elegido: B** — Alta siempre `activo=true`. Checkbox Activo solo en el modal de editar.
