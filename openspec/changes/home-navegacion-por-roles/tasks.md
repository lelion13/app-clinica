# Tareas — Home y navegación por roles

## Pre-implementación

- [x] Q1–Q3 cerradas en `design.md`
- [x] Q4 cerrada en `design.md`
- [ ] Revisión rápida con checklist `docs/go-live-checklist.md` (ítems RBAC)

## Implementación frontend

1. [x] Crear `frontend/src/config/navigation.js` con grupos, rutas y roles
2. [x] Refactorizar `AppLayout.jsx`: menú 2 ítems + submenú distribución (según Q2)
3. [x] Resaltar ítem padre cuando ruta hija está activa (según Q4)
4. [x] Crear `HomePage.jsx` en `/` (bienvenida + accesos según rol)
5. [x] Mover `WeeklyOccupancyPage` a `/ocupacion-semanal` en `main.jsx`
6. [x] Confirmar `LoginPage` redirige a `/` tras login
7. [x] Verificar `ProtectedRoute` en `/usuarios` sin regresiones
8. [ ] Probar responsive (móvil): abrir/cerrar submenú sin perder foco (manual)

## Verificación manual

- [ ] Login como **admin**: menú 2 ítems; las 7 sub-rutas + Usuarios OK
- [ ] Login como **operador**: solo Distribución; 7 sub-rutas OK; `/usuarios` redirige
- [ ] Cerrar sesión y rutas públicas (`/login`, `/setup`) sin cambios

## Cierre

- [ ] Actualizar `design.md` marcando decisiones como resueltas
- [ ] Al merge: mover carpeta a `openspec/changes/archive/home-navegacion-por-roles/`
