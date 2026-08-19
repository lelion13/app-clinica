# Tasks: novedades-produccion-valor-bonos

## 1. Backend — modelo y migración

- [x] 1.1 Agregar modelo `NovedadesProduccionTarifa` (`opcion_id` UNIQUE, `valor_unitario` INTEGER ≥ 0, AuditMixin).
- [x] 1.2 Crear migración Alembic `0021_produccion_tarifa`.

## 2. Backend — schemas y servicio

- [x] 2.1 Schemas: `ProduccionTarifaCreate/Update/Response`, extender `BonoColumnaResponse` (`kind`, `opcion_key`), `CapitalHumanoRowResponse` (`bonos_subtotales`, `monto_bonos`), `CapitalHumanoGridResponse` (`opciones_sin_tarifa`).
- [x] 2.2 Servicio `produccion_tarifas.py`: list, create, update, delete (soft), list_bono_opciones (filtro sin tarifa).
- [x] 2.3 Validaciones: entero ≥ 0; opcion_id existente; no duplicar tarifa activa por opción.

## 3. Backend — valorización Capital Humano

- [x] 3.1 Helper `load_tarifas_by_opcion_key()` desde DB.
- [x] 3.2 En `build_capital_humano_rows`: calcular subtotales y `monto_bonos`; `monto_total = cargas + ajustes + monto_bonos`.
- [x] 3.3 En `build_capital_humano_grid`: duplicar columnas (cantidad + subtotal); poblar `opciones_sin_tarifa`.
- [x] 3.4 Actualizar `export_capital_xlsx_bytes` y `export_capital_bonos_xlsx_bytes` con subtotales y total bonos.

## 4. Backend — API

- [x] 4.1 Rutas CRUD `/novedades/produccion-tarifas` (admin/rrhh).
- [x] 4.2 Ruta `GET /novedades/bono-opciones` para selector Param.

## 5. Frontend — Param Producción

- [x] 5.1 Tab **Producción** entre Módulos y Jefes ↔ servicios.
- [x] 5.2 Grilla + **Nueva producción** + modales editar/eliminar (patrón Servicios, Esc cancela).
- [x] 5.3 Help text disambiguating vs flag módulo `produccion`.

## 6. Frontend — Capital Humano

- [x] 6.1 Render columnas cantidad + subtotal por opción.
- [x] 6.2 Banner cuando `opciones_sin_tarifa` no vacío.
- [x] 6.3 Actualizar textos de ayuda (fórmula total).

## 7. Tests

- [x] 7.1 CRUD tarifa + unique opcion_id (valorize unit tests).
- [x] 7.2 Valorización: qty × valor; 0 sin tarifa; monto_total correcto.
- [x] 7.3 Export XLS con subtotales (grid/export helpers).
- [ ] 7.4 403 jefe_medico en endpoints tarifa (opcional v1).

## 8. Docs

- [x] 8.1 Actualizar `docs/runbook.md`.
- [ ] 8.2 Marcar tasks completadas al finalizar apply; archivar change y merge delta spec.
