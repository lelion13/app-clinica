# Tasks: capital-humano-bonos-resumen

## 1. Datos

- [x] 1.1 Alembic: tablas opción + cantidad por período/profesional (UNIQUE keys)
- [x] 1.2 Models SQLAlchemy + schemas Pydantic (import summary, row bonos map, solo-bonos)

## 2. Backend

- [x] 2.1 Config: `NOVEDADES_BONOS_RESUMEN_URL` (+ timeout opcional); reutilizar token sync
- [x] 2.2 Service fetch + normalize + match CODPROF + sum duplicates + replace snapshot si período open
- [x] 2.3 Bloquear import si período closed / sin fechas (422); fallo externo no muta snapshot
- [x] 2.4 Extender `GET /capital-humano` con columnas/cantidades bonos del período
- [x] 2.5 `POST /capital-humano/bonos/import`, `GET .../bonos/solo`, `GET /export-capital-bonos.xlsx`
- [x] 2.6 Tests: match, sum, replace, freeze closed, fechas faltantes, fallo externo

## 3. Frontend

- [x] 3.1 Botón Importar bonos (período obligatorio; disabled si closed)
- [x] 3.2 Columnas dinámicas a la derecha en grilla
- [x] 3.3 Modal Solo bonos
- [x] 3.4 Tercer botón XLS con bonos + modal resumen/errores

## 4. Docs

- [x] 4.1 Runbook: env URL + token reutilizado + freeze al cerrar período
- [x] 4.2 Marcar tasks al cerrar apply
- [x] 4.3 Archivar change + merge Importar bonos a spec estable (2026-08-20)
