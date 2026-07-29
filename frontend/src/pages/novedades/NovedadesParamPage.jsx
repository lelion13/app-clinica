import { useEffect, useState } from "react";

import { ProfessionalCombobox } from "../../components/ProfessionalCombobox";
import { AlertModal } from "../../components/AlertModal";
import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

const tabs = [
  { id: "servicios", label: "Servicios" },
  { id: "modulos", label: "Módulos" },
  { id: "jefes", label: "Jefes ↔ servicios" },
  { id: "profesionales", label: "Profesionales ↔ servicios" },
  { id: "periodos", label: "Períodos" },
];

export function NovedadesParamPage() {
  const [tab, setTab] = useState("servicios");
  const [error, setError] = useState("");
  const [servicios, setServicios] = useState([]);
  const [modulos, setModulos] = useState([]);
  const [jefes, setJefes] = useState([]);
  const [profLinks, setProfLinks] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [users, setUsers] = useState([]);
  const [allPros, setAllPros] = useState([]);

  const [servicioNombre, setServicioNombre] = useState("");
  const [servicioValorHora, setServicioValorHora] = useState("0");
  const [moduloDesc, setModuloDesc] = useState("");
  const [moduloComentario, setModuloComentario] = useState("");
  const [moduloValor, setModuloValor] = useState("");
  const [moduloServicioIds, setModuloServicioIds] = useState([]);
  const [jefeUserId, setJefeUserId] = useState("");
  const [jefeServicioId, setJefeServicioId] = useState("");
  const [profId, setProfId] = useState("");
  const [profServicioId, setProfServicioId] = useState("");
  const [periodoNombre, setPeriodoNombre] = useState("");
  const [periodoInicio, setPeriodoInicio] = useState("");
  const [periodoFin, setPeriodoFin] = useState("");

  const load = async () => {
    setError("");
    try {
      const [s, m, j, p, u, pl, pros] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/modulos"),
        apiRequestWithRefresh("/novedades/jefe-servicios"),
        apiRequestWithRefresh("/novedades/periodos"),
        apiRequestWithRefresh("/novedades/jefes-candidatos"),
        apiRequestWithRefresh("/novedades/profesional-servicios"),
        apiRequestWithRefresh("/novedades/profesionales"),
      ]);
      setServicios(s);
      setModulos(m);
      setJefes(j);
      setPeriodos(p);
      setUsers(u || []);
      setProfLinks(pl || []);
      setAllPros(pros || []);
    } catch (err) {
      setError(err.message || "Error al cargar");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleModuloServicio = (id) => {
    setModuloServicioIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const createServicio = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/servicios", {
      method: "POST",
      body: JSON.stringify({
        nombre: servicioNombre,
        activo: true,
        valor_hora: Number(servicioValorHora),
      }),
    });
    setServicioNombre("");
    setServicioValorHora("0");
    await load();
  };

  const updateServicioValorHora = async (item, valor) => {
    await apiRequestWithRefresh(`/novedades/servicios/${item.id}`, {
      method: "PUT",
      body: JSON.stringify({
        nombre: item.nombre,
        activo: item.activo,
        valor_hora: Number(valor),
      }),
    });
    await load();
  };

  const createModulo = async (event) => {
    event.preventDefault();
    if (!moduloServicioIds.length) {
      setError("Seleccioná al menos un servicio para el módulo");
      return;
    }
    await apiRequestWithRefresh("/novedades/modulos", {
      method: "POST",
      body: JSON.stringify({
        descripcion: moduloDesc,
        comentario: moduloComentario || null,
        valor: Number(moduloValor),
        servicio_ids: moduloServicioIds.map(Number),
      }),
    });
    setModuloDesc("");
    setModuloComentario("");
    setModuloValor("");
    setModuloServicioIds([]);
    await load();
  };

  const createJefe = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/jefe-servicios", {
      method: "POST",
      body: JSON.stringify({ user_id: Number(jefeUserId), servicio_id: Number(jefeServicioId) }),
    });
    setJefeUserId("");
    setJefeServicioId("");
    await load();
  };

  const createProfLink = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/profesional-servicios", {
      method: "POST",
      body: JSON.stringify({ professional_id: Number(profId), servicio_id: Number(profServicioId) }),
    });
    setProfId("");
    setProfServicioId("");
    await load();
  };

  const createPeriodo = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/periodos", {
      method: "POST",
      body: JSON.stringify({
        nombre: periodoNombre || null,
        fecha_inicio: periodoInicio,
        fecha_fin: periodoFin,
        open_now: true,
      }),
    });
    setPeriodoNombre("");
    setPeriodoInicio("");
    setPeriodoFin("");
    await load();
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Parametrización — Novedades</h1>
      <p style={uiStyles.helpText}>
        Servicios con valor hora propio; módulos asociados a uno o más servicios; asociaciones de jefes y profesionales.
      </p>
      <AlertModal open={Boolean(error)} title="Atención" message={error} onClose={() => setError("")} />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            style={tab === item.id ? uiStyles.buttonPrimary : uiStyles.buttonSecondary}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === "servicios" ? (
        <>
          <form onSubmit={createServicio} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12, alignItems: "center" }}>
            <input value={servicioNombre} onChange={(e) => setServicioNombre(e.target.value)} placeholder="Nombre servicio" required style={uiStyles.formControl} />
            <input type="number" step="0.01" min="0" value={servicioValorHora} onChange={(e) => setServicioValorHora(e.target.value)} placeholder="Valor hora" required style={uiStyles.formControl} />
            <button type="submit" style={uiStyles.buttonPrimary}>Agregar</button>
          </form>
          <ul style={uiStyles.listCard}>
            {servicios.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}`, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <span>#{item.id} · {item.nombre} {item.activo ? "" : "(inactivo)"}</span>
                <label style={{ ...uiStyles.helpText, display: "inline-flex", gap: 6, alignItems: "center" }}>
                  Valor hora
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    defaultValue={item.valor_hora}
                    key={`${item.id}-${item.valor_hora}`}
                    style={{ ...uiStyles.formControl, width: 120 }}
                    onBlur={async (e) => {
                      if (String(e.target.value) !== String(item.valor_hora)) {
                        await updateServicioValorHora(item, e.target.value);
                      }
                    }}
                  />
                </label>
                <button type="button" style={uiStyles.buttonDanger} onClick={async () => { await apiRequestWithRefresh(`/novedades/servicios/${item.id}`, { method: "DELETE" }); await load(); }}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {tab === "modulos" ? (
        <>
          <form onSubmit={createModulo} style={{ display: "grid", gap: 10, marginBottom: 12 }}>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <input value={moduloDesc} onChange={(e) => setModuloDesc(e.target.value)} placeholder="Descripción" required style={uiStyles.formControl} />
              <input value={moduloComentario} onChange={(e) => setModuloComentario(e.target.value)} placeholder="Comentario" style={uiStyles.formControl} />
              <input type="number" step="0.01" min="0" value={moduloValor} onChange={(e) => setModuloValor(e.target.value)} placeholder="Valor ARS" required style={uiStyles.formControl} />
            </div>
            <div>
              <div style={{ ...uiStyles.helpText, marginBottom: 6 }}>Servicios (obligatorio, puede ser más de uno)</div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {servicios.map((s) => (
                  <label key={s.id} style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={moduloServicioIds.includes(s.id)}
                      onChange={() => toggleModuloServicio(s.id)}
                    />
                    {s.nombre}
                  </label>
                ))}
              </div>
            </div>
            <button type="submit" style={{ ...uiStyles.buttonPrimary, width: "fit-content" }}>Agregar módulo</button>
          </form>
          <ul style={uiStyles.listCard}>
            {modulos.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                #{item.id} · {item.descripcion} · ${item.valor}
                <div style={uiStyles.helpText}>
                  Servicios: {(item.servicio_nombres || []).join(", ") || "sin asociar"}
                </div>
                <button type="button" style={{ ...uiStyles.buttonDanger, marginTop: 6 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/modulos/${item.id}`, { method: "DELETE" }); await load(); }}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {tab === "jefes" ? (
        <>
          <form onSubmit={createJefe} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <select value={jefeUserId} onChange={(e) => setJefeUserId(e.target.value)} required style={uiStyles.formControl}>
              <option value="">Jefe médico</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
              ))}
            </select>
            <select value={jefeServicioId} onChange={(e) => setJefeServicioId(e.target.value)} required style={uiStyles.formControl}>
              <option value="">Servicio</option>
              {servicios.map((s) => (
                <option key={s.id} value={s.id}>{s.nombre}</option>
              ))}
            </select>
            <button type="submit" style={uiStyles.buttonPrimary}>Asociar</button>
          </form>
          <ul style={uiStyles.listCard}>
            {jefes.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                {item.user_name || item.user_id} → {item.servicio_nombre || item.servicio_id}{" "}
                <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/jefe-servicios/${item.id}`, { method: "DELETE" }); await load(); }}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {tab === "profesionales" ? (
        <>
          <p style={uiStyles.helpText}>
            Solo los profesionales asociados a un servicio aparecen en la carga.
            También podés gestionarlos en Mis profesionales.
          </p>
          <form onSubmit={createProfLink} style={{ display: "grid", gap: 10, marginBottom: 12, maxWidth: 480 }}>
            <ProfessionalCombobox
              label="Profesional"
              professionals={allPros}
              value={profId}
              onChange={setProfId}
              required
            />
            <select value={profServicioId} onChange={(e) => setProfServicioId(e.target.value)} required style={uiStyles.formControl}>
              <option value="">Servicio</option>
              {servicios.map((s) => (
                <option key={s.id} value={s.id}>{s.nombre}</option>
              ))}
            </select>
            <button type="submit" style={uiStyles.buttonPrimary}>Asociar</button>
          </form>
          <ul style={uiStyles.listCard}>
            {profLinks.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                {item.professional_name || item.professional_id} → {item.servicio_nombre || item.servicio_id}{" "}
                <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/profesional-servicios/${item.id}`, { method: "DELETE" }); await load(); }}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {tab === "periodos" ? (
        <>
          <form onSubmit={createPeriodo} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <input value={periodoNombre} onChange={(e) => setPeriodoNombre(e.target.value)} placeholder="Nombre (opcional)" style={uiStyles.formControl} />
            <input type="date" value={periodoInicio} onChange={(e) => setPeriodoInicio(e.target.value)} required style={uiStyles.formControl} />
            <input type="date" value={periodoFin} onChange={(e) => setPeriodoFin(e.target.value)} required style={uiStyles.formControl} />
            <button type="submit" style={uiStyles.buttonPrimary}>Abrir período</button>
          </form>
          <ul style={uiStyles.listCard}>
            {periodos.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                #{item.id} · {item.nombre || "Sin nombre"} · {item.fecha_inicio} → {item.fecha_fin} · <strong>{item.estado}</strong>{" "}
                {item.estado === "open" ? (
                  <button type="button" style={{ ...uiStyles.buttonSecondary, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/periodos/${item.id}/cerrar`, { method: "POST" }); await load(); }}>
                    cerrar
                  </button>
                ) : (
                  <button type="button" style={{ ...uiStyles.buttonSecondary, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/periodos/${item.id}/reabrir`, { method: "POST" }); await load(); }}>
                    reabrir
                  </button>
                )}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  );
}
