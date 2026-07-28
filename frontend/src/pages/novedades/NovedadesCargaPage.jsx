import { useEffect, useMemo, useState } from "react";

import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

const TIPO_OPTIONS = [
  { value: "hora_extra", label: "Hora extra" },
  { value: "hora_extra_por_ausencia", label: "Hora extra por ausencia" },
];

export function NovedadesCargaPage() {
  const [error, setError] = useState("");
  const [servicios, setServicios] = useState([]);
  const [modulos, setModulos] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [profesionales, setProfesionales] = useState([]);
  const [asignaciones, setAsignaciones] = useState([]);
  const [novedades, setNovedades] = useState([]);
  const [valorHora, setValorHora] = useState(null);

  const [servicioId, setServicioId] = useState("");
  const [periodoId, setPeriodoId] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [moduloId, setModuloId] = useState("");
  const [tipo, setTipo] = useState("hora_extra");
  const [horas, setHoras] = useState("");

  const openPeriodo = useMemo(() => periodos.find((p) => p.estado === "open"), [periodos]);
  const selectedModulo = useMemo(
    () => modulos.find((m) => String(m.id) === String(moduloId)),
    [modulos, moduloId]
  );

  const load = async () => {
    setError("");
    try {
      const [s, m, p, a, n, vh] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/modulos"),
        apiRequestWithRefresh("/novedades/periodos"),
        apiRequestWithRefresh("/novedades/asignaciones-modulos"),
        apiRequestWithRefresh("/novedades/cargas"),
        apiRequestWithRefresh("/novedades/valor-hora"),
      ]);
      setServicios(s);
      setModulos(m);
      setPeriodos(p);
      setAsignaciones(a);
      setNovedades(n);
      setValorHora(vh?.valor_hora ?? null);
      setPeriodoId((current) => {
        if (current) return current;
        const open = p.find((item) => item.estado === "open");
        return open ? String(open.id) : "";
      });
    } catch (err) {
      setError(err.message || "Error al cargar");
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const fetchPros = async () => {
      if (!servicioId) {
        setProfesionales([]);
        setProfessionalId("");
        return;
      }
      try {
        const rows = await apiRequestWithRefresh(`/novedades/profesionales?servicio_id=${servicioId}`);
        setProfesionales(rows);
        setProfessionalId("");
      } catch (err) {
        setError(err.message || "Error al cargar profesionales");
      }
    };
    fetchPros();
  }, [servicioId]);

  const sharedOk = periodoId && servicioId && professionalId;

  const submitAsignacion = async (event) => {
    event.preventDefault();
    setError("");
    if (!sharedOk || !moduloId) {
      setError("Completá período, servicio, profesional y módulo");
      return;
    }
    try {
      await apiRequestWithRefresh("/novedades/asignaciones-modulos", {
        method: "POST",
        body: JSON.stringify({
          periodo_id: Number(periodoId),
          servicio_id: Number(servicioId),
          professional_id: Number(professionalId),
          modulo_id: Number(moduloId),
        }),
      });
      await load();
    } catch (err) {
      setError(err.message || "No se pudo asignar módulo");
    }
  };

  const submitNovedad = async (event) => {
    event.preventDefault();
    setError("");
    if (!sharedOk || !horas) {
      setError("Completá período, servicio, profesional, tipo y horas");
      return;
    }
    try {
      await apiRequestWithRefresh("/novedades/cargas", {
        method: "POST",
        body: JSON.stringify({
          periodo_id: Number(periodoId),
          servicio_id: Number(servicioId),
          professional_id: Number(professionalId),
          tipo,
          horas: Number(horas),
        }),
      });
      setHoras("");
      await load();
    } catch (err) {
      setError(err.message || "No se pudo cargar novedad");
    }
  };

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Carga de módulos / novedades</h1>
        <p style={uiStyles.helpText}>
          Podés asignar solo un módulo (valor del catálogo, no editable), solo una novedad (tipo + horas), o ambos al mismo profesional.
          Los profesionales deben estar asociados al servicio en Parametrización.
          {openPeriodo ? ` Período abierto: #${openPeriodo.id}.` : " No hay período abierto."}
          {valorHora != null ? ` Valor hora: $${valorHora}.` : ""}
        </p>
        {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

        <h2 style={{ margin: "12px 0 8px", fontSize: "1rem" }}>Contexto</h2>
        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", marginBottom: 16 }}>
          <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)} style={uiStyles.formControl}>
            <option value="">Período</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>#{p.id} {p.nombre || ""} ({p.estado})</option>
            ))}
          </select>
          <select value={servicioId} onChange={(e) => setServicioId(e.target.value)} style={uiStyles.formControl}>
            <option value="">Servicio</option>
            {servicios.map((s) => (
              <option key={s.id} value={s.id}>{s.nombre}</option>
            ))}
          </select>
          <select value={professionalId} onChange={(e) => setProfessionalId(e.target.value)} style={uiStyles.formControl}>
            <option value="">{servicioId ? "Profesional del servicio" : "Elegí servicio primero"}</option>
            {profesionales.map((p) => (
              <option key={p.id} value={p.id}>{p.full_name}</option>
            ))}
          </select>
        </div>
        {servicioId && !profesionales.length ? (
          <p style={{ ...uiStyles.helpText, color: uiTheme.colors.danger }}>
            No hay profesionales asociados a este servicio. Asociarlos en Parametrización → Profesionales ↔ servicios.
          </p>
        ) : null}

        <h2 style={{ margin: "8px 0", fontSize: "1rem" }}>1. Asignar módulo (opcional)</h2>
        <form onSubmit={submitAsignacion} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 16 }}>
          <select value={moduloId} onChange={(e) => setModuloId(e.target.value)} style={uiStyles.formControl}>
            <option value="">Módulo del catálogo</option>
            {modulos.map((m) => (
              <option key={m.id} value={m.id}>{m.descripcion}</option>
            ))}
          </select>
          <span style={uiStyles.helpText}>
            Valor (solo lectura): {selectedModulo ? `$${selectedModulo.valor}` : "—"}
          </span>
          <button type="submit" style={uiStyles.buttonPrimary}>Asignar módulo</button>
        </form>

        <h2 style={{ margin: "8px 0", fontSize: "1rem" }}>2. Cargar novedad (opcional)</h2>
        <form onSubmit={submitNovedad} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <select value={tipo} onChange={(e) => setTipo(e.target.value)} style={uiStyles.formControl}>
            {TIPO_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <input
            type="number"
            step="0.25"
            min="0.01"
            value={horas}
            onChange={(e) => setHoras(e.target.value)}
            placeholder="Cantidad de horas"
            required
            style={uiStyles.formControl}
          />
          <span style={uiStyles.helpText}>
            Valor estimado: {horas && valorHora != null ? `$${(Number(horas) * Number(valorHora)).toFixed(2)}` : "—"}
          </span>
          <button type="submit" style={uiStyles.buttonPrimary}>Cargar novedad</button>
        </form>
      </div>

      <div style={uiStyles.pageSection}>
        <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Módulos asignados</h2>
        <ul style={uiStyles.listCard}>
          {asignaciones.slice(0, 20).map((item) => (
            <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
              #{item.id} · {item.modulo_descripcion || item.modulo_id} · valor catálogo ${item.modulo_valor ?? "—"} · prof {item.professional_id}{" "}
              <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/asignaciones-modulos/${item.id}`, { method: "DELETE" }); await load(); }}>
                anular
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div style={uiStyles.pageSection}>
        <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Novedades</h2>
        <ul style={uiStyles.listCard}>
          {novedades.slice(0, 20).map((item) => (
            <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
              #{item.id} · {item.tipo_label || item.tipo} · {item.horas} hs · ${item.valor_calculado ?? "—"}{" "}
              <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/cargas/${item.id}`, { method: "DELETE" }); await load(); }}>
                anular
              </button>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
