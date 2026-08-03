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

/** Null si horas inválidas o duracion_turno ≤ 0 (Q19=A). */
export function rowMetrics(row) {
  const from = parseTimeToMinutes(row?.hora_desde);
  const to = parseTimeToMinutes(row?.hora_hasta);
  const duracion = Number(row?.duracion_turno);
  if (from === null || to === null || !(to > from)) return null;
  if (!Number.isFinite(duracion) || duracion <= 0) return null;
  const diffMinutes = to - from;
  return {
    horas: diffMinutes / 60,
    cantidad_turnos: diffMinutes / duracion,
  };
}

export function buildIndicators(filteredItems) {
  const groups = new Map();
  for (const row of filteredItems) {
    const metrics = rowMetrics(row);
    if (!metrics) continue;
    const id_dominio = row?.id_dominio ?? "";
    const especialidad = row?.especialidad ?? "";
    const medico = row?.medico ?? "";
    const dia = row?.dia ?? "";
    const key = `${id_dominio}\u0001${especialidad}\u0001${medico}\u0001${dia}`;
    const current = groups.get(key) || {
      id_dominio,
      especialidad,
      medico,
      dia,
      horas: 0,
      cantidad_turnos: 0,
    };
    current.horas += metrics.horas;
    current.cantidad_turnos += metrics.cantidad_turnos;
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
