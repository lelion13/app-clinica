# Decisions: novedades-modulos-tipo-dia

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Persistencia | Campo único `tipo_dia`: `semana` \| `sadofe` \| `valor_unico` |
| Q2 | Migración datos | `sadofe=false`→`semana`; `sadofe=true`→`sadofe`; nadie a valor_unico |
| Q3 | Excel | Columna `tipo_dia` (reemplaza `sadofe`) |
| Q4 | Validación Carga API | Igual que ahora (solo UI) |
| Q5 | API JSON | Solo `tipo_dia`; se elimina `sadofe` (mismo deploy FE+BE) |
| Q6 | UI checks | Siempre uno tildado; no se puede quedar en cero |
| Q7 | Excel vacío | Asumir `semana` |
| Q8 | Display eliminar/listado | `Tipo día: Semana \| SADOFE \| Valor único` |
| Q9 | Valores Excel | Exactos: `semana` / `sadofe` / `valor_unico` |
| Q10 | Excel inválido | Error fila → todo-o-nada |

## Derived UI rules

- Order: **Semana** (left) · **SADOFE** · **Valor único** (right of SADOFE).
- Create default: Semana. Edit: keep current `tipo_dia`.
- Carga filter: semana ↔ día semana; sadofe ↔ día SADOFE; valor_unico → always eligible.
