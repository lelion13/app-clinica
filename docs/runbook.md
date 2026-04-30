# Runbook de despliegue

## Preparacion
- Copiar `.env.example` a `.env`.
- Completar secretos reales (especialmente `JWT_SECRET`).
- Crear red de Traefik en el VPS (una sola vez): `docker network create traefik-public`.
- Confirmar que Traefik ya esta conectado a `traefik-public`.

## Build y publicacion de imagenes
- Backend: `docker build -t ghcr.io/<owner>/app-clinica-backend:latest ./backend`
- Frontend: `docker build -t ghcr.io/<owner>/app-clinica-frontend:latest --build-arg VITE_API_BASE_URL=https://api.tudominio.com/api/v1 ./frontend`
- Login GHCR: `echo <token> | docker login ghcr.io -u <owner> --password-stdin`
- Push:
  - `docker push ghcr.io/<owner>/app-clinica-backend:latest`
  - `docker push ghcr.io/<owner>/app-clinica-frontend:latest`

## Deploy
- `docker compose -f docker-compose.prod.yml pull`
- `docker compose -f docker-compose.prod.yml up -d`

## Migraciones
- Ejecutar migraciones despues de levantar backend:
- `docker compose -f docker-compose.prod.yml exec backend alembic upgrade head`

## Verificacion
- Backend: `GET /health`
- Frontend: acceso al host configurado
- Login y flujo setup inicial funcionando
- Verificar routers Traefik para `WEB_HOST` y `API_HOST`

## Rollback
- Cambiar tags de imagen a una version estable previa.
- Ejecutar nuevamente `docker compose -f docker-compose.prod.yml up -d`.
