# Decisions: novedades-capital-humano-importe-descontar

## Survey (closed)

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Columnas Excel | `Legajo`, `Nombre y Apellido`, `Sector`, `Monto` |
| Q2 | Anular | Solo ajustes creados por la importación (no manuales) |
| Q3 | Multi-servicio | Varios ajustes con `servicio_id`; waterfill hasta cargas del servicio |
| Q4 | Orden waterfill | Mayor monto de cargas primero |
| Q5–Q6 / corrección | Tope | Descuento ≤ **cargas + producción**; sobrante sobre cargas va al último servicio |
| Q8 + Q9/Q10 | Exceso / total general negativo | Modal listando legajos; **no importa nada**; sin forzar |
| Q11 | Período | Solo **cerrado** |
| Q12 | Re-import | Debe **Anular** antes de importar de nuevo |
| Q13 | Nombre/Sector | Sin validar (solo comentario) |
| Q14 | Legajo inexistente | Error + abort |
| Q15 | Legajo duplicado en archivo | Error + abort |
| Q16 | Signo Monto | Siempre `-abs(monto)` |
| Q17 | Solo producción | Un ajuste sin `servicio_id` |
| Q18 | Comentario Monto | Valor **negativizado** |
| Q19 | Errores | Todos juntos en el modal |
| Q20 | Roles | `admin` / `rrhh` |
| Q21 | Monto 0 / vacío | Error + abort |
| Q22 | Legajo válido | Debe estar en grilla CH del período (cargas y/o producción) |
| Q23 | Empate cargas | Indistinto |
| Q24 | Headers | Deben coincidir exactamente |
| Q25 | Comentario >500 | Truncar |

## Derived rules

### UI
- Botón **Importe a descontar** **antes** de **Descargar liquidación**.
- Si el período cerrado tiene lote de descuento activo → botón **Anular descuento**.
- Anular elimina (soft-delete) solo ajustes de ese lote.

### Comentario
`{Legajo} - {Nombre y Apellido} - {Sector} - {MontoNegativo}` (truncado a 500).

### Waterfill (con cargas)
1. Agrupar cargas del período por `servicio_id`; ordenar por monto desc.
2. Aplicar `-abs(descuento)` consumiendo capacidad de cargas por servicio.
3. Si descuento > suma(cargas) pero ≤ cargas+producción → resto al **último** servicio de la lista.
4. Si descuento > cargas+producción **o** total general proyectado < 0 → error de ese legajo (bloquea todo el import).

### All-or-nothing
Cualquier error de fila/legajo → ningún ajuste creado.
