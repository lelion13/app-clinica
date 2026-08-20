# Delta for auth-roles

## ADDED Requirements

### Requirement: Usuarios ABM UI (admin)

La pantalla Usuarios MUST mostrar botón **Nuevo usuario** y una grilla de usuarios existentes con el formato de grillas de la app. Acciones de modificar MUST estar a la derecha. Solo rol `admin` MUST acceder (como hoy).

#### Scenario: Ver grilla

- GIVEN admin autenticado en `/usuarios`
- WHEN carga la página
- THEN ve botón Nuevo usuario y grilla con usuarios
- AND cada fila tiene acción de modificar a la derecha

#### Scenario: No admin

- GIVEN usuario no admin
- WHEN intenta acceder a Usuarios
- THEN MUST ser denegado (UI/ruta como hoy)

### Requirement: Modal crear usuario

El modal de alta MUST pedir nombre y apellido, email (login), contraseña y rol; MUST tener Cancelar y Crear. Esc y Cancelar MUST limpiar el formulario y cerrar el modal.

#### Scenario: Crear OK

- GIVEN admin con datos válidos en el modal
- WHEN pulsa Crear
- THEN el usuario se persiste
- AND el modal se cierra
- AND la grilla se actualiza

#### Scenario: Cancelar / Esc

- GIVEN modal abierto con datos cargados
- WHEN pulsa Cancelar o Esc
- THEN el modal se cierra sin persistir
- AND los campos quedan limpios al reabrir

### Requirement: Editar y desactivar usuario

Editar MUST permitir nombre, email, rol, activo/inactivo y contraseña opcional. La UI MUST NOT ofrecer eliminar; desactivar se hace vía `is_active=false`.

#### Scenario: Desactivar

- GIVEN admin edita un usuario activo
- WHEN marca inactivo y guarda
- THEN el usuario queda inactivo
- AND no puede iniciar sesión

### Requirement: Email de bienvenida

Al crear un usuario el sistema MUST intentar enviar un correo a su casilla indicando que ya tiene acceso. Si el envío falla, el usuario MUST crearse igual y la UI MUST avisar del fallo de mail.

#### Scenario: Mail OK

- GIVEN SMTP configurado
- WHEN admin crea usuario
- THEN se envía correo de bienvenida y se cierra el modal

#### Scenario: Mail falla

- GIVEN SMTP caído o mal configurado
- WHEN admin crea usuario
- THEN el usuario existe
- AND la UI muestra aviso de que el mail no se envió

### Requirement: Olvidé mi contraseña

El login MUST ofrecer olvido de contraseña. Al enviar un email, la respuesta MUST ser genérica (se envió el correo) aunque el email no exista. Si existe un usuario **activo** con ese email, MUST enviar un link de reset. Usuario inexistente o **inactivo** MUST NOT recibir mail ni revelar existencia.

#### Scenario: Email inexistente

- GIVEN email no registrado
- WHEN solicita reset
- THEN respuesta genérica de “correo enviado”
- AND no se envía mail

#### Scenario: Usuario inactivo

- GIVEN email de usuario con `is_active=false`
- WHEN solicita reset
- THEN misma respuesta genérica
- AND no se envía mail

#### Scenario: Usuario activo

- GIVEN email de usuario activo
- WHEN solicita reset
- THEN respuesta genérica
- AND se envía mail con link de cambio de contraseña

### Requirement: Token de reset seguro

El token MUST ser aleatorio criptográfico, almacenado solo como hash, TTL 1 hora, un solo uso. El link MUST usar `APP_PUBLIC_URL`. Al consumir un token inválido/expirado/usado o usuario inactivo, MUST fallar sin filtrar detalles útiles a un atacante.

#### Scenario: Reset válido

- GIVEN token no usado y dentro de 1h de usuario activo
- WHEN envía nueva contraseña
- THEN se actualiza el hash bcrypt
- AND el token queda invalidado

#### Scenario: Token reutilizado o expirado

- GIVEN token ya usado o >1h
- WHEN intenta reset
- THEN MUST rechazarse

### Requirement: Config SMTP y URL pública

El envío de correo MUST usar `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_SECURE`. `SMTP_SECURE=false` MUST usar STARTTLS (típicamente 587); `true` TLS implícito (típicamente 465). Links MUST usar `APP_PUBLIC_URL`.

#### Scenario: Variables documentadas

- GIVEN despliegue prod
- WHEN se configura correo
- THEN las variables están en `.env*.example` / runbook

## MODIFIED Requirements

### Requirement: User role enum

(Previously: create/update role validation; password rules unchanged.)

User role validation MUST accept `admin`, `operador`, `jefe_medico`, `rrhh`. Create/update MUST aceptar esos roles. Update MAY incluir email y contraseña opcional (bcrypt). JWT/`/me` MUST exponer el rol. Fallos de auth MUST seguir siendo genéricos.

#### Scenario: Update con contraseña opcional

- GIVEN admin edita usuario y completa nueva contraseña
- WHEN guarda
- THEN el password_hash se actualiza con bcrypt
- AND no se expone la contraseña en respuestas
