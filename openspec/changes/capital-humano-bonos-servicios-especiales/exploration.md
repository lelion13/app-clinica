# Exploration: capital-humano-bonos-servicios-especiales

## Topic

Ajustar Capital Humano para que ciertos profesionales con bonos importados entren en la grilla principal aunque no tengan cargas/módulos.

## Current State

- Grilla principal se arma con profesionales que tienen cargas y/o ajustes.
- Profesionales con solo bonos se muestran en modal `Solo bonos`.
- UI tiene filtro por servicio; backend también soporta `servicio_id`.

## Nuevo requerimiento

- Incluir en la grilla principal a profesionales con bonos del período cuando exista al menos una opción cuyo `servicio` sea exactamente `DEA`, `DEP`, `CAP` o `CAI`.
- Mantener todo lo demás igual.
- Quitar selector de servicio solo en UI de Capital Humano (backend compatible).

## Riesgos

- Doble aparición entre grilla y modal Solo bonos si no se ajusta el cálculo de exclusión.
- Confusión funcional por ocultar filtro solo en UI y mantener parámetro backend.

## Ready for Proposal

Sí. Encuesta cerrada en `decisions.md`.
