# Proposal: Capital Humano — Actualizar + grilla de totales

## Intent

Reordenar **Capital Humano** a un flujo claro: período (default = abierto) → **Actualizar** (import bonos + persistir) → grilla por profesional con totales de cargas, ajustes, producción y general. El **Detalle** unifica cargas + producción + historial de ajustes; desde la grilla se sigue pudiendo **agregar ajuste**. Excel, agrupación por `concepto_liquidacion` y cierre de período quedan para un change posterior.

## Scope

### In Scope

- Selector de período con default al período **open**.
- Botón **Actualizar** (= import bonos actual + refresh); quitar botón **Importar bonos**.
- Mantener **Solo bonos** y reglas de elegibilidad actuales (DEA/DEP/CAP/CAI).
- Grilla de columnas fijas: Legajo, Profesional, Total cargas, Ajustes, Total producción, Total general + acciones.
- Al entrar: mostrar datos persistidos; Actualizar re-importa si open.
- Detalle unificado (cargas + producción + historial ajustes); agregar ajuste desde grilla.
- Filtro texto + banner opciones sin tarifa.
- Actualizar disabled si período closed.

### Out of Scope

- Rediseño / lógica nueva de exportaciones Excel.
- Flujo confirmar OK → cerrar período.
- Agrupar/ordenar la grilla por `concepto_liquidacion` (reservado al Excel).
- Cambiar match CODPROF, tarifas Producción, o fórmula de valorización.

## Approach

1. UI: toolbar período + Actualizar + Solo bonos + filtro; simplificar columnas de grilla.
2. Reusar `POST /capital-humano/bonos/import` desde Actualizar; default `periodoId` = open.
3. Detalle: extender payload/UI para incluir producción (cantidades/subtotales) + listado de ajustes; grilla conserva create ajuste.
4. Specs delta + runbook; tests de default período / disabled closed / columnas.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `NovedadesXlsPage.jsx` | High | Layout, Actualizar, columnas, Detalle |
| `capital_humano` / schemas | Medium | Detalle enriquecido si hace falta |
| Specs / runbook | Medium | Pantalla Capital Humano |
| Excel endpoints | Low | Sin cambio de lógica (pueden quedar botones actuales o intactos) |

## Risks

- Detalle más pesado (más datos) — paginar/limitar solo si hace falta.
- Confusión si quedan botones Excel viejos mientras el change de Excel no existe — documentar en runbook.

## Success Criteria

- [ ] Al entrar, período open preseleccionado (si existe).
- [ ] Actualizar importa bonos (open) y refresca; closed → disabled.
- [ ] Grilla: 1 fila/profesional con totales fijos; sin columnas dinámicas de bonos.
- [ ] Detalle: cargas + producción + historial ajustes; agregar ajuste desde grilla.
- [ ] Solo bonos + elegibilidad sin cambio de criterio.
- [ ] Sin cambios de Excel en este change.
