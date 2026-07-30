# Implementation notes — novedades-sincro-profesionales

Registro final del change (implementado + ops). Archivado 2026-07-30.

## Qué se entregó

1. **Catálogo Novedades aparte** — tabla `novedades_profesional` (`codprof` UNIQUE string con leading zeros, `full_name`, `codprov` persistido sin UI, `is_active`). Distribución sigue en `professionals` + sync MySQL.
2. **Sync HTTP** — `POST /novedades/profesionales/sync` vía `httpx` a `NOVEDADES_PROF_SYNC_URL` + Bearer `NOVEDADES_PROF_SYNC_TOKEN`. Upsert por `CODPROF`; inactiva ausentes **solo si el GET fue exitoso**; reactiva + actualiza nombre/`CODPROV` si reaparecen.
3. **Botones sync** — Parametrización (`admin`/`rrhh`); Mis profesionales (`admin`/`rrhh`/`jefe_medico`). Resumen en `AlertModal` (creados/actualizados/inactivados/errores).
4. **Inactivos** — no se pueden cargar módulos/novedades ni asociar de nuevo; vínculos existentes quedan y se muestran “Inactivo” en Mis profesionales para limpieza manual (soft-delete del vínculo).
5. **Limpiar cargas** — solo Parametrización (`admin`/`rrhh`); hard-delete asignaciones + novedades + vínculos profesional↔servicio; conserva servicios/módulos/períodos/jefes; modal Cancelar/Confirmar.
6. **Migración `0008_novedades_profesional`** — crea tabla; **borra** filas transaccionales al retarget de FKs (no hay map CODPROF desde `professionals.id`).

## Decisiones (sin ambigüedad)

Fuente: `decisions.md` Q1–Q13.

| Tema | Decisión |
|------|----------|
| Catálogos | **Dos**: Distribución ≠ Novedades |
| Identidad sync | `CODPROF` **string** (ej. `"001"`) |
| Clean slate | Borrar solo transaccional (cargas + vínculos); conservar param |
| Sync roles | Param: admin/rrhh · Mis prof.: + jefe |
| ABM catálogo | Solo sync (sin alta/edición manual) |
| Inactivo + vínculo | Vínculo queda; visible; sin cargas |
| `CODPROV` | Guardar; sin UI |
| Limpiar | Botón aparte (Param); hard-delete + confirm |
| Reactivar | Automático si vuelve en sync |
| Feedback sync | Modal con conteos |

## Aprendizajes / trampas (importante)

### L1 — Migración destructiva ≠ botón Limpiar

- **Hecho:** `0008` **debe** vaciar asignaciones/novedades/vínculos para poder cambiar el FK de `professionals` → `novedades_profesional`.
- **Producto:** el botón Limpiar es para **resets operativos posteriores**; el primer deploy ya limpia vía migración.
- **Ops:** backup DB **antes** de `alembic upgrade head`.

### L2 — Deploy sin migrar / sin env

- Sin `0008` → 500 en listados Novedades (FK/tabla nueva).
- Sin `NOVEDADES_PROF_SYNC_URL`/`TOKEN` → sync responde 422 “no configurado”.
- Checklist: `pull` → `up -d` → **`alembic upgrade head`** → verificar env → sync en Param.

### L3 — Fallo del API externo no debe inactivar

- Si el GET falla (red/401/timeout), **no** pasar el loop de inactivación.
- Inactivar solo sobre respuesta **exitosa** parseada.

### L4 — Leading zeros

- Nunca castear `CODPROF` a `int`. Persistencia y match siempre `str`.
- Tests cubren `"001"` ≠ `"1"`.

### L5 — Token / secretos

- Bearer **solo** env (nunca repo, logs ni OpenSpec).
- Si el token circuló en chat: **rotar** antes de prod.
- `.env.prod` no se commitea; en VPS agregar las 3 vars al archivo existente.

### L6 — Alembic revision id ≤ 32

- Usar ids cortos (`0008_novedades_profesional`); `alembic_version.version_num` es VARCHAR(32).

### L7 — Orden post-deploy de producto

1. Migrar  
2. Sync en Parametrización  
3. Reasociar en Mis profesionales  
4. Recién ahí cargar módulos/novedades  

Sin paso 2–3, Carga no tiene profesionales.

## Archivos clave

| Área | Path |
|------|------|
| Migración | `backend/alembic/versions/0008_novedades_profesional.py` |
| Modelo | `backend/app/models/novedades.py` → `NovedadesProfesional` |
| Sync | `backend/app/services/novedades/prof_sync.py` |
| Purge | `backend/app/services/novedades/purge.py` |
| Directory / cargas | `professional_directory.py`, `cargas.py`, `helpers.py`, `export_xls.py` |
| API | `POST /novedades/profesionales/sync`, `POST /novedades/transaccional/purge` |
| UI | `NovedadesParamPage.jsx`, `NovedadesMisProfesionalesPage.jsx` |
| Env | `.env.example`, `.env.prod.example` → `NOVEDADES_PROF_SYNC_*` |
| Tests | `backend/tests/test_novedades_prof_sync.py` |

## Deploy checklist (ops)

1. Backup DB  
2. Push código + imágenes GHCR (CI o build manual)  
3. En VPS: agregar `NOVEDADES_PROF_SYNC_*` a `.env.prod` (token rotado)  
4. `docker compose ... pull && up -d`  
5. `exec backend alembic upgrade head`  
6. Smoke: Param sync → Mis profesionales reasociar → Carga  

## Fuera de este change

- Unificar catálogos Distribución ↔ Novedades  
- Cron de sync automático  
- UI / filtros por `CODPROV`  
- Sync MySQL de Distribución (sin cambios)
