# Design: usuarios-abm-email-reset

## Technical Approach

Ampliar ABM usuarios (PATCH email/password; UI grilla+modales; sin delete en UI), añadir SMTP + mails (bienvenida/reset/reenvío), y flujo público forgot/reset con tokens hasheados (1h, un uso). Solo admin en Usuarios.

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
| Rate limit | Cooldown simple por IP+email (memoria) | Anti-abuso |
| Error create UI | Alert en modal; no cerrar | P1 |
| Firma mails | Append en `send_email` | P2 |
| Reenvío | `POST /users/{id}/resend-welcome` | P3 |
| Setup link | Oculto en login | P4 |

## Data Flow

```text
Crear: Admin → POST /users → bcrypt → commit → SMTP welcome → 201 (+ warning?)
Reenvío: Admin → POST /users/{id}/resend-welcome → SMTP welcome → sent/warning
Forgot: POST /auth/forgot-password → always 204 → if active user → token hash → SMTP link
Reset:  POST /auth/reset-password {token, password} → verify → bcrypt → invalidate
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `models/password_reset.py` + `0023_password_reset` | Create | tokens hasheados |
| `core/config.py` | Modify | SMTP_* + APP_PUBLIC_URL |
| `services/email_service.py` | Create | SMTP + firma fija |
| `services/password_reset_service.py` | Create | issue/consume + cooldown |
| `api/routers/auth.py` | Modify | forgot + reset |
| `user_service` / `users` router | Modify | update email/pwd; create warning; resend |
| `UsersPage.jsx` | Modify | grilla + modales + alert + reenvío |
| `LoginPage.jsx` / `ResetPasswordPage.jsx` | Modify/Create | forgot; sin link setup |
| `.env*.example`, `docs/runbook.md` | Modify | documentar vars |

## Interfaces / Contracts

```text
POST /auth/forgot-password { email } → 204
POST /auth/reset-password { token, password } → 204 | 400 genérico
POST /users → UserCreateResponse (+ welcome_email_sent / warning)
PATCH /users/{id} { name?, email?, role?, is_active?, password? }
POST /users/{id}/resend-welcome → WelcomeEmailResponse
```

Link: `{APP_PUBLIC_URL}/reset-password?token={raw}`

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | hash token; expire/reuse; inactivo no mail; update password |
| Unit | create warning si mail falla |
| UI smoke | error en modal create; reenvío; Esc; forgot genérico |

## Migration / Rollout

1. `alembic upgrade head` (`0023_password_reset`)
2. Set SMTP_* + APP_PUBLIC_URL en `.env.prod`
3. Deploy backend + frontend

## Open Questions

None.
