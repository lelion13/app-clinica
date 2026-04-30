# Backlog Tecnico V1

## Sprint 1 - Plataforma y seguridad base
- T1: Inicializar backend FastAPI y frontend React.
- T2: Definir `.env.example` y politicas de secretos.
- T3: Implementar login con bcrypt + JWT access/refresh.
- T4: Implementar cookies httpOnly y endpoint refresh.
- T5: Implementar endpoint setup bootstrap-admin.
- T6: Agregar tests de autenticacion y setup.

## Sprint 2 - Datos y permisos
- T7: Crear migraciones de users, locations, consulting_rooms, professionals.
- T8: Agregar auditoria completa y soft delete.
- T9: Implementar RBAC admin/operador en dependencias backend.
- T10: Exponer CRUD usuarios solo para admin.

## Sprint 3 - Agenda y reglas de negocio
- T11: Crear tabla bookings con constraint anti-solapamiento.
- T12: Validar horarios operativos por dia de semana.
- T13: Implementar CRUD reservas con errores 409 en conflicto.
- T14: Tests de concurrencia sobre reservas.

## Sprint 4 - Frontend funcional
- T15: Pantalla login con control de errores.
- T16: Pantalla setup inicial condicionada por backend.
- T17: Dashboard con calendario dia/semana y filtros.
- T18: ABM de maestras y reservas con control por rol.

## Sprint 5 - Entrega productiva
- T19: Dockerfiles y compose prod con labels Traefik.
- T20: GitHub Actions para build/tag/push a GHCR.
- T21: Documentar deploy manual y rollback.
- T22: Checklist de seguridad y smoke tests finales.
