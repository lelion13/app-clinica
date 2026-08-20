# Tasks: usuarios-abm-email-reset

## 1. Foundation

- [x] 1.1 Config: `SMTP_*` + `APP_PUBLIC_URL` en `backend/app/core/config.py`
- [x] 1.2 `.env.example` / `.env.prod.example` + notas runbook
- [x] 1.3 Modelo + Alembic (id ≤32): tabla `password_reset_tokens` (token_hash, user_id, expires_at, used_at)
- [x] 1.4 `email_service.py`: send con STARTTLS/`SMTP_SECURE`

## 2. Users API

- [x] 2.1 `UserUpdateRequest`: email + password opcional; service actualiza bcrypt/email único
- [x] 2.2 Create: tras commit, welcome mail; response con flag/warning si falla
- [x] 2.3 (Opcional) Deprecar uso de DELETE en UI; endpoint puede quedar

## 3. Auth reset

- [x] 3.1 `password_reset_service`: issue (solo activo), consume (1h, un uso, activo)
- [x] 3.2 `POST /auth/forgot-password` + `POST /auth/reset-password` (público, sin filtrar existencia)
- [x] 3.3 Rate-limit/cooldown básico forgot (IP+email)

## 4. Frontend

- [x] 4.1 `UsersPage`: botón Nuevo usuario + grilla + editar derecha (sin eliminar)
- [x] 4.2 Modal crear: campos + Cancelar/Crear + Esc; refresh grilla; aviso mail
- [x] 4.3 Modal editar: nombre, email, rol, activo, password opcional
- [x] 4.4 Login: link Olvidé contraseña → pide email → mensaje genérico
- [x] 4.5 `ResetPasswordPage` + ruta `/reset-password`

## 5. Tests / docs

- [x] 5.1 Tests: forgot genérico; inactivo sin mail; token expire/reuse; update password
- [x] 5.2 Runbook SMTP + APP_PUBLIC_URL + flujo reset
- [x] 5.3 Marcar tasks al cerrar apply
