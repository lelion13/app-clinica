import { useEffect, useMemo, useState } from "react";

import { ProfessionalCombobox } from "../../components/ProfessionalCombobox";
import { AlertModal } from "../../components/AlertModal";
import { ForceSinProduccionModal } from "../../components/ForceSinProduccionModal";
import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";
import { CargasListGrid } from "./CargasListGrid";

const TIPO_OPTIONS = [
  { value: "hora_extra", label: "Hora extra" },
  { value: "hora_extra_por_ausencia", label: "Hora extra por ausencia" },
];

const MSG_SIN_PRODUCCION =
  "El profesional no tiene producción en esa fecha. No se puede cargar módulo ni novedad para ese día.";

const MOTIVO_LABELS = {
  vacaciones: "Vacaciones",
  enfermedad: "Enfermedad",
};

function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** @returns {Promise<boolean>} true if tiene producción */
async function checkTieneProduccion(fecha, codprof) {
  if (!fecha || !codprof) {
    const err = new Error("Faltan fecha o CODPROF para verificar producción");
    err.code = "produccion_params";
    throw err;
  }
  const params = new URLSearchParams({ fecha, codprof: String(codprof) });
  const result = await apiRequestWithRefresh(`/novedades/bonos/tiene-produccion?${params}`);
  return Boolean(result?.tiene_produccion);
}

/** Edit fecha: block without force modal */
async function assertTieneProduccion(fecha, codprof) {
  const ok = await checkTieneProduccion(fecha, codprof);
  if (!ok) {
    const err = new Error(MSG_SIN_PRODUCCION);
    err.code = "sin_produccion";
    throw err;
  }
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
  const [submitting, setSubmitting] = useState(false);
  const [forceOpen, setForceOpen] = useState(false);
  const [forceLoading, setForceLoading] = useState(false);

  const openPeriodo = useMemo(() => periodos.find((p) => p.estado === "open"), [periodos]);
  const selectedModulo = useMemo(
    () => modulos.find((m) => String(m.id) === String(moduloId)),
    [modulos, moduloId]
  );

  const fechaBounds = useMemo(() => {
    const periodo = periodos.find((p) => String(p.id) === String(periodoId)) || openPeriodo;
    const today = todayISO();
    if (!periodo?.fecha_inicio || !periodo?.fecha_fin) {
      return { min: undefined, max: today, valid: true };
    }
    const min = periodo.fecha_inicio;
    const max = periodo.fecha_fin < today ? periodo.fecha_fin : today;
    // Si el período aún no empezó (o min > max), no hay días seleccionables.
    const valid = min <= max;
    return {
      min: valid ? min : undefined,
      max: valid ? max : undefined,
      valid,
      periodoInicio: periodo.fecha_inicio,
      periodoFin: periodo.fecha_fin,
    };
  }, [periodos, periodoId, openPeriodo]);

  useEffect(() => {
    if (!fechaBounds.valid) {
      setFechaRealizacion("");
      return;
    }
    setFechaRealizacion((current) => {
      if (current && fechaBounds.min && fechaBounds.max) {
        if (current >= fechaBounds.min && current <= fechaBounds.max) return current;
      }
      return fechaBounds.max || todayISO();
    });
  }, [fechaBounds.min, fechaBounds.max, fechaBounds.valid]);

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
      professional_codprof: item.professional_codprof,
      concepto: item.modulo_descripcion || `Módulo #${item.modulo_id}`,
      horas: null,
      valor: item.modulo_valor,
      fecha_realizacion: item.fecha_realizacion,
      fecha_carga: item.created_at,
      motivo_sin_produccion: item.motivo_sin_produccion,
      motivo_sin_produccion_label: item.motivo_sin_produccion
        ? MOTIVO_LABELS[item.motivo_sin_produccion] || item.motivo_sin_produccion
        : null,
      observacion_sin_produccion: item.observacion_sin_produccion,
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
      professional_codprof: item.professional_codprof,
      concepto: item.tipo_label || item.tipo,
      horas: item.horas,
      valor: item.valor_calculado,
      fecha_realizacion: item.fecha_realizacion,
      fecha_carga: item.created_at,
      motivo_sin_produccion: item.motivo_sin_produccion,
      motivo_sin_produccion_label: item.motivo_sin_produccion
        ? MOTIVO_LABELS[item.motivo_sin_produccion] || item.motivo_sin_produccion
        : null,
      observacion_sin_produccion: item.observacion_sin_produccion,
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

  const performCreate = async (sinProd = null) => {
    const hasModulo = Boolean(moduloId);
    const hasNovedad = incluirNovedad || Boolean(horas);
    const extra = sinProd
      ? {
          motivo_sin_produccion: sinProd.motivo_sin_produccion,
          observacion_sin_produccion: sinProd.observacion_sin_produccion,
        }
      : {};
    if (hasModulo) {
      await apiRequestWithRefresh("/novedades/asignaciones-modulos", {
        method: "POST",
        body: JSON.stringify({
          periodo_id: Number(periodoId),
          servicio_id: Number(servicioId),
          professional_id: Number(professionalId),
          modulo_id: Number(moduloId),
          fecha_realizacion: fechaRealizacion,
          ...extra,
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
          ...extra,
        }),
      });
    }
    clearCargaFields();
    await load();
  };

  const submitCarga = async (event) => {
    event.preventDefault();
    setError("");
    setForceOpen(false);

    if (!periodoId || !servicioId || !professionalId || !fechaRealizacion) {
      setError("Completá período, servicio, profesional y fecha de realización");
      return;
    }
    if (!fechaBounds.valid) {
      setError("No hay fechas de realización válidas para este período (debe estar en curso y no ser futura)");
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

    const selectedProf = profesionales.find((p) => String(p.id) === String(professionalId));
    const codprof = selectedProf?.codprof;
    if (!codprof) {
      setError("El profesional seleccionado no tiene CODPROF; no se puede verificar producción");
      return;
    }

    setSubmitting(true);
    try {
      const tiene = await checkTieneProduccion(fechaRealizacion, codprof);
      if (!tiene) {
        setForceOpen(true);
        return;
      }
      await performCreate(null);
    } catch (err) {
      setError(err.message || "No se pudo cargar");
    } finally {
      setSubmitting(false);
    }
  };

  const confirmForceLoad = async (sinProd) => {
    setForceLoading(true);
    setError("");
    try {
      await performCreate(sinProd);
      setForceOpen(false);
    } catch (err) {
      setError(err.message || "No se pudo cargar");
      setForceOpen(false);
    } finally {
      setForceLoading(false);
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
        <AlertModal open={Boolean(error)} title="Atención" message={error} onClose={() => setError("")} />
        <ForceSinProduccionModal
          open={forceOpen}
          message={MSG_SIN_PRODUCCION}
          loading={forceLoading}
          onCancel={() => {
            setForceOpen(false);
            clearCargaFields();
          }}
          onConfirm={confirmForceLoad}
        />

        <form onSubmit={submitCarga}>
          <h2 style={{ margin: "12px 0 8px", fontSize: "1rem" }}>Contexto</h2>
          <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", marginBottom: 8, alignItems: "end" }}>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Período</span>
              <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)} style={uiStyles.formControl} required>
                <option value="">Elegí período</option>
                {periodos.map((p) => (
                  <option key={p.id} value={p.id}>#{p.id} {p.nombre || ""} ({p.estado})</option>
                ))}
              </select>
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Servicio</span>
              <select value={servicioId} onChange={(e) => setServicioId(e.target.value)} style={uiStyles.formControl} required>
                <option value="">Elegí servicio</option>
                {servicios.map((s) => (
                  <option key={s.id} value={s.id}>{s.nombre}</option>
                ))}
              </select>
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Fecha realización</span>
              <input
                type="date"
                value={fechaRealizacion}
                min={fechaBounds.min}
                max={fechaBounds.max}
                onChange={(e) => setFechaRealizacion(e.target.value)}
                required={fechaBounds.valid}
                disabled={!fechaBounds.valid}
                style={uiStyles.formControl}
              />
            </label>
          </div>
          {!fechaBounds.valid && periodoId ? (
            <p style={{ ...uiStyles.helpText, color: uiTheme.colors.danger, marginTop: 0, marginBottom: 16 }}>
              El período va del {fechaBounds.periodoInicio} al {fechaBounds.periodoFin} y aún no hay días
              realizables (la fecha no puede ser posterior a hoy). Cuando el período esté en curso vas a poder elegir días.
            </p>
          ) : (
            <div style={{ marginBottom: 8 }} />
          )}

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

          <button type="submit" style={uiStyles.buttonPrimary} disabled={submitting}>
            {submitting ? "Verificando…" : "Cargar novedad"}
          </button>
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
            const codprof = row.professional_codprof;
            if (!codprof) {
              throw new Error("El profesional no tiene CODPROF; no se puede verificar producción");
            }
            await assertTieneProduccion(fecha, codprof);
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
