import { useEffect, useMemo, useState } from "react";

import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

export function NovedadesCargaPage() {
  const [error, setError] = useState("");
  const [servicios, setServicios] = useState([]);
  const [modulos, setModulos] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [profesionales, setProfesionales] = useState([]);
  const [asignaciones, setAsignaciones] = useState([]);
  const [novedades, setNovedades] = useState([]);

  const [servicioId, setServicioId] = useState("");
  const [periodoId, setPeriodoId] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [moduloId, setModuloId] = useState("");
  const [valor, setValor] = useState("");
  const [justificacion, setJustificacion] = useState("");

  const openPeriodo = useMemo(() => periodos.find((p) => p.estado === "open"), [periodos]);

  const load = async () => {
    setError("");
    try {
      const [s, m, p, a, n] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/modulos"),
        apiRequestWithRefresh("/novedades/periodos"),
        apiRequestWithRefresh("/novedades/asignaciones-modulos"),
        apiRequestWithRefresh("/novedades/cargas"),
      ]);
      setServicios(s);
      setModulos(m);
      setPeriodos(p);
      setAsignaciones(a);
      setNovedades(n);
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
      const path = servicioId
        ? `/novedades/profesionales?servicio_id=${servicioId}`
        : "/novedades/profesionales";
      try {
        const rows = await apiRequestWithRefresh(path);
        setProfesionales(rows);
      } catch (err) {
        setError(err.message || "Error al cargar profesionales");
      }
    };
    fetchPros();
  }, [servicioId]);

  useEffect(() => {
    const selected = modulos.find((m) => String(m.id) === String(moduloId));
    if (selected) {
      setValor(String(selected.valor));
    }
  }, [moduloId, modulos]);

  const submitAsignacion = async (event) => {
    event.preventDefault();
    setError("");
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
    try {
      await apiRequestWithRefresh("/novedades/cargas", {
        method: "POST",
        body: JSON.stringify({
          periodo_id: Number(periodoId),
          servicio_id: Number(servicioId),
          professional_id: Number(professionalId),
          modulo_id: Number(moduloId),
          valor: Number(valor),
          justificacion,
        }),
      });
      setJustificacion("");
      await load();
    } catch (err) {
      setError(err.message || "No se pudo cargar novedad");
    }
  };

  const nameById = (list, id, key = "nombre") => list.find((x) => x.id === id)?.[key] || id;

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Carga de módulos / novedades</h1>
        <p style={uiStyles.helpText}>
          Dos flujos: asignar módulos al profesional, o cargar una novedad con concepto, valor y justificación.
          {openPeriodo ? ` Período abierto: #${openPeriodo.id}.` : " No hay período abierto."}
        </p>
        {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", marginBottom: 12 }}>
          <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)} style={uiStyles.formControl} required>
            <option value="">Período</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>#{p.id} {p.nombre || ""} ({p.estado})</option>
            ))}
          </select>
          <select value={servicioId} onChange={(e) => setServicioId(e.target.value)} style={uiStyles.formControl} required>
            <option value="">Servicio</option>
            {servicios.map((s) => (
              <option key={s.id} value={s.id}>{s.nombre}</option>
            ))}
          </select>
          <select value={professionalId} onChange={(e) => setProfessionalId(e.target.value)} style={uiStyles.formControl} required>
            <option value="">Profesional</option>
            {profesionales.map((p) => (
              <option key={p.id} value={p.id}>{p.full_name}</option>
            ))}
          </select>
          <select value={moduloId} onChange={(e) => setModuloId(e.target.value)} style={uiStyles.formControl} required>
            <option value="">Módulo / concepto</option>
            {modulos.map((m) => (
              <option key={m.id} value={m.id}>{m.descripcion} (${m.valor})</option>
            ))}
          </select>
        </div>

        <form onSubmit={submitAsignacion} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
          <button type="submit" style={uiStyles.buttonPrimary}>Asignar módulo</button>
        </form>

        <form onSubmit={submitNovedad} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-start" }}>
          <input type="number" step="0.01" min="0" value={valor} onChange={(e) => setValor(e.target.value)} placeholder="Valor ARS" required style={uiStyles.formControl} />
          <input value={justificacion} onChange={(e) => setJustificacion(e.target.value)} placeholder="Justificación (obligatoria)" required style={{ ...uiStyles.formControl, minWidth: 260 }} />
          <button type="submit" style={uiStyles.buttonPrimary}>Cargar novedad</button>
        </form>
      </div>

      <div style={uiStyles.pageSection}>
        <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Asignaciones recientes</h2>
        <ul style={uiStyles.listCard}>
          {asignaciones.slice(0, 20).map((item) => (
            <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
              #{item.id} · servicio {nameById(servicios, item.servicio_id)} · prof {item.professional_id} · módulo {nameById(modulos, item.modulo_id, "descripcion")}{" "}
              <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/asignaciones-modulos/${item.id}`, { method: "DELETE" }); await load(); }}>
                anular
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div style={uiStyles.pageSection}>
        <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Novedades recientes</h2>
        <ul style={uiStyles.listCard}>
          {novedades.slice(0, 20).map((item) => (
            <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
              #{item.id} · ${item.valor} · {item.justificacion}{" "}
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
