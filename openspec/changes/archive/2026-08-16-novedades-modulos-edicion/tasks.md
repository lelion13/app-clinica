# Tasks: novedades-modulos-edicion

## 1. Backend

- [x] 1.1 Alembic `0018_modulo_produccion`
- [x] 1.2 Model + schemas create/update/response + `ModuloServiciosUpdateRequest`
- [x] 1.3 `update_modulo` sin servicios; `update_modulo_servicios` allow `[]`
- [x] 1.4 Router PUT datos + PUT `/modulos/{id}/servicios`
- [x] 1.5 Tests produccion default / update split / empty servicios

## 2. Frontend Param

- [x] 2.1 Create checkbox `produccion` (en modal alta)
- [x] 2.2 Modal editar (Cancelar/Guardar) + botón `editar`
- [x] 2.3 Modal servicios (Cancelar/Aceptar, allow 0) + botón `servicios`
- [x] 2.4 Alta solo vía modal **Nuevo módulo** (Cancelar/Cargar); lista sin form inline
- [x] 2.5 Modal confirmar eliminar (datos + Cancelar/Eliminar; Esc cancela)

## 3. Frontend Carga

- [x] 3.1 Skip `tiene-produccion` si módulo seleccionado tiene `produccion=false`

## 4. Docs

- [x] 4.1 Runbook breve + marcar tasks
- [x] 4.2 implementation-notes + verify-report (pre-archive)
