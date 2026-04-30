## App Clinica

Sistema para gestion de carga de consultorios con React + FastAPI + PostgreSQL.

## Entornos

- `docker-compose.yml`: stack local basico
- `docker-compose.prod.yml`: despliegue productivo con Traefik y GHCR

## Variables importantes

- `WEB_HOST`: host publico del frontend (ej. `app.midominio.com`).
- `API_HOST`: host publico del backend (ej. `api.midominio.com`)
- `GHCR_OWNER`: owner de GitHub para resolver imagenes de GHCR
- `BACKEND_IMAGE_TAG` y `FRONTEND_IMAGE_TAG`: tag a desplegar

## Deploy en VPS (Hostinger)

1. Configurar `.env` en el servidor.
2. Asegurar red `traefik-public`.
3. Ejecutar:
  - `docker compose -f docker-compose.prod.yml pull`
  - `docker compose -f docker-compose.prod.yml up -d`
4. Ejecutar migraciones:
  - `docker compose -f docker-compose.prod.yml exec backend alembic upgrade head`

