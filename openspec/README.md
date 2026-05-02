# OpenSpec (SDD) — app-clinica

Este directorio concentra la **especificación orientada a cambios** para que humanos y agentes trabajen con el mismo ritmo: propuesta → especificación → diseño → tareas → implementación → verificación → archivo.

## Estructura

| Carpeta / archivo | Rol |
|-------------------|-----|
| `config.yaml` | Reglas y contexto del proyecto para SDD |
| `GUIA-SDD.md` | Guía operativa en español (flujo día a día) |
| `templates/` | Plantillas para nuevos cambios |
| `specs/` | Especificaciones **estables** del producto (cuando existan) |
| `changes/` | Cambios **activos**: cada subcarpeta es un tema/feature/fix |
| `changes/archive/` | Cambios **cerrados** (histórico) |

## Flujo resumido

1. Crear `openspec/changes/<nombre-del-cambio>/` (nombre en `kebab-case`).
2. Copiar o adaptar `templates/cambio.md` en archivos del cambio (p. ej. `proposal.md`, `spec.md`, `design.md`, `tasks.md`) según necesidad.
3. Implementar en `frontend/` y `backend/` siguiendo `AGENTS.md` y las reglas de `config.yaml`.
4. Verificar (tests, checklist en la plantilla).
5. Archivar la carpeta del cambio bajo `changes/archive/` al cerrar el trabajo.

Documentación detallada: **[GUIA-SDD.md](./GUIA-SDD.md)**.
