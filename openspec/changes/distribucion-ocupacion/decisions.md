# Decisions — distribucion-ocupacion

**Estado:** SURVEY CLOSED (delta persistencia Q24–Q28)  
**Change:** `distribucion-ocupacion`  
**Modo:** una pregunta a la vez (cerrada)

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1–Q19 | (ver detalle abajo) | — | Survey previa |
| Q13 | Cálculo horas | **D** | horas = hora_hasta − hora_desde |
| Q15 | Agrupación indicadores | **D** | id_dominio + especialidad + medico + dia |
| Q19 | Filas sin horas válidas | **A** | Excluir del cálculo (sin `dia` también) |
| Q20 | Métricas turnos | **D** | API `cantidad_turnos` + `cantidad_sobreturno`; mismo id_agenda por dia |
| Q21 | Sin `dia` | **A** | Excluir del cálculo |
| Q22 | Repeticiones | **B** | Sumar cantidades de todas las filas |
| Q23 | Horas en modal | **B** | horas calculadas + cantidad_turnos + cantidad_sobreturno |
| Q24 | Sync persistencia | **A** | Wipe + reload transaccional; endpoint mandante |
| Q25 | Cuándo se sincroniza | **C** | Grilla lee DB; Actualizar = sync + recargar |
| Q26 | Qué columnas persistir | **A** | Todos los campos del JSON en columnas tipadas |
| Q27 | Filtro fecha_hasta al listar | **A** | Listar UI con fecha_hasta >= hoy; sync guarda todo |
| Q28 | Columnas derivadas del split | **A** | Persistir tipo / especialidad_agenda / medico en sync |

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

**Decisión: D** — Agrupar por `id_dominio` + `especialidad` + `medico` + `dia`.

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

---

## Q20 — Métricas de turnos ✅

**Decisión: D** — Mismo `id_agenda` se consolida en el mismo `dia`. Usar campos API `cantidad_turnos` y `cantidad_sobreturno` (no calcular turnos por duración).

## Q21 — Registros sin `dia` ✅

**Decisión:** Excluir del cálculo filas con `dia` vacío/null.

## Q22 — Repeticiones id_agenda+dia ✅

**Decisión: B** — Sumar `cantidad_turnos` y `cantidad_sobreturno` de todas las filas.

## Q23 — Horas en modal ✅

**Decisión: B** — Modal: `horas` (calculadas) + `cantidad_turnos` + `cantidad_sobreturno` (suma API), agrupado por id_dominio + especialidad + medico + dia.

---

## Q24 — Sync persistencia ✅

**Decisión: A** — Wipe + reload en una transacción tras GET OK. Si falla el GET, no se modifica la tabla.

---

## Q25 — Cuándo se sincroniza contra el endpoint ✅

**Decisión: C** — La grilla lee siempre de DB. “Actualizar” dispara sync (wipe+reload) y luego recarga la grilla. Carga inicial: solo DB (sin sync automático).

---

## Q26 — Qué persistir del endpoint ✅

**Decisión: A** — Todos los campos del JSON en columnas tipadas. PK natural candidata: `id_dato`.

---

## Q27 — Filtro `fecha_hasta >= hoy` al leer la grilla ✅

**Decisión: A** — Sync persiste todo; el listado UI sigue filtrando `fecha_hasta >= hoy`.

---

## Q28 — Columnas `tipo` / `especialidad_agenda` / `medico` ✅

**Decisión: A** — Calcular en sync y persistir. PK de tabla: `id_dato`.
