/** Helpers de filtros e indicadores para la grilla Ocupación. */

const EMPTY_TOKEN = "__empty__";

export function cellToFilterValue(value) {
  if (value === null || value === undefined || value === "") return EMPTY_TOKEN;
  return String(value);
}

export function filterValueLabel(token) {
  return token === EMPTY_TOKEN ? "(vacío)" : token;
}

export function distinctColumnValues(items, key) {
  const set = new Set();
  for (const row of items) {
    set.add(cellToFilterValue(row?.[key]));
  }
  return Array.from(set).sort((a, b) => {
    if (a === EMPTY_TOKEN) return 1;
    if (b === EMPTY_TOKEN) return -1;
    return a.localeCompare(b, "es", { numeric: true, sensitivity: "base" });
  });
}

/** OR dentro de columna; AND entre columnas. Select vacío = sin filtro en esa columna. */
export function applyColumnFilters(items, filtersByKey) {
  const active = Object.entries(filtersByKey || {}).filter(([, selected]) => selected?.length > 0);
  if (!active.length) return items;
  return items.filter((row) =>
    active.every(([key, selected]) => selected.includes(cellToFilterValue(row?.[key])))
  );
}

export function parseTimeToMinutes(value) {
  const text = String(value ?? "").trim();
  const match = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(text);
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  const seconds = Number(match[3] || 0);
  if (
    !Number.isFinite(hours) ||
    !Number.isFinite(minutes) ||
    !Number.isFinite(seconds) ||
    hours > 23 ||
    minutes > 59 ||
    seconds > 59
  ) {
    return null;
  }
  return hours * 60 + minutes + seconds / 60;
}

function asNonNegNumber(value) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) return 0;
  return n;
}

/**
 * Null si falta dia o horas inválidas (Q19/Q21).
 * Turnos/sobreturnos vienen de la API (Q20); se suman aunque sean 0.
 */
export function rowMetrics(row) {
  const dia = String(row?.dia ?? "").trim();
  if (!dia) return null;

  const from = parseTimeToMinutes(row?.hora_desde);
  const to = parseTimeToMinutes(row?.hora_hasta);
  if (from === null || to === null || !(to > from)) return null;

  return {
    horas: (to - from) / 60,
    cantidad_turnos: asNonNegNumber(row?.cantidad_turnos),
    cantidad_sobreturno: asNonNegNumber(row?.cantidad_sobreturno),
  };
}

/** Agrupa por id_dominio + especialidad + medico + dia; suma métricas de todas las filas. */
export function buildIndicators(filteredItems) {
  const groups = new Map();
  for (const row of filteredItems) {
    const metrics = rowMetrics(row);
    if (!metrics) continue;
    const id_dominio = row?.id_dominio ?? "";
    const especialidad = row?.especialidad ?? "";
    const medico = row?.medico ?? "";
    const dia = String(row?.dia ?? "").trim();
    const key = `${id_dominio}\u0001${especialidad}\u0001${medico}\u0001${dia}`;
    const current = groups.get(key) || {
      id_dominio,
      especialidad,
      medico,
      dia,
      horas: 0,
      cantidad_turnos: 0,
      cantidad_sobreturno: 0,
    };
    current.horas += metrics.horas;
    current.cantidad_turnos += metrics.cantidad_turnos;
    current.cantidad_sobreturno += metrics.cantidad_sobreturno;
    groups.set(key, current);
  }
  return Array.from(groups.values()).sort((a, b) => {
    const d = String(a.id_dominio).localeCompare(String(b.id_dominio), "es", { numeric: true });
    if (d) return d;
    const e = String(a.especialidad).localeCompare(String(b.especialidad), "es");
    if (e) return e;
    const m = String(a.medico).localeCompare(String(b.medico), "es");
    if (m) return m;
    return String(a.dia).localeCompare(String(b.dia), "es");
  });
}

export function formatMetric(value, digits = 2) {
  if (!Number.isFinite(value)) return "";
  const rounded = Number(value.toFixed(digits));
  return Number.isInteger(rounded) ? String(rounded) : String(rounded);
}

function asNonNegFinite(value) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) return 0;
  return n;
}

/** Ids de horario remoto (payload `id`) del set filtrado de ocupación. */
export function occupancyHorarioIds(items) {
  const ids = new Set();
  for (const row of items || []) {
    const id = Number(row?.id);
    if (Number.isFinite(id) && id > 0) ids.add(id);
  }
  return ids;
}

/**
 * Filtra filas de ocupación según filtros de Indicadores (en memoria).
 * location: id_dominio + tipo; roomAgendas: Set de id_agenda cuando hay consultorio.
 */
export function filterOccupancyForIndicadores(items, { location, roomAgendaIds, especialidad, medico } = {}) {
  return (items || []).filter((row) => {
    if (location) {
      if (Number(row?.id_dominio) !== Number(location.id_dominio)) return false;
      if (String(row?.tipo ?? "").trim() !== String(location.tipo ?? "").trim()) return false;
    }
    if (roomAgendaIds) {
      const idAgenda = Number(row?.id_agenda);
      if (!Number.isFinite(idAgenda) || !roomAgendaIds.has(idAgenda)) return false;
    }
    if (especialidad) {
      const esp = String(row?.especialidad ?? "").trim();
      const espAg = String(row?.especialidad_agenda ?? "").trim();
      const sel = String(especialidad).trim();
      if (esp !== sel && espAg !== sel) return false;
    }
    if (medico) {
      if (String(row?.medico ?? "").trim() !== String(medico).trim()) return false;
    }
    return true;
  });
}

/**
 * Agrega detalle de turnos-resumen para ids en scope.
 * Contadores = suma; % desde totales; espera ponderada por total_turnos.
 */
export function aggregateTurnosResumen(detalle, horarioIds) {
  const idSet = horarioIds instanceof Set ? horarioIds : new Set(horarioIds || []);
  const rows = (detalle || []).filter((row) => {
    const id = Number(row?.turno_horario_id);
    return Number.isFinite(id) && idSet.has(id);
  });

  let total_turnos = 0;
  let turnos_pendientes = 0;
  let turnos_confirmados = 0;
  let turnos_cancelados = 0;
  let turnos_atendidos = 0;
  let turnos_ausentes = 0;
  let esperaWeighted = 0;

  for (const row of rows) {
    const total = asNonNegFinite(row.total_turnos);
    total_turnos += total;
    turnos_pendientes += asNonNegFinite(row.turnos_pendientes);
    turnos_confirmados += asNonNegFinite(row.turnos_confirmados);
    turnos_cancelados += asNonNegFinite(row.turnos_cancelados);
    turnos_atendidos += asNonNegFinite(row.turnos_atendidos);
    turnos_ausentes += asNonNegFinite(row.turnos_ausentes);
    esperaWeighted += asNonNegFinite(row.espera_promedio_dias) * total;
  }

  const pct = (part) => (total_turnos > 0 ? Math.round((part / total_turnos) * 10000) / 100 : 0);

  return {
    matched_rows: rows.length,
    total_turnos,
    turnos_pendientes,
    turnos_confirmados,
    turnos_cancelados,
    turnos_atendidos,
    turnos_ausentes,
    porcentaje_pendientes: pct(turnos_pendientes),
    porcentaje_confirmados: pct(turnos_confirmados),
    porcentaje_cancelados: pct(turnos_cancelados),
    porcentaje_atendidos: pct(turnos_atendidos),
    porcentaje_ausentes: pct(turnos_ausentes),
    espera_promedio_dias:
      total_turnos > 0 ? Math.round((esperaWeighted / total_turnos) * 100) / 100 : 0,
  };
}

/** Primer y último día del mes `YYYY-MM`. */
export function monthDateRange(monthValue) {
  const text = String(monthValue || "").trim();
  const match = /^(\d{4})-(\d{2})$/.exec(text);
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (month < 1 || month > 12) return null;
  const lastDay = new Date(year, month, 0).getDate();
  const mm = String(month).padStart(2, "0");
  return {
    fecha_desde: `${year}-${mm}-01`,
    fecha_hasta: `${year}-${mm}-${String(lastDay).padStart(2, "0")}`,
  };
}
