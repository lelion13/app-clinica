# Especificación — Home y navegación por roles

## Requisitos MUST

1. El menú principal del panel MUST mostrar exactamente dos entradas de primer nivel: **Distribución de consultorios** y **Usuarios** (esta última solo para usuarios con rol `admin`).
2. Al acceder a **Distribución de consultorios**, el usuario MUST poder llegar a: Ocupación semanal, Agenda, Ubicaciones, Profesionales, Consultorios, Horarios consultorio y Estadística.
3. Al acceder a **Usuarios**, el usuario `admin` MUST ver la pantalla de ABM de usuarios existente (`/usuarios`).
4. Un usuario `operador` MUST NOT poder gestionar usuarios: la entrada Usuarios MUST NOT mostrarse (o MUST bloquear navegación); la API MUST seguir respondiendo 403 en endpoints de usuarios.
5. Todas las rutas de aplicación autenticadas MUST seguir exigiendo sesión JWT válida.
6. Los paths de las pantallas de distribución MUST ser: `/ocupacion-semanal`, `/agenda`, `/ubicaciones`, `/profesionales`, `/consultorios`, `/horarios-consultorio`, `/estadisticas`.
7. La ruta `/` MUST mostrar una pantalla de bienvenida (home neutro) sin reemplazar la funcionalidad de los módulos hijos.
8. Tras login exitoso, el usuario SHOULD aterrizar en `/` (home).
9. Cuando el usuario está en una pantalla hija de distribución, el ítem de menú **Distribución de consultorios** MUST mostrarse en estado activo/resaltado.
10. En la ruta `/` (home), el ítem **Distribución de consultorios** MUST NOT mostrarse como activo.

## Requisitos SHOULD

1. La navegación SHOULD ser usable en viewport móvil (menú colapsable o panel desplegable táctil).

## Escenarios

### Escenario 1 — Admin ve menú completo

- **Given** un usuario autenticado con rol `admin`
- **When** abre el panel
- **Then** ve “Distribución de consultorios” y “Usuarios”
- **And** puede abrir las siete sub-opciones de distribución
- **And** puede abrir Usuarios y operar el ABM

### Escenario 2 — Operador sin Usuarios

- **Given** un usuario autenticado con rol `operador`
- **When** abre el panel
- **Then** ve “Distribución de consultorios”
- **And** NO ve “Usuarios”
- **When** intenta navegar manualmente a `/usuarios`
- **Then** es redirigido fuera de la pantalla (comportamiento actual de `ProtectedRoute adminOnly`)

### Escenario 3 — Operador en maestros y agenda

- **Given** un usuario `operador` autenticado
- **When** navega a Ubicaciones, Consultorios o Agenda
- **Then** las pantallas cargan datos con éxito (API 200)
- **And** las acciones de escritura permitidas hoy siguen funcionando

### Escenario 4 — URL directa

- **Given** un usuario autenticado
- **When** ingresa directamente `/estadisticas` en el navegador
- **Then** la pantalla de estadísticas se muestra
- **And** el menú refleja el contexto de “Distribución de consultorios”

### Escenario 5 — Home tras login

- **Given** un usuario autenticado
- **When** inicia sesión
- **Then** es redirigido a `/`
- **And** ve la pantalla de bienvenida (no Ocupación semanal embebida en `/`)

### Escenario 6 — Ocupación semanal en nueva ruta

- **Given** un usuario autenticado
- **When** navega a `/ocupacion-semanal` desde el submenú
- **Then** ve la grilla de ocupación semanal (misma funcionalidad que antes en `/`)
