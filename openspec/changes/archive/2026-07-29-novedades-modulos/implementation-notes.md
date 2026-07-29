# Implementation notes — novedades-modulos

Registro de lo implementado/arreglado **después** del survey inicial, para que el change quede alineado con el código.

## Evolución de producto (vs survey original)

| Original (proposal/spec temprano) | Estado actual |
|-----------------------------------|---------------|
| Novedad = concepto FK módulo + valor ARS + justificación | Novedad = `tipo` + `horas`; sin justificación |
| Valor hora global / config | `valor_hora` en cada **servicio** |
| Módulos globales en carga | Módulos filtrados por asociación N:N al servicio |
| Profesional libre | Debe estar en ABM profesional↔servicio |
| Listados carga “dump” | Scope jefe + order servicio/profesional |
| Listas `<ul>` | Grilla `CargasListGrid` + filtros/sort |
| Anular directo | Modal confirmación con resumen |

Detalle de decisiones: `decisions.md` (Q* + R1–R11). Specs canónicas: `specs/novedades/spec.md`.

## Fixes operativos

1. **Alembic revision id too long**  
   - Problema: `0006_novedades_modulo_servicio_valor_hora` > 32 chars → falla insert en `alembic_version`.  
   - Fix: `revision = "0006_mod_svc_valor_hora"`.  
   - Nota: el **filename** puede seguir siendo largo; importa el `revision` string.

2. **Flash UI en Carga**  
   - Al elegir servicio, no mostrar “No hay profesionales…” hasta terminar el fetch (`loadingServicio`).

3. **Errores al anular**  
   - El modal captura throws de `onAnular`; el padre no debe tragarse el error sin re-lanzar.

## Archivos clave añadidos/tocados en refinamientos

- `backend/app/services/novedades/helpers.py` — `scoped_servicio_ids`
- `backend/app/services/novedades/cargas.py` — `list_asignaciones` / `list_novedades` con user + order
- `backend/app/api/routers/novedades.py` — responses enriquecidas
- `backend/app/schemas/novedades.py` — campos nombre en responses
- `frontend/src/pages/novedades/CargasListGrid.jsx` — grilla + modal
- `frontend/src/pages/novedades/NovedadesCargaPage.jsx` — form + integración grilla
- `backend/alembic/versions/0005_*.py`, `0006_*.py`
- `docs/runbook.md`

## Checklist manual sugerido (task 4.5)

- [ ] Login `jefe_medico` con 2 servicios: listado solo esos; orden servicio→profesional
- [ ] Login `admin`: ve cargas de todos los servicios
- [ ] Filtros/sort de grilla Carga
- [ ] Modal: Cancelar no borra; Confirmar anula (período abierto)
- [ ] Período cerrado: anular/cargar rechazado
- [ ] RRHH: Param + XLS; sin Carga
- [ ] Operador: sin menú Novedades
