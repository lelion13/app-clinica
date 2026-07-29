# Decisions — novedades-modulos

**Estado:** SURVEY CLOSED (2026-07-28) + refinamientos post-implementación (2026-07-28 / 2026-07-29)  
**Change:** `novedades-modulos`

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Módulo vs novedad | **B** | Asignar módulos ≠ cargar novedades (dos flujos) |
| Q2 | Concepto | **A → actualizado 2026-07-28** | Módulo = catálogo FK sin valor editable en carga; Novedad = tipo (`hora_extra` / `hora_extra_por_ausencia`) + horas enteras |
| Q3 | Valor | **A → actualizado** | Módulo: valor catálogo. Novedad: horas × **valor hora del servicio** |
| Q14 | Justificación | **A → reemplazado** | Novedades **no** usan justificación; usan tipo + horas |
| Q4 | Servicio | **A** | Maestro (id, nombre, activo, **valor_hora**); sin agenda |
| Q5 | Roles | **A** | `jefe_medico`, `rrhh`; `operador` sin Novedades |
| Q6 | Matriz | **A** | Ver tabla abajo |
| Q7 | Período | **B** + **Q7b=A** | Rango libre + nombre opcional; un solo abierto |
| Q8 | Cierre | **B** | `admin`+`rrhh` cierran y reabren |
| Q9 | Edición cargas | **A** | Abierto: editar+soft-delete; cerrado: sin escritura |
| Q10 | Profesionales | **C** + **Q10b=B** | Reusar `professionals` (origen swappeable); N servicios |
| Q11 | XLS/grilla | **A** | Columnas/filtros propuestos (+ horas, valor hora) |
| Q12 | Jefe↔servicio | **B** | Muchos-a-muchos |
| Q13 | Param UI | **A** | Una pantalla con pestañas (valor hora, módulo↔servicio, profesional↔servicio) |

## Refinamientos post-survey (implementados)

| # | Tema | Decisión | Fecha |
|---|------|----------|-------|
| R1 | Valor módulo en carga | Solo lectura desde catálogo; jefe/admin **no** editan valor al asignar | 2026-07-28 |
| R2 | Modelo novedad | `tipo` enum + `horas` entero ≥ 1; valor reportado = horas × valor_hora del **servicio** | 2026-07-28 |
| R3 | Valor hora | Por **servicio** (`novedades_servicio.valor_hora`), no parámetro global de carga | 2026-07-28 |
| R4 | Módulo ↔ servicio | N:N; en carga solo se listan módulos asociados al servicio elegido | 2026-07-28 |
| R5 | Profesional ↔ servicio | ABM en Parametrización; **obligatorio** para poder cargar | 2026-07-28 |
| R6 | UX submit carga | Un botón “Cargar novedad”; limpia profesional/módulo/horas tras OK (mantiene período/servicio) | 2026-07-28 |
| R7 | Listado carga (alcance) | `jefe_medico` solo ve cargas de **sus** servicios; `admin` ve todas | 2026-07-29 |
| R8 | Orden listado | Por defecto: **servicio → profesional** (API + grilla) | 2026-07-29 |
| R9 | UI listado carga | Grilla unificada módulos+novedades con columnas, filtro texto/tipo/servicio y sort por columna | 2026-07-29 |
| R10 | Anular | Modal de confirmación con resumen; Cancelar / Confirmar | 2026-07-29 |
| R11 | Alembic `0006` | `revision` id corto `0006_mod_svc_valor_hora` (VARCHAR(32) en `alembic_version`) | 2026-07-28 |

## Matriz RBAC

| Capacidad | admin | jefe_medico | rrhh | operador |
|-----------|-------|-------------|------|----------|
| Cargar módulos / novedades | sí | sí (sus servicios) | no | no |
| Ver listado cargas (grilla en Carga) | sí (todas) | sí (solo sus servicios) | no | no |
| Anular cargas (período abierto) | sí | sí (sus servicios) | no | no |
| Grilla + XLS (Generación) | sí | no | sí | no |
| Cerrar / reabrir período | sí | no | sí | no |
| ABM módulos/servicios/asociaciones | sí | no | sí | no |
