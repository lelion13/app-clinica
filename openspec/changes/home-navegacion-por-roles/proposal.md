# Home y navegación por roles — propuesta

## ID / nombre

`home-navegacion-por-roles`

## Problema

El panel muestra un menú horizontal plano con 7–8 enlaces. No refleja la agrupación funcional del producto ni un punto de entrada claro. Se requiere reorganizar la navegación sin debilitar el RBAC ya implementado (JWT, `admin` / `operador`, guards en API).

## Objetivo (acordado con producto)

- **Menú principal (2 opciones):**
  1. **Distribución de consultorios** — al activarla, el usuario accede a las sub-opciones:
     - Ocupación semanal
     - Agenda
     - Ubicaciones
     - Profesionales
     - Consultorios
     - Horarios consultorio
     - Estadística
  2. **Usuarios** — navegación directa a la pantalla de ABM de usuarios.

- **Seguridad:** mantener las reglas actuales sin cambios de permisos en backend salvo necesidad explícita futura:
  - `admin`: acceso a todo, incluido Usuarios.
  - `operador`: acceso a todas las pantallas de “Distribución de consultorios”; **sin** Usuarios (403 en API, oculto o bloqueado en UI).

## Fuera de alcance (v1 de este cambio)

- Nuevos roles o permisos granulares por pantalla.
- Cambios en contratos de API o esquema de base de datos.
- Rediseño visual completo del panel (solo navegación y landing acordadas).

## Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Operador accede a `/usuarios` por URL | `ProtectedRoute adminOnly` (ya existe) + 403 en API |
| Bookmarks a rutas hijas dejan de funcionar | Conservar paths actuales (`/agenda`, `/ubicaciones`, etc.) |
| Menú desplegable inaccesible en móvil | Submenú en header con clic + cierre al elegir opción; probar en viewport estrecho |
| Confusión si `/` deja de ser Ocupación semanal | Definir landing (pendiente Q3) |

## Preguntas abiertas

- **Q2 (resuelta):** submenú desplegable en header (opción A).
- **Q3 (resuelta):** home neutro en `/`; ocupación en `/ocupacion-semanal` (opción B).
- **Q4 (resuelta):** resaltar padre “Distribución de consultorios” en rutas hijas.

**Estado:** plan cerrado — listo para implementación.

## Artefactos relacionados

- `spec.md` — requisitos y escenarios
- `design.md` — decisiones técnicas y matriz de módulos
- `tasks.md` — checklist de implementación

## Verificación (resumen)

- [ ] Menú muestra solo “Distribución de consultorios” + “Usuarios” (este último solo `admin`)
- [ ] Submenú de distribución lista las 7 pantallas
- [ ] Operador: 403 o redirect en `/usuarios`; admin: ABM funcional
- [ ] Rutas hijas existentes siguen protegidas con JWT
- [ ] Prueba manual según `tasks.md`
