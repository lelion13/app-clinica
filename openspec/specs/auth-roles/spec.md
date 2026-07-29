# Auth Roles Specification

## Purpose

Roles de usuario del panel clínico y reglas de autorización asociadas (JWT + ABM usuarios).

## Requirements

### Requirement: User role enum

User role validation MUST accept four values: `admin`, `operador`, `jefe_medico`, `rrhh`. JWT/`/me` MUST expose the role. Password rules and generic auth failures MUST remain unchanged.

#### Scenario: Crear usuario RRHH

- GIVEN `admin` en ABM usuarios
- WHEN crea usuario con rol `rrhh`
- THEN login succeeds and `/me` returns `rrhh`

#### Scenario: Rol inválido

- GIVEN create/update user with unknown role
- WHEN submitted
- THEN MUST return 422

### Requirement: Guards Novedades

Protected Novedades endpoints MUST require JWT and the role allowed for each operation (admin/jefe_medico/rrhh según matriz de Novedades). Unauthorized roles MUST receive 403 without leaking user enumeration details.

#### Scenario: Operador llama API Novedades

- GIVEN token de `operador`
- WHEN llama un endpoint de Novedades
- THEN response is 403
