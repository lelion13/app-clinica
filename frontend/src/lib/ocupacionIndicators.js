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
 * Contadores = suma; Total turnos excluye cancelados; espera ponderada por total API.
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
  let rawTotal = 0;

  for (const row of rows) {
    const total = asNonNegFinite(row.total_turnos);
    rawTotal += total;
    for (const key of Object.keys(sums)) {
      if (key === "total_turnos") continue;
      sums[key] += asNonNegFinite(row[key]);
    }
    esperaWeighted += asNonNegFinite(row.espera_promedio_dias) * total;
  }

  // Total visible: sin cancelados.
  sums.total_turnos = Math.max(0, rawTotal - sums.cancelados);

  const pctOfActive = (part) =>
    sums.total_turnos > 0 ? Math.round((part / sums.total_turnos) * 10000) / 100 : 0;
  const pctOfRaw = (part) => (rawTotal > 0 ? Math.round((part / rawTotal) * 10000) / 100 : 0);
  const pctOfCancel = (part) =>
    sums.cancelados > 0 ? Math.round((part / sums.cancelados) * 10000) / 100 : 0;

  return {
    matched_rows: rows.length,
    ...sums,
    espera_promedio_dias: rawTotal > 0 ? Math.round((esperaWeighted / rawTotal) * 100) / 100 : 0,
    pct_cancelados: pctOfRaw(sums.cancelados),
    pct_ausentismo: pctOfActive(sums.ausentes),
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

/** Python weekday: lunes=0 … domingo=6 (mismo convenio que sync ocupación). */
const DIA_TO_PY_WEEKDAY = {
  lunes: 0,
  martes: 1,
  miercoles: 2,
  miércoles: 2,
  jueves: 3,
  viernes: 4,
  sabado: 5,
  sábado: 5,
  domingo: 6,
};

function normDiaKey(dia) {
  return String(dia ?? "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

export function pyWeekdayFromDia(dia) {
  const key = normDiaKey(dia);
  if (!key) return null;
  return Object.prototype.hasOwnProperty.call(DIA_TO_PY_WEEKDAY, key) ? DIA_TO_PY_WEEKDAY[key] : null;
}

function pyWeekdayFromISO(iso) {
  const text = String(iso || "").slice(0, 10);
  const d = new Date(`${text}T12:00:00`);
  if (Number.isNaN(d.getTime())) return null;
  const js = d.getDay(); // 0=domingo
  return js === 0 ? 6 : js - 1;
}

function parseISODateLocal(iso) {
  const text = String(iso || "").slice(0, 10);
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
  if (!m) return null;
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  return Number.isNaN(d.getTime()) ? null : d;
}

function listISODatesInclusive(fechaDesde, fechaHasta) {
  const start = parseISODateLocal(fechaDesde);
  const end = parseISODateLocal(fechaHasta);
  if (!start || !end || end < start) return [];
  const out = [];
  const cur = new Date(start);
  while (cur <= end) {
    const y = cur.getFullYear();
    const m = String(cur.getMonth() + 1).padStart(2, "0");
    const d = String(cur.getDate()).padStart(2, "0");
    out.push(`${y}-${m}-${d}`);
    cur.setDate(cur.getDate() + 1);
  }
  return out;
}

/** Cupos teóricos de una franja: minutos(franja) / duracion_turno. */
export function rowMaxTurnosPerSession(row) {
  const from = parseTimeToMinutes(row?.hora_desde);
  const to = parseTimeToMinutes(row?.hora_hasta);
  const dur = Number(row?.duracion_turno);
  if (from === null || to === null || !(to > from) || !Number.isFinite(dur) || !(dur > 0)) return 0;
  return Math.floor((to - from) / dur);
}

function rowVigenteOnISO(row, iso) {
  const day = parseISODateLocal(iso);
  if (!day) return false;
  const desde = parseISODateLocal(row?.fecha_desde);
  const hasta = parseISODateLocal(row?.fecha_hasta);
  if (!desde || !hasta) return false;
  return day >= desde && day <= hasta;
}

/**
 * Cantidad máxima de turnos del set de ocupación filtrado en el período.
 * Día: 1 ocurrencia si el weekday del selector coincide y la fila está vigente.
 * Mes: ocurrencias del weekday de la fila dentro del mes ∩ vigencia.
 */
export function computeCantidadTurnosMax(occupancyRows, { period, day, month } = {}) {
  let dates = [];
  if (period === "month") {
    const range = monthDateRange(month);
    if (!range) return 0;
    dates = listISODatesInclusive(range.fecha_desde, range.fecha_hasta);
  } else if (day) {
    dates = [String(day).slice(0, 10)];
  }
  if (!dates.length) return 0;

  let total = 0;
  for (const row of occupancyRows || []) {
    const perSession = rowMaxTurnosPerSession(row);
    if (perSession <= 0) continue;
    const rowWd = pyWeekdayFromDia(row?.dia);
    if (rowWd === null) continue;
    let occurrences = 0;
    for (const iso of dates) {
      if (pyWeekdayFromISO(iso) !== rowWd) continue;
      if (!rowVigenteOnISO(row, iso)) continue;
      occurrences += 1;
    }
    if (occurrences > 0) total += perSession * occurrences;
  }
  return total;
}
