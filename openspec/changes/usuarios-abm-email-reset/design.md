# Design: usuarios-abm-email-reset

## Technical Approach

Ampliar ABM usuarios (PATCH email/password; UI grilla+modales; sin delete en UI), añadir SMTP + mails (bienvenida/reset), y flujo público forgot/reset con tokens hasheados (1h, un uso). Solo admin en Usuarios.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Desactivar | `is_active=false`; UI sin Eliminar | Q6 |
| Inactivo + reset | Tratar como inexistente (sin mail) | Q6 aclaración |
| Token | `secrets.token_urlsafe`; guardar SHA-256; TTL 1h; marcar `used_at` | Q2 + seguridad |
| Base URL | `APP_PUBLIC_URL` | Q3 |
| SMTP_SECURE | false→STARTTLS; true→SSL implícito | Q4 |
| Bienvenida falla | Crear user + warning en response/UI | Q5 |
| Enumeración | Mismo mensaje + timing similar en forgot | Req. 7 |
| Rate limit | Cooldown simple por IP+email (memoria o DB) | Anti-abuso |

## Data Flow

```text
Crear: Admin → POST /users → bcrypt → commit → SMTP welcome → 201 (+ warning?)
Forgot: POST /auth/forgot-password → always 204/msg → if active user → token hash → SMTP link
Reset:  POST /auth/reset-password {token, password} → verify hash/TTL/unused/active → bcrypt → invalidate
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/.../models/password_reset.py` | Create | token_hash, user_id, expires_at, used_at |
| Alembic migration | Create | tabla reset (id ≤32 chars) |
| `core/config.py` | Modify | SMTP_* + APP_PUBLIC_URL |
| `services/email_service.py` | Create | send via smtplib |
| `services/password_reset_service.py` | Create | issue/consume token |
| `api/routers/auth.py` | Modify | forgot + reset públicos |
| `schemas/user.py` + `user_service.py` | Modify | email/password en update; create + mail flag |
| `api/routers/users.py` | Modify | create response warning opcional |
| `UsersPage.jsx` | Modify | grilla + modales crear/editar |
| `LoginPage.jsx` + `ResetPasswordPage.jsx` | Modify/Create | forgot + reset UI |
| `main.jsx` | Modify | ruta `/reset-password` |
| `.env*.example`, `docs/runbook.md` | Modify | documentar vars |

## Interfaces / Contracts

```text
POST /auth/forgot-password { email } → 204 (siempre si payload válido)
POST /auth/reset-password { token, password } → 204 | 400 genérico
POST /users → UserResponse + opcional welcome_email_sent: bool / warning
PATCH /users/{id} { name?, email?, role?, is_active?, password? }
```

Link: `{APP_PUBLIC_URL}/reset-password?token={raw}`

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | hash token; expire/reuse; inactivo no mail |
| Unit | SMTP_SECURE starttls vs ssl |
| API | forgot mismo status con/sin user |
| UI smoke | modal Esc; grilla refresh; login forgot |

## Migration / Rollout

1. Migración tabla tokens.
2. Set SMTP_* + APP_PUBLIC_URL en `.env.prod`.
3. Deploy; probar create + forgot con casilla real.

## Open Questions

None (survey closed).
