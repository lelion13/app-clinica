# Tasks: novedades-modulos-import-excel

## 1. Backend

- [x] 1.1 Schemas: errores por fila + response created/errors
- [x] 1.2 `modulos_import.py`: build template (servicios activos + DataValidation Sí/No)
- [x] 1.3 `modulos_import.py`: parse + validate all (dup descripción, servicio, valor, Sí/No)
- [x] 1.4 Import commit atómico vía `create_modulo` (1 servicio_id)
- [x] 1.5 Router: `GET /novedades/modulos/import/template` + `POST /novedades/modulos/import` (admin/rrhh)

## 2. Frontend

- [x] 2.1 Tab Módulos: botón Plantilla de importación (download blob)
- [x] 2.2 Botón Carga masiva + file input `.xlsx`
- [x] 2.3 Modal resultado: lista fila + motivo si falla; aviso created si OK + refresh

## 3. Tests / docs

- [x] 3.1 Tests: todo-o-nada; dup; servicio inválido; valor vacío→0; Sí/No
- [x] 3.2 Runbook: columnas plantilla + reglas
- [x] 3.3 Marcar tasks al cerrar apply
