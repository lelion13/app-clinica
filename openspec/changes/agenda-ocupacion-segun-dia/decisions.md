# Decisions: agenda-ocupacion-segun-dia

| ID | Tema | Decisión |
|----|------|----------|
| D1 | Scope AO | Assign/unassign **solo** el weekday del día del calendario. |
| D2 | Scope Consultorios assign | Solo días aún Sin consultorio → ese room; no pisa otros rooms. |
| D3 | Consultorios assign fallos | Todo-o-nada; modal conflicto; no persiste nada. |
| D4 | Consultorios unassign | Quita vínculos a **ese** room; si parcial, **un día** (fila); si full, todos los días de esa agenda en ese room. |
| D5 | Visibilidad AO | Solo agendas con bloque sync ese weekday. |
| D6 | Validación DnD | Horario box + solape **solo** ese weekday. |
| D7 | Migración | Mapa actual → una fila por cada weekday sync de ese `id_agenda` en el mismo room. |
| D8 | Orden rooms | Número extraído del `code` asc; sin número al final; desempate por `code`. |
| D9 | Scroll | Barra H si no caben; auto-scroll al drag cerca del borde. |
| D10 | Sin consultorio | Sticky izq. si tiene ítems; si vacía, scroll con columnas. |
| D11 | Labels Consultorios | Full (todos los días de la agenda en ese room) → solo nombre; parcial → una fila por día `nombre - {día}`. |
| D12 | Roles | Sin cambio. |
| D13 | Nombre | `agenda-ocupacion-segun-dia`. |
