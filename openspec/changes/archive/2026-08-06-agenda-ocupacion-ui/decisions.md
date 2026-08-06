# Decisions: agenda-ocupacion-ui

Survey CLOSED + ajuste post-implementación.

| Q | Tema | Decisión |
|---|------|----------|
| Q1 | Layout / viewport | **C** — Full-bleed + altura al viewport; scroll **dentro** de la grilla; cabecera sticky; columnas `minmax` generosas + scroll-x |
| Q2 | Sin consultorio vs filtros | **C** — Filtros UI tipo/especialidad/médico; Sin consultorio y el resto respetan todos |
| Q3 | Forma de filtros | Survey **A** (multi-select) → **ajustado a selects single** en una fila (igual Ubicación). Motivo: multi robaba altura; la grilla debe dominar para ver huecos libres |
| Q4 | Detalle al click | **B** — Modal centrado + overlay; Esc / overlay / Cerrar |

Sin encuesta (aceptado):

- Alinear filas con columna HORA (bug box-model).
- Título/ayuda mínimos para maximizar grilla.

## Fuera de este change (ver notes)

- `locations.tipo` / 0016 → change `locations-tipo`
- Split `nombre_agenda` con `-` compacto → doc en `locations-tipo` + notes
- GHCR `oauth token denied` en Backend #41 → checklist ops en notes
