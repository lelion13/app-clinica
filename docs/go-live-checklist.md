# Go-Live Checklist V1

## Seguridad
- [ ] `JWT_SECRET` fuerte y unico por entorno.
- [ ] `COOKIE_SECURE=true` en produccion.
- [ ] `CORS_ORIGINS` limitado a dominios reales.
- [ ] Logs sin secretos, tokens ni passwords.
- [ ] Header checks activos (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`).

## Base de datos
- [ ] Backup inicial validado antes de salida.
- [ ] `alembic upgrade head` aplicado en produccion.
- [ ] Constraint anti-solapamiento de bookings verificado.

## Aplicacion
- [ ] Setup inicial bloqueado tras crear primer admin.
- [ ] Admin puede ABM usuarios.
- [ ] Operador no puede ABM usuarios (403).
- [ ] Login bloquea usuarios inactivos.
- [ ] Agenda permite alta, edicion y baja de reservas sin solapamientos.

## Infraestructura
- [ ] Traefik rutea `WEB_HOST` por HTTPS (API via `https://<WEB_HOST>/api/...`).
- [ ] Contenedores con healthchecks en estado healthy.
- [ ] Imagenes fijadas por tag estable.
- [ ] Plan de rollback validado.

## QA minimo previo a salida
- [ ] Pruebas de smoke backend.
- [ ] Pruebas de smoke frontend.
- [ ] Flujo completo: setup -> login -> ABM -> agenda.
