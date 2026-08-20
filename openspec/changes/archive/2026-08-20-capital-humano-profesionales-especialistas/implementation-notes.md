# Implementation notes — capital-humano-profesionales-especialistas

## Survey → código

| Q | Decisión | Código |
|---|----------|--------|
| Q1 | Solo módulos | `create_asignacion` / update; novedades sin factor |
| Q2 | Plus al cargar | columna `valor` en `novedades_asignacion_modulo` |
| Q3 | Sync solo Param | `?include_especialistas=1`; Mis profesionales sin flag |
| Q4 | Fallo parcial | `especialistas_warning`; flags intactos |
| Q5 | Visible en Detalle CH | `es_especialista` en row + texto Detalle |

## Hallazgo de diseño

Las asignaciones **no** guardaban valor: leían `modulo.valor` del catálogo. Para cumplir “persistir ×1.20 al cargar” hizo falta snapshot `asignacion.valor` (migración `0022` + backfill).

## Aprendizajes (errores)

### F1 — `alembic_version.version_num` VARCHAR(32)

**Qué pasó:** `revision = "0022_especialista_asignacion_valor"` (34 chars). El DDL corrió; falló al UPDATE de `alembic_version` → columnas creadas, version quedó en `0021`.

**Lección:** revision id **siempre ≤ 32**. Preferir nombres cortos (`0022_especialista_valor`). Tras un fallo a mitad, hacer `upgrade` **idempotente** (`information_schema`) para re-deploy seguro.

### F2 — Mismo endpoint, distinto comportamiento Param vs Mis profesionales

**Qué pasó:** ambos UI llamaban `POST /profesionales/sync`.

**Lección:** query flag (`include_especialistas`) en el mismo endpoint evita duplicar rutas y deja Mis profesionales sin pegarle a la API de especialistas.

### F3 — Match `profesional` → `codprof` string

**Lección:** misma regla que bonos/CODPROF (trim, no castear a int). Unmatched no crean filas de catálogo; solo modal.

### F4 — Cargas históricas

**Lección:** backfill de `valor` = catálogo sin plus. Cargas nuevas de especialistas llevan ×1.20; no hay recálculo automático de histórico.

## Migraciones

- `0022_especialista_valor` (≤32; idempotente)

Post-deploy: set `NOVEDADES_PROF_ESPECIALISTAS_URL`, `alembic upgrade head`, sync desde Param.

## Smoke (ops)

- [x] Migración aplicada en VPS tras fix F1
- [x] Usuario confirmó que funcionó
