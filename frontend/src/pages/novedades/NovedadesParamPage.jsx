import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

const tabs = [
  { id: "servicios", label: "Servicios" },
  { id: "modulos", label: "Módulos" },
  { id: "valor_hora", label: "Valor hora" },
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
  const [valorHora, setValorHora] = useState("");

  const [servicioNombre, setServicioNombre] = useState("");
  const [moduloDesc, setModuloDesc] = useState("");
  const [moduloComentario, setModuloComentario] = useState("");
  const [moduloValor, setModuloValor] = useState("");
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
      const [s, m, j, p, u, pl, pros, vh] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/modulos"),
        apiRequestWithRefresh("/novedades/jefe-servicios"),
        apiRequestWithRefresh("/novedades/periodos"),
        apiRequestWithRefresh("/novedades/jefes-candidatos"),
        apiRequestWithRefresh("/novedades/profesional-servicios"),
        apiRequestWithRefresh("/novedades/profesionales"),
        apiRequestWithRefresh("/novedades/valor-hora"),
      ]);
      setServicios(s);
      setModulos(m);
      setJefes(j);
      setPeriodos(p);
      setUsers(u || []);
      setProfLinks(pl || []);
      setAllPros(pros || []);
      setValorHora(vh?.valor_hora != null ? String(vh.valor_hora) : "");
    } catch (err) {
      setError(err.message || "Error al cargar");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const createServicio = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/servicios", {
      method: "POST",
      body: JSON.stringify({ nombre: servicioNombre, activo: true }),
    });
    setServicioNombre("");
    await load();
  };

  const createModulo = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/modulos", {
      method: "POST",
      body: JSON.stringify({
        descripcion: moduloDesc,
        comentario: moduloComentario || null,
        valor: Number(moduloValor),
      }),
    });
    setModuloDesc("");
    setModuloComentario("");
    setModuloValor("");
    await load();
  };

  const saveValorHora = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/novedades/valor-hora", {
      method: "PUT",
      body: JSON.stringify({ valor_hora: Number(valorHora) }),
    });
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
        ABM de servicios, módulos, valor hora, asociaciones y períodos. Asociá profesionales a servicios antes de cargar.
      </p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

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
          <form onSubmit={createServicio} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <input value={servicioNombre} onChange={(e) => setServicioNombre(e.target.value)} placeholder="Nombre servicio" required style={uiStyles.formControl} />
            <button type="submit" style={uiStyles.buttonPrimary}>Agregar</button>
          </form>
          <ul style={uiStyles.listCard}>
            {servicios.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                #{item.id} · {item.nombre} {item.activo ? "" : "(inactivo)"}{" "}
                <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/servicios/${item.id}`, { method: "DELETE" }); await load(); }}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {tab === "modulos" ? (
        <>
          <form onSubmit={createModulo} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <input value={moduloDesc} onChange={(e) => setModuloDesc(e.target.value)} placeholder="Descripción" required style={uiStyles.formControl} />
            <input value={moduloComentario} onChange={(e) => setModuloComentario(e.target.value)} placeholder="Comentario" style={uiStyles.formControl} />
            <input type="number" step="0.01" min="0" value={moduloValor} onChange={(e) => setModuloValor(e.target.value)} placeholder="Valor ARS" required style={uiStyles.formControl} />
            <button type="submit" style={uiStyles.buttonPrimary}>Agregar</button>
          </form>
          <ul style={uiStyles.listCard}>
            {modulos.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                #{item.id} · {item.descripcion} · ${item.valor}{" "}
                <button type="button" style={{ ...uiStyles.buttonDanger, marginLeft: 8 }} onClick={async () => { await apiRequestWithRefresh(`/novedades/modulos/${item.id}`, { method: "DELETE" }); await load(); }}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {tab === "valor_hora" ? (
        <>
          <p style={uiStyles.helpText}>Se usa para calcular el valor de novedades: horas × valor hora.</p>
          <form onSubmit={saveValorHora} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <input type="number" step="0.01" min="0" value={valorHora} onChange={(e) => setValorHora(e.target.value)} placeholder="Valor hora ARS" required style={uiStyles.formControl} />
            <button type="submit" style={uiStyles.buttonPrimary}>Guardar valor hora</button>
          </form>
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
          <p style={uiStyles.helpText}>Solo los profesionales asociados a un servicio aparecen en la carga de módulos/novedades.</p>
          <form onSubmit={createProfLink} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <select value={profId} onChange={(e) => setProfId(e.target.value)} required style={uiStyles.formControl}>
              <option value="">Profesional</option>
              {allPros.map((p) => (
                <option key={p.id} value={p.id}>{p.full_name}</option>
              ))}
            </select>
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
