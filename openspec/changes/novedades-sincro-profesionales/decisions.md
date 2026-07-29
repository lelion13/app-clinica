# Decisions: novedades-sincro-profesionales

Survey reiniciada 2026-07-29 · **cerrada** tras Q13.

## Q1 — Catálogo

**Elegido: A** — Dos catálogos separados.

- Distribución sigue con `professionals` (sync MySQL actual).
- Novedades usa un catálogo/tabla nuevo alimentado solo por la API HTTP (`/profesionales/activos`).
- Cada módulo consume solo su catálogo.

## Q2 — Clave de identidad (sync HTTP)

**Elegido:** `CODPROF` del API.

- Guardar como **string** (respetar ceros a la izquierda, p. ej. `"001"` ≠ `"1"`).
- Payload observado: `CODPROF`, `NOMBRES`, `CODPROV`.

## Q3 — Datos Novedades existentes

**Elegido: D** — Eliminar lo cargado en Novedades (clean slate hacia el catálogo nuevo).

## Q4 — Alcance del borrado

**Elegido: A** — Solo transaccional:

- Borrar: asignaciones de módulo, novedades, vínculos profesional↔servicio.
- Conservar: servicios, módulos catálogo, períodos, jefes↔servicio.

## Q5 — Quién sincroniza

**Elegido: C**

- Parametrización: botón sync solo `admin` / `rrhh`.
- Mis profesionales: botón sync también para `jefe_medico` (además de admin/rrhh).

## Q6 — ABM local catálogo Novedades

**Elegido: A** — Solo sync: sin alta/edición manual. Lectura + sync + asociar a servicio.

## Q7 — Vínculos al inactivar por sync

**Elegido: C**

- El vínculo profesional↔servicio **permanece**.
- En Mis profesionales se muestra como **inactivo** para limpieza manual.
- Sin cargas de módulos/novedades mientras el profesional esté inactivo.

## Q8 — Campo `CODPROV`

**Elegido: B** — Guardar como string (con ceros) para auditoría/futuro; **no** UI en este change.

## Q9 — Cuándo borrar lo transaccional

**Elegido: B** — Botón explícito “limpiar cargas” (admin/rrhh), **aparte** del sync.

## Q10 — Reactivación

**Elegido: A** — Si vuelve en el sync: reactivar automáticamente y actualizar `NOMBRES` (+ `CODPROV` almacenado).

## Q11 — Tipo de borrado al limpiar

**Elegido: B** — Hard-delete (irreversible) + confirmación modal obligatoria.

## Q12 — Ubicación botón limpiar

**Elegido: A** — Solo en **Parametrización** (`admin`/`rrhh`).

## Q13 — Feedback del sync

**Elegido: A** — Resumen creados / actualizados / inactivados / errores en modal con OK (`AlertModal`).

## Security

- URL y Bearer token solo por variables de entorno (nunca en repo/commits).
- Rotar token si quedó expuesto en chat.
