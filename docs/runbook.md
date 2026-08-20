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
- Cambio `novedades-modulos` (rev `0004` → `0005` → `0006_mod_svc_valor_hora`):
  - `0004`: roles `jefe_medico`/`rrhh` + tablas base Novedades
  - `0005`: novedades por **tipo + horas** (deja justificación/concepto-módulo)
  - `0006`: módulos↔servicios N:N + **valor_hora por servicio**
  - Importante: el `revision` id de `0006` es corto (`0006_mod_svc_valor_hora`) porque `alembic_version.version_num` es VARCHAR(32).
- Cambio `novedades-jefe-profesionales-fecha-carga` (rev `0007_fecha_realizacion`):
  - `fecha_realizacion` en asignaciones y novedades (dentro del período y ≤ hoy)
  - menú **Mis profesionales** (jefe/admin/rrhh) para asociar/desasociar scoped
  - grilla/XLS con Fecha realización + Fecha carga
  - **Tras cada deploy de backend con migraciones nuevas: ejecutar `alembic upgrade head`** (si no → 500 por columnas faltantes)
- Cambio `novedades-sincro-profesionales` (rev `0008_novedades_profesional`):
  - Tabla `novedades_profesional` (match `CODPROF` string; catálogo aparte de Distribución)
  - Migración **borra** asignaciones/novedades/vínculos profesional↔servicio al retarget de FKs — **backup antes**
  - Env: `NOVEDADES_PROF_SYNC_URL`, `NOVEDADES_PROF_SYNC_TOKEN`, `NOVEDADES_PROF_SYNC_TIMEOUT`
  - Ops: migrar → setear token (rotar si se expuso) → sync en Parametrización → reasociar Mis profesionales → cargas
  - Botón **Limpiar cargas** (Param, admin/rrhh): hard-delete transaccional con confirmación
  - Sync también desde Mis profesionales (admin/rrhh/jefe); si el API falla **no** inactiva locales
- Cambio `novedades-capital-humano-legajo` (rev `0009_capital_humano_legajo`):
  - Campo `legajo` en sync (`LEGAJO`, string + trim + ceros)
  - Pantalla **Capital Humano** (ex Generación XLS): grilla 1 fila/profesional + ajustes (+/−) + 2 XLS
  - Tabla `novedades_ajuste_capital`; ajustes permitidos con período cerrado
- Cambio `capital-humano-bonos-resumen` (rev `0010_bonos_resumen`):
  - Importar bonos desde `NOVEDADES_BONOS_RESUMEN_URL` (Bearer = `NOVEDADES_PROF_SYNC_TOKEN`)
  - Fechas del período → `fecha_desde` / `fecha_hasta`; match por `CODPROF`
  - Snapshot persistido; re-import solo con período **open**; cerrado = congelado
  - Columnas dinámicas + modal Solo bonos + 3er XLS con bonos
- Cambio `capital-humano-grilla-actualizar`:
  - Toolbar: período (default = **open**) + **Actualizar** (= import bonos + refresh); se quitó botón Importar bonos
  - Grilla: columnas fijas Legajo · Profesional · Total cargas · Ajustes · Total producción · Total general (+ Detalle / Agregar importe)
  - Detalle unificado: cargas + producción (cantidad/subtotal) + historial de ajustes
  - Solo bonos + elegibilidad DEA/DEP/CAP/CAI sin cambio; Excel/concepto liquidación → change posterior
  - Actualizar disabled si período closed; al entrar muestra datos persistidos
- Cambio `capital-humano-profesionales-especialistas` (rev `0022_especialista_valor`):
  - Env `NOVEDADES_PROF_ESPECIALISTAS_URL` (+ timeout opcional); Bearer = `NOVEDADES_PROF_SYNC_TOKEN`
  - Sync **Parametrización** (`?include_especialistas=1`): marca `es_especialista`; modal/aviso de códigos sin match; si falla API especialistas no toca flags
  - Mis profesionales sync **sin** especialistas
  - Carga de **módulo**: si especialista, valor persistido = catálogo × 1.20 (columna `valor` en asignación); novedades sin plus
  - Capital Humano Detalle indica especialista
  - Nota: `alembic_version.version_num` es VARCHAR(32); revision ids deben ser ≤32 chars
- Cambio `distribucion-ocupacion`:
  - Menú Distribución → **Ocupación** (`/ocupacion`); convive con Ocupación semanal
  - Tabla `ocupacion_horario_activo` (rev `0013_ocupacion_serial`): PK serial local; `payload` JSONB = cada fila del endpoint tal cual
  - Importante: `id_dato` del API **no es único** → se guarda 1 fila DB por cada fila del JSON (no colapsar)
  - Derivados `tipo`/`especialidad_agenda`/`medico` + `fecha_hasta` para filtro/UI
  - `GET .../horarios-activos` lee DB (`fecha_hasta >= hoy`); `POST .../sync` wipe+reload (botón Actualizar)
  - Env: `DISTRIBUCION_HORARIOS_ACTIVOS_URL` (+ timeout; default 120s); Bearer = `NOVEDADES_PROF_SYNC_TOKEN`
  - Tras deploy: set env en `.env.prod`, `alembic upgrade head`, redeploy backend+frontend, **Actualizar** en Ocupación (esperar synced ≈ miles de filas)
  - **Agenda ocupación** (`/agenda-ocupacion`): grilla día × consultorios (+ **Sin consultorio**); viewport full-bleed + scroll interno; filtros en una fila (selects: ubicación/tipo/especialidad/médico + día); detalle en modal (Esc/overlay); sync solo desde Ocupación
  - **Indicadores ocupación** (`/indicadores-ocupacion`): torta global del día; % = horas sync (agendas mapeadas) ÷ `room_operating_hours`; `GET .../ocupacion/indicadores`; filtros ubicación/consultorio/especialidad/médico; sin horario → aviso fuera de torta; convive con Estadística (bookings)
  - Mapeo `id_agenda` → consultorio (rev `0015_room_id_agenda`): en ficha **Consultorios**; typeahead `GET .../ocupacion/agenda-lookup?q=`
  - `locations.id_dominio` (rev `0014`) + `locations.tipo` (rev `0016_locations_tipo`): vínculo con ocupación por par `(id_dominio, tipo)` único entre activas; `tipo` obligatorio al crear/editar; existentes migran con `PENDIENTE-{id}` hasta corregir en UI; Agenda ocupación filtra ubicación por dominio+tipo
  - Split `nombre_agenda`: `" - "` o fallback `-` (valores compactos); tras cambiar parser → **Actualizar** en Ocupación
  - OpenSpec Distribución (archivados 2026-08-06): `distribucion-ocupacion`, `agenda-ocupacion-sync`, `mapeo-agenda-consultorio`, `locations-tipo`, `agenda-ocupacion-ui` → spec estable `openspec/specs/distribucion/spec.md`
  - Si Actions Backend GHCR falla con `failed to fetch oauth token: denied`: revisar Package settings del package `app-clinica-backend` → Manage Actions access (Write); re-run workflow (Frontend puede haber pasado igual)
- Cambio `novedades-tiene-produccion`:
  - Proxy `GET /novedades/bonos/tiene-produccion` → `NOVEDADES_BONOS_TIENE_PRODUCCION_URL` (mismo Bearer)
  - UI Carga (admin/jefe): al **crear**, si `false` → modal force (motivo Vacaciones/Enfermedad + observación) → POST con `motivo_sin_produccion` / `observacion_sin_produccion` (rev `0017_sin_prod_motivo`); Cancelar no POST
  - Editar fecha o error del proxy: bloqueo simple (sin force). Create API no reconsulta producción; valida enum/obs si vienen
  - Si el **módulo** tiene `produccion=false` (rev `0018_modulo_produccion`), al cargar ese módulo (solo o con novedad) **no** se llama al proxy
- Cambio `novedades-modulos-edicion`: Param → Módulos: `editar` (datos + checkbox producción) y `servicios` (permite 0); `PUT /modulos/{id}` vs `PUT /modulos/{id}/servicios`
- Cambio `novedades-sadofe-feriados-descuento` (rev `0019_sadofe_feriados` + `0020_servicio_concepto`):
  - Módulo checkbox **SADOFE** (off = Semana); Carga filtra combo según fecha + feriados (lun–vie no feriado = Semana; sáb/dom/feriado = SADOFE)
  - Param tab **Feriados** (fecha + nombre; ABM admin/rrhh)
  - Novedad tipo **Horas a descontar**: valor = −(horas × valor_hora); entra en grilla/XLS/Capital Humano
  - Servicios: campo opcional **concepto liquidación** (entero ≥ 1; vacío/`0` = NULL); ABM en modales como Módulos (Nuevo servicio / editar / eliminar; Esc). Alta siempre activa. Uso en Capital Humano queda para un change posterior
- Cambio `capital-humano-bonos-servicios-especiales`:
  - Capital Humano sin selector de servicio en UI (opera en todos los servicios)
  - Profesionales con solo bonos se incorporan a grilla principal solo si tienen opción de bono con `servicio` exacto `DEA`, `DEP`, `CAP` o `CAI`
  - Esos profesionales dejan de verse en modal **Solo bonos**
- Cambio `novedades-produccion-valor-bonos` (rev `0021_produccion_tarifa`):
  - Param tab **Producción**: alta múltiple con el mismo `valor_unitario` (combobox searchable multi-select + POST bulk)
  - No confundir con flag **Producción** del módulo (skip check externo)
  - Capital Humano: columnas cantidad + subtotal por opción; `monto_total = cargas ± ajustes + bonos valorizados`
  - Opciones sin tarifa: cantidad visible, subtotal 0, banner aviso en CH
  - XLS con bonos incluye subtotales; XLS agregado refleja total con bonos
  - Tras **Importar bonos**: soft-delete de opciones que no vienen en ese import, **sin tarifa en Producción** y **sin cantidades en ningún período** (limpia DOMINGO/SABADO huérfanos al pasar a SADOFE)

## Roles (panel)
- `admin`: distribución + novedades (todo) + usuarios
- `operador`: solo distribución de consultorios
- `jefe_medico`: asignar módulos (valor de catálogo, no editable) y cargar novedades (tipo + horas) **solo en sus servicios**; el listado de cargas de la página Carga está **scoped** a esos servicios (orden servicio → profesional); gestiona **Mis profesionales** de sus servicios
- `rrhh`: parametrización + Mis profesionales (todos) + grilla/XLS + cierre/reapertura de período (**sin** carga)

## Usuarios, SMTP y reset de contraseña
- Pantalla **Usuarios** (solo `admin`): grilla + modal alta/edición; desactivar con `is_active` (sin eliminar en UI). Usuario inactivo no puede login ni “olvidé mi contraseña”.
- Errores de alta se muestran **dentro del modal** (no cierran el diálogo).
- Al crear usuario se intenta mail de bienvenida; si falla SMTP el usuario igual se crea y la UI avisa. Desde **Modificar** se puede **reenviar** el mail de bienvenida (`POST /users/{id}/resend-welcome`, solo activo).
- Todos los mails cierran con firma: `Departamento de Tecnologia y Modernizacion.`
- Login → **Olvidé mi contraseña**: respuesta genérica siempre; mail con link solo si el email pertenece a un usuario **activo**. El link “Crear admin inicial” no se muestra en login (`/setup` sigue por URL).
- Link: `{APP_PUBLIC_URL}/reset-password?token=...` (token 1h, un solo uso, hash en DB).
- Variables en `.env.prod` (ver `.env.prod.example`):
  - `APP_PUBLIC_URL` (ej. `https://clinica.lionapp.cloud`)
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_SECURE`
  - `SMTP_SECURE=false` → STARTTLS (típico puerto 587); `true` → TLS implícito (típico 465)
- Migración: `0023_password_reset` (`alembic upgrade head` tras deploy).
- Archive SDD: `openspec/changes/archive/2026-08-20-usuarios-abm-email-reset/`

## Flujo Novedades (resumen)
1. Parametrización: servicios (**valor hora** + **concepto liquidación** opcional), módulos, **Producción** (tarifas bonos), jefes↔servicios, profesionales↔servicios, período abierto, feriados.
   - Tab **Módulos**: **Plantilla de importación** descarga Excel con columnas `descripcion`, `comentario`, `valor`, `produccion`, `sadofe`, `servicio` (desplegable de servicios activos + Sí/No). **Carga masiva** importa todo-o-nada; errores en modal (fila + motivo). Valor vacío → 0; descripción duplicada o servicio inexistente = error (no se crea ninguno).
2. Mis profesionales: asociar/quitar profesionales al servicio (typeahead); desasociar no borra cargas históricas.
3. Carga: módulo solo / novedad solo / ambos + **fecha de realización** (calendario; sin días si el período aún no empezó). Valor novedad = horas × valor hora **del servicio** (negativo si tipo Horas a descontar). Combo de módulos filtrado Semana/SADOFE según fecha y feriados. Errores en modal OK.
4. Listado inferior (Carga): grilla unificada con F. realización y F. carga; editar fecha si período abierto; **anular** con modal.
5. Generación XLS (admin/rrhh): grilla + filtros + descarga (incluye ambas fechas).
6. Parametrización: Feriados globales (fecha + nombre) al lado de Períodos.

## Docs del change
- Archivados: `openspec/changes/archive/2026-07-29-novedades-modulos/`, `openspec/changes/archive/2026-07-29-novedades-jefe-profesionales-fecha-carga/`, `openspec/changes/archive/2026-07-30-novedades-sincro-profesionales/`
- Specs estables: `openspec/specs/novedades/`, `openspec/specs/auth-roles/`

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
