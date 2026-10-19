# Decisions: novedades-capital-humano-mail-liquidacion

## Locked (from product, before survey)

| Topic | Decision |
|--------|----------|
| Entry point | Botón en **Capital Humano** |
| Período | MUST estar **cerrado** para iniciar el envío |
| Destinatarios | Un mail por profesional que aparece en el listado CH del período (misma población/agrupación que la grilla) |
| Contenido mínimo | Importe a facturar + detalle de lo cargado (alineado a CH) |
| Email del profesional | Sync Integrando: campo JSON **`MAIL`** → columna `novedades_profesional.email` (trim; vacío/`null` → NULL) |
| Entrega | Lote + cola/worker + throttle (no blast sincrónico en el request del botón); estados por destinatario; reintentos / reanudar fallidos |
| Canal | SMTP existente de la app (ESP externo out of scope salvo que el survey diga lo contrario) |

## Survey

| # | Topic | Options | Choice |
|---|--------|---------|--------|
| Q1 | Quién puede disparar el envío | A = solo `admin` · B = `admin` + `rrhh` · C = otro | **B** — `admin` + `rrhh` |
| Q2 | Formato del mail | A = solo HTML/texto en el cuerpo · B = cuerpo + PDF adjunto · C = solo PDF | **A** — solo cuerpo HTML/texto |
| Q3 | “Importe a facturar” | A = Total general fila CH · B = solo cargas · C = otro | **A** — Total general CH |
| Q4 | Detalle en el cuerpo | A = mismo desglose que Detalle CH · B = solo cargas · C = resúmenes por bloque | **A** — mismo desglose que Detalle CH |
| Q5 | Profesionales sin mail válido | A = excluir y enviar resto · B = bloquear lote · C = encolar como failed | **B** — bloquear todo el lote hasta corregir |
| Q6 | Confirmación antes de encolar | A = modal N destinatarios · B = un click · C = preview ejemplo | **A** — modal con N destinatarios + confirmar |
| Q7 | Reenvío del mismo período | A = nuevo lote completo · B = solo reintentar `failed` · C = ambos | **B** — solo reintentar `failed` del lote actual |
| Q8 | Seguimiento en UI | A = contadores en CH · B = solo toast · C = lista por profesional | **A** — contadores (enviados/pendientes/fallidos) + reintentar fallidos |
| Q9 | Profesionales con Total general = 0 | A = incluir · B = excluir sin bloquear · C = bloquear lote | **A** — incluir (mail con $0 + detalle) |
| Q10 | Copia (CC/BCC) además del profesional | A = sin copia · B = BCC env · C = CC al disparador | **A** — sin copia |
| Q11 | Lote 100% enviado (0 fallidos) | A = período cerrado para mails · B = admin/rrhh lote nuevo · C = solo admin fuerza | **A** — no se puede volver a enviar ese período |
| Q12 | Campo `email` en catálogo Novedades | A = este change incluye migración + sync · B = change aparte | **A** — migración + mapear sync Integrando |
| Q13 | Clave JSON Integrando | Confirmado por producto | **`MAIL`** (ej. `"MAIL": "aaa@bbb.com"`) |

## Survey status

**Closed** (Q1–Q13). Clave sync: `MAIL`.
