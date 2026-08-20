# Decisions: usuarios-abm-email-reset

Survey: **una pregunta a la vez**. Estado: **CLOSED**.

## Acuerdos previos (fuera de survey)

- Solo `admin` accede a Usuarios.
- Alta en modal: nombre, email, contraseña, rol; Cancelar / Crear; Esc = cancelar.
- Email bienvenida al crear.
- SMTP desde env: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_SECURE`.
- Forgot password: respuesta genérica siempre; mail con link solo si el usuario existe.
- Passwords solo bcrypt; no exponer existencia de emails.

## Decisiones

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Campos del editar | **B** | Nombre, email, rol, activo + contraseña opcional |
| Q2 | Token reset (TTL / un solo uso) | **A** | 1 hora, un solo uso |
| Q3 | Base URL del link | **A** | `APP_PUBLIC_URL` en `.env.prod` |
| Q4 | SMTP_SECURE | **B** | `false` = STARTTLS (típicamente puerto 587); `true` = TLS implícito (465) |
| Q5 | Fallo mail bienvenida | **A** | Crear usuario igual + aviso de que el mail falló |
| Q6 | Eliminar / desactivar | **A** | Solo desactivar; usuario inactivo **no** puede restablecer contraseña |
