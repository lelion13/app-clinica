# Tasks: capital-humano-profesionales-especialistas

## 1. Datos / config

- [x] 1.1 Alembic: `novedades_profesional.es_especialista` + `novedades_asignacion_modulo.valor` (persistir plus)
- [x] 1.2 Model + schemas (sync response unmatched/warning; CH `es_especialista`)
- [x] 1.3 Config: `NOVEDADES_PROF_ESPECIALISTAS_URL` (+ timeout); token reutilizado
- [x] 1.4 `.env.example` / `.env.prod.example`

## 2. Backend sync

- [x] 2.1 Fetch + normalize especialistas (`profesional`, `descripcion`)
- [x] 2.2 Integrar en sync Param (`sync_especialistas=True`); set/clear flags; unmatched
- [x] 2.3 Fallo especialistas → warning; no mutar flags
- [x] 2.4 Mis profesionales: mismo endpoint sin `include_especialistas` (default false)

## 3. Backend carga módulo

- [x] 3.1 Create/update asignación: si especialista, `valor = catalogo × 1.20`
- [x] 3.2 Export/CH leen `asignacion.valor`; novedades sin factor

## 4. Frontend

- [x] 4.1 Param: sync con `include_especialistas=1`; modal/info unmatched + warning
- [x] 4.2 Capital Humano Detalle: indica especialista
- [x] 4.3 `es_especialista` en row CH

## 5. Docs / tests

- [x] 5.1 Tests: match/unmatched, fail parcial, módulo ×1.20
- [x] 5.2 Runbook
- [x] 5.3 Marcar tasks al cerrar apply
