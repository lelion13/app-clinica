# Cierre — consultorios-ui

**Archivado:** 2026-10-03 → `openspec/changes/archive/2026-10-03-consultorios-ui/`

## Alcance final (implementado)

- UI `/consultorios`: grilla Ubicación | Nombre (`code`), filtro Todas, Agregar/Editar/Agendas/Horarios/Eliminar
- Modales draft Aceptar/Cancelar; horarios multi-día + Modificar franja
- `PUT .../id-agendas` y `PUT .../hours` replace atómico
- Lookup con `current_room_id` / `current_room_code`
- Eliminado menú y ruta **Horarios consultorio** (`/horarios-consultorio`)
- Nota en `docs/runbook.md`

## Spec estable

`openspec/specs/distribucion/spec.md` — § Mapeo (actualizado) + § UI Consultorios
