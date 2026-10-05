# Delta Spec: distribucion — indicadores-ocupacion-ui

## ADDED Requirements

### Requirement: Indicadores — período Día o Mes

`/indicadores-ocupacion` MUST ofrecer un control de modo **Día | Mes**.

- **Día:** date picker (`YYYY-MM-DD`); cálculo como hoy para ese día.
- **Mes:** selector año-mes (`YYYY-MM`); cálculo MUST sumar sobre todos los días del mes calendario:
  - **Denominador:** suma de `room_operating_hours` por cada día (weekday JS de ese día) para rooms incluidos.
  - **Numerador:** suma de duraciones de bloques sync mapeados cuya vigencia solapa cada día del mes (misma lógica de día que el modo Día, agregada).

Filtros ubicación / consultorio / especialidad / médico MUST aplicar en ambos modos.

`GET /api/v1/distribucion/ocupacion/indicadores` MUST aceptar período explícito, p. ej. `period=day` + `date=YYYY-MM-DD` o `period=month` + `month=YYYY-MM` (nombres exactos en design). JWT `admin`|`operador` sin cambio.

#### Scenario: Mes suma

- **Given** rooms con horario L–V y sync mapeado en varios días de un mes
- **When** period=month ese mes
- **Then** `enabled_hours` y `occupied_hours` son la suma de todos los días del mes (no el promedio de %)

### Requirement: Indicadores — torta con horas y %

La torta MUST mostrar para cada segmento (Ocupado / Libre) **horas y porcentaje** (leyenda y/o label de segmento). El % global KPI MAY permanecer.

#### Scenario: Leyenda informativa

- **Given** enabled_hours > 0
- **When** se renderiza la torta
- **Then** Ocupado y Libre muestran horas y %

### Requirement: Indicadores — tops especialidad y médico

Al costado de la torta MUST haber dos secciones: **Top especialidad** y **Top médico**.

Cada top MUST listar hasta **10** ítems con horas > 0, ordenados por horas desc. Cada fila MUST mostrar:
- nombre (label)
- horas
- **% box** = horas del ítem ÷ `enabled_hours` de la respuesta (mismo denom que torta); si enabled=0 → null/—
- **% ocupado** = horas del ítem ÷ `occupied_hours` de la respuesta; si occupied=0 → null/—

Agrupación MUST usar `payload.especialidad` y `payload.medico_responsable_equipo` (fallback legado `payload.medico`). Valores vacíos MUST agruparse como **“Sin especialidad”** / **“Sin médico”**.

Los tops MUST respetar el mismo período y filtros que la torta. Response API MUST incluir estas listas.

#### Scenario: Top 10 por horas

- **Given** más de 10 especialidades con horas en el período filtrado
- **When** se calculan indicadores
- **Then** el top especialidad tiene 10 filas, la primera con más horas

#### Scenario: Vacio en payload

- **Given** bloques mapeados sin `especialidad` en payload
- **When** tops
- **Then** sus horas entran en **“Sin especialidad”**

## MODIFIED Requirements

### Requirement: Agenda filter-options y match especialidad/médico

`GET .../ocupacion/agenda/filter-options` MUST poblar:
- `especialidad`: valores distintos no vacíos de **`payload.especialidad`** únicamente (MUST NOT incluir `especialidad_agenda`).
- `medico`: valores distintos no vacíos de **`payload.medico_responsable_equipo`** (fallback legado `payload.medico`) únicamente (MUST NOT usar solo la columna derivada si difiere del payload; fuente = campo payload).

Al filtrar por `especialidad` / `medico` en **Agenda ocupación** (`events`) e **Indicadores**, el match MUST ser solo contra esos campos payload (MUST NOT matchear `especialidad_agenda` para el filtro especialidad).

#### Scenario: Opciones sin especialidad_agenda

- **Given** filas con `especialidad_agenda=TRAUMA` y `payload.especialidad` vacío o distinto
- **When** filter-options
- **Then** TRAUMA de `especialidad_agenda` MUST NOT aparecer en `especialidad` salvo que también esté en `payload.especialidad`

#### Scenario: Filtro especialidad estricto

- **Given** bloque con solo `especialidad_agenda` coincidente y `payload.especialidad` distinto
- **When** filtro especialidad = valor de `especialidad_agenda`
- **Then** ese bloque MUST NOT contar (Indicadores) / MUST NOT listarse (Agenda events)

### Requirement: API e UI Indicadores ocupación (sync)

Además del cálculo día existente, la API/UI MUST soportar período mes, torta con horas+%, y tops (ver requisitos ADDED). La fórmula base sync÷box y la regla % MAY > 100 MUST permanecer. Especialidad/médico MUST filtrar solo el numerador (y tops derivados del numerador filtrado); el denominador del box MUST seguir siendo por rooms incluidos (ubicación/consultorio), no reducido por especialidad/médico.

### Requirement: Split de nombre_agenda / columna medico (Ocupación sync)

MODIFIED respecto a la spec estable previa: el backend MUST seguir derivando solo `tipo` y `especialidad_agenda` desde `nombre_agenda` (split `" - "` o fallback `-`).

La columna **`medico`** (grilla `/ocupacion`, columna DB `ocupacion_horario_activo.medico`, filtros/tops que leen médico del sync) MUST completarse desde **`payload.medico_responsable_equipo`** (strip; ausente/vacío → null). MUST NOT asignar a `medico` el resto del split de `nombre_agenda`.

Tras el cambio, MUST re-sync (**Actualizar** en Ocupación) para refrescar filas locales.

#### Scenario: medico_responsable_equipo en grilla

- **Given** fila remota con `nombre_agenda` = `00.TOTEM - PB - CONSULTORIOS` y `medico_responsable_equipo` = `LOPEZ JUAN`
- **When** sync Actualizar
- **Then** la columna `medico` muestra `LOPEZ JUAN` (no `CONSULTORIOS`)

#### Scenario: Sin responsable

- **Given** fila con `nombre_agenda` de tres partes y sin `medico_responsable_equipo`
- **When** sync
- **Then** `tipo`/`especialidad_agenda` derivados del nombre; `medico` = null
