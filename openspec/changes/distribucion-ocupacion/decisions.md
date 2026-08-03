# Decisions — distribucion-ocupacion

**Estado:** SURVEY CLOSED  
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
