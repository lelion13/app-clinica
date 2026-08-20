# Decisions: capital-humano-grilla-actualizar

Survey: **una pregunta a la vez**. Estado: **CLOSED** (2026-08-20).

## Contexto heredado (sin reabrir)

- Match bonos por CODPROF; opción `centro|servicio|semana|horario`.
- Valorización vía tab Producción; sin tarifa → subtotal 0 + banner.
- Promoción DEA/DEP/CAP/CAI a grilla; resto en Solo bonos.
- Ajustes con comentario no vacío; permitidos con período closed.
- Excel / confirmar OK / cerrar período → **change posterior** (concepto/orden fino también ahí).

## Decisiones

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Qué hace Actualizar | **A** | Solo import de bonos (mismo API); persistir snapshot y recargar grilla |
| Q2 | Importar bonos / Solo bonos | **A** | Quitar Importar bonos (lo reemplaza Actualizar); mantener Solo bonos |
| Q3 | Carga al entrar | **A** | Mostrar datos ya persistidos del período; Actualizar re-importa |
| Q4 | Qué es “concepto” | **A** | `concepto_liquidacion` del servicio Param (uso en **Excel posterior**, no en grilla de este change) |
| Q5 | Grano de grilla | **D** | 1 fila por profesional: legajo, nombre, total cargas, (ajustes), total producción, total general. Detalle = desglose. Concepto/orden → Excel |
| Q6 | Columnas | **B** | Fijas: Legajo · Profesional · Total cargas · Ajustes · Total producción · Total general (+ acciones). Sin columnas dinámicas de bonos en grilla |
| Q7 | Detalle / ajustes | **B+** | Detalle unificado: cargas + producción + historial ajustes. En grilla: acción **agregar ajuste**. Historial/detalle de ajustes visible desde Detalle |
| Q8 | Open / closed | **A** | Actualizar solo con período **open**; closed → disabled + se ve snapshot |
| Q9 | Filtro + banner | **A** | Mantener filtro legajo/nombre + banner opciones sin tarifa |
| Q10 | Elegibilidad | **A** | Misma regla hoy: cargas/ajustes o solo-bonos DEA/DEP/CAP/CAI → grilla; resto → Solo bonos. Excel out of scope |

## Implicaciones

- Default UI: al montar, seleccionar el período con `estado=open` si existe.
- `POST .../bonos/import` se dispara desde **Actualizar** (mismo contrato).
- Response de grilla puede simplificar `columns` dinámicas en UI (backend MAY seguir enviándolas para Detalle/valorización).
- `concepto_liquidacion` no cambia el grano de esta grilla; queda para el change de Excel.
