# Decisions: locations-tipo

Survey informal (chat) — CLOSED.

| Q | Tema | Decisión |
|---|------|----------|
| Q1 | Unique | **`(id_dominio, tipo)`** entre activas — no solo `id_dominio` |
| Q2 | tipo al crear | **Obligatorio** (create y edit) |
| Q3 | Migración filas existentes | Placeholder único `PENDIENTE-{id}` hasta editar en UI |

## Relacionado (parser sync)

| Tema | Decisión |
|------|----------|
| Split `nombre_agenda` | Primero `" - "`; si no hay, fallback por `-` (valores compactos del API) |
| Tras fix parser | Re-sync Ocupación (Actualizar) obligatorio |
