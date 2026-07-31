# Decisions: novedades-capital-humano-legajo

Survey **cerrada** tras Q11 (2026-07-30).

## Q1 — Monto total

**Elegido: A** — Suma de todas las cargas del profesional (módulos + novedades) en el **período filtrado**; si hay filtro de servicio, solo ese servicio.

## Q2 — Ajustes (+/−)

**Elegido: A** — Se persisten; monto total = cargas ± ajustes; histórico (quién/cuándo/comentario). Alcance del ajuste alineado al filtro (período + servicio si aplica).

## Q3 — Quién ajusta

**Elegido: A** — Solo `admin` y `rrhh` (misma audiencia de la pantalla).

## Q4 — Ciclo de vida del ajuste

**Elegido: A** — Solo alta; no editar ni borrar (corrección = nuevo ajuste compensatorio).

## Q5 — Campo LEGAJO

**Elegido: A** — String; `trim` de espacios extremos; conservar ceros a la izquierda del valor útil.

## Q6 — Descarga XLS / grillas

**Elegido: D** — En Capital Humano: grilla **nueva** (1 fila/profesional) en pantalla; **dos** botones de descarga:
1. XLS de la grilla agregada (nueva).
2. XLS con el formato anterior (detalle por carga).

## Q7 — LEGAJO faltante en sync

**Elegido: A** — Profesional se sincroniza igual; `legajo = null`; en UI se muestra vacío / “—”.

## Q8 — Ver ajustes en UI

**Elegido: C** — Columna en grilla con suma de ajustes; al clic se abre historial (+ alta en ese flujo/modal).

## Q9 — Período cerrado

**Elegido: B** — Sí se pueden cargar ajustes con período cerrado (admin/rrhh). Cargas de módulos/novedades siguen bloqueadas.

## Q10 — Modal +/−

**Elegido: A** — Un campo numérico con signo (positivo suma, negativo resta) + comentario obligatorio.

## Q11 — Filas en grilla

**Elegido: A** — Solo profesionales con al menos una carga o un ajuste en el alcance del filtro (período ± servicio).
