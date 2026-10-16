# Design: novedades-indices-modulos

## Overview

Admin-only **Índices** under Novedades (period aggregates) plus catalog field **`módulo.horas`** so Índices can sum structured module duration + novedad hours.

## Data

Migration: nullable integer `horas` on `novedades_modulo` (existing → NULL).  
Create/Update: require `horas` int ≥ 1 (Pydantic + Param UI). Import Excel módulos unchanged.

## API

`GET /novedades/indices?periodo_id=` → `IndicesResponse` (`require_admin`).

## Aggregation

**Horas:** Σ `coalesce(modulo.horas, 0)` per assignment + net novedad hours (`horas_a_descontar` subtracts).

**Monto (servicio):** cargas (módulos+novedades) + ajustes with that `servicio_id`.

**Producción (profesional):** same as CH (`monto_bonos` + cantidad of eligible items).

## UI

- Param Módulos: field **Horas** on create/edit (required).
- `/novedades/indices`: period + two tables; nav last, admin only.

## Files

| File | Change |
|------|--------|
| Alembic + model/schemas/masters | `horas` |
| `NovedadesParamPage.jsx` | Field |
| `services/novedades/indices.py` | Aggregation |
| Page + navigation + router | Índices |
| tests + runbook | Coverage |
