import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

export function ProfessionalsPage() {
  const [error, setError] = useState("");
  const [professionals, setProfessionals] = useState([]);
  const [includeInactive, setIncludeInactive] = useState(false);
  const [syncSummary, setSyncSummary] = useState(null);
  const [syncing, setSyncing] = useState(false);

  const load = async () => {
    setError("");
    const query = includeInactive ? "?include_inactive=true" : "";
    await safeLoad(`/professionals${query}`, setProfessionals, setError);
  };

  useEffect(() => {
    load();
  }, [includeInactive]); // eslint-disable-line react-hooks/exhaustive-deps

  const runSync = async () => {
    setError("");
    setSyncing(true);
    try {
      const summary = await apiRequestWithRefresh("/professionals/sync", { method: "POST" });
      setSyncSummary(summary);
      await load();
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setSyncing(false);
    }
  };

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Profesionales</h1>
      <p style={{ color: "#64748b" }}>
        Catálogo sincronizado desde sistema externo (solo lectura local). Los inactivos no se pueden usar en nuevas
        asignaciones o reservas.
      </p>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16, alignItems: "center" }}>
        <button type="button" onClick={runSync} disabled={syncing}>
          {syncing ? "Sincronizando..." : "Sincronizar ahora"}
        </button>
        <label style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(event) => setIncludeInactive(event.target.checked)}
          />
          Ver inactivos
        </label>
      </div>
      {syncSummary ? (
        <div style={{ marginBottom: 12, background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}>
          <strong>Última sincronización:</strong> {new Date(syncSummary.synced_at).toLocaleString()} <br />
          Creados: {syncSummary.created} · Actualizados: {syncSummary.updated} · Inactivados: {syncSummary.inactivated} ·
          Omitidos: {syncSummary.skipped}
          {syncSummary.errors?.length ? (
            <div style={{ marginTop: 6, color: "#b91c1c" }}>Errores: {syncSummary.errors.join(" | ")}</div>
          ) : null}
        </div>
      ) : null}
      <ul style={{ paddingLeft: 20 }}>
        {professionals.map((item) => (
          <li key={item.id} style={{ marginBottom: 8 }}>
            #{item.id} - {item.full_name} ({item.license_number || "sin matrícula"}) · Doc:{" "}
            {item.external_document || "-"} · {item.specialty || "sin especialidad"} ·{" "}
            <strong style={{ color: item.is_active ? "#166534" : "#b91c1c" }}>
              {item.is_active ? "Activo" : "Inactivo"}
            </strong>
          </li>
        ))}
      </ul>
    </section>
  );
}
