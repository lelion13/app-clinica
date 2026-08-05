import { useEffect, useRef, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

function AgendaTypeahead({ onSelect }) {
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const rootRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const onPointerDown = (event) => {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (q.trim().length < 2) {
      setItems([]);
      return undefined;
    }
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await apiRequestWithRefresh(
          `/distribucion/ocupacion/agenda-lookup?q=${encodeURIComponent(q.trim())}`
        );
        setItems(Array.isArray(data?.items) ? data.items : []);
        setOpen(true);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [q]);

  return (
    <div ref={rootRef} style={{ position: "relative", flex: "1 1 240px", minWidth: 200 }}>
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onFocus={() => items.length && setOpen(true)}
        placeholder="Buscar médico…"
        style={{ ...uiStyles.formControl, width: "100%" }}
      />
      {loading ? (
        <div style={{ fontSize: 11, color: uiTheme.colors.textMuted, marginTop: 4 }}>Buscando…</div>
      ) : null}
      {open && items.length > 0 ? (
        <ul
          style={{
            position: "absolute",
            zIndex: 40,
            left: 0,
            right: 0,
            top: "100%",
            margin: 0,
            padding: 0,
            listStyle: "none",
            maxHeight: 220,
            overflowY: "auto",
            background: uiTheme.colors.surface,
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.sm,
            boxShadow: "0 8px 20px rgba(0,0,0,0.12)",
          }}
        >
          {items.map((item) => (
            <li key={item.id_agenda}>
              <button
                type="button"
                onClick={() => {
                  onSelect(item);
                  setQ("");
                  setItems([]);
                  setOpen(false);
                }}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: "8px 10px",
                  border: "none",
                  background: "transparent",
                  cursor: "pointer",
                  fontSize: 13,
                }}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export function ConsultingRoomsPage() {
  const [error, setError] = useState("");
  const [locations, setLocations] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [roomLocationId, setRoomLocationId] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [selectedRoomId, setSelectedRoomId] = useState(null);
  const [agendas, setAgendas] = useState([]);
  const [agendaError, setAgendaError] = useState("");

  const load = async () => {
    setError("");
    await Promise.all([safeLoad("/locations", setLocations, setError), safeLoad("/consulting-rooms", setRooms, setError)]);
  };

  const loadAgendas = async (roomId) => {
    if (!roomId) {
      setAgendas([]);
      return;
    }
    setAgendaError("");
    try {
      const data = await apiRequestWithRefresh(`/consulting-rooms/${roomId}/id-agendas`);
      setAgendas(Array.isArray(data?.items) ? data.items : []);
    } catch (err) {
      setAgendas([]);
      setAgendaError(err.message || "No se pudieron cargar agendas");
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    loadAgendas(selectedRoomId);
  }, [selectedRoomId]);

  const submitRoom = async (event) => {
    event.preventDefault();
    const created = await apiRequestWithRefresh("/consulting-rooms", {
      method: "POST",
      body: JSON.stringify({ location_id: Number(roomLocationId), code: roomCode }),
    });
    setRoomCode("");
    await load();
    if (created?.id) setSelectedRoomId(created.id);
  };

  const removeItem = async (id) => {
    await apiRequestWithRefresh(`/consulting-rooms/${id}`, { method: "DELETE" });
    if (selectedRoomId === id) setSelectedRoomId(null);
    await load();
  };

  const addAgenda = async (item, confirmMove = false) => {
    if (!selectedRoomId) return;
    setAgendaError("");
    try {
      await apiRequestWithRefresh(`/consulting-rooms/${selectedRoomId}/id-agendas`, {
        method: "POST",
        body: JSON.stringify({ id_agenda: item.id_agenda, confirm_move: confirmMove }),
      });
      await loadAgendas(selectedRoomId);
    } catch (err) {
      const detail = err?.detail || err?.body?.detail || null;
      const payload = typeof detail === "object" ? detail : null;
      if (err.status === 409 || payload?.requires_confirm_move) {
        const info = typeof err.detail === "object" && err.detail ? err.detail : payload || {};
        const code = info.current_room_code || info.current_room_id || "?";
        const ok = window.confirm(
          `El id_agenda ${item.id_agenda} ya está en el consultorio ${code}. ¿Moverlo a este consultorio?`
        );
        if (ok) await addAgenda(item, true);
        return;
      }
      setAgendaError(err.message || "No se pudo asociar la agenda");
    }
  };

  const removeAgenda = async (idAgenda) => {
    if (!selectedRoomId) return;
    await apiRequestWithRefresh(`/consulting-rooms/${selectedRoomId}/id-agendas/${idAgenda}`, {
      method: "DELETE",
    });
    await loadAgendas(selectedRoomId);
  };

  const selectedRoom = rooms.find((r) => r.id === selectedRoomId) || null;
  const locationName = (id) => locations.find((l) => l.id === id)?.name || id;

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Consultorios</h1>
      <p style={uiStyles.helpText}>
        Salas vinculadas a una ubicación. Asociá agendas del sync (`id_agenda`) para la grilla de Agenda ocupación.
      </p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      <form onSubmit={submitRoom} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <select value={roomLocationId} onChange={(event) => setRoomLocationId(event.target.value)} required style={uiStyles.formControl}>
          <option value="">Ubicación</option>
          {locations.map((location) => (
            <option key={location.id} value={location.id}>
              #{location.id} - {location.name}
            </option>
          ))}
        </select>
        <input value={roomCode} onChange={(event) => setRoomCode(event.target.value)} placeholder="Código" required style={uiStyles.formControl} />
        <button type="submit" style={uiStyles.buttonPrimary}>Agregar</button>
      </form>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(220px, 1fr) minmax(280px, 1.4fr)", gap: 16 }}>
        <ul style={{ ...uiStyles.listCard, margin: 0 }}>
          {rooms.map((item) => (
            <li
              key={item.id}
              style={{
                padding: "8px 10px",
                borderBottom: `1px solid ${uiTheme.colors.border}`,
                background: selectedRoomId === item.id ? uiTheme.colors.primarySoft : "transparent",
                cursor: "pointer",
              }}
              onClick={() => setSelectedRoomId(item.id)}
            >
              <div style={{ fontWeight: 600 }}>
                #{item.id} — {item.code}
              </div>
              <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>{locationName(item.location_id)}</div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeItem(item.id);
                }}
                style={{ ...uiStyles.buttonDanger, marginTop: 6 }}
              >
                eliminar
              </button>
            </li>
          ))}
        </ul>

        <div
          style={{
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.md,
            padding: 14,
            background: uiTheme.colors.surface,
          }}
        >
          {!selectedRoom ? (
            <p style={{ color: uiTheme.colors.textMuted, margin: 0 }}>Seleccioná un consultorio para mapear agendas.</p>
          ) : (
            <>
              <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>
                {selectedRoom.code}{" "}
                <span style={{ fontWeight: 400, color: uiTheme.colors.textMuted, fontSize: 14 }}>
                  ({locationName(selectedRoom.location_id)})
                </span>
              </h2>
              <p style={{ margin: "0 0 12px", fontSize: 13, color: uiTheme.colors.textMuted }}>
                Escribí el nombre del médico, elegí la agenda; se guarda el <code>id_agenda</code>.
              </p>
              {agendaError ? <p style={{ color: uiTheme.colors.danger }}>{agendaError}</p> : null}
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
                <AgendaTypeahead onSelect={(item) => addAgenda(item, false)} />
              </div>
              <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                {agendas.length === 0 ? (
                  <li style={{ color: uiTheme.colors.textMuted, fontSize: 13 }}>Sin agendas asociadas.</li>
                ) : (
                  agendas.map((a) => (
                    <li
                      key={a.id_agenda}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        gap: 8,
                        padding: "8px 0",
                        borderBottom: `1px solid ${uiTheme.colors.border}`,
                        fontSize: 13,
                      }}
                    >
                      <span>{a.label}</span>
                      <button type="button" style={uiStyles.buttonSecondary} onClick={() => removeAgenda(a.id_agenda)}>
                        Quitar
                      </button>
                    </li>
                  ))
                )}
              </ul>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
