import { useEffect, useMemo, useState } from "react";

import { ProfessionalCombobox } from "../../components/ProfessionalCombobox";
import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";
import { CargasListGrid } from "./CargasListGrid";

const TIPO_OPTIONS = [
  { value: "hora_extra", label: "Hora extra" },
  { value: "hora_extra_por_ausencia", label: "Hora extra por ausencia" },
];

function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

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
  const [fechaRealizacion, setFechaRealizacion] = useState(todayISO());
  const [loadingServicio, setLoadingServicio] = useState(false);

  const openPeriodo = useMemo(() => periodos.find((p) => p.estado === "open"), [periodos]);
  const selectedModulo = useMemo(
    () => modulos.find((m) => String(m.id) === String(moduloId)),
    [modulos, moduloId]
  );

  const fechaBounds = useMemo(() => {
    const periodo = periodos.find((p) => String(p.id) === String(periodoId)) || openPeriodo;
    if (!periodo) return { min: undefined, max: todayISO() };
    const today = todayISO();
    const max = periodo.fecha_fin < today ? periodo.fecha_fin : today;
    return { min: periodo.fecha_inicio, max };
  }, [periodos, periodoId, openPeriodo]);

  const gridRows = useMemo(() => {
    const moduloRows = asignaciones.map((item) => ({
      kind: "modulo",
      kind_label: "Módulo",
      id: item.id,
      periodo_id: item.periodo_id,
      periodo_nombre: item.periodo_nombre,
      servicio_id: item.servicio_id,
      servicio_nombre: item.servicio_nombre,
      professional_id: item.professional_id,
      professional_name: item.professional_name,
      concepto: item.modulo_descripcion || `Módulo #${item.modulo_id}`,
      horas: null,
      valor: item.modulo_valor,
      fecha_realizacion: item.fecha_realizacion,
      fecha_carga: item.created_at,
      periodo_estado: periodos.find((p) => p.id === item.periodo_id)?.estado,
    }));
    const novedadRows = novedades.map((item) => ({
      kind: "novedad",
      kind_label: "Novedad",
      id: item.id,
      periodo_id: item.periodo_id,
      periodo_nombre: item.periodo_nombre,
      servicio_id: item.servicio_id,
      servicio_nombre: item.servicio_nombre,
      professional_id: item.professional_id,
      professional_name: item.professional_name,
      concepto: item.tipo_label || item.tipo,
      horas: item.horas,
      valor: item.valor_calculado,
      fecha_realizacion: item.fecha_realizacion,
      fecha_carga: item.created_at,
      periodo_estado: periodos.find((p) => p.id === item.periodo_id)?.estado,
    }));
    return [...moduloRows, ...novedadRows];
  }, [asignaciones, novedades, periodos]);

  const clearCargaFields = () => {
    setProfessionalId("");
    setModuloId("");
    setTipo("hora_extra");
    setHoras("");
    setIncluirNovedad(false);
    setFechaRealizacion(todayISO());
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
    let cancelled = false;

    const fetchProsAndModulos = async () => {
      if (!servicioId) {
        setProfesionales([]);
        setModulos([]);
        setValorHora(null);
        setProfessionalId("");
        setModuloId("");
        setLoadingServicio(false);
        return;
      }

      setLoadingServicio(true);
      setProfesionales([]);
      setModulos([]);
      setProfessionalId("");
      setModuloId("");

      const selected = servicios.find((s) => String(s.id) === String(servicioId));
      setValorHora(selected?.valor_hora ?? null);

      try {
        const [rows, mods] = await Promise.all([
          apiRequestWithRefresh(`/novedades/profesionales?servicio_id=${servicioId}`),
          apiRequestWithRefresh(`/novedades/modulos?servicio_id=${servicioId}`),
        ]);
        if (cancelled) return;
        setProfesionales(rows);
        setModulos(mods);
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Error al cargar datos del servicio");
        }
      } finally {
        if (!cancelled) {
          setLoadingServicio(false);
        }
      }
    };

    fetchProsAndModulos();
    return () => {
      cancelled = true;
    };
  }, [servicioId, servicios]);

  const submitCarga = async (event) => {
    event.preventDefault();
    setError("");

    if (!periodoId || !servicioId || !professionalId || !fechaRealizacion) {
      setError("Completá período, servicio, profesional y fecha de realización");
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
            fecha_realizacion: fechaRealizacion,
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
            fecha_realizacion: fechaRealizacion,
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
          Indicá el día de realización (dentro del período y no posterior a hoy).
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
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Fecha realización</span>
              <input
                type="date"
                value={fechaRealizacion}
                min={fechaBounds.min}
                max={fechaBounds.max}
                onChange={(e) => setFechaRealizacion(e.target.value)}
                required
                style={uiStyles.formControl}
              />
            </label>
          </div>

          <div style={{ marginBottom: 16, maxWidth: 420 }}>
            <ProfessionalCombobox
              label="Profesional"
              professionals={profesionales}
              value={professionalId}
              onChange={setProfessionalId}
              required
              placeholder={servicioId ? "Buscar profesional del servicio…" : "Elegí servicio primero"}
            />
          </div>

          {loadingServicio ? (
            <p style={uiStyles.helpText}>Cargando profesionales y módulos del servicio…</p>
          ) : null}
          {!loadingServicio && servicioId && !profesionales.length ? (
            <p style={{ ...uiStyles.helpText, color: uiTheme.colors.danger }}>
              No hay profesionales asociados a este servicio. Asociarlos en Mis profesionales.
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
        <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Cargas</h2>
        <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
          Módulos y novedades de tus servicios. Orden por defecto: servicio → profesional.
          Podés filtrar, ordenar y editar la fecha de realización si el período está abierto.
        </p>
        <CargasListGrid
          rows={gridRows}
          onAnular={async (row) => {
            const path =
              row.kind === "modulo"
                ? `/novedades/asignaciones-modulos/${row.id}`
                : `/novedades/cargas/${row.id}`;
            await apiRequestWithRefresh(path, { method: "DELETE" });
            await load();
          }}
          onUpdateFecha={async (row, fecha) => {
            const path =
              row.kind === "modulo"
                ? `/novedades/asignaciones-modulos/${row.id}`
                : `/novedades/cargas/${row.id}`;
            await apiRequestWithRefresh(path, {
              method: "PUT",
              body: JSON.stringify({ fecha_realizacion: fecha }),
            });
            await load();
          }}
        />
      </div>
    </section>
  );
}
