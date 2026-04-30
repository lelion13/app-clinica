# Plan de Implementacion V1

## Etapa 1 - Fundacion tecnica
- Estructura de repositorio: frontend, backend, infra, docker, docs.
- Variables de entorno y convenciones de seguridad.
- Compose local para levantar el stack.

## Etapa 2 - Datos y migraciones
- Modelo SQL con auditoria completa.
- Soft delete en entidades maestras.
- Indices para agenda y filtros.
- Constraint anti-solapamiento por consultorio.

## Etapa 3 - Seguridad
- Login con email y password hasheada.
- JWT access + refresh.
- Cookies httpOnly como transporte de sesion.
- Bloqueo de usuarios inactivos.

## Etapa 4 - Setup inicial
- Bootstrap de primer admin solo cuando no hay usuarios.
- Cierre definitivo del setup tras primer admin.

## Etapa 5 - RBAC
- Admin con acceso total.
- Operador sin ABM de usuarios.
- Autorizacion validada por backend en cada endpoint protegido.

## Etapa 6 - ABM y agenda
- CRUD de ubicaciones, consultorios, horarios operativos y profesionales.
- CRUD de usuarios solo para admin.
- CRUD de reservas con validacion de horario y colisiones.

## Etapa 7 - Frontend
- Login, setup inicial y dashboard.
- Grilla dia/semana con filtros.
- Acciones de crear, editar y eliminar reservas.

## Etapa 8 - Infra y despliegue
- Dockerfiles y compose de produccion con Traefik.
- GH Actions para build/push en GHCR.
- Runbook de despliegue manual en Hostinger.

## Etapa 9 - QA y hardening
- Tests de auth, setup, RBAC y reservas concurrentes.
- Checklist de seguridad para go-live.
