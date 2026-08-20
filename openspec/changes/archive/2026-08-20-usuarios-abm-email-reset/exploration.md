# Exploration: usuarios-abm-email-reset

## Topic

Mejorar **Usuarios** (admin): grilla + modal alta; email de bienvenida; login **Olvidé mi contraseña** con reset seguro; SMTP vía `.env.prod`.

## Current State

- `UsersPage.jsx`: form inline + lista simple; crear + eliminar; sin modal; sin editar.
- Backend: `POST/GET/DELETE /users` (admin); passwords bcrypt (`hash_password`); JWT cookies.
- Roles: `admin`, `operador`, `jefe_medico`, `rrhh`.
- Sin SMTP / sin forgot-password / sin tokens de reset.

## User intent (draft)

1. Botón **Nuevo usuario** + grilla (formato resto app) + acciones editar a la derecha.
2. Modal alta: nombre, email (login), contraseña, rol; Cancelar / Crear; Esc = cancelar.
2.1 Crear OK → persistir, cerrar, refresh grilla.
2.2 Cancelar/Esc → limpiar y cerrar.
3. Email de bienvenida al crear.
4. Solo admin (como hoy).
5. SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_SECURE`.
6. Login: Olvidé contraseña → pide email → mensaje genérico siempre; si existe, mail con link de cambio.
7. Seguridad anti-enumeración / anti-robo.

## Ambiguities (survey)

| # | Tema |
|---|------|
| Q1 | Qué incluye “modificar” (nombre/email/rol/activo/password) |
| Q2 | TTL y uso único del link de reset |
| Q3 | URL pública base del link (`APP_PUBLIC_URL` / `WEB_HOST`) |
| Q4 | Significado `SMTP_SECURE` (TLS/STARTTLS) |
| Q5 | Si falla el mail de bienvenida: ¿rollback user o user OK + warning? |
| Q6 | Eliminar: ¿sigue soft-delete / confirmación modal? |

## Security baseline (proposed)

- Nunca revelar si el email existe (forgot + responses genéricas).
- Token reset: random criptográfico, guardar **solo hash**, TTL corto, un solo uso, invalidar al usarlo.
- Rate-limit / cooldown en forgot (por IP + email).
- Password: bcrypt; no loguear tokens ni passwords.
- Link HTTPS en prod.

## Risks

- SMTP mal configurado bloquea alta o deja users sin mail.
- Enumeración de usuarios si mensajes/timing diferencian.
- Reset tokens en DB sin hash = robo de DB = account takeover.
