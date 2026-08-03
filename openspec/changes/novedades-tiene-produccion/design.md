# Design: novedades-tiene-produccion

## Decisions

See `decisions.md` Q1–Q8.

## External API

```
GET {NOVEDADES_BONOS_TIENE_PRODUCCION_URL}?fecha=YYYY-MM-DD&codprof={CODPROF}
Authorization: Bearer {NOVEDADES_PROF_SYNC_TOKEN}
→ true | false  (JSON boolean o string parseable)
```

## App API

```
GET /novedades/bonos/tiene-produccion?fecha=YYYY-MM-DD&codprof=...
Auth: JWT; roles admin | jefe_medico (mismos que pueden cargar)
Response: { "tiene_produccion": boolean }
```

- 422 si faltan params / no configurado token|url
- 502 si falla el externo (front trata como bloqueo)

## UI flow

1. Usuario completa form / modal fecha.
2. Al confirmar: llamar proxy con `fecha_realizacion` + `professional.codprof`.
3. Si `tiene_produccion === true` → continuar submit actual.
4. Si `false` → AlertModal con texto Q7; abort.
5. Si error → AlertModal error técnico; abort.

## Files

| File | Action |
|------|--------|
| `config.py`, `.env*.example`, runbook | Modify |
| `services/novedades/tiene_produccion.py` | Create |
| `routers/novedades.py` | Modify |
| `NovedadesCargaPage.jsx`, `CargasListGrid.jsx` | Modify |
| tests | Create |
