# Implementation notes: usuarios-abm-email-reset

## Follow-ups post-apply

1. **Error create en modal** — no usar `setError` de página; `createModalError` + `role="alert"`.
2. **Firma** — centralizada en `send_email` para bienvenida y reset.
3. **Reenvío** — `POST /users/{id}/resend-welcome`; UI deshabilita si inactivo.
4. **Login** — ocultar setup para no competir con “Olvidé mi contraseña”.

## Ops

- Migración: `0023_password_reset` (≤32 chars).
- Env: `APP_PUBLIC_URL`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_SECURE`.
