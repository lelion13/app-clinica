# Proposal: novedades-capital-humano-export-liquidacion

## Intent

Agregar en Capital Humano un botón **Descargar liquidación** que genere un `.xlsx` con columnas `empresa`, `legajo`, `monto`, `concepto`, agrupado por liquidación (concepto del servicio + reglas de empresa), sumando producción y ajustes sobre las filas de cargas, **sin modificar** las exportaciones existentes.

## Scope

### In Scope
- Nuevo endpoint `GET /novedades/export-liquidacion.xlsx?periodo_id=…` (`admin`/`rrhh`).
- Solo períodos **cerrados**.
- Armado de filas desde cargas (módulos/novedades) por `concepto_liquidacion` del servicio.
- Empresa: `concepto > 100` → `CHI`; caso contrario → `CMG`.
- Producción valorizada (bonos, prácticas, internaciones) sumada a esas filas; si varios conceptos de la misma empresa → partes iguales; si no hay conceptos de esa empresa → repartir en todos los conceptos de carga del profesional.
- Sin cargas: exportar solo si hay bonos especiales DEA/DEP/CAP/CAI, usando conceptos fijos 90/91/122/123.
- Ajustes (“Agregar importe”) prorrateados en partes iguales sobre los conceptos del profesional.
- Bloqueo total si algún servicio de las cargas del período no tiene `concepto_liquidacion` (mensaje con nombres de servicios).
- UI: botón **Descargar liquidación** junto a los downloads actuales (habilitado solo con período cerrado).

### Out of Scope
- Cambiar grilla on-screen, Actualizar, Detalle, Agregar importe UX.
- Reemplazar o alterar `export-capital.xlsx` / `export-capital-bonos.xlsx` / `export.xlsx`.
- Editar ABM de conceptos en servicios (ya existe).

## Approach

1. Service puro `build_liquidacion_rows(db, periodo_id)` + `export_liquidacion_xlsx_bytes`.
2. Reusar snapshots/eligibility/valorization de Capital Humano existentes.
3. Endpoint nuevo + botón UI.
4. Tests unitarios de prorrateo, fail-closed sin concepto, período abierto, solo-producción.
