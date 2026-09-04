# Archive Report: novedades-capital-humano-export-liquidacion

## Change Summary
- **Change Name:** `novedades-capital-humano-export-liquidacion`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-09-04

## Delivered Capabilities
1. Botón **Descargar liquidación** en Capital Humano (solo período cerrado); exports previos intactos.
2. Endpoint `GET /novedades/export-liquidacion.xlsx?periodo_id=…` (`admin`/`rrhh`).
3. XLS con columnas `empresa`, `legajo`, `monto`, `concepto`.
4. Filas por `concepto_liquidacion` de cargas; empresa CHI si concepto > 100, si no CMG.
5. Producción (bonos/prácticas/internaciones) sumada a filas de carga (partes iguales / fallback).
6. Sin cargas: solo DEA/DEP/CAP/CAI con conceptos fijos 90/91/122/123.
7. Ajustes prorrateados; bloqueo si falta concepto en algún servicio (con nombres).

## Verification
- User-tested OK (2026-09-04).
- Automated: `159 passed` pytest; frontend Vite build OK.
- Docs: `docs/runbook.md` updated.
