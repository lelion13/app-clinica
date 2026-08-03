# Decisions — distribucion-ocupacion

**Estado:** SURVEY CLOSED (delta filtros + indicadores Q13–Q19)  
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
| Q11 | Sin fecha_hasta / inválida | **A** | Excluir del resultado filtrado |
| Q12 | Posición columna `dia` | **B** | Tras `especialidad`, antes de `fecha_desde` |
| Q13 | Cálculo horas | **D** | horas = hora_hasta − hora_desde |
| Q14 | Cálculo cantidad turnos | **A** | (diff minutos) / duracion_turno |
| Q15 | Agrupación indicadores | **D** | Por id_dominio + especialidad + medico + dia |
| Q16 | UI del botón indicadores | **A** | Modal con tabla resumen |
| Q17 | UI filtros por columna | **C** | Select con valores distintos por columna |
| Q18 | Select: uno o varios valores | **B** | Multi-select por columna |
| Q19 | Filas sin horas/duración válidas | **A** | Excluir del cálculo de indicadores |

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

---

## Q11 — Filas sin `fecha_hasta` o inválida ✅

**Decisión: A** — Excluirlas. Filtro backend: `fecha_hasta >= hoy` en `BUSINESS_TIMEZONE`.

---

## Q12 — Dónde va la columna `dia` ✅

**Decisión: B** — … `especialidad`, `dia`, `fecha_desde` …

---

## Q13 — Cálculo de horas ✅

**Decisión: D** — Horas = diferencia `hora_hasta − hora_desde`.

## Q14 — Cantidad de turnos ✅

**Decisión: A** — `cantidad_turnos = (diferencia en minutos) / duracion_turno` (minutos).

---

## Q15 — Cómo agrupa el botón de indicadores ✅

**Decisión: D** — Agrupar por `id_dominio` + `especialidad` + `medico` + `dia`; métricas: horas y cantidad_turnos (sumadas).

---

## Q16 — Dónde se muestran los indicadores ✅

**Decisión: A** — Modal al pulsar el botón (tabla resumen + cerrar).

---

## Q17 — Cómo filtrar por columnas ✅

**Decisión: C** — Select con valores distintos por columna (AND entre columnas).

---

## Q18 — Cada select permite ✅

**Decisión: B** — Multi-select por columna (OR dentro de la columna; AND entre columnas).

---

## Q19 — Filas con `hora_desde`/`hora_hasta` inválidas o `duracion_turno` ≤ 0 ✅

**Decisión: A** — Excluirlas del cálculo de indicadores.
