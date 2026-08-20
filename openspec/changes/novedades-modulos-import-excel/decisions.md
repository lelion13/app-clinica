# Decisions: novedades-modulos-import-excel

Survey: **una pregunta a la vez**. Estado: **CLOSED**.

## Acuerdos previos (del pedido)

- Tab Módulos: botones **Plantilla de importación** y **Carga masiva**.
- Plantilla trae servicios existentes como lista desplegable en Excel.
- Al importar: informar registros no importados y el motivo.
- Roles: `admin` / `rrhh` (Param).

## Decisiones

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Asociación a servicios (1 o N) | **A** | Un solo servicio por fila (desplegable) |
| Q2 | Duplicados (misma descripción) | **A** | No importar; reportar como omitida/error (duplicado) |
| Q3 | Filas inválidas vs resto | **B** | Todo o nada: si hay error, no importa ninguna |
| Q4 | Columnas booleanas (producción / SADOFE) | **A** | Desplegable Sí / No |
| Q5 | Comentario vacío / valor | **B** | Valor opcional (vacío → 0); comentario opcional; descripción + servicio obligatorios |
| Q6 | Resultado del import | **A** | Modal con lista fila + motivo |
