# Decisions — novedades-modulos

**Estado:** SURVEY CLOSED (2026-07-28)  
**Change:** `novedades-modulos`

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Módulo vs novedad | **B** | Asignar módulos ≠ cargar novedades (dos flujos) |
| Q2 | Concepto | **A → actualizado 2026-07-28** | Módulo = catálogo FK sin valor editable en carga; Novedad = tipo (hora extra / hora extra por ausencia) + horas |
| Q3 | Valor | **A → actualizado** | Módulo: valor catálogo. Novedad: horas × **valor hora** (param) |
| Q14 | Justificación | **A → reemplazado** | Novedades ya no usan justificación; usan tipo + horas |
| Q4 | Servicio | **A** | Maestro nuevo (id, nombre, activo); sin agenda |
| Q5 | Roles | **A** | `jefe_medico`, `rrhh`; `operador` sin Novedades |
| Q6 | Matriz | **A** | Ver tabla abajo |
| Q7 | Período | **B** + **Q7b=A** | Rango libre + nombre opcional; un solo abierto |
| Q8 | Cierre | **B** | `admin`+`rrhh` cierran y reabren |
| Q9 | Edición cargas | **A** | Abierto: editar+soft-delete; cerrado: sin escritura |
| Q10 | Profesionales | **C** + **Q10b=B** | Reusar `professionals` (origen swappeable); N servicios |
| Q11 | XLS/grilla | **A** | Columnas/filtros propuestos |
| Q12 | Jefe↔servicio | **B** | Muchos-a-muchos |
| Q13 | Param UI | **A** | Una pantalla con pestañas (incluye valor hora y profesional↔servicio) |

## Matriz RBAC

| Capacidad | admin | jefe_medico | rrhh | operador |
|-----------|-------|-------------|------|----------|
| Cargar módulos / novedades | sí | sí (sus servicios) | no | no |
| Grilla + XLS | sí | no | sí | no |
| Cerrar / reabrir período | sí | no | sí | no |
| ABM módulos/servicios/asociaciones | sí | no | sí | no |
