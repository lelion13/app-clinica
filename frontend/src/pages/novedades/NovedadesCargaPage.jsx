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
  const [incluirNovedad, setIncluirNovedad] = useState(false);

  const openPeriodo = useMemo(() => periodos.find((p) => p.estado === "open"), [periodos]);
  const selectedModulo = useMemo(
    () => modulos.find((m) => String(m.id) === String(moduloId)),
    [modulos, moduloId]
  );

  const clearCargaFields = () => {
    setProfessionalId("");
    setModuloId("");
    setTipo("hora_extra");
    setHoras("");
    setIncluirNovedad(false);
  };

  const load = async () => {
    setError("");
    try {
      const [s, p, a, n] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/periodos"),
        apiRequestWithRefresh("/novedades/asignaciones-modulos"),
        apiRequestWithRefresh("/novedades/cargas"),
      ]);
      setServicios(s);
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
    const fetchProsAndModulos = async () => {
      if (!servicioId) {
        setProfesionales([]);
        setModulos([]);
        setValorHora(null);
        setProfessionalId("");
        setModuloId("");
        return;
      }
      const selected = servicios.find((s) => String(s.id) === String(servicioId));
      setValorHora(selected?.valor_hora ?? null);
      try {
        const [rows, mods] = await Promise.all([
          apiRequestWithRefresh(`/novedades/profesionales?servicio_id=${servicioId}`),
          apiRequestWithRefresh(`/novedades/modulos?servicio_id=${servicioId}`),
        ]);
        setProfesionales(rows);
        setModulos(mods);
        setModuloId("");
      } catch (err) {
        setError(err.message || "Error al cargar datos del servicio");
      }
    };
    fetchProsAndModulos();
  }, [servicioId, servicios]);

  const submitCarga = async (event) => {
    event.preventDefault();
    setError("");

    if (!periodoId || !servicioId || !professionalId) {
      setError("Completá período, servicio y profesional");
      return;
    }

    const hasModulo = Boolean(moduloId);
    const hasNovedad = incluirNovedad || Boolean(horas);
    if (!hasModulo && !hasNovedad) {
      setError("Seleccioná un módulo y/o completá las horas de la novedad");
      return;
    }

    if (hasNovedad) {
      const horasInt = Number(horas);
      if (!Number.isInteger(horasInt) || horasInt < 1) {
        setError("La cantidad de horas debe ser un entero mayor o igual a 1");
        return;
      }
    }

    try {
      if (hasModulo) {
        await apiRequestWithRefresh("/novedades/asignaciones-modulos", {
          method: "POST",
          body: JSON.stringify({
            periodo_id: Number(periodoId),
            servicio_id: Number(servicioId),
            professional_id: Number(professionalId),
            modulo_id: Number(moduloId),
          }),
        });
      }
      if (hasNovedad) {
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
      }
      clearCargaFields();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo cargar");
    }
  };

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Carga de módulos / novedades</h1>
        <p style={uiStyles.helpText}>
          Podés cargar módulo, novedad (tipo + horas enteras) o ambos.
          Los módulos listados son los asociados al servicio elegido. El valor hora es el del servicio.
          {openPeriodo ? ` Período abierto: #${openPeriodo.id}.` : " No hay período abierto."}
          {valorHora != null ? ` Valor hora del servicio: $${valorHora}.` : ""}
        </p>
        {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

        <form onSubmit={submitCarga}>
          <h2 style={{ margin: "12px 0 8px", fontSize: "1rem" }}>Contexto</h2>
          <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", marginBottom: 16 }}>
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

          <h2 style={{ margin: "8px 0", fontSize: "1rem" }}>Módulo (opcional)</h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 16 }}>
            <select value={moduloId} onChange={(e) => setModuloId(e.target.value)} style={uiStyles.formControl}>
              <option value="">Sin módulo</option>
              {modulos.map((m) => (
                <option key={m.id} value={m.id}>{m.descripcion}</option>
              ))}
            </select>
            <span style={uiStyles.helpText}>
              Valor (solo lectura): {selectedModulo ? `$${selectedModulo.valor}` : "—"}
            </span>
          </div>

          <h2 style={{ margin: "8px 0", fontSize: "1rem" }}>Novedad (opcional)</h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 16 }}>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)} style={uiStyles.formControl}>
              {TIPO_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <input
              type="number"
              step="1"
              min="1"
              inputMode="numeric"
              value={horas}
              onChange={(e) => {
                const raw = e.target.value;
                if (raw === "") {
                  setHoras("");
                  return;
                }
                const onlyDigits = raw.replace(/[^\d]/g, "");
                setHoras(onlyDigits);
                if (onlyDigits) setIncluirNovedad(true);
              }}
              placeholder="Cantidad de horas (entero)"
              style={uiStyles.formControl}
            />
            <span style={uiStyles.helpText}>
              Valor estimado: {horas && valorHora != null ? `$${(Number(horas) * Number(valorHora)).toFixed(2)}` : "—"}
            </span>
          </div>

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
