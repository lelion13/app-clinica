# Implementation notes — novedades-jefe-profesionales-fecha-carga

Registro final del change (implementado + aprendizajes en prod). Archivado 2026-07-29.

## Qué se entregó

1. **Mis profesionales** (`/novedades/mis-profesionales`): admin/rrhh/jefe; jefe scoped; typeahead; soft-delete vínculo siempre OK.
2. **`fecha_realizacion`** en asignaciones y novedades (migración `0007_fecha_realizacion`); validación período ∩ ≤ hoy; grilla/XLS con ambas fechas; edición con período abierto.
3. **UX**: labels alineados; date picker sin rango inválido; `AlertModal` (OK) para errores; `ProfessionalCombobox` en Carga/Mis/Param.

## Decisiones (resumen)

Ver `decisions.md` Q1–Q9 + R12–R14.

## Aprendizajes / fallas (importante)

### F1 — Deploy sin Alembic → 500 en listados

- **Síntoma:** `GET /novedades/asignaciones-modulos` y `/cargas` → 500; UI “Internal Server Error”; dropdowns vacíos (falla el `Promise.all` de load). Log: columna `fecha_realizacion` does not exist.
- **Causa:** se publicaron imágenes con el modelo nuevo **sin** `alembic upgrade head`.
- **Fix:** `docker compose ... exec backend alembic upgrade head` → `0007_fecha_realizacion`.
- **Lección:** checklist post-deploy Novedades: **pull/up + siempre migrar**. Un 401 puntual en `/auth/me` al refrescar cookie no explica el 500.

### F2 — Date picker todo gris (min > max)

- **Síntoma:** período “Agosto” abierto pero hoy aún en julio → ningún día clickeable.
- **Causa:** UI ponía `min=fecha_inicio` y `max=hoy` con `min > max`; el browser deshabilita todo.
- **Fix (R13):** rango válido = `[inicio, min(fin, hoy)]`; si vacío → disable + mensaje; no enviar min>max.
- **Producto:** coherente con Q6 (dentro del período y ≤ hoy): un período futuro abierto **no** admite cargas de realización hasta que empiece.

### F3 — RRHH bloqueado al asociar profesionales

- **Causa:** reutilizar `assert_can_load_servicio` (solo admin/jefe) en create/delete de profesional↔servicio.
- **Fix:** `assert_can_manage_profesional_servicio` (admin/rrhh global; jefe scoped).

### F4 — Alertas poco visibles

- Labels rojos fáciles de pasar por alto / mal alineados con el flujo.
- **Fix (R14):** `AlertModal` con OK en pantallas Novedades.

### F5 — Alembic revision id (contexto previo)

- `alembic_version.version_num` VARCHAR(32): ids largos fallan. Usar ids cortos (`0007_fecha_realizacion`).

## Archivos clave

| Área | Path |
|------|------|
| Migración | `backend/alembic/versions/0007_fecha_realizacion.py` |
| Validación fecha / roster | `backend/app/services/novedades/helpers.py` |
| Cargas + profesional-servicios | `backend/app/services/novedades/cargas.py` |
| Export | `backend/app/services/novedades/export_xls.py` |
| Página Mis profesionales | `frontend/src/pages/novedades/NovedadesMisProfesionalesPage.jsx` |
| Carga + fechas | `frontend/src/pages/novedades/NovedadesCargaPage.jsx` |
| Alert modal | `frontend/src/components/AlertModal.jsx` |
| Combobox | `frontend/src/components/ProfessionalCombobox.jsx` |

## Deploy checklist (ops)

1. Build/push imágenes backend + frontend  
2. `pull` + `up -d`  
3. **`alembic upgrade head`** (obligatorio si hay revision nueva)  
4. Smoke: login jefe → Carga carga listados; Mis profesionales; date picker con período en curso  

## Fuera de este change

- Sync sábana de profesionales desde API externa (otro change futuro).
