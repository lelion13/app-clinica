## App Clinica

Sistema para gestion de carga de consultorios con React + FastAPI + PostgreSQL.

## Entornos

- `docker-compose.yml`: stack local basico
- `docker-compose.prod.yml`: despliegue productivo con Traefik y GHCR

## Variables importantes

- `WEB_HOST`: host publico unico (frontend + API via `/api`, ej. `clinica.lionapp.cloud`).
- `GHCR_OWNER`: owner de GitHub para resolver imagenes de GHCR
- `BACKEND_IMAGE_TAG` y `FRONTEND_IMAGE_TAG`: tag a desplegar

## Deploy en VPS (Hostinger)

1. Configurar `.env.prod` en el servidor.
2. Verificar que Traefik este corriendo (proyecto `traefik-wpez`).
3. Ejecutar:
  - `docker compose --env-file .env.prod -f docker-compose.prod.yml pull`
  - `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d`
4. Ejecutar migraciones:
  - `docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend alembic upgrade head`

