# Decisions: capital-humano-bonos-resumen

**Survey cerrada** (2026-07-31).

## Checklist

- [x] Q1 — Match del campo `profesional` del API con el catálogo local
- [x] Q2 — Qué define cada columna dinámica (“opción”)
- [x] Q3 — Persistencia vs solo sesión
- [x] Q4 — Auth / URL del API externo (env, token, timeout)
- [x] Q5 — Filas: ¿solo profesionales ya en grilla o también solo-bonos?
- [x] Q5b — UX para ver profesionales “solo bonos”
- [x] Q6 — Sumar si hay múltiples filas API misma opción+profesional
- [x] Q6b — Re-ejecutar el botón: ¿reemplaza snapshot del período?
- [x] Q6c — Cuándo “congela” Capital Humano / desbloquea XLS
- [x] Q7 — Incluir columnas de bonos en XLS agregado
- [x] Q8 — Comportamiento si el API falla o período sin fechas
- [x] Q9 — Roles (¿mismo admin/rrhh?)
- [x] Q10 — Etiqueta del botón y feedback de carga

---

## Q1 — Match `profesional`

**Elegido: A** — Match contra `CODPROF` (string; preservar ceros si aplica, comparar con el valor del API tal como venga tras normalización string/trim).

## Q2 — Columnas dinámicas

**Elegido: A** — Una columna por combinación completa `centro|servicio|semana|horario` (header legible con esos 4 valores).

## Q3 — Persistencia

**Elegido: B** — Persistir en DB por período; al reabrir Capital Humano con ese período se muestran sin re-llamar el API. (Pendiente Q: si re-ejecutar el botón reemplaza o acumula.)

## Q4 — Auth / llamada externa

**Elegido: D** —
- Proxy solo backend.
- **Bearer token = el mismo** que sync de profesionales (`NOVEDADES_PROF_SYNC_TOKEN`).
- Query params obligatorios: `fecha_desde` = inicio del período, `fecha_hasta` = fin del período (ISO date).
- URL del resumen: configurable por env (p. ej. `NOVEDADES_BONOS_RESUMEN_URL`), default/documentar `https://api.cpmgsa.com.ar:8001/bonos/resumen`; timeout reutilizable o env propio.

## Q5 — Filas / solo-bonos

**Elegido: B** — Se persisten/asocian también bonos de profesionales del catálogo matched por CODPROF aunque no tengan cargas/ajustes. CODPROF desconocido en catálogo se ignora.

## Q5b — UX solo-bonos

**Elegido: C** — No van en la grilla principal de Capital Humano. Un botón abre un **modal** con esa lista (profesionales con bonos y sin cargas/ajustes en el período).

## Q6 — Duplicados API

**Elegido: A** — Sumar `cantidad` cuando coincide profesional + misma opción (`centro|servicio|semana|horario`).

## Q6b — Re-importar

**Elegido: A** — Mientras NO esté congelado: re-ejecutar **reemplaza** el snapshot de bonos del período. Tras congelar: no se puede pisar (ver Q6c).

## Q6c — Congelar / XLS

**Elegido: B (con excepción temporal de pruebas)** —
- Congelar = al **cerrar el período** de Novedades: no se puede re-importar/pisar bonos de ese período.
- Con período **abierto**: se puede importar/reemplazar bonos.
- **XLS:** por ahora (pruebas) permitir descarga **siempre**. Más adelante se podrá restringir a período cerrado; no bloquear XLS en este change.

## Q7 — XLS y bonos

**Elegido: C** — Tercer botón de descarga: **“XLS con bonos”** (agregado + columnas dinámicas). Los dos XLS actuales (agregado y detalle) quedan sin cambios.

## Q8 — Errores / fechas

**Elegido: C** — Si falla el API: modal de error; **no** modificar snapshot persistido. Si el período no tiene `fecha_inicio`/`fecha_fin` válidas: 422 claro **sin** llamar al API.

## Q9 — Roles

**Elegido: A** — Solo `admin` y `rrhh` (misma audiencia de Capital Humano).

## Q10 — Botón / feedback

**Elegido: A** — Botón **“Importar bonos”**; al éxito modal resumen (recibidas / matcheadas / solo-bonos / columnas / ignorados) + refresh de grilla. Período obligatorio antes de ejecutar.

