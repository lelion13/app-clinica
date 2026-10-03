# Dashboard Estadísticas — propuesta v1

## Problema

Necesitamos una vista de métricas tipo BI (filtros + KPIs + gráficos) sin depender de herramientas externas en una primera iteración.

## Alcance v1

- Nueva entrada de menú **Estadística** → ruta `/estadisticas`.
- **Rango de fechas** obligatorio (desde / hasta) para todos los cálculos.
- **Filtros multi-selección** (opcional; si está vacío = “todos los que aplique”):
  - Ubicación(es)
  - Profesional(es)
  - Consultorio(s)
- Los filtros se combinan con **AND** entre dimensiones (ej.: ubicación A **y** profesional X **y** consultorios 1,2).

## KPI principal (v1)

**Porcentaje de ocupación de consultorios**

- **Denominador**: suma de **horas habilitadas** según `room_operating_hours` en el rango de fechas, solo para consultorios que pasan el filtro (y ubicaciones vía `consulting_rooms.location_id`).
- **Numerador**: suma de **horas efectivamente reservadas** (`bookings` no eliminados, `deleted_at` null) en el mismo rango y mismos filtros.
- **Visualización**: valor % + gráfico de torta (ocupado vs libre).
- Notas:
  - Calendario de negocio según `BUSINESS_TIMEZONE` (alinear con validación de reservas).
  - Si un día no tiene franja configurada, aporta 0 horas habilitadas (no inventar horas).

## KPIs adicionales sugeridos (prioridad)

| Prioridad | KPI | Utilidad |
|-----------|-----|----------|
| Alta | Horas reservadas / horas habilitadas (mismo cálculo que %, en horas absolutas) | Contexto del % |
| Alta | Cantidad de reservas en el período | Volumen operativo |
| Media | Top N consultorios por % ocupación o por horas reservadas | Detectar cuellos |
| Media | Distribución de reservas por **día de semana** (barras) | Planificar refuerzos |
| Media | Horas por profesional (barras / ranking) | Carga por persona |
| Baja | Duración media de cada reserva | Patrón de turnos |
| Baja | Comparación vs período anterior (mismo largo de ventana) | Tendencia (v2) |

## Fuera de alcance v1

- Export Excel/PDF.
- Métricas en tiempo real WebSocket.
- Cuotas por profesional o metas configurables.

## Backend

- Endpoint(s) agregados bajo prefijo existente, ej. `GET /api/v1/stats/summary` con query params: fechas, ids de ubicaciones, profesionales, consultorios (listas repetidas o CSV según convención del proyecto).
- Respuesta JSON con KPIs y series para gráficos (torta = `{ ocupado, libre }` o similar).

## Frontend

- Página con filtros + cards KPI + `recharts` (o librería liviana ya alineada al stack).
- Reutilizar patrones de `api.js` y layout (`AppLayout`).

## Verificación

- Con datos de prueba: ocupación 0% sin reservas; 100% si todas las horas están cubiertas (caso sintético).
- Filtros que reducen denominador y numerador de forma coherente.
