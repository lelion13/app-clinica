# Proposal: novedades-carga-novedad-extra

## Intent

En Carga, para módulos con `produccion=false`, permitir marcar **Novedad extra**: forzar el modal “sin producción” (sin llamar al API) y bloquear la novedad de horas, sin romper el skip actual cuando el check no está tildado.

## Scope

### In Scope
- Checkbox **Novedad extra** junto al selector de módulo cuando `produccion=false`.
- Default destildado; al cambiar a módulo con producción → ocultar y limpiar.
- Tildado: limpiar y deshabilitar bloque novedad (tipo/horas); al submit abrir mismo modal force-load sin proxy; POST solo asignación de módulo con motivo/obs.
- Destildado: comportamiento actual del flag módulo (skip check, puede ir con novedad).

### Out of Scope
- Nueva columna/flag en DB.
- Cambios en Param, Capital Humano, o API `tiene-produccion`.
- Nuevos motivos fuera de Vacaciones/Enfermedad.

## Approach

UI-only en `NovedadesCargaPage`: branch `novedadExtra` antes del skip/check; reutilizar modal force existente.

## Affected Areas

| Area | Impact |
|------|--------|
| `frontend/.../NovedadesCargaPage.jsx` | Modified |
| `openspec/specs/novedades/spec.md` | Delta |
| `docs/runbook.md` | Modified (al apply) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Confundir “Novedad extra” con fila novedad | Med | Copy clara; bloque horas limpio/disabled |
| Regresión skip sin check | Low | Destildado = path actual |

## Rollback Plan

Quitar checkbox y branch; volver al skip incondicional para `produccion=false`.

## Success Criteria

- [ ] Módulo sin prod + check off → POST directo (como hoy).
- [ ] Módulo sin prod + check on → modal force, sin API, solo módulo, sin horas.
- [ ] Módulo con prod → sin checkbox; flujo producción intacto.
