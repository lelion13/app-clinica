# Implementation notes — novedades-produccion-valor-bonos

Registro de lo implementado (survey + iteraciones post-apply) y aprendizajes para futuros changes.

## Survey → código

| Q | Elegido | Implementación |
|---|---------|----------------|
| Q1 | Match 4 campos | FK `opcion_id` → `novedades_bono_opcion` |
| Q2 | Una tarifa / opción; editar | UNIQUE `opcion_id` + soft-delete |
| Q3 | Solo 4 campos + valor ≥ 0 | modelo + schemas |
| Q4 | Cantidad + subtotal | `kind` / `opcion_key` en columnas |
| Q5 | Sin tarifa → 0 + banner | `opciones_sin_tarifa` |
| Q6 | Total = cargas + ajustes + bonos | `monto_bonos` + `monto_total` |
| Q7 | XLS con subtotales + agregado | export helpers |
| Q8 | admin/rrhh | deps existentes |
| Q9 | Selector desde opciones importadas | `GET /bono-opciones?sin_tarifa=1` |

## Post-survey / post-apply (misma change)

1. **Alta múltiple** — `POST /novedades/produccion-tarifas/bulk` con `{ opcion_ids, valor_unitario }` para cargar varias opciones con el mismo valor.
2. **Selector searchable** — reemplazo de checkboxes por `BonoOpcionMultiCombobox` (filtrar al escribir, multi-select, chips).
3. **Cleanup de opciones huérfanas en import** — `cleanup_unused_opciones()` al importar bonos: soft-delete si (a) no viene en el import actual, (b) no tiene tarifa Producción, (c) no tiene cantidades en ningún período.

## Migraciones

- `0021_produccion_tarifa` — tabla `novedades_produccion_tarifa`

Post-deploy: `alembic upgrade head`. Re-importar bonos del período activo si hace falta limpiar opciones `DOMINGO`/`SABADO` huérfanas tras pasar a SADOFE.

## Dependencias

- Requiere `capital-humano-bonos-resumen` (snapshot + columnas).
- Requiere `capital-humano-bonos-servicios-especiales` (promoción DEA/DEP/CAP/CAI); este change **cambia** `monto_total` para incluir bonos valorizados.

## Aprendizajes (errores / fricción)

### F1 — Colisión de nombres en React state (`editProduccion`)

**Qué pasó:** en `NovedadesParamPage.jsx` el tab Módulos ya usaba `editProduccion` (boolean del checkbox módulo). El modal de tarifas Producción reutilizó el mismo nombre → build/GHCR falló por redeclaración.

**Lección:** en páginas Param con varios ABMs, prefijar estado por dominio (`editTarifa`, `editTarifaValor`, `deleteTarifa`). Antes de agregar state, buscar el identificador en el archivo.

### F2 — Build local vs imagen GHCR (`recharts`)

**Qué pasó:** `npm run build` local falló por `recharts` ausente (área Estadísticas/Indicadores), mientras el cambio de Producción era correcto.

**Lección:** no atribuir un fallo de build al change en curso sin mirar el módulo que Rollup reporta. Verificar `package.json` / lockfile del área señalada; no bloquear archive de Novedades por deps de otra feature.

### F3 — Catálogo de opciones vs snapshot por período

**Qué pasó:** el selector de Producción listaba opciones históricas; al cambiar el import a SADOFE quedaban claves `DOMINGO`/`SABADO` huérfanas.

**Lección:** separar “hechos del período” (cantidades) de “catálogo global” (opciones). Si el catálogo se alimenta del import, definir cleanup explícito con condiciones de seguridad (tarifa / cantidades históricas) y documentarlo en runbook.

### F4 — UX de listas largas en modales

**Qué pasó:** checkboxes scrolleables no escalan con decenas de opciones.

**Lección:** preferir combobox con filtro + multi-select + chips desde el primer diseño cuando el catálogo es dinámico/largo.

### F5 — Naming de dominio “Producción”

**Qué pasó:** tab Param **Producción** (tarifas bonos) vs flag módulo `produccion` (skip check externo) generan confusión.

**Lección:** help text obligatorio en UI + runbook; en código usar nombres distintos (`produccion_tarifa` / `modulo.produccion`).

## Deferred

- Test explícito 403 `jefe_medico` en endpoints tarifa (task 7.4 opcional) — deps admin/rrhh ya cubren el patrón; smoke RBAC post-deploy.

## Smoke sugerido

- [ ] Param → Producción → buscar opción → multi-select → Cargar bulk
- [ ] Editar valor; Eliminar (Esc/Cancelar no borra)
- [ ] Capital Humano: cantidad + subtotal; banner si falta tarifa
- [ ] `monto_total` incluye bonos; XLS agregado y XLS con bonos coherentes
- [ ] Re-import limpia opciones sin tarifa ni cantidades
