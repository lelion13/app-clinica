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
 * Agrega detalle de turnos-resumen (shape API real) para ids en scope.
 * Contadores = suma; % desde totales; espera ponderada por total_turnos.
 * pct_cancel_paciente/otros se recalculan sobre cancelados (no sobre total).
 */
export function aggregateTurnosResumen(detalle, horarioIds) {
  const idSet = horarioIds instanceof Set ? horarioIds : new Set(horarioIds || []);
  const rows = (detalle || []).filter((row) => {
    const id = Number(row?.turno_horario_id);
    return Number.isFinite(id) && idSet.has(id);
  });

  const sums = {
    total_turnos: 0,
    asignados: 0,
    en_espera: 0,
    presentes: 0,
    atendidos: 0,
    ausentes: 0,
    cancelados: 0,
    reserva_telefonico: 0,
    reserva_persona: 0,
    reserva_web: 0,
    reserva_api: 0,
    cancelados_paciente: 0,
    cancelados_otros: 0,
  };
  let esperaWeighted = 0;

  for (const row of rows) {
    const total = asNonNegFinite(row.total_turnos);
    sums.total_turnos += total;
    for (const key of Object.keys(sums)) {
      if (key === "total_turnos") continue;
      sums[key] += asNonNegFinite(row[key]);
    }
    esperaWeighted += asNonNegFinite(row.espera_promedio_dias) * total;
  }

  const pctOfTotal = (part) =>
    sums.total_turnos > 0 ? Math.round((part / sums.total_turnos) * 10000) / 100 : 0;
  const pctOfCancel = (part) =>
    sums.cancelados > 0 ? Math.round((part / sums.cancelados) * 10000) / 100 : 0;

  return {
    matched_rows: rows.length,
    ...sums,
    espera_promedio_dias:
      sums.total_turnos > 0 ? Math.round((esperaWeighted / sums.total_turnos) * 100) / 100 : 0,
    pct_cancelados: pctOfTotal(sums.cancelados),
    pct_ausentismo: pctOfTotal(sums.ausentes),
    pct_cancel_paciente: pctOfCancel(sums.cancelados_paciente),
    pct_cancel_otros: pctOfCancel(sums.cancelados_otros),
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
