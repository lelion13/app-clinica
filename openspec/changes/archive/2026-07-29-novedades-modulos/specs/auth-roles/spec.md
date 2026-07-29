# Delta for auth-roles

## ADDED Requirements

### Requirement: Roles jefe_medico y rrhh

The system MUST recognize `jefe_medico` and `rrhh` as valid user roles alongside `admin` and `operador`. JWT/`/me` MUST expose the role. Password rules and generic auth failures MUST remain unchanged.

#### Scenario: Crear usuario RRHH

- GIVEN `admin` en ABM usuarios
- WHEN crea usuario con rol `rrhh`
- THEN login succeeds and `/me` returns `rrhh`

### Requirement: Guards Novedades

Protected Novedades endpoints MUST require JWT and the role allowed for each operation per `decisions.md` matrix. Unauthorized roles MUST receive 403 without leaking user enumeration details.

#### Scenario: Operador llama API Novedades

- GIVEN token de `operador`
- WHEN llama un endpoint de Novedades
- THEN response is 403

## MODIFIED Requirements

### Requirement: User role enum

User role validation MUST accept four values: `admin`, `operador`, `jefe_medico`, `rrhh`.
(Previously: only `admin`, `operador`)

#### Scenario: Rol inválido

- GIVEN create/update user with unknown role
- WHEN submitted
- THEN MUST return 422
