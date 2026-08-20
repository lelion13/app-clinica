# Implementation notes — capital-humano-bonos-resumen

Registro de lo implementado (survey Q1–Q10) y aprendizajes. Behavior de filas/columnas/XLS fue **refinado** por archives posteriores del mismo día / siguientes; este change es la base de import + snapshot.

## Survey → código

| Q | Elegido | Implementación |
|---|---------|----------------|
| Q1 | Match `CODPROF` string/trim | `bonos_import` match |
| Q2 | Columna = 4 campos | `novedades_bono_opcion` UNIQUE |
| Q3 | Persistencia por período | `novedades_bono_cantidad` |
| Q4 | URL env + Bearer sync | `NOVEDADES_BONOS_RESUMEN_URL` + `NOVEDADES_PROF_SYNC_TOKEN` |
| Q5/Q5b | Solo-bonos en modal, no grilla | `list_solo_bonos` (luego supersedido para DEA/DEP/CAP/CAI) |
| Q6 | Sumar duplicados | normalize + sum |
| Q6b | Re-import replace si open | delete+insert cantidades del período |
| Q6c | Closed congela import | 422 |
| Q7 | 3er XLS con bonos | `export-capital-bonos.xlsx` |
| Q8 | Fallo externo no muta | try/except sin commit parcial |
| Q9 | admin/rrhh | deps |
| Q10 | Botón + modal resumen | `NovedadesXlsPage` |

## Migraciones

- `0010_bonos_resumen` — `novedades_bono_opcion`, `novedades_bono_cantidad`

## Supersession (archives posteriores)

| Tema en este change | Quedó en |
|---------------------|----------|
| Solo-bonos nunca en grilla | `2026-08-20-capital-humano-bonos-servicios-especiales` (promoción DEA/DEP/CAP/CAI) |
| Solo cantidades en columnas / total sin bonos | `2026-08-20-novedades-produccion-valor-bonos` (cantidad + subtotal; `monto_total` + bonos) |
| Cleanup opciones huérfanas al import | mismo archive tarifas (post-apply) |

La **spec estable** refleja el estado final; este archive conserva el intent original del import.

## Aprendizajes (errores / fricción)

### F1 — Hechos por período vs catálogo de opciones

**Qué pasó:** las cantidades son snapshot por `periodo_id`; las opciones (`centro|servicio|semana|horario`) son catálogo global reutilizado. Re-import reemplaza cantidades del período, no “borra” opciones automáticamente (hasta el cleanup posterior).

**Lección:** documentar en design/runbook qué se replacea y qué es compartido; si el API cambia dimensiones (ej. DOMINGO→SADOFE), hace falta política de limpieza explícita.

### F2 — Match CODPROF como string

**Qué pasó:** ceros a la izquierda / tipos distintos entre API y catálogo rompen el match si se castean a int.

**Lección:** normalizar siempre a string + trim; tests con CODPROF tipo `"0111"`.

### F3 — Fallo externo no debe tocar snapshot

**Qué pasó:** requisito explícito Q8; fácil romperlo si se hace delete antes del HTTP.

**Lección:** fetch + validate primero; solo entonces replace en transacción. Tests de “API falla → snapshot intacto”.

### F4 — Congelar al cerrar período

**Qué pasó:** re-import bloqueado en closed; XLS quedó permitido siempre (excepción de pruebas Q6c).

**Lección:** separar “mutación de datos” vs “lectura/export” en survey; si más adelante se restringe XLS, es un change aparte.

### F5 — Cadena de changes sobre la misma grilla

**Qué pasó:** tres changes sucesivos tocaron Capital Humano (import → promoción → tarifas).

**Lección:** al archivar, merge en orden y anotar supersession en `implementation-notes`; no reescribir el delta histórico — la spec estable lleva el resultado final.

## Smoke sugerido

- [ ] Período open + Importar bonos → resumen modal + columnas
- [ ] Re-import reemplaza cantidades
- [ ] Período closed → import rechazado
- [ ] CODPROF desconocido en resumen “ignored”
- [ ] Modal Solo bonos (tras promoción: solo no-especiales)
- [ ] XLS con bonos descarga
