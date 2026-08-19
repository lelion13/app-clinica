# Tasks: capital-humano-bonos-servicios-especiales

## 1. Backend

- [x] 1.1 Extraer helper de elegibilidad “servicio especial” (`DEA|DEP|CAP|CAI`) sobre `bonos_by_prof`.
- [x] 1.2 Actualizar `build_capital_humano_rows` para incluir profesionales sin cargas/ajustes si cumplen regla especial.
- [x] 1.3 Ajustar `list_solo_bonos` para excluir profesionales promovidos a grilla principal.
- [x] 1.4 Mantener `monto_total = monto_cargas + monto_ajustes` sin cambios.

## 2. Frontend

- [x] 2.1 Quitar selector de servicio en `NovedadesXlsPage`.
- [x] 2.2 Dejar requests de grilla/import/export/detalle/ajustes sin enviar `servicio_id` desde esa UI.
- [x] 2.3 Ajustar textos de ayuda para reflejar ausencia de filtro de servicio.

## 3. Tests

- [x] 3.1 Agregar test: profesional solo-bonos CAP aparece en grilla principal.
- [x] 3.2 Agregar test: profesional solo-bonos de servicio no especial permanece en modal Solo bonos.
- [x] 3.3 Agregar test: profesional promovido no aparece en modal Solo bonos.

## 4. Docs

- [x] 4.1 Actualizar runbook con la nueva regla DEA/DEP/CAP/CAI.
- [x] 4.2 Actualizar delta spec y marcar tareas completadas al finalizar apply.
