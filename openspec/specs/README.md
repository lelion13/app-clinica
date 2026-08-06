# Especificaciones estables

Aquí van las especificaciones **de producto** que aplican más allá de un solo cambio (capacidades permanentes, reglas de negocio globales).

| Dominio | Spec | Origen (archives) |
|---------|------|-------------------|
| `novedades/` | `spec.md` | `2026-07-29-novedades-modulos` + `2026-07-29-novedades-jefe-profesionales-fecha-carga` + `2026-07-30-novedades-sincro-profesionales` (+ capital humano / bonos según archives posteriores) |
| `auth-roles/` | `spec.md` | `2026-07-29-novedades-modulos` (delta roles) |
| `distribucion/` | `spec.md` | `2026-08-06-distribucion-ocupacion` + `2026-08-06-agenda-ocupacion-sync` + `2026-08-06-mapeo-agenda-consultorio` + `2026-08-06-locations-tipo` + `2026-08-06-agenda-ocupacion-ui` |

**Anti-ambigüedad Distribución:** la tabla de *Traceability* dentro de `distribucion/spec.md` indica qué archive aporta cada capacidad. Si un delta archivado contradice la spec estable (p. ej. FullCalendar, PK=`id_dato`), prevalece la spec estable.
