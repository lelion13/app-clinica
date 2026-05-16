# Diseño — Home y navegación por roles

## Enfoque elegido (borrador)

### Árbol de navegación

```
Panel (AppLayout)
├── Distribución de consultorios  [admin, operador]
│   ├── Ocupación semanal         → /ocupacion-semanal
│   ├── Agenda                    → /agenda
│   ├── Ubicaciones               → /ubicaciones
│   ├── Profesionales             → /profesionales
│   ├── Consultorios              → /consultorios
│   ├── Horarios consultorio      → /horarios-consultorio
│   └── Estadística               → /estadisticas
└── Usuarios                      → /usuarios  [solo admin]
```

### Matriz de permisos (sin cambios respecto a V1)

| Módulo | Ruta | UI visible (operador) | UI visible (admin) | API guard |
|--------|------|----------------------|----------------------|-----------|
| Ocupación semanal | `/` (TBD) | Sí | Sí | `require_operator_or_admin` |
| Agenda | `/agenda` | Sí | Sí | `require_operator_or_admin` |
| Ubicaciones | `/ubicaciones` | Sí | Sí | `require_operator_or_admin` |
| Profesionales | `/profesionales` | Sí | Sí | `require_operator_or_admin` |
| Consultorios | `/consultorios` | Sí | Sí | `require_operator_or_admin` |
| Horarios consultorio | `/horarios-consultorio` | Sí | Sí | `require_operator_or_admin` |
| Estadística | `/estadisticas` | Sí | Sí | `require_operator_or_admin` |
| Usuarios | `/usuarios` | No | Sí | `require_admin` |

### Frontend (propuesta técnica)

1. **`frontend/src/config/navigation.js`** (nuevo): definición declarativa de grupos, rutas, etiquetas y `roles: ['admin','operador'] | ['admin']`.
2. **`AppLayout.jsx`**: reemplazar `NavLink` planos por:
   - Ítem **“Distribución de consultorios”** con **submenú desplegable en el header** (clic o hover según accesibilidad móvil; ver implementación).
   - Las 7 opciones del submenú son `NavLink` a las rutas existentes.
   - Ítem **“Usuarios”** condicionado a `isAdmin`.
3. **`ProtectedRoute`**: mantener `adminOnly` en ruta `/usuarios`; opcionalmente helper `hasRole(user, allowedRoles)` reutilizable.
4. **Rutas en `main.jsx`**:
   - `/` → nueva `HomePage` (bienvenida + accesos rápidos alineados con permisos).
   - `WeeklyOccupancyPage` → `/ocupacion-semanal`.
   - Redirect `/` antiguo bookmark: opcional `Navigate` desde ruta legacy si se desea compatibilidad (recomendado: redirect 301-like en SPA desde `/` solo a home; rutas hijas sin cambio salvo ocupación).
   - Tras login (`LoginPage`): `navigate("/")` (home neutro).

### Backend

**Sin cambios** en esta iteración: RBAC ya aplicado en `app/api/deps.py`.

### Alternativas descartadas

- **Nuevo rol o permisos por pantalla:** fuera de alcance; duplicaría lógica sin necesidad actual.
- **Eliminar URLs actuales:** rompería bookmarks y tests E2E manuales.

## Decisiones resueltas

| # | Decisión |
|---|----------|
| Q1 | Menú principal: **Distribución de consultorios** (7 hijas) + **Usuarios** (solo admin) |
| Q2 | **A — Submenú desplegable en la barra superior** (sin página hub `/distribucion`) |
| Q3 | **B — Home neutro en `/`**; Ocupación semanal en **`/ocupacion-semanal`**; login redirige a `/` |
| Q4 | **Sí** — resaltar “Distribución de consultorios” cuando la ruta activa es cualquiera de las 7 hijas |

## Notas de implementación (Q4)

- Definir en `navigation.js` el array `distributionPaths` para `matchPath` / `useLocation().pathname`.
- El trigger del dropdown usa estilo activo (`navPillStyle(true)`) si `pathname` está en ese conjunto o es prefijo acordado.
- En `/` (home) el padre **no** debe aparecer activo (solo hijas de distribución).

## Impacto en archivos (estimado)

- `frontend/src/layouts/AppLayout.jsx` — navegación
- `frontend/src/config/navigation.js` — nuevo
- `frontend/src/router/ProtectedRoute.jsx` — posible extensión por roles
- `frontend/src/main.jsx` — solo si cambia index route
- Tests: opcional test de configuración de navegación (roles)
