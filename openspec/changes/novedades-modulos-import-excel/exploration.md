# Exploration: novedades-modulos-import-excel

## Topic

Importación masiva de **módulos** desde Excel en Parametrización (tab Módulos): plantilla descargable + carga masiva, con servicios existentes como lista desplegable en el Excel, y reporte de filas no importadas.

## Current State

- Módulos: ABM manual (modal Nuevo módulo / editar / servicios / eliminar).
- Campos: `descripcion`, `comentario`, `valor`, `produccion`, `sadofe`, ≥1 `servicio_ids`.
- Excel en backend: export (`openpyxl`); sin import de catálogo módulos.
- Servicios ya existen en Param (lista para asociar).

## User intent

1. Botón **Plantilla de importación** → descarga Excel con columnas a completar.
2. La plantilla MUST incluir servicios existentes como **lista desplegable** (data validation) para asociar.
3. Botón **Carga masiva** → import; informar registros no importados y por qué.

## Ambiguities (survey)

Ver `decisions.md`.
