# Decisions: capital-humano-bonos-servicios-especiales

Survey: **una pregunta a la vez**. Estado: **CLOSED**.

## Contexto heredado (sin cambios)

Se mantiene vigente lo definido en `capital-humano-bonos-resumen` para:
- importación de bonos
- persistencia snapshot por período
- restricciones de período abierto/cerrado
- botón y feedback del import
- modal Solo bonos
- estructura de columnas dinámicas

## Nuevas decisiones

### Q1 — Inclusión de profesionales en grilla principal
**Elegido: A** — Si el profesional tiene bonos importados en el período, debe entrar a grilla principal solo cuando la opción del bono tenga `servicio` exacto en: `DEA`, `DEP`, `CAP`, `CAI`, aunque no tenga módulos/cargas.

### Q2 — Monto total para esos casos
**Elegido: D→A (temporal)** — Por ahora `monto_total = monto_cargas + monto_ajustes`. El valor económico de bonos se definirá en otro change.

### Q3 — Filtro de servicio en Capital Humano
**Elegido: D** — Se elimina la posibilidad de filtrar por servicio **solo en UI** de Capital Humano. No se cambia la lógica de negocio general.

### Q4 — Alcance técnico del punto anterior
**Elegido: A** — Endpoints backend siguen aceptando `servicio_id` por compatibilidad; la UI de Capital Humano deja de enviarlo.

### Q5 — Relación con modal Solo bonos
**Elegido: A** — Si un profesional entra en la grilla principal por regla DEA/DEP/CAP/CAI, ya no debe aparecer en modal Solo bonos.

### Q6 — Regla de comparación de servicio especial
**Elegido: A** — Match exacto de texto: `DEA`, `DEP`, `CAP`, `CAI` (mayúsculas).

### Q7 — Exportaciones
**Elegido: A** — Los profesionales incorporados por esta regla también deben aparecer en `XLS con bonos` y en `XLS agregado`.

### Q8 — Detalle/Ajustes al quitar filtro UI
**Elegido: A** — Solo cambia UI. Detalle/Ajustes conservan soporte backend existente.

## Resumen

- Grilla principal de Capital Humano incorpora profesionales “solo bonos” cuando tengan al menos una opción con servicio `DEA|DEP|CAP|CAI`.
- Solo aplica con período seleccionado y snapshot de bonos.
- Sin valorización monetaria de bonos en este change.
- Selector de servicio se oculta en la UI de Capital Humano.
