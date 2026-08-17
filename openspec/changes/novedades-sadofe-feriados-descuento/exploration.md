# Exploration: novedades-sadofe-feriados-descuento

## Topic

Tres piezas relacionadas en Novedades:
1. Nuevo tipo de novedad **horas a descontar** (valor negativo = −horas × valor_hora del servicio).
2. Categorización de módulos **Semana** vs **SADOFE** (sábado, domingo y feriado) y validación al cargar módulo según `fecha_realizacion`.
3. ABM **Feriados** en Parametrización (grilla + Nuevo feriado + editar/eliminar como Módulos).

## Current State

- Novedad tipos: solo `hora_extra`, `hora_extra_por_ausencia`; valor = horas × valor_hora (siempre positivo).
- Módulo: tiene `produccion` bool (skip check externo); **no** hay Semana/SADOFE.
- Param tabs: Servicios, Módulos, Jefes, Profesionales, Períodos — **sin** Feriados.
- No existe tabla de feriados.
- Carga valida fecha vs período/hoy; no valida tipo de día vs módulo.
- Branch actual: `feature/tiene-produccion-force` (changes previos ya archivados en spec estable).

## Affected Areas

- `backend` models/schemas/services/routers/alembic; Capital Humano / export si suman valores
- `frontend` `NovedadesCargaPage`, `NovedadesParamPage`, posiblemente grilla/XLS labels
- `openspec/specs/novedades/spec.md` (delta)

## Recommendation

Un solo change SDD `novedades-sadofe-feriados-descuento` (cohesión fecha↔módulo↔feriado↔descuento). Survey antes de design/apply. Preferir branch nueva desde `master` tras merge de lo ya en VPS.

## Risks

- Confusión `produccion` (flag actual) vs Semana/SADOFE (nuevo).
- Feriados recurrentes vs fecha absoluta.
- Signo negativo en totales Capital Humano / XLS.
- Validación solo UI vs también backend.

## Survey

Abierta en `decisions.md` — **una pregunta a la vez**.

## Ready for Proposal

Yes — survey Q1–Q14 closed (`decisions.md`).
