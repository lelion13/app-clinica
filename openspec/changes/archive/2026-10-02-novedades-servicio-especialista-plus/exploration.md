# Exploration: novedades-servicio-especialista-plus

## Intent
Gate the +20% specialist module factor on **both** professional `es_especialista` **and** a new per-service flag (UI “Especialista”, like Activo). Apply only when the jefe loads the module **in a service that has the flag on**. Multi-service modules: factor depends on the **service of the assignment**, not on whether another linked service has the flag.

## Current behavior
- `modulo_valor_para_profesional(catalog, es_especialista)` → ×1.20 if professional flag only
- Used on create/update asignación; novedades never get the factor
- CH/export use persisted `asignacion.valor`

## Survey
CLOSED — see decisions.md
