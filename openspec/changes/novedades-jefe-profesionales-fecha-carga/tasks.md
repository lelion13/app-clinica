# Tasks: novedades-jefe-profesionales-fecha-carga

## Phase 1: Fecha de realización (datos + API)

- [x] 1.1 Alembic `0007_*`: `fecha_realizacion` DATE NOT NULL en asignacion_modulo y novedad + backfill
- [x] 1.2 Models + Pydantic (create/update/response + grid row)
- [x] 1.3 Validación: ∈ [periodo.inicio, periodo.fin] y ≤ hoy; helper reutilizable
- [x] 1.4 Create/update asignaciones y novedades exigen/permiten `fecha_realizacion` (período abierto)
- [x] 1.5 Export XLS + endpoint grilla: columna Fecha realización (+ mantener Fecha carga)

## Phase 2: Mis profesionales (RBAC + API)

- [x] 2.1 Ampliar guards `profesional-servicios` a admin|rrhh|jefe con `assert_can_load_servicio` para jefe
- [x] 2.2 List scoped para jefe; admin/rrhh ven todos
- [x] 2.3 Delete (soft) siempre permitido aunque existan cargas
- [x] 2.4 Picker: profesionales activos, typeahead al tipear (reuse `ProfessionalCombobox`), excluir ya vinculados al servicio

## Phase 3: Frontend

- [x] 3.1 Nav “Mis profesionales” (roles admin, rrhh, jefe_medico)
- [x] 3.2 Página Mis profesionales: servicio (scoped) + `ProfessionalCombobox` (filtra al tipear) + asociar/quitar
- [x] 3.3 Carga: date picker obligatorio; default hoy si válido; clear tras submit; profesional con typeahead (no select plano)
- [x] 3.3b Labels Período/Servicio/Fecha alineados; manejo período futuro (sin días válidos + aviso)
- [x] 3.3c Alertas de error/validación vía `AlertModal` (OK) en Carga / Mis profesionales / Param / XLS
- [x] 3.4 Grilla Carga: columna + sort/filter; editar fecha (período abierto) o flujo mínimo de update
- [x] 3.5 XLS page: mostrar nueva columna
- [x] 3.6 Param tab profesionales: alinear picker al mismo typeahead

## Phase 4: Tests y docs

- [x] 4.1 Tests fecha (fuera período, futura, ok)
- [x] 4.2 Tests RBAC Mis profesionales (scope vía assert_can_load + list user) — covered by existing + fecha helpers
- [x] 4.3 Runbook breve
- [ ] 4.4 Verify manual; al merge archivar change y sync `openspec/specs/novedades`

## Cierre

- [x] Survey cerrada ✅
- [x] Implementación aplicada — pendiente verify manual / archive
