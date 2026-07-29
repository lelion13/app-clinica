# Decisions — novedades-jefe-profesionales-fecha-carga

**Estado:** SURVEY CLOSED (2026-07-29)  
**Change:** `novedades-jefe-profesionales-fecha-carga`

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Catálogo al asociar (jefe) | **B** | Cualquier profesional activo del catálogo; UI con búsqueda/filtro; no ofrecer los ya asociados a ese servicio |
| Q2 | UI superficie jefe | **B** | Nueva entrada en menú Novedades (ej. “Mis profesionales”); Parametrización sigue para admin/rrhh |
| Q3 | Quitar con cargas existentes | **A** | Soft-delete del vínculo siempre permitido; cargas históricas/abiertas se conservan; deja de listarse para nuevas cargas |
| Q4 | Quién ve “Mis profesionales” | **C** | `jefe_medico` + `admin` + `rrhh`; admin/rrhh todos los servicios; Param puede mantener el tab |
| Q5 | Semántica fecha | **A** | Día de **realización** del módulo/novedad |
| Q6 | Validación fecha | **D** | ∈ [periodo.inicio, periodo.fin] **y** ≤ hoy (día de carga); no futuras |
| Q7 | Futuro / hoy | **cubierta por Q6** | “hoy” = día calendario al momento de create/update |
| Q8 | Grilla / XLS | **A** | Columnas: Fecha realización **+** Fecha carga |
| Q9 | Editar fecha post-carga | **B** | Editable mientras período **abierto** (admin/jefe scoped); cerrado → no |
| R12 | Búsqueda profesionales (typeahead) | **A** | Mismo patrón que `ProfessionalCombobox` (ocupación semanal): filtrar al tipear y mostrar matches |

## Matriz RBAC (delta)

| Capacidad | admin | jefe_medico | rrhh | operador |
|-----------|-------|-------------|------|----------|
| Mis profesionales (UI + API scoped/global) | sí (todos los servicios) | sí (sus servicios) | sí (todos) | no |
| Parametrización tab profesional↔servicio | sí | no | sí | no |
| Cargar / editar fecha realización (período abierto) | sí | sí (sus servicios) | no | no |
