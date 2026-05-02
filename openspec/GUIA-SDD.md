# Guía SDD para app-clinica

## Objetivo

Ordenar el trabajo en **cambios acotados**, con artefactos legibles antes y después del código, alineados con `AGENTS.md` y la seguridad del proyecto (JWT, bcrypt, validación Pydantic).

## Cuándo crear un cambio en `openspec/changes/`

- Nueva funcionalidad (p. ej. informes, nuevo rol).
- Cambio de comportamiento visible para usuarios o integraciones.
- Refactor grande que toca contratos de API o esquema de base de datos.

Para un fix de una línea sin ambigüedad, podeís saltar documentación larga; al menos un párrafo en `changes/<nombre>/notas.md` ayuda al histórico.

## Nombre de la carpeta

- Formato: `kebab-case`, tema único: `filtro-agenda-por-consultorio`, `export-reservas-csv`.
- Evitar nombres genéricos: `fix`, `update`, `mejoras`.

## Artefactos recomendados por cambio

| Archivo | Contenido mínimo |
|---------|------------------|
| `proposal.md` | Problema, alcance, fuera de alcance, riesgos. |
| `spec.md` | Requisitos y escenarios (Given/When/Then). Delta respecto al comportamiento actual. |
| `design.md` | Decisiones técnicas, alternativas descartadas, impacto en DB/API/UI. |
| `tasks.md` | Lista numerada implementable (migraciones, endpoints, pantallas, pruebas). |

Podés fusionar proposal + spec en un solo archivo al inicio y partirlo cuando crezca.

## Dominio del producto (recordatorios)

- **Roles**: `admin` (usuarios ABM), `operador` y admin para agenda, maestros y reservas según API.
- **Reservas**: validación contra horarios operativos del consultorio; día de semana alineado con el front (0 = domingo … 6 = sábado); uso de `BUSINESS_TIMEZONE` en backend para comparar horas “de consultorio”.
- **Despliegue**: imágenes desde GHCR; variables en `.env.prod`; migraciones con Alembic antes de asumir tablas nuevas.

## Verificación antes de dar por cerrado el cambio

- [ ] Tests backend relevantes pasan (`pytest`).
- [ ] Rutas protegidas siguen exigiendo JWT; ABM de usuarios solo admin.
- [ ] Sin secretos en commits; `.env.prod.example` actualizado si hay nuevas variables públicas.
- [ ] Si hay migración: documentado orden sugerido (`upgrade head`) en el PR o en `tasks.md`.

## Archivar

Al fusionar o cerrar el cambio, mover `openspec/changes/<nombre>/` → `openspec/changes/archive/<nombre>/` (o copiar y dejar un README breve en archive con fecha/PR).

Si el cambio incorporó requisitos que son **política de producto** permanente, extraer un resumen a `openspec/specs/` (un archivo por capacidad estable).
