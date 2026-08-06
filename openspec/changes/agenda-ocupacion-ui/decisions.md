# Decisions: agenda-ocupacion-ui

Survey CLOSED.

| Q | Tema | Decisión |
|---|------|----------|
| Q1 | Layout / viewport | **C** — Ancho completo + altura al final del viewport; scroll **dentro** de la grilla; cabecera HORA/consultorios sticky; columnas `minmax` más generosas + scroll horizontal si hace falta |
| Q2 | Sin consultorio vs filtros | **C** — Agregar filtros UI (tipo / especialidad / médico); “Sin consultorio” y el resto respetan **todos** los filtros aplicados |
| Q3 | Forma de filtros | **A** — Multi-select: tipo, especialidad (incluye `especialidad_agenda`), médico |
| Q4 | Detalle al click | **B** — Modal centrado con overlay; cerrar con Esc, clic en overlay, o botón Cerrar |

Sin encuesta (aceptado):

- Alinear filas de la grilla con la columna HORA (bug visual de desfase).
