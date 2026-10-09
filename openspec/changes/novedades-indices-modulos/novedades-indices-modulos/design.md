# Design: novedades-indices-modulos

## Overview

Admin-only **Índices** page under Novedades: period-scoped aggregates by service and by professional. No migration; read-only aggregation over existing cargas, ajustes, and bonos snapshot.

## API

`GET /novedades/indices?periodo_id=` → `IndicesResponse`  
Auth: `require_admin` only.

```
IndicesResponse
  periodo_id
  por_servicio: [{ servicio_id, servicio_nombre, horas, monto, profesionales, modulos }]
  por_profesional: [{ professional_id, legajo, professional_name, horas, modulos,
                      produccion_monto, produccion_cantidad }]
```

## Aggregation

**Sources:** `novedades_asignacion_modulo`, `novedades_novedad`, `novedades_ajuste_capital` (non-deleted), `novedades_bono_cantidad` via `load_bonos_snapshot`, module catalog `valor` for assignment ARS (as export_xls).

**Horas:** net novedad hours; `horas_a_descontar` subtracts when that tipo exists in the DB enum; otherwise all tipos add.

**Monto (servicio):** Σ module catalog valores for assignments + Σ (horas × valor_hora) for novedades + Σ ajustes with that `servicio_id`.

**Producción (profesional):** cantidad = Σ bonos quantities (CH snapshot). Monto ARS = 0 on this codebase generation if no producción tarifas wired into CH (same surface as current CH qty-only columns); when tarifas exist later, align to CH valorización.

## UI

`/novedades/indices` — period select + two stacked tables. Nav item last in `NOVEDADES_ITEMS`, roles `["admin"]`.

## Files

| File | Change |
|------|--------|
| `services/novedades/indices.py` | New |
| `schemas/novedades.py` | Response models |
| `api/routers/novedades.py` | Endpoint |
| `NovedadesIndicesPage.jsx` | New |
| `navigation.js`, `main.jsx` | Wire |
| `docs/runbook.md` | Note |
| `tests/test_indices.py` | Unit helpers |
