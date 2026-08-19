import { useEffect, useState } from "react";

import { ProfessionalCombobox } from "../../components/ProfessionalCombobox";
import { BonoOpcionMultiCombobox } from "../../components/BonoOpcionMultiCombobox";
import { AlertModal } from "../../components/AlertModal";
import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

const tabs = [
  { id: "servicios", label: "Servicios" },
  { id: "modulos", label: "Módulos" },
  { id: "produccion", label: "Producción" },
  { id: "jefes", label: "Jefes ↔ servicios" },
  { id: "profesionales", label: "Profesionales ↔ servicios" },
  { id: "periodos", label: "Períodos" },
  { id: "feriados", label: "Feriados" },
];

export function NovedadesParamPage() {
  const [tab, setTab] = useState("servicios");
  const [error, setError] = useState("");
  const [servicios, setServicios] = useState([]);
  const [modulos, setModulos] = useState([]);
  const [jefes, setJefes] = useState([]);
  const [profLinks, setProfLinks] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [feriados, setFeriados] = useState([]);
  const [produccionTarifas, setProduccionTarifas] = useState([]);
  const [createProduccionOpen, setCreateProduccionOpen] = useState(false);
  const [createProduccionSaving, setCreateProduccionSaving] = useState(false);
  const [produccionOpcionIds, setProduccionOpcionIds] = useState([]);
  const [produccionValor, setProduccionValor] = useState("");
  const [bonoOpciones, setBonoOpciones] = useState([]);
  const [editTarifa, setEditTarifa] = useState(null);
  const [editTarifaValor, setEditTarifaValor] = useState("");
  const [editTarifaSaving, setEditTarifaSaving] = useState(false);
  const [deleteTarifa, setDeleteTarifa] = useState(null);
  const [deleteTarifaSaving, setDeleteTarifaSaving] = useState(false);
  const [users, setUsers] = useState([]);
  const [allPros, setAllPros] = useState([]);

  const [servicioNombre, setServicioNombre] = useState("");
  const [servicioValorHora, setServicioValorHora] = useState("0");
  const [servicioConcepto, setServicioConcepto] = useState("");
  const [createServicioOpen, setCreateServicioOpen] = useState(false);
  const [createServicioSaving, setCreateServicioSaving] = useState(false);
  const [editServicio, setEditServicio] = useState(null);
  const [editServicioNombre, setEditServicioNombre] = useState("");
  const [editServicioValorHora, setEditServicioValorHora] = useState("0");
  const [editServicioConcepto, setEditServicioConcepto] = useState("");
  const [editServicioActivo, setEditServicioActivo] = useState(true);
  const [editServicioSaving, setEditServicioSaving] = useState(false);
  const [deleteServicio, setDeleteServicio] = useState(null);
  const [deleteServicioSaving, setDeleteServicioSaving] = useState(false);
  const [moduloDesc, setModuloDesc] = useState("");
  const [moduloComentario, setModuloComentario] = useState("");
  const [moduloValor, setModuloValor] = useState("");
  const [moduloProduccion, setModuloProduccion] = useState(false);
  const [moduloSadofe, setModuloSadofe] = useState(false);
  const [moduloServicioIds, setModuloServicioIds] = useState([]);
  const [createModuloOpen, setCreateModuloOpen] = useState(false);
  const [createModuloSaving, setCreateModuloSaving] = useState(false);
  const [editModulo, setEditModulo] = useState(null);
  const [editDesc, setEditDesc] = useState("");
  const [editComentario, setEditComentario] = useState("");
  const [editValor, setEditValor] = useState("");
  const [editProduccion, setEditProduccion] = useState(false);
  const [editSadofe, setEditSadofe] = useState(false);
  const [editSaving, setEditSaving] = useState(false);
  const [serviciosModulo, setServiciosModulo] = useState(null);
  const [serviciosIdsEdit, setServiciosIdsEdit] = useState([]);
  const [serviciosSaving, setServiciosSaving] = useState(false);
  const [deleteModulo, setDeleteModulo] = useState(null);
  const [deleteModuloSaving, setDeleteModuloSaving] = useState(false);
  const [createFeriadoOpen, setCreateFeriadoOpen] = useState(false);
  const [createFeriadoSaving, setCreateFeriadoSaving] = useState(false);
  const [feriadoFecha, setFeriadoFecha] = useState("");
  const [feriadoNombre, setFeriadoNombre] = useState("");
  const [editFeriado, setEditFeriado] = useState(null);
  const [editFeriadoFecha, setEditFeriadoFecha] = useState("");
  const [editFeriadoNombre, setEditFeriadoNombre] = useState("");
  const [editFeriadoSaving, setEditFeriadoSaving] = useState(false);
  const [deleteFeriado, setDeleteFeriado] = useState(null);
  const [deleteFeriadoSaving, setDeleteFeriadoSaving] = useState(false);
  const [jefeUserId, setJefeUserId] = useState("");
  const [jefeServicioId, setJefeServicioId] = useState("");
  const [profId, setProfId] = useState("");
  const [profServicioId, setProfServicioId] = useState("");
  const [periodoNombre, setPeriodoNombre] = useState("");
  const [periodoInicio, setPeriodoInicio] = useState("");
  const [periodoFin, setPeriodoFin] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [purging, setPurging] = useState(false);
  const [confirmPurge, setConfirmPurge] = useState(false);
  const [infoMessage, setInfoMessage] = useState("");

  const load = async () => {
    setError("");
    try {
      const [s, m, j, p, u, pl, pros, f, pt] = await Promise.all([
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/modulos"),
        apiRequestWithRefresh("/novedades/jefe-servicios"),
        apiRequestWithRefresh("/novedades/periodos"),
        apiRequestWithRefresh("/novedades/jefes-candidatos"),
        apiRequestWithRefresh("/novedades/profesional-servicios"),
        apiRequestWithRefresh("/novedades/profesionales"),
        apiRequestWithRefresh("/novedades/feriados"),
        apiRequestWithRefresh("/novedades/produccion-tarifas"),
      ]);
      setServicios(s);
      setModulos(m);
      setJefes(j);
      setPeriodos(p);
      setUsers(u || []);
      setProfLinks(pl || []);
      setAllPros(pros || []);
      setFeriados(f || []);
      setProduccionTarifas(pt || []);
    } catch (err) {
      setError(err.message || "Error al cargar");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const parseConceptoLiquidacion = (raw) => {
    const trimmed = String(raw ?? "").trim();
    if (trimmed === "") return null;
    const n = Number(trimmed);
    if (!Number.isFinite(n) || n < 0 || !Number.isInteger(n)) return undefined;
    return n === 0 ? null : n;
  };

  const resetCreateServicioForm = () => {
    setServicioNombre("");
    setServicioValorHora("0");
    setServicioConcepto("");
  };

  const openCreateServicio = () => {
    resetCreateServicioForm();
    setCreateServicioOpen(true);
  };

  const closeCreateServicio = () => {
    if (createServicioSaving) return;
    setCreateServicioOpen(false);
    resetCreateServicioForm();
  };

  const createServicio = async () => {
    if (!servicioNombre.trim() || servicioValorHora === "") {
      setError("Completá nombre y valor hora del servicio");
      return;
    }
    const concepto = parseConceptoLiquidacion(servicioConcepto);
    if (concepto === undefined) {
      setError("Concepto liquidación debe ser un entero positivo o vacío");
      return;
    }
    setCreateServicioSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh("/novedades/servicios", {
        method: "POST",
        body: JSON.stringify({
          nombre: servicioNombre.trim(),
          activo: true,
          valor_hora: Number(servicioValorHora),
          concepto_liquidacion: concepto,
        }),
      });
      setCreateServicioOpen(false);
      resetCreateServicioForm();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo crear el servicio");
    } finally {
      setCreateServicioSaving(false);
    }
  };

  const openEditServicio = (item) => {
    setEditServicio(item);
    setEditServicioNombre(item.nombre || "");
    setEditServicioValorHora(String(item.valor_hora ?? "0"));
    setEditServicioConcepto(item.concepto_liquidacion == null ? "" : String(item.concepto_liquidacion));
    setEditServicioActivo(Boolean(item.activo));
  };

  const closeEditServicio = () => {
    if (editServicioSaving) return;
    setEditServicio(null);
  };

  const saveEditServicio = async () => {
    if (!editServicio) return;
    if (!editServicioNombre.trim() || editServicioValorHora === "") {
      setError("Completá nombre y valor hora del servicio");
      return;
    }
    const concepto = parseConceptoLiquidacion(editServicioConcepto);
    if (concepto === undefined) {
      setError("Concepto liquidación debe ser un entero positivo o vacío");
      return;
    }
    setEditServicioSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/servicios/${editServicio.id}`, {
        method: "PUT",
        body: JSON.stringify({
          nombre: editServicioNombre.trim(),
          activo: Boolean(editServicioActivo),
          valor_hora: Number(editServicioValorHora),
          concepto_liquidacion: concepto,
        }),
      });
      setEditServicio(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo guardar el servicio");
    } finally {
      setEditServicioSaving(false);
    }
  };

  const closeDeleteServicio = () => {
    if (deleteServicioSaving) return;
    setDeleteServicio(null);
  };

  const confirmDeleteServicio = async () => {
    if (!deleteServicio) return;
    setDeleteServicioSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/servicios/${deleteServicio.id}`, { method: "DELETE" });
      setDeleteServicio(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo eliminar el servicio");
    } finally {
      setDeleteServicioSaving(false);
    }
  };

  const toggleModuloServicio = (id) => {
    setModuloServicioIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const resetCreateModuloForm = () => {
    setModuloDesc("");
    setModuloComentario("");
    setModuloValor("");
    setModuloProduccion(false);
    setModuloSadofe(false);
    setModuloServicioIds([]);
  };

  const openCreateModulo = () => {
    resetCreateModuloForm();
    setCreateModuloOpen(true);
  };

  const closeCreateModulo = () => {
    if (createModuloSaving) return;
    setCreateModuloOpen(false);
    resetCreateModuloForm();
  };

  const createModulo = async () => {
    if (!moduloDesc.trim() || moduloValor === "") {
      setError("Completá descripción y valor del módulo");
      return;
    }
    if (!moduloServicioIds.length) {
      setError("Seleccioná al menos un servicio para el módulo");
      return;
    }
    setCreateModuloSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh("/novedades/modulos", {
        method: "POST",
        body: JSON.stringify({
          descripcion: moduloDesc,
          comentario: moduloComentario || null,
          valor: Number(moduloValor),
          produccion: Boolean(moduloProduccion),
          sadofe: Boolean(moduloSadofe),
          servicio_ids: moduloServicioIds.map(Number),
        }),
      });
      setCreateModuloOpen(false);
      resetCreateModuloForm();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo crear el módulo");
    } finally {
      setCreateModuloSaving(false);
    }
  };

  const openEditModulo = (item) => {
    setEditModulo(item);
    setEditDesc(item.descripcion || "");
    setEditComentario(item.comentario || "");
    setEditValor(String(item.valor ?? ""));
    setEditProduccion(Boolean(item.produccion));
    setEditSadofe(Boolean(item.sadofe));
  };

  const closeEditModulo = () => {
    if (editSaving) return;
    setEditModulo(null);
  };

  const saveEditModulo = async () => {
    if (!editModulo) return;
    setEditSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/modulos/${editModulo.id}`, {
        method: "PUT",
        body: JSON.stringify({
          descripcion: editDesc,
          comentario: editComentario || null,
          valor: Number(editValor),
          produccion: Boolean(editProduccion),
          sadofe: Boolean(editSadofe),
        }),
      });
      setEditModulo(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo guardar el módulo");
    } finally {
      setEditSaving(false);
    }
  };

  const openServiciosModulo = (item) => {
    setServiciosModulo(item);
    setServiciosIdsEdit([...(item.servicio_ids || [])]);
  };

  const closeServiciosModulo = () => {
    if (serviciosSaving) return;
    setServiciosModulo(null);
  };

  const toggleServicioEdit = (id) => {
    setServiciosIdsEdit((current) =>
      current.includes(id) ? current.filter((x) => x !== id) : [...current, id]
    );
  };

  const saveServiciosModulo = async () => {
    if (!serviciosModulo) return;
    setServiciosSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/modulos/${serviciosModulo.id}/servicios`, {
        method: "PUT",
        body: JSON.stringify({ servicio_ids: serviciosIdsEdit.map(Number) }),
      });
      setServiciosModulo(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudieron actualizar los servicios");
    } finally {
      setServiciosSaving(false);
    }
  };

  const closeDeleteModulo = () => {
    if (deleteModuloSaving) return;
    setDeleteModulo(null);
  };

  const confirmDeleteModulo = async () => {
    if (!deleteModulo) return;
    setDeleteModuloSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/modulos/${deleteModulo.id}`, { method: "DELETE" });
      setDeleteModulo(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo eliminar el módulo");
    } finally {
      setDeleteModuloSaving(false);
    }
  };

  const resetFeriadoForm = () => {
    setFeriadoFecha("");
    setFeriadoNombre("");
  };

  const openCreateFeriado = () => {
    resetFeriadoForm();
    setCreateFeriadoOpen(true);
  };

  const closeCreateFeriado = () => {
    if (createFeriadoSaving) return;
    setCreateFeriadoOpen(false);
    resetFeriadoForm();
  };

  const createFeriado = async () => {
    if (!feriadoFecha || !feriadoNombre.trim()) {
      setError("Completá fecha y nombre del feriado");
      return;
    }
    setCreateFeriadoSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh("/novedades/feriados", {
        method: "POST",
        body: JSON.stringify({ fecha: feriadoFecha, nombre: feriadoNombre.trim() }),
      });
      setCreateFeriadoOpen(false);
      resetFeriadoForm();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo crear el feriado");
    } finally {
      setCreateFeriadoSaving(false);
    }
  };

  const openEditFeriado = (item) => {
    setEditFeriado(item);
    setEditFeriadoFecha(String(item.fecha || "").slice(0, 10));
    setEditFeriadoNombre(item.nombre || "");
  };

  const closeEditFeriado = () => {
    if (editFeriadoSaving) return;
    setEditFeriado(null);
  };

  const saveEditFeriado = async () => {
    if (!editFeriado) return;
    setEditFeriadoSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/feriados/${editFeriado.id}`, {
        method: "PUT",
        body: JSON.stringify({ fecha: editFeriadoFecha, nombre: editFeriadoNombre.trim() }),
      });
      setEditFeriado(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo guardar el feriado");
    } finally {
      setEditFeriadoSaving(false);
    }
  };

  const closeDeleteFeriado = () => {
    if (deleteFeriadoSaving) return;
    setDeleteFeriado(null);
  };

  const confirmDeleteFeriado = async () => {
    if (!deleteFeriado) return;
    setDeleteFeriadoSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/feriados/${deleteFeriado.id}`, { method: "DELETE" });
      setDeleteFeriado(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo eliminar el feriado");
    } finally {
      setDeleteFeriadoSaving(false);
    }
  };

  const resetCreateProduccionForm = () => {
    setProduccionOpcionIds([]);
    setProduccionValor("");
    setBonoOpciones([]);
  };

  const openCreateProduccion = async () => {
    resetCreateProduccionForm();
    setError("");
    try {
      const opts = await apiRequestWithRefresh("/novedades/bono-opciones?sin_tarifa=1");
      setBonoOpciones(Array.isArray(opts) ? opts : []);
      setCreateProduccionOpen(true);
    } catch (err) {
      setError(err.message || "No se pudieron cargar opciones de bonos");
    }
  };

  const closeCreateProduccion = () => {
    if (createProduccionSaving) return;
    setCreateProduccionOpen(false);
    resetCreateProduccionForm();
  };

  const createProduccion = async () => {
    if (!produccionOpcionIds.length || produccionValor === "") {
      setError("Seleccioná al menos una opción e ingresá el valor unitario");
      return;
    }
    const valor = Number(produccionValor);
    if (!Number.isFinite(valor) || valor < 0 || !Number.isInteger(valor)) {
      setError("El valor unitario debe ser un entero ≥ 0");
      return;
    }
    setCreateProduccionSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh("/novedades/produccion-tarifas/bulk", {
        method: "POST",
        body: JSON.stringify({ opcion_ids: produccionOpcionIds.map(Number), valor_unitario: valor }),
      });
      setCreateProduccionOpen(false);
      resetCreateProduccionForm();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo crear la tarifa");
    } finally {
      setCreateProduccionSaving(false);
    }
  };

  const openEditTarifa = (item) => {
    setEditTarifa(item);
    setEditTarifaValor(String(item.valor_unitario ?? ""));
  };

  const closeEditTarifa = () => {
    if (editTarifaSaving) return;
    setEditTarifa(null);
  };

  const saveEditTarifa = async () => {
    if (!editTarifa) return;
    const valor = Number(editTarifaValor);
    if (!Number.isFinite(valor) || valor < 0 || !Number.isInteger(valor)) {
      setError("El valor unitario debe ser un entero ≥ 0");
      return;
    }
    setEditTarifaSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/produccion-tarifas/${editTarifa.id}`, {
        method: "PUT",
        body: JSON.stringify({ valor_unitario: valor }),
      });
      setEditTarifa(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo guardar la tarifa");
    } finally {
      setEditTarifaSaving(false);
    }
  };

  const closeDeleteTarifa = () => {
    if (deleteTarifaSaving) return;
    setDeleteTarifa(null);
  };

  const confirmDeleteTarifa = async () => {
    if (!deleteTarifa) return;
    setDeleteTarifaSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh(`/novedades/produccion-tarifas/${deleteTarifa.id}`, { method: "DELETE" });
      setDeleteTarifa(null);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo eliminar la tarifa");
    } finally {
      setDeleteTarifaSaving(false);
    }
  };

  useEffect(() => {
    if (
      !createServicioOpen && !editServicio && !deleteServicio
      && !createModuloOpen && !editModulo && !serviciosModulo && !deleteModulo
      && !createFeriadoOpen && !editFeriado && !deleteFeriado
      && !createProduccionOpen && !editTarifa && !deleteTarifa
    ) return undefined;
    const onKey = (e) => {
      if (e.key !== "Escape") return;
      if (deleteServicio) closeDeleteServicio();
      else if (editServicio) closeEditServicio();
      else if (createServicioOpen) closeCreateServicio();
      else if (deleteTarifa) closeDeleteTarifa();
      else if (editTarifa) closeEditTarifa();
      else if (createProduccionOpen) closeCreateProduccion();
      else if (deleteFeriado) closeDeleteFeriado();
      else if (editFeriado) closeEditFeriado();
      else if (createFeriadoOpen) closeCreateFeriado();
      else if (deleteModulo) closeDeleteModulo();
      else if (serviciosModulo) closeServiciosModulo();
      else if (editModulo) closeEditModulo();
      else if (createModuloOpen) closeCreateModulo();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [
    createServicioOpen,
    createServicioSaving,
    editServicio,
    editServicioSaving,
    deleteServicio,
    deleteServicioSaving,
    createModuloOpen,
    createModuloSaving,
    editModulo,
    editSaving,
    serviciosModulo,
    serviciosSaving,
    deleteModulo,
    deleteModuloSaving,
    createFeriadoOpen,
    createFeriadoSaving,
    editFeriado,
    editFeriadoSaving,
    deleteFeriado,
    deleteFeriadoSaving,
    createProduccionOpen,
    createProduccionSaving,
    editTarifa,
    editTarifaSaving,
    deleteTarifa,
    deleteTarifaSaving,
  ]);

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

  const runSync = async () => {
    setError("");
    setSyncing(true);
    try {
      const summary = await apiRequestWithRefresh("/novedades/profesionales/sync", { method: "POST" });
      setInfoMessage(
        `Sincronización OK · creados ${summary.created} · actualizados ${summary.updated} · inactivados ${summary.inactivated}` +
          (summary.errors?.length ? ` · avisos: ${summary.errors.slice(0, 3).join("; ")}` : "")
      );
      await load();
    } catch (err) {
      setError(err.message || "Error al sincronizar profesionales");
    } finally {
      setSyncing(false);
    }
  };

  const runPurge = async () => {
    setError("");
    setPurging(true);
    try {
      const result = await apiRequestWithRefresh("/novedades/transaccional/purge", { method: "POST" });
      setConfirmPurge(false);
      setInfoMessage(
        `Limpieza OK · asignaciones ${result.deleted_asignaciones} · novedades ${result.deleted_novedades} · vínculos ${result.deleted_profesional_servicios}`
      );
      await load();
    } catch (err) {
      setError(err.message || "Error al limpiar cargas");
    } finally {
      setPurging(false);
    }
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Parametrización — Novedades</h1>
      <p style={uiStyles.helpText}>
        Servicios con valor hora propio; módulos asociados a uno o más servicios; asociaciones de jefes y profesionales.
        El catálogo de profesionales de Novedades se sincroniza desde el sistema externo (no usa Distribución).
      </p>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <button type="button" style={uiStyles.buttonPrimary} onClick={runSync} disabled={syncing}>
          {syncing ? "Sincronizando…" : "Sincronizar profesionales"}
        </button>
        <button type="button" style={uiStyles.buttonDanger} onClick={() => setConfirmPurge(true)} disabled={purging}>
          Limpiar cargas
        </button>
      </div>
      <AlertModal open={Boolean(error)} title="Atención" message={error} onClose={() => setError("")} />
      <AlertModal open={Boolean(infoMessage)} title="Listo" message={infoMessage} onClose={() => setInfoMessage("")} />
      {confirmPurge ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1100,
            background: "rgba(15, 43, 39, 0.45)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "max(16px, 4vh) 16px",
          }}
          onClick={() => !purging && setConfirmPurge(false)}
        >
          <div
            role="alertdialog"
            aria-modal="true"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 440,
              width: "100%",
              padding: 22,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem" }}>¿Limpiar cargas?</h2>
            <p style={{ marginTop: 0, marginBottom: 18, fontSize: 14, lineHeight: 1.45 }}>
              Se eliminarán de forma permanente asignaciones de módulo, novedades y vínculos profesional↔servicio.
              Se conservan servicios, módulos, períodos y jefes. Esta acción no se puede deshacer.
            </p>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
              <button type="button" style={uiStyles.buttonSecondary} disabled={purging} onClick={() => setConfirmPurge(false)}>
                Cancelar
              </button>
              <button type="button" style={uiStyles.buttonDanger} disabled={purging} onClick={runPurge}>
                {purging ? "Eliminando…" : "Confirmar"}
              </button>
            </div>
          </div>
        </div>
      ) : null}

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
          <div style={{ marginBottom: 12 }}>
            <button type="button" style={uiStyles.buttonPrimary} onClick={openCreateServicio}>
              Nuevo servicio
            </button>
          </div>
          <ul style={uiStyles.listCard}>
            {servicios.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between" }}>
                  <div style={{ flex: "1 1 200px" }}>
                    #{item.id} · {item.nombre} {item.activo ? "" : "(inactivo)"} · Concepto liquidación {item.concepto_liquidacion == null ? "—" : item.concepto_liquidacion}
                    <div style={uiStyles.helpText}>
                      Concepto liquidación {item.concepto_liquidacion == null ? "—" : item.concepto_liquidacion}
                      {" · "}
                      Valor hora ${item.valor_hora}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => openEditServicio(item)}>
                      editar
                    </button>
                    <button type="button" style={uiStyles.buttonDanger} onClick={() => setDeleteServicio(item)}>
                      eliminar
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>

          {createServicioOpen ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeCreateServicio}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="create-servicio-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 520,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="create-servicio-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Nuevo servicio
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Nombre</span>
                    <input
                      value={servicioNombre}
                      onChange={(e) => setServicioNombre(e.target.value)}
                      placeholder="Nombre servicio"
                      style={uiStyles.formControl}
                      disabled={createServicioSaving}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Valor hora</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={servicioValorHora}
                      onChange={(e) => setServicioValorHora(e.target.value)}
                      placeholder="Valor hora"
                      style={uiStyles.formControl}
                      disabled={createServicioSaving}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Concepto liquidación</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      value={servicioConcepto}
                      onChange={(e) => setServicioConcepto(e.target.value)}
                      placeholder="Opcional"
                      style={uiStyles.formControl}
                      disabled={createServicioSaving}
                    />
                  </label>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" onClick={closeCreateServicio} style={uiStyles.buttonSecondary} disabled={createServicioSaving}>
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={createServicio}
                    style={uiStyles.buttonPrimary}
                    disabled={createServicioSaving || !servicioNombre.trim() || servicioValorHora === ""}
                  >
                    {createServicioSaving ? "Cargando…" : "Cargar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {editServicio ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeEditServicio}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="edit-servicio-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 520,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="edit-servicio-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Editar servicio #{editServicio.id}
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Nombre</span>
                    <input
                      value={editServicioNombre}
                      onChange={(e) => setEditServicioNombre(e.target.value)}
                      style={uiStyles.formControl}
                      disabled={editServicioSaving}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Valor hora</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={editServicioValorHora}
                      onChange={(e) => setEditServicioValorHora(e.target.value)}
                      style={uiStyles.formControl}
                      disabled={editServicioSaving}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Concepto liquidación</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      value={editServicioConcepto}
                      onChange={(e) => setEditServicioConcepto(e.target.value)}
                      placeholder="Opcional"
                      style={uiStyles.formControl}
                      disabled={editServicioSaving}
                    />
                  </label>
                  <label style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={editServicioActivo}
                      onChange={(e) => setEditServicioActivo(e.target.checked)}
                      disabled={editServicioSaving}
                    />
                    Activo
                  </label>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" onClick={closeEditServicio} style={uiStyles.buttonSecondary} disabled={editServicioSaving}>
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={saveEditServicio}
                    style={uiStyles.buttonPrimary}
                    disabled={editServicioSaving || !editServicioNombre.trim() || editServicioValorHora === ""}
                  >
                    {editServicioSaving ? "Guardando…" : "Guardar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {deleteServicio ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeDeleteServicio}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="delete-servicio-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 520,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="delete-servicio-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Eliminar servicio
                </h2>
                <p style={{ marginTop: 0 }}>¿Confirmás eliminar este servicio?</p>
                <div style={{ display: "grid", gap: 6, marginBottom: 16, fontSize: 14 }}>
                  <div>
                    <strong>ID:</strong> #{deleteServicio.id}
                  </div>
                  <div>
                    <strong>Nombre:</strong> {deleteServicio.nombre || "—"}
                  </div>
                  <div>
                    <strong>Valor hora:</strong> ${deleteServicio.valor_hora}
                  </div>
                  <div>
                    <strong>Concepto liquidación:</strong>{" "}
                    {deleteServicio.concepto_liquidacion == null ? "—" : deleteServicio.concepto_liquidacion}
                  </div>
                  <div>
                    <strong>Activo:</strong> {deleteServicio.activo ? "sí" : "no"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
                  <button type="button" onClick={closeDeleteServicio} style={uiStyles.buttonSecondary} disabled={deleteServicioSaving}>
                    Cancelar
                  </button>
                  <button type="button" onClick={confirmDeleteServicio} style={uiStyles.buttonDanger} disabled={deleteServicioSaving}>
                    {deleteServicioSaving ? "Eliminando…" : "Eliminar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}
        </>
      ) : null}

      {tab === "modulos" ? (
        <>
          <div style={{ marginBottom: 12 }}>
            <button type="button" style={uiStyles.buttonPrimary} onClick={openCreateModulo}>
              Nuevo módulo
            </button>
          </div>
          <ul style={uiStyles.listCard}>
            {modulos.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between" }}>
                  <div style={{ flex: "1 1 200px" }}>
                    #{item.id} · {item.descripcion} · ${item.valor}
                    <div style={uiStyles.helpText}>
                      Servicios: {(item.servicio_nombres || []).join(", ") || "sin asociar"}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => openEditModulo(item)}>
                      editar
                    </button>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => openServiciosModulo(item)}>
                      servicios
                    </button>
                    <button type="button" style={uiStyles.buttonDanger} onClick={() => setDeleteModulo(item)}>
                      eliminar
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>

          {createModuloOpen ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeCreateModulo}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="create-modulo-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 520,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="create-modulo-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Nuevo módulo
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Descripción</span>
                    <input
                      value={moduloDesc}
                      onChange={(e) => setModuloDesc(e.target.value)}
                      placeholder="Descripción"
                      style={uiStyles.formControl}
                      disabled={createModuloSaving}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Comentario</span>
                    <input
                      value={moduloComentario}
                      onChange={(e) => setModuloComentario(e.target.value)}
                      placeholder="Comentario"
                      style={uiStyles.formControl}
                      disabled={createModuloSaving}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Valor ARS</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={moduloValor}
                      onChange={(e) => setModuloValor(e.target.value)}
                      placeholder="Valor ARS"
                      style={uiStyles.formControl}
                      disabled={createModuloSaving}
                    />
                  </label>
                  <label style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={moduloProduccion}
                      onChange={(e) => setModuloProduccion(e.target.checked)}
                      disabled={createModuloSaving}
                    />
                    Producción
                  </label>
                  <label style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={moduloSadofe}
                      onChange={(e) => setModuloSadofe(e.target.checked)}
                      disabled={createModuloSaving}
                    />
                    SADOFE
                  </label>
                  <div>
                    <div style={{ ...uiStyles.helpText, marginBottom: 6 }}>Servicios (obligatorio, puede ser más de uno)</div>
                    <div style={{ display: "grid", gap: 8 }}>
                      {servicios.map((s) => (
                        <label key={s.id} style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                          <input
                            type="checkbox"
                            checked={moduloServicioIds.includes(s.id)}
                            onChange={() => toggleModuloServicio(s.id)}
                            disabled={createModuloSaving}
                          />
                          {s.nombre}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" onClick={closeCreateModulo} style={uiStyles.buttonSecondary} disabled={createModuloSaving}>
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={createModulo}
                    style={uiStyles.buttonPrimary}
                    disabled={createModuloSaving || !moduloDesc.trim() || moduloValor === ""}
                  >
                    {createModuloSaving ? "Cargando…" : "Cargar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {editModulo ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeEditModulo}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="edit-modulo-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 480,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="edit-modulo-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Editar módulo #{editModulo.id}
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Descripción</span>
                    <input value={editDesc} onChange={(e) => setEditDesc(e.target.value)} required style={uiStyles.formControl} disabled={editSaving} />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Comentario</span>
                    <input value={editComentario} onChange={(e) => setEditComentario(e.target.value)} style={uiStyles.formControl} disabled={editSaving} />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Valor ARS</span>
                    <input type="number" step="0.01" min="0" value={editValor} onChange={(e) => setEditValor(e.target.value)} required style={uiStyles.formControl} disabled={editSaving} />
                  </label>
                  <label style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={editProduccion}
                      onChange={(e) => setEditProduccion(e.target.checked)}
                      disabled={editSaving}
                    />
                    Producción
                  </label>
                  <label style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={editSadofe}
                      onChange={(e) => setEditSadofe(e.target.checked)}
                      disabled={editSaving}
                    />
                    SADOFE
                  </label>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" onClick={closeEditModulo} style={uiStyles.buttonSecondary} disabled={editSaving}>
                    Cancelar
                  </button>
                  <button type="button" onClick={saveEditModulo} style={uiStyles.buttonPrimary} disabled={editSaving || !editDesc || editValor === ""}>
                    {editSaving ? "Guardando…" : "Guardar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {serviciosModulo ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeServiciosModulo}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="servicios-modulo-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 480,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="servicios-modulo-title" style={{ marginTop: 0, marginBottom: 8, fontSize: "1.1rem" }}>
                  Servicios — módulo #{serviciosModulo.id}
                </h2>
                <p style={{ ...uiStyles.helpText, marginTop: 0, marginBottom: 12 }}>
                  {serviciosModulo.descripcion}. Podés dejar sin servicios.
                </p>
                <div style={{ display: "grid", gap: 8, marginBottom: 16 }}>
                  {servicios.map((s) => (
                    <label key={s.id} style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                      <input
                        type="checkbox"
                        checked={serviciosIdsEdit.includes(s.id)}
                        onChange={() => toggleServicioEdit(s.id)}
                        disabled={serviciosSaving}
                      />
                      {s.nombre}
                    </label>
                  ))}
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
                  <button type="button" onClick={closeServiciosModulo} style={uiStyles.buttonSecondary} disabled={serviciosSaving}>
                    Cancelar
                  </button>
                  <button type="button" onClick={saveServiciosModulo} style={uiStyles.buttonPrimary} disabled={serviciosSaving}>
                    {serviciosSaving ? "Guardando…" : "Aceptar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {deleteModulo ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeDeleteModulo}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="delete-modulo-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 480,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="delete-modulo-title" style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem" }}>
                  ¿Eliminar este módulo?
                </h2>
                <p style={{ marginTop: 0, marginBottom: 12, color: uiTheme.colors.textMuted, fontSize: 14 }}>
                  Vas a eliminar el siguiente módulo. Esta acción no se puede deshacer desde acá.
                </p>
                <div style={{ ...uiStyles.kpiCard, marginBottom: 14, lineHeight: 1.55, fontSize: 14 }}>
                  <div>
                    <strong>ID:</strong> #{deleteModulo.id}
                  </div>
                  <div>
                    <strong>Descripción:</strong> {deleteModulo.descripcion || "—"}
                  </div>
                  <div>
                    <strong>Comentario:</strong> {deleteModulo.comentario || "—"}
                  </div>
                  <div>
                    <strong>Valor:</strong> ${deleteModulo.valor}
                  </div>
                  <div>
                    <strong>Producción:</strong> {deleteModulo.produccion ? "sí" : "no"}
                  </div>
                  <div>
                    <strong>SADOFE:</strong> {deleteModulo.sadofe ? "sí" : "no"}
                  </div>
                  <div>
                    <strong>Servicios:</strong>{" "}
                    {(deleteModulo.servicio_nombres || []).join(", ") || "sin asociar"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
                  <button type="button" onClick={closeDeleteModulo} style={uiStyles.buttonSecondary} disabled={deleteModuloSaving}>
                    Cancelar
                  </button>
                  <button type="button" onClick={confirmDeleteModulo} style={uiStyles.buttonDanger} disabled={deleteModuloSaving}>
                    {deleteModuloSaving ? "Eliminando…" : "Eliminar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}
        </>
      ) : null}

      {tab === "produccion" ? (
        <>
          <p style={uiStyles.helpText}>
            Tarifas para valorizar bonos importados en Capital Humano (cantidad × valor). No confundir con el flag
            <strong> Producción</strong> del módulo (omite check externo de producción al cargar).
          </p>
          <div style={{ marginBottom: 12 }}>
            <button type="button" style={uiStyles.buttonPrimary} onClick={openCreateProduccion}>
              Nueva producción
            </button>
          </div>
          <ul style={uiStyles.listCard}>
            {produccionTarifas.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between" }}>
                  <div style={{ flex: "1 1 200px" }}>
                    #{item.id} · {item.label}
                    <div style={uiStyles.helpText}>Valor unitario ${Number(item.valor_unitario).toLocaleString("es-AR")}</div>
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => openEditTarifa(item)}>
                      editar
                    </button>
                    <button type="button" style={uiStyles.buttonDanger} onClick={() => setDeleteTarifa(item)}>
                      eliminar
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          {!produccionTarifas.length ? (
            <p style={uiStyles.helpText}>Sin tarifas. Importá bonos primero para detectar opciones disponibles.</p>
          ) : null}

          {createProduccionOpen ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeCreateProduccion}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="create-produccion-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 520,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="create-produccion-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Nueva producción
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <BonoOpcionMultiCombobox
                    options={bonoOpciones}
                    selectedIds={produccionOpcionIds}
                    onChange={setProduccionOpcionIds}
                    disabled={createProduccionSaving}
                    label="Opciones de bono (podés elegir varias con el mismo valor)"
                  />
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Valor unitario (entero ≥ 0)</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      value={produccionValor}
                      onChange={(e) => setProduccionValor(e.target.value)}
                      placeholder="Valor unitario"
                      style={uiStyles.formControl}
                      disabled={createProduccionSaving}
                    />
                  </label>
                  {!bonoOpciones.length ? (
                    <p style={uiStyles.helpText}>Importá bonos para detectar opciones disponibles.</p>
                  ) : null}
                  <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={closeCreateProduccion} disabled={createProduccionSaving}>
                      Cancelar
                    </button>
                    <button
                      type="button"
                      style={uiStyles.buttonPrimary}
                      onClick={createProduccion}
                      disabled={createProduccionSaving || !produccionOpcionIds.length || produccionValor === ""}
                    >
                      {createProduccionSaving ? "Guardando…" : "Cargar"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : null}

          {editTarifa ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeEditTarifa}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="edit-produccion-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 520,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="edit-produccion-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Editar tarifa
                </h2>
                <p style={uiStyles.helpText}>{editTarifa.label}</p>
                <label style={{ display: "grid", gap: 4 }}>
                  <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Valor unitario (entero ≥ 0)</span>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={editTarifaValor}
                    onChange={(e) => setEditTarifaValor(e.target.value)}
                    style={uiStyles.formControl}
                    disabled={editTarifaSaving}
                  />
                </label>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 16 }}>
                  <button type="button" style={uiStyles.buttonSecondary} onClick={closeEditTarifa} disabled={editTarifaSaving}>
                    Cancelar
                  </button>
                  <button type="button" style={uiStyles.buttonPrimary} onClick={saveEditTarifa} disabled={editTarifaSaving}>
                    {editTarifaSaving ? "Guardando…" : "Guardar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {deleteTarifa ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: 16,
              }}
              onClick={closeDeleteTarifa}
            >
              <div
                role="dialog"
                aria-modal="true"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 440,
                  width: "100%",
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 style={{ marginTop: 0 }}>Eliminar tarifa</h2>
                <p style={uiStyles.helpText}>
                  ¿Eliminar tarifa de <strong>{deleteTarifa.label}</strong> (${deleteTarifa.valor_unitario})?
                </p>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                  <button type="button" style={uiStyles.buttonSecondary} onClick={closeDeleteTarifa} disabled={deleteTarifaSaving}>
                    Cancelar
                  </button>
                  <button type="button" style={uiStyles.buttonDanger} onClick={confirmDeleteTarifa} disabled={deleteTarifaSaving}>
                    {deleteTarifaSaving ? "Eliminando…" : "Eliminar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}
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

      {tab === "feriados" ? (
        <>
          <div style={{ marginBottom: 12 }}>
            <button type="button" style={uiStyles.buttonPrimary} onClick={openCreateFeriado}>
              Nuevo feriado
            </button>
          </div>
          <ul style={uiStyles.listCard}>
            {feriados.map((item) => (
              <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between" }}>
                  <div style={{ flex: "1 1 200px" }}>
                    #{item.id} · {String(item.fecha || "").slice(0, 10)} · {item.nombre}
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => openEditFeriado(item)}>
                      editar
                    </button>
                    <button type="button" style={uiStyles.buttonDanger} onClick={() => setDeleteFeriado(item)}>
                      eliminar
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          {!feriados.length ? (
            <p style={uiStyles.helpText}>Todavía no hay feriados cargados.</p>
          ) : null}

          {createFeriadoOpen ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeCreateFeriado}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="create-feriado-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 480,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="create-feriado-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Nuevo feriado
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Fecha</span>
                    <input type="date" value={feriadoFecha} onChange={(e) => setFeriadoFecha(e.target.value)} style={uiStyles.formControl} disabled={createFeriadoSaving} />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Nombre</span>
                    <input value={feriadoNombre} onChange={(e) => setFeriadoNombre(e.target.value)} placeholder="Nombre" style={uiStyles.formControl} disabled={createFeriadoSaving} />
                  </label>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" onClick={closeCreateFeriado} style={uiStyles.buttonSecondary} disabled={createFeriadoSaving}>
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={createFeriado}
                    style={uiStyles.buttonPrimary}
                    disabled={createFeriadoSaving || !feriadoFecha || !feriadoNombre.trim()}
                  >
                    {createFeriadoSaving ? "Cargando…" : "Cargar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {editFeriado ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeEditFeriado}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="edit-feriado-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 480,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="edit-feriado-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.1rem" }}>
                  Editar feriado #{editFeriado.id}
                </h2>
                <div style={{ display: "grid", gap: 10 }}>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Fecha</span>
                    <input type="date" value={editFeriadoFecha} onChange={(e) => setEditFeriadoFecha(e.target.value)} style={uiStyles.formControl} disabled={editFeriadoSaving} />
                  </label>
                  <label style={{ display: "grid", gap: 4 }}>
                    <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Nombre</span>
                    <input value={editFeriadoNombre} onChange={(e) => setEditFeriadoNombre(e.target.value)} style={uiStyles.formControl} disabled={editFeriadoSaving} />
                  </label>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" onClick={closeEditFeriado} style={uiStyles.buttonSecondary} disabled={editFeriadoSaving}>
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={saveEditFeriado}
                    style={uiStyles.buttonPrimary}
                    disabled={editFeriadoSaving || !editFeriadoFecha || !editFeriadoNombre.trim()}
                  >
                    {editFeriadoSaving ? "Guardando…" : "Guardar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {deleteFeriado ? (
            <div
              role="presentation"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                background: "rgba(15, 43, 39, 0.45)",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: "max(16px, 4vh) 16px",
                overflowY: "auto",
              }}
              onClick={closeDeleteFeriado}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="delete-feriado-title"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: "#fff",
                  borderRadius: uiTheme.radius.md,
                  maxWidth: 480,
                  width: "100%",
                  marginBottom: 24,
                  padding: 22,
                  boxShadow: uiTheme.shadow.md,
                  border: `1px solid ${uiTheme.colors.border}`,
                }}
              >
                <h2 id="delete-feriado-title" style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem" }}>
                  ¿Eliminar este feriado?
                </h2>
                <p style={{ marginTop: 0, marginBottom: 12, color: uiTheme.colors.textMuted, fontSize: 14 }}>
                  Vas a eliminar el siguiente feriado. Esta acción no se puede deshacer desde acá.
                </p>
                <div style={{ ...uiStyles.kpiCard, marginBottom: 14, lineHeight: 1.55, fontSize: 14 }}>
                  <div>
                    <strong>ID:</strong> #{deleteFeriado.id}
                  </div>
                  <div>
                    <strong>Fecha:</strong> {String(deleteFeriado.fecha || "").slice(0, 10)}
                  </div>
                  <div>
                    <strong>Nombre:</strong> {deleteFeriado.nombre || "—"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
                  <button type="button" onClick={closeDeleteFeriado} style={uiStyles.buttonSecondary} disabled={deleteFeriadoSaving}>
                    Cancelar
                  </button>
                  <button type="button" onClick={confirmDeleteFeriado} style={uiStyles.buttonDanger} disabled={deleteFeriadoSaving}>
                    {deleteFeriadoSaving ? "Eliminando…" : "Eliminar"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
