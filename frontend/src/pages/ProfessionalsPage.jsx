import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

export function ProfessionalsPage() {
  const [error, setError] = useState("");
  const [professionals, setProfessionals] = useState([]);
  const [professionalName, setProfessionalName] = useState("");
  const [professionalLicense, setProfessionalLicense] = useState("");

  const load = async () => {
    setError("");
    await safeLoad("/professionals", setProfessionals, setError);
  };

  useEffect(() => {
    load();
  }, []);

  const submitProfessional = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/professionals", {
      method: "POST",
      body: JSON.stringify({ full_name: professionalName, license_number: professionalLicense || null }),
    });
    setProfessionalName("");
    setProfessionalLicense("");
    await load();
  };

  const removeItem = async (id) => {
    await apiRequestWithRefresh(`/professionals/${id}`, { method: "DELETE" });
    await load();
  };

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Profesionales</h1>
      <p style={{ color: "#64748b" }}>Personas que pueden aparecer en las reservas de la agenda.</p>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <form onSubmit={submitProfessional} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input
          value={professionalName}
          onChange={(event) => setProfessionalName(event.target.value)}
          placeholder="Nombre completo"
          required
          style={{ minWidth: 200 }}
        />
        <input
          value={professionalLicense}
          onChange={(event) => setProfessionalLicense(event.target.value)}
          placeholder="Matrícula"
          style={{ minWidth: 140 }}
        />
        <button type="submit">Agregar</button>
      </form>
      <ul style={{ paddingLeft: 20 }}>
        {professionals.map((item) => (
          <li key={item.id} style={{ marginBottom: 8 }}>
            #{item.id} - {item.full_name} ({item.license_number || "sin matrícula"}){" "}
            <button type="button" onClick={() => removeItem(item.id)}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
