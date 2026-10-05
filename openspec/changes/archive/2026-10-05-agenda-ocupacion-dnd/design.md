# Design: agenda-ocupacion-dnd

## Technical Approach

Añadir reassign/unassign de `id_agenda` con validación autoritativa en backend; UI Agenda ocupación con drag horizontal entre columnas (HTML5 Drag and Drop o pointer-based), confirmaciones y modal de error.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Endpoint dedicado reassign | Encapsula validate + move/unassign; evita que UI arme PUT replace completo del room |
| Validación solo en path DnD/reassign | Q10: Consultorios Agendas sin cambio |
| Server-side authoritative | UI puede pre-chequear, pero 4xx manda |
| Excluir propio `id_agenda` del solape | Evita auto-conflicto al reasignar / multi-franja |
| Column-only DnD | Q8; horas del sync |

## API (propuesto)

`POST /api/v1/distribucion/ocupacion/agenda/reassign`  
JWT `admin`|`operador`

```json
{
  "id_agenda": 12345,
  "target_room_id": 7,
  "confirm_move": false
}
```

- `target_room_id`: int → asignar/mover a ese room; `null` → desasignar (Sin consultorio).
- Desasignar: requiere confirmación en UI; body MAY incluir `confirm_unassign: true` (o `target_room_id: null` solo tras confirm UI — backend MAY exigir flag explícito).
- Si agenda está en otro room y `confirm_move` false → **409** con `requires_confirm_move` + room actual (igual espíritu que Agendas).
- Si falla horario o solape → **422** (o 409) con detalle estructurado: weekday(s), intervalo, room, agenda conflictiva si aplica.
- Éxito **200**: `{ id_agenda, room_id }` (`room_id` null si unassign).

Unassign: DELETE mapeo existente (cualquier room); **no** corre validación horario/solape.

### Validation algorithm (assign/move)

Para el `id_agenda` y room destino:

1. Cargar todas las filas sync de ese `id_agenda` con `dia`+horas parseables.
2. Agrupar por weekday JS (o py) → lista de intervalos `[hora_desde, hora_hasta)`.
3. Para cada weekday con intervalos:
   - Obtener franjas `room_operating_hours` del room ese weekday.
   - Cada intervalo de la agenda MUST estar **contenido** en la unión de franjas del box (o en alguna franja continua — design: contenido en la unión; gaps del box no cubren).
   - Cargar otras agendas mapeadas al room; materializar sus intervalos ese weekday desde sync; MUST NOT overlap (excluir mismo `id_agenda`).
4. Si algún weekday falla → reject con mensaje listando el primero o todos los conflictos.

“Espacio disponible” del día visible es consecuencia de (3); no se valida solo el día UI (Q6=B).

## UI

- Bloques draggables; drop zones = columnas de rooms visibles + Sin consultorio.
- Drag threshold para no pelear con click → DetailModal.
- Drop a room con agenda en otro room → modal confirm robo → retry `confirm_move=true`.
- Drop Sin consultorio → modal confirm desasignar → `target_room_id=null`.
- 422/409 validación → modal motivo; revert posición visual.
- Tras 200 → reload `events` (o patch local `resource_id` + reload seguro).

Filtros: solo columnas renderizadas son destinos; no inventar rooms ocultos.

## File Changes

| File | Change |
|------|--------|
| `room_agenda_map.py` o `agenda_reassign.py` | validate + reassign/unassign |
| `distribucion` router + schemas | POST reassign |
| `AgendaOcupacionPage.jsx` | DnD + modals |
| tests | validate/reassign cases |
| runbook + delta spec | docs |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Definición “contenido en horario” con multi-franja box | Spec: cada intervalo agenda ⊆ unión de hours del weekday |
| Solape edge (fin=inicio) | Tratar half-open `[start,end)` → adyacentes OK |
| Divergencia Consultorios | Runbook + decisions Q10 |

## Open Questions

None — survey Q1–Q10 closed.
