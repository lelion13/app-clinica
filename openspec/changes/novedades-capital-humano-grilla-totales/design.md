# Design: novedades-capital-humano-grilla-totales

## Approach

```js
const gridTotals = useMemo(() => {
  let cargas = 0, ajustes = 0, bonos = 0, total = 0;
  for (const r of visibleRows) {
    cargas += Number(r.monto_cargas) || 0;
    ajustes += Number(r.monto_ajustes) || 0;
    bonos += Number(r.monto_bonos) || 0;
    total += Number(r.monto_total) || 0;
  }
  return { cargas, ajustes, bonos, total };
}, [visibleRows]);
```

Render `<tfoot>` with `formatMoney(...)`; text cells empty; slightly stronger font-weight for hierarchy.

## Files

| File | Change |
|------|--------|
| `frontend/.../NovedadesXlsPage.jsx` | totals + tfoot |
| `docs/runbook.md` | note |
| delta `specs/novedades/spec.md` | ADDED requirement |
