# Decisions: novedades-capital-humano-ajuste-mas-menos

## Survey (closed)

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Convivencia con Importe a descontar | **A** — lotes independientes; pueden coexistir; cada uno con su Anular |
| Q2 | Anular | **A** — mismo patrón; **Anular Ajuste +/-** soft-borra solo el lote de este import |
| Q3 | Positivos: tope / waterfill | **A** — misma waterfill multi-servicio, **sin tope** (total puede subir libremente) |
| Q4 | Negativos | **A** — idénticos a Importe a descontar (`-abs`, waterfill, tope cargas+producción, total general ≥ 0) |
| Q5 | Excel | **A** — headers exactos `Legajo`, `Nombre y Apellido`, `Sector`, `Monto`; vacío/0 error; sin signo = positivo; `-` descuenta; `+`/nada suma |
| Q6 | Comentario | **A** — `Legajo - Nombre - Sector - {importe con signo}`, truncado 500 |
| Q7 | Orden UI | **A** — inmediatamente a la derecha de Importe a descontar / Anular descuento; antes de Descargar liquidación |
| Q8 | Nombre change | **A** — `novedades-capital-humano-ajuste-mas-menos` |

## Derived rules

### UI
- Botones: … | Importe a descontar / Anular descuento | **Ajuste +/-** / **Anular Ajuste +/-** | Descargar liquidación | …
- Solo período **cerrado**; roles `admin`/`rrhh`.
- Lote Ajuste +/- independiente del lote descuento (`descuento_lote_id`).

### Signo Monto
- `importe` persistido = valor firmado del Monto (después de parse); **nunca** forzar `-abs` en filas positivas.
- Negativo: `importe = -abs(Monto)` (igual descontar).
- Positivo / `+`: `importe = +abs(Monto)`.

### Waterfill
- Con cargas: misma orden (mayor cargas primero); resto al último servicio de la lista.
- Negativo: tope `cargas + producción` + regla total general no negativo.
- Positivo: **sin** tope ni bloqueo por “total alto”.
- Solo producción: un ajuste con `servicio_id` null.

### All-or-nothing
Cualquier error de fila/legajo → ningún ajuste del import Ajuste +/-.
