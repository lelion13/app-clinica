import { useEffect, useMemo, useState } from "react";

import { ProfessionalCombobox } from "../../components/ProfessionalCombobox";
import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

export function NovedadesMisProfesionalesPage() {
  const [error, setError] = useState("");
  const [servicios, setServicios] = useState([]);
  const [links, setLinks] = useState([]);
  const [candidatos, setCandidatos] = useState([]);
  const [servicioId, setServicioId] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [loading, setLoading] = useState(false);

  const linksDelServicio = useMemo(
    () => links.filter((l) => String(l.servicio_id) === String(servicioId)),
    [links, servicioId]
  );

  const load = async () => {
    setError("");
    try {
      const [s, l] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/profesional-servicios"),
      ]);
      setServicios(s);
      setLinks(l);
      setServicioId((current) => {
        if (current && s.some((item) => String(item.id) === String(current))) return current;
        return s.length ? String(s[0].id) : "";
      });
    } catch (err) {
      setError(err.message || "Error al cargar");
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    let cancelled = false;
    const fetchCandidatos = async () => {
      if (!servicioId) {
        setCandidatos([]);
        setProfessionalId("");
        return;
      }
      setLoading(true);
      try {
        const rows = await apiRequestWithRefresh(
          `/novedades/profesionales?servicio_id=${servicioId}&exclude_linked=true`
        );
        if (!cancelled) {
          setCandidatos(rows);
          setProfessionalId("");
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Error al cargar profesionales");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchCandidatos();
    return () => {
      cancelled = true;
    };
  }, [servicioId, links]);

  const asociar = async (event) => {
    event.preventDefault();
    setError("");
    if (!servicioId || !professionalId) {
      setError("Elegí servicio y profesional");
      return;
    }
    try {
      await apiRequestWithRefresh("/novedades/profesional-servicios", {
        method: "POST",
        body: JSON.stringify({
          servicio_id: Number(servicioId),
          professional_id: Number(professionalId),
        }),
      });
      setProfessionalId("");
      await load();
    } catch (err) {
      setError(err.message || "No se pudo asociar");
    }
  };

  const quitar = async (linkId) => {
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/profesional-servicios/${linkId}`, { method: "DELETE" });
      await load();
    } catch (err) {
      setError(err.message || "No se pudo desasociar");
    }
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Mis profesionales</h1>
      <p style={uiStyles.helpText}>
        Asociá o quitá profesionales de tus servicios. Al quitar, las cargas históricas se conservan;
        el profesional deja de aparecer para cargas nuevas.
      </p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

      <form onSubmit={asociar} style={{ display: "grid", gap: 12, marginBottom: 20, maxWidth: 520 }}>
        <label style={{ display: "grid", gap: 4 }}>
          <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Servicio</span>
          <select
            value={servicioId}
            onChange={(e) => setServicioId(e.target.value)}
            style={uiStyles.formControl}
            required
          >
            <option value="">Elegí servicio</option>
            {servicios.map((s) => (
              <option key={s.id} value={s.id}>{s.nombre}</option>
            ))}
          </select>
        </label>

        <ProfessionalCombobox
          label="Profesional a asociar"
          professionals={candidatos}
          value={professionalId}
          onChange={setProfessionalId}
          required
          placeholder="Buscar por nombre, DNI o matrícula…"
        />
        {loading ? <p style={uiStyles.helpText}>Cargando candidatos…</p> : null}
        {!loading && servicioId && !candidatos.length ? (
          <p style={uiStyles.helpText}>No hay más profesionales activos para asociar a este servicio.</p>
        ) : null}

        <button type="submit" style={uiStyles.buttonPrimary}>Asociar</button>
      </form>

      <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>
        Asociados {servicioId ? `· ${servicios.find((s) => String(s.id) === String(servicioId))?.nombre || ""}` : ""}
      </h2>
      <ul style={uiStyles.listCard}>
        {linksDelServicio.map((item) => (
          <li
            key={item.id}
            style={{
              padding: "10px 12px",
              borderBottom: `1px solid ${uiTheme.colors.border}`,
              display: "flex",
              justifyContent: "space-between",
              gap: 8,
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <span>{item.professional_name || `Prof #${item.professional_id}`}</span>
            <button type="button" style={uiStyles.buttonDanger} onClick={() => quitar(item.id)}>
              Quitar
            </button>
          </li>
        ))}
        {!linksDelServicio.length ? (
          <li style={{ padding: 12, color: uiTheme.colors.textMuted }}>Sin profesionales asociados.</li>
        ) : null}
      </ul>
    </section>
  );
}
