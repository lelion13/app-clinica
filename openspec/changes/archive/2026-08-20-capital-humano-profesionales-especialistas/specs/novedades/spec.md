# Delta: novedades

## ADDED Requirements

### Requirement: Profesionales especialistas

The system MUST support marking Novedades catalog professionals as specialists using an external list. Configuration MUST use `NOVEDADES_PROF_ESPECIALISTAS_URL` and the same Bearer token as professional sync (`NOVEDADES_PROF_SYNC_TOKEN`).

Each remote item MUST provide `profesional` (matched to `codprof`, string/trim) and `descripcion`. On a successful specialists fetch during **Parametrización** professional sync, the system MUST set `es_especialista=true` for matched professionals and `es_especialista=false` for other active catalog professionals not in the list. Professionals present in the specialists API but absent from the catalog MUST be returned to the UI for a post-sync modal (`profesional` + `descripcion`) and MUST NOT create catalog rows.

If the specialists API fails after a successful catalog sync, the catalog sync MUST remain committed, existing `es_especialista` flags MUST remain unchanged, and the UI MUST show a warning.

**Mis profesionales** sync MUST NOT call the specialists endpoint.

#### Scenario: Match y flag

- GIVEN catálogo con CODPROF `1099`
- AND especialistas API incluye `profesional: "1099"`
- WHEN admin sincroniza profesionales desde Parametrización
- THEN `es_especialista` MUST ser true para ese profesional

#### Scenario: Unmatched modal

- GIVEN especialistas API incluye `profesional: "9999"` no presente en catálogo
- WHEN sync Param termina
- THEN la UI MUST mostrar modal con ese profesional y su descripcion

#### Scenario: Fallo parcial

- GIVEN catálogo sync OK
- AND especialistas API falla
- WHEN termina el flujo
- THEN flags `es_especialista` MUST permanecer como estaban
- AND MUST mostrarse aviso de error de especialistas

### Requirement: Plus 20% en módulos de especialistas

When creating a **module assignment** (not a novedad) for a professional with `es_especialista=true`, the persisted assignment `valor` MUST be the module catalog value multiplied by **1.20**. Historical assignments keep their stored `valor`. Novedades MUST NOT receive this factor. Capital Humano and exports MUST use the assignment’s persisted `valor` for modules (no second multiplication).

#### Scenario: Carga módulo especialista

- GIVEN profesional especialista y módulo con valor catálogo 1000
- WHEN se carga el módulo
- THEN el valor persistido MUST ser 1200

#### Scenario: Novedad sin plus

- GIVEN profesional especialista
- WHEN se carga una novedad
- THEN el valor MUST calcularse como hoy (horas × valor_hora), sin ×1.20 por especialista

## MODIFIED Requirements

### Requirement: Detalle unificado Capital Humano

In addition to cargas, producción, and adjustment history, Detalle MUST indicate whether the professional is marked `es_especialista`.

#### Scenario: Detalle muestra especialista

- GIVEN profesional con `es_especialista=true`
- WHEN admin abre Detalle en Capital Humano
- THEN MUST indicarse que es especialista
