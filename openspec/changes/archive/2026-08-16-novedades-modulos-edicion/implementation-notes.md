# Implementation notes — novedades-modulos-edicion

Registro de lo implementado **después** del survey (Q1–Q10), para alinear el archive con el código.

## Survey → código

| Q | Elegido | Implementación |
|---|---------|----------------|
| Q1 A | Modal editar: datos + produccion, sin servicios | `PUT /modulos/{id}` |
| Q2 B | Asociar permite 0 | `PUT /modulos/{id}/servicios` + `allow_empty` |
| Q3 B | API split | datos vs servicios |
| Q4 B | Default `false` + checkbox en alta | create + modal |
| Q5 B | Skip check externo si módulo `produccion=false` | `NovedadesCargaPage` |
| Q6 A | Desasociar siempre ok | sin bloqueo histórico |
| Q7 A | Botones `editar` / `servicios` | lista |
| Q8 B | Sin badge en lista | — |
| Q9 A | admin/rrhh | deps existentes |
| Q10 B | Misma branch | `feature/tiene-produccion-force` |

## Post-survey UX (misma change)

1. **Alta en modal** — Form inline reemplazado por **Nuevo módulo** → modal Cancelar/Cargar (mismo `POST`).
2. **Eliminar con confirmación** — Modal con resumen (id, descripción, comentario, valor, producción, servicios); Cancelar / Eliminar; Esc cancela.
3. **Esc global** en tab Módulos cierra el modal activo (create/edit/servicios/delete) si no hay request en curso.

## Dependencia

Requiere `novedades-tiene-produccion` (proxy + force-load + columnas motivo/obs). Archivar **después** o el **mismo día** que ese change para que la spec estable quede coherente.

## Migraciones

- `0017_sin_prod_motivo` — change hermano (motivos en cargas)
- `0018_modulo_produccion` — este change

Post-deploy: `alembic upgrade head`.

## Checklist smoke sugerido

- [ ] Param → Nuevo módulo → Cargar crea; Cancelar no crea
- [ ] Editar cambia valor/produccion sin alterar servicios
- [ ] Servicios → 0 checkboxes → “sin asociar”
- [ ] Eliminar: Esc/Cancelar no borra; Confirmar soft-delete
- [ ] Carga con módulo `produccion=false`: no llama proxy
- [ ] Carga solo novedad: sí llama proxy / force
