# Runbook de despliegue

## Preparacion
- Copiar `.env.prod.example` a `.env.prod`.
- Completar secretos reales (especialmente `JWT_SECRET`).
- Confirmar que Traefik del VPS este corriendo (en tu VPS corre como proyecto `traefik-wpez`).

## Build y publicacion de imagenes
- Backend: `docker build -t ghcr.io/<owner>/app-clinica-backend:latest ./backend`
- Frontend (mismo dominio, recomendado): `docker build -t ghcr.io/<owner>/app-clinica-frontend:latest ./frontend`
- Frontend (dev / dominio separado, opcional): `docker build -t ghcr.io/<owner>/app-clinica-frontend:latest --build-arg VITE_API_BASE_URL=http://localhost:8000/api/v1 ./frontend`
- Login GHCR: `echo <token> | docker login ghcr.io -u <owner> --password-stdin`
- Push:
  - `docker push ghcr.io/<owner>/app-clinica-backend:latest`
  - `docker push ghcr.io/<owner>/app-clinica-frontend:latest`

## Deploy
- `docker compose --env-file .env.prod -f docker-compose.prod.yml pull`
- `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d`

## Migraciones
- Ejecutar migraciones despues de levantar backend:
- `docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend alembic upgrade head`

## Verificacion
- App (mismo dominio): `GET https://<WEB_HOST>/health`
- App (mismo dominio): `GET https://<WEB_HOST>/api/v1/auth/me` (debe fallar 401 si no hay cookie, pero debe responder)
- Frontend: acceso al host configurado
- Login y flujo setup inicial funcionando
- Verificar router Traefik para `WEB_HOST`
- Verificar checklist de salida en `docs/go-live-checklist.md`

## Rollback
- Cambiar tags de imagen a una version estable previa.
- Ejecutar nuevamente `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d`.
