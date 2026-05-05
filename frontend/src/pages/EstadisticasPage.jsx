import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

const PIE_COLORS = ["#0f766e", "#cbd5e1"];

function todayISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function monthStartISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  return `${y}-${m}-01`;
}

function specialtyTokens(rawSpecialty) {
  if (!rawSpecialty) return [];
  return String(rawSpecialty)
    .split("|")
    .map((token) => token.trim())
    .filter(Boolean);
}

export function EstadisticasPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState([]);
  const [professionals, setProfessionals] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [stats, setStats] = useState(null);

  const [startDate, setStartDate] = useState(monthStartISO);
  const [endDate, setEndDate] = useState(todayISO);
  const [selLocations, setSelLocations] = useState(() => new Set());
  const [selProfessionals, setSelProfessionals] = useState(() => new Set());
  const [selRooms, setSelRooms] = useState(() => new Set());
  const [selSpecialties, setSelSpecialties] = useState(() => new Set());

  const specialtyOptions = useMemo(() => {
    const options = new Set();
    for (const p of professionals) {
      for (const token of specialtyTokens(p.specialty)) {
        options.add(token);
      }
    }
    return [...options].sort((a, b) => a.localeCompare(b, "es"));
  }, [professionals]);

  const selectedSpecialtyNames = useMemo(() => {
    return specialtyOptions.filter((name) => selSpecialties.has(name));
  }, [specialtyOptions, selSpecialties]);

  useEffect(() => {
    const load = async () => {
      setError("");
      await Promise.all([
        safeLoad("/locations", setLocations, setError),
        safeLoad("/professionals", setProfessionals, setError),
        safeLoad("/consulting-rooms", setRooms, setError),
      ]);
    };
    load();
  }, []);

  const buildQuery = useCallback(() => {
    const params = new URLSearchParams();
    params.set("start_date", startDate);
    params.set("end_date", endDate);
    selLocations.forEach((id) => params.append("location_ids", String(id)));
    selProfessionals.forEach((id) => params.append("professional_ids", String(id)));
    selRooms.forEach((id) => params.append("room_ids", String(id)));
    selSpecialties.forEach((name) => params.append("specialty_filters", name));
    return params.toString();
  }, [startDate, endDate, selLocations, selProfessionals, selRooms, selSpecialties]);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiRequestWithRefresh(`/stats/summary?${buildQuery()}`);
      setStats(data);
    } catch (e) {
      setError(e.message);
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, [buildQuery]);

  useEffect(() => {
    fetchStats();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps -- carga inicial; el usuario pulsa Actualizar para refetch con filtros

  const pieData = useMemo(() => {
    if (!stats) return [];
    return [
      { name: "Ocupado (horas)", value: stats.pie_occupied_hours },
      { name: "Libre (horas)", value: stats.pie_free_hours },
    ];
  }, [stats]);

  const barData = useMemo(() => {
    if (!stats) return [];
    return stats.hours_by_weekday.map((row) => ({
      name: row.label,
      horas: row.booked_hours,
    }));
  }, [stats]);

  const toggleSet = (setFn, id) => {
    setFn((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const clearAllFilters = () => {
    setSelLocations(new Set());
    setSelProfessionals(new Set());
    setSelRooms(new Set());
    setSelSpecialties(new Set());
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
        <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Estadísticas</h1>
        <p style={{ color: "#64748b", marginTop: -8 }}>
          Filtrá por ubicación y/o consultorio para delimitar el alcance. El % de ocupación es{" "}
          <strong>horas asignadas semanalmente (proyectadas al período) ÷ horas habilitadas</strong> según los horarios
          de consultorio. Si elegís especialidad, el numerador usa solo esas especialidades (la capacidad habilitada se
          mantiene).
        </p>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "flex-end", marginBottom: 16 }}>
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
            Desde
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
            Hasta
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </label>
          <button type="button" onClick={fetchStats} disabled={loading}>
            {loading ? "Calculando…" : "Actualizar"}
          </button>
          <button
            type="button"
            onClick={clearAllFilters}
            style={{ border: "1px solid #cbd5e1", background: "#fff", borderRadius: 6, padding: "6px 10px", cursor: "pointer" }}
          >
            Limpiar filtros
          </button>
        </div>

        {selectedSpecialtyNames.length > 0 ? (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: 6 }}>
              Especialidades seleccionadas ({selectedSpecialtyNames.length})
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {selectedSpecialtyNames.map((name) => (
                <span
                  key={name}
                  style={{
                    fontSize: "0.78rem",
                    border: "1px solid #99f6e4",
                    background: "#f0fdfa",
                    color: "#115e59",
                    borderRadius: 999,
                    padding: "2px 8px",
                  }}
                >
                  {name}
                </span>
              ))}
            </div>
          </div>
        ) : null}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          <fieldset style={{ margin: 0, border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
            <legend>Ubicaciones</legend>
            <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 160, overflowY: "auto" }}>
              {locations.map((loc) => (
                <label key={loc.id} style={{ display: "flex", gap: 8, alignItems: "center", fontSize: "0.9rem" }}>
                  <input
                    type="checkbox"
                    checked={selLocations.has(loc.id)}
                    onChange={() => toggleSet(setSelLocations, loc.id)}
                  />
                  #{loc.id} {loc.name}
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset style={{ margin: 0, border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
            <legend>Profesionales</legend>
            <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 160, overflowY: "auto" }}>
              {professionals.map((p) => (
                <label key={p.id} style={{ display: "flex", gap: 8, alignItems: "center", fontSize: "0.9rem" }}>
                  <input
                    type="checkbox"
                    checked={selProfessionals.has(p.id)}
                    onChange={() => toggleSet(setSelProfessionals, p.id)}
                  />
                  #{p.id} {p.full_name}
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset style={{ margin: 0, border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
            <legend>Consultorios</legend>
            <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 160, overflowY: "auto" }}>
              {rooms.map((r) => (
                <label key={r.id} style={{ display: "flex", gap: 8, alignItems: "center", fontSize: "0.9rem" }}>
                  <input
                    type="checkbox"
                    checked={selRooms.has(r.id)}
                    onChange={() => toggleSet(setSelRooms, r.id)}
                  />
                  #{r.id} {r.code}
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset style={{ margin: 0, border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
            <legend>Especialidades</legend>
            <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 160, overflowY: "auto" }}>
              {specialtyOptions.map((name) => (
                <label key={name} style={{ display: "flex", gap: 8, alignItems: "center", fontSize: "0.9rem" }}>
                  <input
                    type="checkbox"
                    checked={selSpecialties.has(name)}
                    onChange={() => toggleSet(setSelSpecialties, name)}
                  />
                  {name}
                </label>
              ))}
              {specialtyOptions.length === 0 ? <span style={{ color: "#64748b", fontSize: "0.85rem" }}>Sin especialidades</span> : null}
            </div>
          </fieldset>
        </div>

        {error ? <p style={{ color: "crimson", marginTop: 12 }}>{error}</p> : null}
      </section>

      {stats ? (
        <>
          <section
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
              gap: 12,
            }}
          >
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, background: "#f8fafc" }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                {selSpecialties.size > 0 ? "% Ocupación (especialidad)" : "% Ocupación"}
              </div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stats.occupancy_rate_percent}%</div>
            </div>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, background: "#f8fafc" }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Horas habilitadas</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stats.enabled_hours}</div>
            </div>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, background: "#f8fafc" }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Horas asignadas</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stats.booked_hours}</div>
            </div>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, background: "#f8fafc" }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Ocurrencias</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stats.bookings_count}</div>
            </div>
            {stats.booked_hours_filtered != null ? (
              <>
                <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, background: "#fffbeb" }}>
                  <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Horas (filtro profesional)</div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stats.booked_hours_filtered}</div>
                </div>
                <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, background: "#fffbeb" }}>
                  <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Ocurrencias (filtro profesional)</div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stats.bookings_count_filtered}</div>
                </div>
              </>
            ) : null}
          </section>

          <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 16 }}>
            <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, background: "#fff", minHeight: 320 }}>
              <h2 style={{ fontSize: "1rem", marginTop: 0 }}>Ocupación / disponibilidad (horas)</h2>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={88}>
                    {pieData.map((_, index) => (
                      <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v) => `${Number(v).toFixed(2)} h`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, background: "#fff", minHeight: 320 }}>
              <h2 style={{ fontSize: "1rem", marginTop: 0 }}>Horas reservadas por día de semana</h2>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(v) => `${Number(v).toFixed(2)} h`} />
                  <Bar dataKey="horas" fill="#0f766e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
            <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, background: "#fff" }}>
              <h2 style={{ fontSize: "1rem", marginTop: 0 }}>Top consultorios (horas)</h2>
              <ul style={{ paddingLeft: 18, margin: 0 }}>
                {stats.top_rooms.map((row) => (
                  <li key={row.room_id}>
                    {row.room_code}: <strong>{row.booked_hours}</strong> h
                  </li>
                ))}
                {stats.top_rooms.length === 0 ? <li>Sin datos</li> : null}
              </ul>
            </div>
            <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, background: "#fff" }}>
              <h2 style={{ fontSize: "1rem", marginTop: 0 }}>Top profesionales (horas)</h2>
              <ul style={{ paddingLeft: 18, margin: 0 }}>
                {stats.top_professionals.map((row) => (
                  <li key={row.professional_id}>
                    {row.full_name}: <strong>{row.booked_hours}</strong> h
                  </li>
                ))}
                {stats.top_professionals.length === 0 ? <li>Sin datos</li> : null}
              </ul>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
