# Proposal: Usuarios — ABM modal + email bienvenida + olvido de contraseña

## Intent

Modernizar Usuarios (grilla + modal alta/edición), notificar por correo al crear cuentas, y permitir recuperación de contraseña segura desde el login, con SMTP por entorno.

## Scope

### In Scope

- UI Usuarios (admin): **Nuevo usuario**, grilla estilo app, **editar** a la derecha.
- Modal alta: nombre, email (login), contraseña, rol; Cancelar / Crear; Esc = cancelar; errores en el modal.
- Modal editar: nombre, email, rol, activo + contraseña opcional + reenvío de bienvenida.
- Solo **desactivar** (sin eliminar en UI); inactivo no puede resetear contraseña ni login.
- Email de bienvenida al crear; si SMTP falla → usuario creado + aviso.
- Firma fija en todos los mails: `Departamento de Tecnologia y Modernizacion.`
- Forgot password: mensaje genérico siempre; mail con link solo si usuario **activo** existe.
- Reset: token 1h, un solo uso; URL con `APP_PUBLIC_URL`.
- SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_SECURE` (+ `APP_PUBLIC_URL`).
- Login sin link visible de “Crear admin inicial”.

### Out of Scope

- 2FA / SSO.
- Plantillas HTML avanzadas.
- Soft-delete/`DELETE` desde UI (queda fuera; solo `is_active`).

## Approach

Backend: servicio SMTP + tokens de reset (hash en DB); ampliar PATCH usuario (email/password); endpoints públicos forgot/reset; reenvío de bienvenida. Frontend: grilla + modales; login + página reset.

## Risks

- Enumeración de emails; tokens; SMTP mal configurado.

## Success Criteria

- [x] Admin crea/edita/desactiva por UI; grilla actualiza.
- [x] Bienvenida enviada o warning si falla mail; reenvío desde editar.
- [x] Forgot siempre genérico; reset solo activo + token válido.
- [x] SMTP y `APP_PUBLIC_URL` documentados; firma en mails.
- [x] Solo admin en Usuarios; error de alta en modal; setup oculto en login.

## Survey

Cerrada en `decisions.md` (Q1–Q6 + post-apply P1–P4).
