# Verify report: usuarios-abm-email-reset

**Date:** 2026-08-20  
**Status:** PASS (implementation + post-apply follow-ups)

## Spec coverage

| Requirement | Evidence |
|-------------|----------|
| ABM UI admin | `UsersPage.jsx` grilla + Nuevo usuario + Modificar |
| Modal crear / Esc / error en modal | `createModalError` en modal |
| Editar + desactivar + reenvío | PATCH + `POST .../resend-welcome` |
| Bienvenida + firma | `email_service.send_email` append firma |
| Forgot genérico / inactivo | `password_reset_service.request_password_reset` |
| Token 1h un uso | `PasswordResetToken` + consume |
| SMTP + APP_PUBLIC_URL | `config.py`, `.env*.example`, runbook |
| Setup oculto en login | `LoginPage.jsx` sin link setup |

## Tests

- `tests/test_password_reset.py` + `tests/test_user_service.py` → **10 passed**

## Critical issues

None.

## Notes

- Soft-delete `DELETE /users` permanece en API pero no en UI.
- Ruta `/setup` sigue disponible por URL directa.
