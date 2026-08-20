# Tasks: capital-humano-grilla-actualizar

## 1. Frontend — toolbar y flujo

- [x] 1.1 Default `periodoId` al período `open` al cargar periodos
- [x] 1.2 Botón **Actualizar** → import bonos + refresh; disabled si closed / sin período
- [x] 1.3 Quitar botón **Importar bonos**; mantener **Solo bonos**
- [x] 1.4 Mantener filtro texto + banner `opciones_sin_tarifa`

## 2. Frontend — grilla

- [x] 2.1 Columnas fijas: Legajo, Profesional, Total cargas, Ajustes, Total producción, Total general
- [x] 2.2 Ocultar columnas dinámicas de bonos en grilla principal
- [x] 2.3 Acciones: Detalle + agregar ajuste (importe) en grilla

## 3. Frontend — Detalle unificado

- [x] 3.1 Modal Detalle: sección cargas (existente)
- [x] 3.2 Sección producción (cantidades/subtotales del profesional)
- [x] 3.3 Sección historial de ajustes (lectura)

## 4. Backend (solo si hace falta)

- [x] 4.1 Extender response de detalle/ajustes si la UI no puede armar el unificado con endpoints actuales — **no hizo falta** (grilla row + `/grilla` + `/ajustes`)
- [x] 4.2 Sin cambio de contrato de `POST .../bonos/import` (salvo docs)

## 5. Docs / verify

- [x] 5.1 Actualizar `docs/runbook.md` (Actualizar, columnas, Excel diferido)
- [ ] 5.2 Tests/smoke: default open, Actualizar closed disabled, grilla sin columns dinámicas
- [x] 5.3 Marcar tasks al cerrar apply
