# Archive report: 2026-08-20-usuarios-abm-email-reset

**Date:** 2026-08-20  
**Archived to:** `openspec/changes/archive/2026-08-20-usuarios-abm-email-reset/`

## Specs synced

| Domain | Action | Details |
|--------|--------|---------|
| `auth-roles` | Modified | User role enum (+ update email/password) |
| `auth-roles` | Added | Usuarios ABM UI; modal crear (error en modal); editar/desactivar + reenvío; bienvenida + firma; forgot; token reset; SMTP/APP_PUBLIC_URL |
| `openspec/specs/README.md` | Updated | origins |

## Migration

- `0023_password_reset` (≤32 chars)

## Post-apply documented

- P1 error en modal create
- P2 firma `Departamento de Tecnologia y Modernizacion.`
- P3 reenvío bienvenida desde Modificar
- P4 ocultar “Crear admin inicial” en login

## Source of truth

`openspec/specs/auth-roles/spec.md`
