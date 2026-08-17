# Implementation notes — novedades-tiene-produccion

## v1 + v2 entregado

- Proxy `GET /novedades/bonos/tiene-produccion`
- Check en Cargar + editar fecha; fail-closed
- Force modal: Vacaciones/Enfermedad + obs; Cancelar/Cargar
- Persist `motivo_sin_produccion` / `observacion_sin_produccion` (rev `0017_sin_prod_motivo`)
- Columna “Sin prod.” en grilla Carga

## Post-survey UX

1. **Cancelar force limpia controles de carga** — profesional, módulo, tipo/horas, fecha (período/servicio quedan). Ver `clearCargaFields` en `NovedadesCargaPage`.
2. Componente `ForceSinProduccionModal.jsx`.

## Interacción posterior (`novedades-modulos-edicion`)

Si el módulo seleccionado tiene `produccion=false`, Carga **omite** el proxy (documentado en ese change; no reabre Q1–Q15).

## Archivos clave

- `backend/app/services/novedades/tiene_produccion.py`
- `backend/app/services/novedades/helpers.py` — `normalize_motivo_sin_produccion`
- `backend/alembic/versions/0017_sin_prod_motivo.py`
- `frontend/src/components/ForceSinProduccionModal.jsx`
- `frontend/src/pages/novedades/NovedadesCargaPage.jsx`, `CargasListGrid.jsx`
- `backend/tests/test_tiene_produccion.py`, domain tests motivo
- `.env.example`, `.env.prod.example`, `docs/runbook.md`

## Smoke sugerido

- [ ] Carga con producción true → POST normal
- [ ] false → force; Cancelar limpia form y no POST
- [ ] force Cargar con motivo+obs → filas con campos
- [ ] API error → modal error, sin force
- [ ] Editar fecha false → bloqueo simple
