# Decisions: novedades-servicio-especialista-plus

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Historial de cargas | **D** — recalcular lo ya cargado queda **fuera de este change** (después) |
| Q2 | Default flag en servicios existentes | **A** — todos **OFF**; tildar a mano donde aplique |
| Q3 | Editar asignación existente | **B** — solo al **crear** aplica la nueva regla; editar no recalcula valor |
| Q4 | Default al crear servicio nuevo | **A** — OFF |
| Q5 | Dónde distinguir el plus | **A** — solo Capital Humano Detalle (Cargas) |
| Q6 | Cómo detectar plus en Detalle | **B** — inferir si `valor ≈ catálogo × 1.20` (sin columna nueva) |
| Q7 | Excel detalle | **A** — no; solo en Detalle CH en pantalla |
| Q8 | UI en Detalle CH | **A** — columna **Plus esp.** → Sí / — |
| Q9 | Label checkbox servicio | **A** — `Especialista` |
| Q10 | Especialista vs Activo | **A** — independientes |

## Survey status
CLOSED

## Rule (create only)
Plus ×1.20 on module assignment **create** iff:
- professional `es_especialista` AND
- the **assignment’s servicio** has `especialista` (service flag) ON
