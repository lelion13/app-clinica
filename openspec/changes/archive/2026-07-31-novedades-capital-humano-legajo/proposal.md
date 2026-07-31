# Proposal: Capital Humano + LEGAJO

## Intent

1. Extender el catálogo Novedades con **`LEGAJO`** del sync HTTP (string, trim, leading zeros).
2. Renombrar **Generación archivo XLS** → **Capital Humano** y reemplazar la grilla en pantalla por **un registro por profesional** (legajo, nombre, monto total, suma de ajustes) con ajustes persistidos (+/− con comentario) y dos descargas XLS (agregada + detalle histórico).

## Scope

### In Scope

- Columna `legajo` en `novedades_profesional` + sync (`LEGAJO`); ceros a la izquierda; ausente → null.
- Nav/título: **Capital Humano** (roles `admin`/`rrhh` sin cambio).
- Grilla agregada: 1 fila/profesional con actividad (carga o ajuste) en filtro período (± servicio).
- Monto total = suma cargas (módulos+novedades) ± ajustes en ese alcance.
- Columna suma ajustes; clic → modal historial + alta (importe con signo + comentario obligatorio).
- Ajustes: solo alta; admin/rrhh; permitidos con período cerrado.
- Dos botones XLS: (1) vista agregada, (2) formato detalle por carga actual.
- Filtro/orden estilo grilla de Carga.
- Migración Alembic, tests, runbook, delta specs.

### Out of Scope

- Edit/delete de ajustes.
- Cron sync / cambios a Distribución `professionals`.
- UI de `CODPROV`.
- Rol jefe en Capital Humano.

## Approach

1. Alembic: `legajo` nullable string; tabla `novedades_ajuste_capital` (professional_id, periodo_id, servicio_id nullable, importe signed, comentario, audit).
2. Extender `prof_sync` para mapear `LEGAJO`.
3. API: grilla agregada + CRUD-alta ajustes + list historial; exports agregada y detalle.
4. Frontend: renombrar página/nav; nueva grilla + modal; dos downloads.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/.../novedades` models/sync/export/router | Modified/New |
| `frontend/.../NovedadesXlsPage` + `navigation.js` | Modified |
| `docs/runbook.md` + OpenSpec | Modified |

## Risks

| Risk | Mitigation |
|------|------------|
| Ajustes con período cerrado confunden con “cargas cerradas” | Copy UI + API distinta; spec Q9 |
| Doble conteo servicio null vs filtrado | Ajuste guarda el mismo alcance que la grilla al crearlo |
| LEGAJO con espacios | trim extremos (Q5) |

## Rollback Plan

Revert deploy + migration down si no hay ajustes críticos; ajustes ya cargados requieren backup.

## Dependencies

- Archive `novedades-sincro-profesionales` (catálogo HTTP).
- API externa incluye `LEGAJO`.

## Success Criteria

- Sync persiste `legajo` con zeros; UI Capital Humano agregada; ajustes impactan total; 2 XLS; filtros/sort OK.
