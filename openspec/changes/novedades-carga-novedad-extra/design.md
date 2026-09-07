# Design: novedades-carga-novedad-extra

## Approach
UI-only in `NovedadesCargaPage`: state `novedadExtra`. When module `produccion===false`, show checkbox. Checked → clear/disable novedad fields; on submit open existing `ForceSinProduccionModal` without proxy; `performCreate` only módulo + motivo/obs.

## Decisions
| Topic | Choice |
|-------|--------|
| Persistence | Existing sin-prod fields only |
| Modal | Reuse ForceSinProduccionModal |
| Skip path | Unchecked → unchanged |

## Files
| File | Change |
|------|--------|
| `NovedadesCargaPage.jsx` | Checkbox + submit branch |
| `docs/runbook.md` | Note |

## Testing
Manual: módulo sin prod ± check; módulo con prod; solo novedad.
