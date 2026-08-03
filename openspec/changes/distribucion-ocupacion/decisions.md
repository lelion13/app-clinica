# Decisions — distribucion-ocupacion

**Estado:** SURVEY CLOSED (delta nombre_agenda Q7–Q10)  
**Change:** `distribucion-ocupacion`  
**Modo:** una pregunta a la vez (cerrada)

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Relación con “Ocupación semanal” | **A** | Ítem nuevo “Ocupación”; “Ocupación semanal” intacta |
| Q2 | Proxy vs sync DB | **A** | Proxy BFF live; sin persistir en DB v1 |
| Q3 | Roles con acceso | **A** | admin + operador |
| Q4 | Carga de datos (live / botón refresh) | **A** | Auto-load al abrir + botón Actualizar |
| Q5 | Env URL del endpoint externo | **A** | DISTRIBUCION_HORARIOS_ACTIVOS_URL (+ timeout opcional) |
| Q6 | Path / label exactos en menú | **A** | Label “Ocupación”, path `/ocupacion` |
| Q7 | Labels split `nombre_agenda` | **B** | `tipo` / `especialidad_agenda` / `medico` |
| Q8 | Filas con ≠ 3 partes | **A** | 1→tipo, 2→especialidad_agenda, resto→medico |
| Q9 | Columnas de la grilla | **A** | 7 actuales + tipo / especialidad_agenda / medico |
| Q10 | Orden de columnas | **A** | id_dominio, tipo, especialidad_agenda, medico, especialidad, fechas… |

---

## Q1 — Relación con el ítem existente “Ocupación semanal” ✅

**Decisión: A** — Agregar **Ocupación** como ítem nuevo; **Ocupación semanal** permanece sin cambios.

---

## Q2 — Cómo obtener los datos de la API externa ✅

**Decisión: A** — Proxy BFF live; token solo en backend; sin persistir en DB en esta v1.

---

## Q3 — Quién puede ver “Ocupación” ✅

**Decisión: A** — `admin` + `operador` (igual que el resto de Distribución).

---

## Q4 — Cuándo se cargan los datos ✅

**Decisión: A** — Auto-load al abrir la pantalla + botón “Actualizar”.

---

## Q5 — Configuración de la URL externa ✅

**Decisión: A** — `DISTRIBUCION_HORARIOS_ACTIVOS_URL` (+ timeout opcional); token = `NOVEDADES_PROF_SYNC_TOKEN`.

---

## Q6 — Label y path del menú ✅

**Decisión: A** — Label **Ocupación**, path `/ocupacion`.

---

## Q7 — Labels split `nombre_agenda` ✅

**Decisión: B** — Columnas: `tipo`, `especialidad_agenda`, `medico` (separador ` - `).

---

## Q8 — Si `nombre_agenda` no tiene exactamente 3 partes ✅

**Decisión: A** — Parte 1 → `tipo`, parte 2 → `especialidad_agenda`, resto unido → `medico`; faltantes vacías.

---

## Q9 — Qué columnas muestra la grilla ahora ✅

**Decisión: A** — Mantener las 7 actuales y sumar `tipo`, `especialidad_agenda`, `medico` (sin columna `nombre_agenda` crudo).

---

## Q10 — Orden de las columnas ✅

**Decisión: A** — `id_dominio`, `tipo`, `especialidad_agenda`, `medico`, `especialidad`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`.

Separador: ` - ` (espacio-guión-espacio). Parseo en backend.
