# Proposal: consultorios-ui

## Intent

Unificar la gestión de consultorios en `/consultorios`: grilla filtrable, edición, agendas y horarios en modales con Aceptar/Cancelar, y retirar la pantalla/menú “Horarios consultorio”.

## Scope

### In Scope
- Grilla auto-load: Ubicación | Nombre (`code`) | Editar | Agendas | Horarios | Eliminar (`window.confirm`).
- Filtro ubicación: “Todas” + una ubicación.
- Modales Agregar/Editar (ubicación + código); Agendas (typeahead + quitar + confirm mover en draft); Horarios (franjas día/desde/hasta).
- Draft hasta Aceptar; Cancelar descarta.
- Batch PUT transaccional agendas y hours; lookup enriquecido con consultorio actual.
- Quitar menú y ruta `/horarios-consultorio`.

### Out of Scope
- Campo `nombre` distinto de `code`.
- Cambios de roles.
- Borrar endpoints unitarios agendas/hours (compat).
- Rediseño visual global del menú Distribución.

## Approach

1. Backend: PUT replace agendas/hours por room; enriquecer agenda-lookup con `current_room_*`.
2. Frontend: reescribir `ConsultingRoomsPage` (grilla + 4 modales draft); quitar nav/ruta Horarios.
3. Tests backend batch + conflicto; nota runbook si hace falta.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `ConsultingRoomsPage.jsx` | Modified | Grilla + modales |
| `navigation.js`, `main.jsx` | Modified | Quitar Horarios |
| `RoomHoursPage.jsx` | Removed/orphan | Sin ruta |
| `consulting_rooms` router/schemas/services | Modified | Batch PUT |
| `distribucion` agenda-lookup | Modified | Enrichment |
| `openspec/specs/distribucion` | Modified | Merge on archive |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Race confirm_move | Med | Revalidar en batch; 409 sin apply |
| Partial UX confusion | Low | Labels claros Aceptar/Cancelar |
| Favoritos ruta vieja | Low | 404 aceptado |

## Rollback Plan

Revert branch/PR; restaurar menú/ruta Horarios y UI previa de Consultorios. Sin migración DB obligatoria.

## Dependencies

- APIs rooms/agendas/hours y agenda-lookup existentes.
- Ubicaciones (`/locations`) para filtro y selects.

## Success Criteria

- [ ] Al abrir Consultorios se ve la grilla filtrable con acciones por fila.
- [ ] Cada modal aplica solo con Aceptar; Cancelar no persiste.
- [ ] Horarios gestionables desde modal; menú/ruta Horarios eliminados.
- [ ] Batch agendas/hours atómicos; conflicto con confirm en draft + revalidación.
