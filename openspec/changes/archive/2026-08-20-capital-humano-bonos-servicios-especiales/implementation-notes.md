# Implementation notes — capital-humano-bonos-servicios-especiales

Registro de lo implementado tras survey y aprendizajes para futuros changes.

## Survey → código

| Q | Elegido | Implementación |
|---|---------|----------------|
| Q1 | Solo-bonos especiales → grilla | `build_capital_humano_rows` promoción |
| Q2 | Promovidos fuera de Solo bonos | `list_solo_bonos` excluye promovidos |
| Q3 | `monto_total` sin valorizar bonos | `cargas + ajustes` (sin `monto_bonos`) |
| Q4 | Quitar selector servicio en UI | `NovedadesXlsPage` sin `servicio_id` |
| Q5 | Match exacto `DEA\|DEP\|CAP\|CAI` | helper sobre `servicio` de la opción |
| Q6 | Incluir en XLS agregado / con bonos | misma elegibilidad de filas |

## Post-survey

Ningún delta UX mayor. Valorización monetaria quedó **fuera de alcance** y se implementó en change hermano `novedades-produccion-valor-bonos` (ese change **modifica** la fórmula de `monto_total`).

## Dependencias

- Requiere `capital-humano-bonos-resumen` (import, snapshot, modal Solo bonos, columnas dinámicas).
- Archivar **antes o el mismo día** que `novedades-produccion-valor-bonos` para que la spec estable refleje primero la promoción y luego la valorización.

## Aprendizajes (errores / fricción)

### F1 — Orden de changes y fórmula de `monto_total`

**Qué pasó:** este change dejó explícito `monto_total = cargas + ajustes`. El change de tarifas lo reescribió a `+ monto_bonos`.

**Lección:** si un change A documenta una fórmula y el change B la cambia, el delta de B debe ser **MODIFIED** claro sobre el mismo requirement; en archive, sincronizar en orden A → B y anotar supersession en `implementation-notes` / archive-report.

### F2 — Match de “servicio” del bono ≠ servicio Param

**Qué pasó:** el `servicio` de la opción de bono es un string del API externo (`CAP`, `DEA`, …), no el id/nombre del maestro `novedades_servicio`.

**Lección:** al diseñar reglas de negocio sobre bonos, nombrar el campo (`opción.servicio` / `bono_servicio`) y fijar match exacto vs trim/case en survey; no asumir FK al ABM de Servicios.

### F3 — Compatibilidad backend al quitar filtro UI

**Qué pasó:** se quitó el select de servicio en Capital Humano pero se mantuvo `servicio_id` opcional en API.

**Lección:** “retirar de UI” ≠ “borrar contrato”; documentar en design que el backend queda compatible para scripts/tests.

### F4 — Tests de elegibilidad

**Qué pasó:** hace falta cubrir tres caminos: especial → grilla; no especial → Solo bonos; promovido ausente del modal.

**Lección:** para reglas de inclusión/exclusión simétricas, tres tests mínimos evitan regresiones al tocar `build_capital_humano_rows` / `list_solo_bonos` juntos.

## Smoke sugerido

- [ ] Profesional solo-bonos `CAP` aparece en grilla con montos 0 (pre-tarifas) / con bonos valorizados (post-tarifas)
- [ ] Profesional solo-bonos de servicio no especial solo en modal Solo bonos
- [ ] Capital Humano sin selector de servicio; filtros período + texto OK
- [ ] XLS agregado / con bonos incluyen promovidos
