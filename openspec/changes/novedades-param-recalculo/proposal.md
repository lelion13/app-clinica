# Proposal: Recálculo de valores (módulos / horas) en Parametrización

## Intent

Permitir a `admin`/`rrhh` recalcular los importes ya persistidos de **asignaciones de módulo** y/o **novedades de horas** de un período, usando el catálogo/`valor_hora` **actual**, con preview de impacto antes de aplicar — pestaña **Recálculo** en Parametrización (después de Feriados).

## Scope

### In Scope
- Nueva pestaña **Recálculo** en Parametrización (después de Feriados).
- Filtros: período (abierto o cerrado) + modo (solo horas / solo módulos / ambos).
- Preview: resumen por módulo de catálogo (actual vs nuevo) + bloque horas (actual vs nuevo).
- Apply solo si hay al menos un cambio; actualiza filas cuyo importe nuevo ≠ actual.
- Módulos: nuevo valor = misma regla de carga (incl. plus especialista ×1.20 si aplica).
- Horas: mantiene cantidad `horas`; nuevo importe = horas × `valor_hora` del servicio (signo por tipo).
- Excluye soft-deleted. Roles: `admin`/`rrhh`.

### Out of Scope
- Filtro por servicio o profesional.
- Cambiar cantidad de horas o cambiar el módulo asociado.
- Recálculo de producción/bonos/ajustes CH.
- Histórico/auditoría dedicada más allá de `updated_at`/`updated_by` existentes.

## Approach

1. APIs preview + apply (`admin`/`rrhh`) sobre cargas del período.
2. Comparar valor persistido vs valor recalculado desde catálogo/`valor_hora`.
3. UI pestaña: selects + Vista previa + Confirmar.

## Affected Areas

| Area | Impact |
|------|--------|
| `NovedadesParamPage` | Nueva tab Recálculo |
| API/services novedades | Preview + apply recalculo |
| `novedades_asignacion_modulo.valor` / novedades valor | Update selectivo |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Recalc en período cerrado altera liquidación ya vista | Med | Preview obligatorio; confirmación explícita |
| Plus especialista mal aplicado | Med | Reusar `modulo_valor_para_profesional` |

## Rollback Plan

Quitar tab + endpoints; valores ya recalculados no se revierten automáticamente.

## Dependencies

Ninguna externa.

## Success Criteria

- [ ] Tab Recálculo visible para `admin`/`rrhh` después de Feriados.
- [ ] Preview muestra desglose módulo + bloque horas; Apply bloqueado si no hay cambios.
- [ ] Apply actualiza solo filas con diferencia; soft-delete excluidas.
