# Design: novedades-modulos-filtro-ui

## Technical Approach

Implement in-memory filtering in `frontend/src/pages/novedades/NovedadesParamPage.jsx`.

### 1. Text Normalization Helper

A fast normalization helper stripping diacritics and lowercasing:
```javascript
const normalizeText = (str) =>
  String(str || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
```

### 2. State & Computation

- State: `const [moduloFiltro, setModuloFiltro] = useState("");`
- Filter logic:
```javascript
const modulosFiltrados = useMemo(() => {
  const q = normalizeText(moduloFiltro);
  if (!q) return modulos;
  return modulos.filter((item) => {
    if (normalizeText(item.descripcion).includes(q)) return true;
    if (normalizeText(item.comentario).includes(q)) return true;
    if ((item.servicio_nombres || []).some((s) => normalizeText(s).includes(q))) return true;
    return false;
  });
}, [modulos, moduloFiltro]);
```

### 3. UI Placement

In the toolbar of `tab === "modulos"`:
```jsx
<div style={{ marginBottom: 12, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
  <button type="button" style={uiStyles.buttonPrimary} onClick={openCreateModulo}>
    Nuevo módulo
  </button>
  <input
    type="text"
    value={moduloFiltro}
    onChange={(e) => setModuloFiltro(e.target.value)}
    placeholder="Filtrar por módulo o servicio…"
    style={{ ...uiStyles.formControl, width: 240, minWidth: 180 }}
  />
  <button type="button" style={uiStyles.buttonSecondary} onClick={downloadModulosTemplate} disabled={moduloImporting}>
    Plantilla de importación
  </button>
  ...
</div>
```
