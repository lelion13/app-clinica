import { useEffect, useRef, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const WEEKDAYS = [
  ["0", "Domingo"],
  ["1", "Lunes"],
  ["2", "Martes"],
  ["3", "Miércoles"],
  ["4", "Jueves"],
  ["5", "Viernes"],
  ["6", "Sábado"],
];

const overlayStyle = {
  position: "fixed",
  inset: 0,
  zIndex: 1100,
  background: "rgba(15, 43, 39, 0.45)",
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "center",
  padding: "max(16px, 4vh) 16px",
  overflowY: "auto",
};

const modalStyle = {
  background: "#fff",
  borderRadius: uiTheme.radius.md,
  maxWidth: 520,
  width: "100%",
  marginBottom: 24,
  padding: 22,
  boxShadow: uiTheme.shadow.md,
  border: `1px solid ${uiTheme.colors.border}`,
};

function ModalShell({ title, error, onCancel, onAccept, acceptLabel = "Aceptar", busy, children }) {
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape" && !busy) onCancel?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);

  return (
    <div role="presentation" style={overlayStyle} onClick={() => !busy && onCancel?.()}>
      <div role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()} style={modalStyle}>
        <h2 style={{ marginTop: 0, marginBottom: 12, fontSize: "1.15rem" }}>{title}</h2>
        {error ? <p style={{ color: uiTheme.colors.danger, fontSize: 13 }}>{error}</p> : null}
        <div style={{ marginBottom: 16 }}>{children}</div>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
          <button type="button" style={uiStyles.buttonSecondary} onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
          <button type="button" style={uiStyles.buttonPrimary} onClick={onAccept} disabled={busy}>
            {busy ? "Guardando…" : acceptLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

function AgendaTypeahead({ onSelect, roomId }) {
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
    <div ref={rootRef} style={{ position: "relative", width: "100%" }}>
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
                  onSelect(item, roomId);
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
                {item.current_room_code ? (
                  <span style={{ color: uiTheme.colors.textMuted, fontSize: 12 }}>
                    {" "}
                    (hoy: {item.current_room_code})
                  </span>
                ) : null}
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
  const [filterLocationId, setFilterLocationId] = useState("");
  const [modal, setModal] = useState(null);
  const [activeRoom, setActiveRoom] = useState(null);
  const [modalError, setModalError] = useState("");
  const [busy, setBusy] = useState(false);

  const [formLocationId, setFormLocationId] = useState("");
  const [formCode, setFormCode] = useState("");

  const [agendaDraft, setAgendaDraft] = useState([]);
  const [hoursDraft, setHoursDraft] = useState([]);
  const [hourWeekdays, setHourWeekdays] = useState(["1"]);
  const [hourStart, setHourStart] = useState("08:00");
  const [hourEnd, setHourEnd] = useState("12:00");
  const [editingHourKey, setEditingHourKey] = useState(null);

  const locationName = (id) => locations.find((l) => l.id === id)?.name || id;

  const load = async () => {
    setError("");
    await Promise.all([safeLoad("/locations", setLocations, setError), safeLoad("/consulting-rooms", setRooms, setError)]);
  };

  useEffect(() => {
    load();
  }, []);

  const resetHourForm = () => {
    setHourWeekdays(["1"]);
    setHourStart("08:00");
    setHourEnd("12:00");
    setEditingHourKey(null);
  };

  const resetModalState = () => {
    setModal(null);
    setActiveRoom(null);
    setModalError("");
    setFormLocationId("");
    setFormCode("");
    setAgendaDraft([]);
    setHoursDraft([]);
    resetHourForm();
  };

  const closeModal = () => {
    if (busy) return;
    resetModalState();
  };

  const openAdd = () => {
    setModal("add");
    setActiveRoom(null);
    setModalError("");
    setFormLocationId("");
    setFormCode("");
  };

  const openEdit = (room) => {
    setModal("edit");
    setActiveRoom(room);
    setModalError("");
    setFormLocationId(String(room.location_id));
    setFormCode(room.code || "");
  };

  const openAgendas = async (room) => {
    setModal("agendas");
    setActiveRoom(room);
    setModalError("");
    setBusy(true);
    try {
      const data = await apiRequestWithRefresh(`/consulting-rooms/${room.id}/id-agendas`);
      const items = Array.isArray(data?.items) ? data.items : [];
      setAgendaDraft(items.map((a) => ({ id_agenda: a.id_agenda, label: a.label, confirm_move: false })));
    } catch (err) {
      setAgendaDraft([]);
      setModalError(err.message || "No se pudieron cargar agendas");
    } finally {
      setBusy(false);
    }
  };

  const openHours = async (room) => {
    setModal("hours");
    setActiveRoom(room);
    setModalError("");
    resetHourForm();
    setBusy(true);
    try {
      const data = await apiRequestWithRefresh(`/consulting-rooms/${room.id}/hours`);
      const items = Array.isArray(data) ? data : [];
      setHoursDraft(
        items.map((h, idx) => ({
          key: `h-${h.id ?? idx}`,
          weekday: String(h.weekday),
          start_time: String(h.start_time).slice(0, 5),
          end_time: String(h.end_time).slice(0, 5),
        }))
      );
    } catch (err) {
      setHoursDraft([]);
      setModalError(err.message || "No se pudieron cargar horarios");
    } finally {
      setBusy(false);
    }
  };

  const acceptAddOrEdit = async () => {
    setModalError("");
    if (!formLocationId || !formCode.trim()) {
      setModalError("Ubicación y código son obligatorios");
      return;
    }
    setBusy(true);
    try {
      if (modal === "add") {
        await apiRequestWithRefresh("/consulting-rooms", {
          method: "POST",
          body: JSON.stringify({ location_id: Number(formLocationId), code: formCode.trim() }),
        });
      } else if (modal === "edit" && activeRoom) {
        await apiRequestWithRefresh(`/consulting-rooms/${activeRoom.id}`, {
          method: "PATCH",
          body: JSON.stringify({ location_id: Number(formLocationId), code: formCode.trim() }),
        });
      }
      await load();
      resetModalState();
    } catch (err) {
      setModalError(err.message || "No se pudo guardar");
    } finally {
      setBusy(false);
    }
  };

  const onSelectAgenda = (item, roomId) => {
    setModalError("");
    if (agendaDraft.some((a) => a.id_agenda === item.id_agenda)) return;

    const currentId = item.current_room_id != null ? Number(item.current_room_id) : null;
    if (currentId && currentId === Number(roomId)) {
      setAgendaDraft((prev) => [...prev, { id_agenda: item.id_agenda, label: item.label, confirm_move: false }]);
      return;
    }
    if (currentId && currentId !== Number(roomId)) {
      const code = item.current_room_code || currentId;
      const ok = window.confirm(
        `El id_agenda ${item.id_agenda} ya está en el consultorio ${code}. ¿Moverlo a este consultorio?`
      );
      if (!ok) return;
      setAgendaDraft((prev) => [...prev, { id_agenda: item.id_agenda, label: item.label, confirm_move: true }]);
      return;
    }
    setAgendaDraft((prev) => [...prev, { id_agenda: item.id_agenda, label: item.label, confirm_move: false }]);
  };

  const acceptAgendas = async () => {
    if (!activeRoom) return;
    setModalError("");
    setBusy(true);
    try {
      await apiRequestWithRefresh(`/consulting-rooms/${activeRoom.id}/id-agendas`, {
        method: "PUT",
        body: JSON.stringify({
          items: agendaDraft.map((a) => ({ id_agenda: a.id_agenda, confirm_move: Boolean(a.confirm_move) })),
        }),
      });
      resetModalState();
    } catch (err) {
      setModalError(err.message || "No se pudieron guardar las agendas");
    } finally {
      setBusy(false);
    }
  };

  const toggleHourWeekday = (value) => {
    setHourWeekdays((prev) => {
      if (editingHourKey) return [value];
      if (prev.includes(value)) {
        return prev.filter((d) => d !== value);
      }
      return [...prev, value].sort((a, b) => Number(a) - Number(b));
    });
  };

  const startEditHour = (hour) => {
    setModalError("");
    setEditingHourKey(hour.key);
    setHourWeekdays([String(hour.weekday)]);
    setHourStart(hour.start_time);
    setHourEnd(hour.end_time);
  };

  const cancelEditHour = () => {
    setModalError("");
    resetHourForm();
  };

  const saveHourDraft = () => {
    setModalError("");
    if (!hourStart || !hourEnd || hourStart >= hourEnd) {
      setModalError("Rango horario inválido");
      return;
    }
    if (hourWeekdays.length === 0) {
      setModalError("Seleccioná al menos un día");
      return;
    }

    if (editingHourKey) {
      const weekday = hourWeekdays[0];
      setHoursDraft((prev) =>
        prev.map((h) =>
          h.key === editingHourKey
            ? { ...h, weekday, start_time: hourStart, end_time: hourEnd }
            : h
        )
      );
      resetHourForm();
      return;
    }

    const stamp = Date.now();
    setHoursDraft((prev) => [
      ...prev,
      ...hourWeekdays.map((weekday, idx) => ({
        key: `new-${stamp}-${idx}`,
        weekday,
        start_time: hourStart,
        end_time: hourEnd,
      })),
    ]);
    resetHourForm();
  };

  const acceptHours = async () => {
    if (!activeRoom) return;
    setModalError("");
    setBusy(true);
    try {
      await apiRequestWithRefresh(`/consulting-rooms/${activeRoom.id}/hours`, {
        method: "PUT",
        body: JSON.stringify({
          items: hoursDraft.map((h) => ({
            weekday: Number(h.weekday),
            start_time: h.start_time,
            end_time: h.end_time,
          })),
        }),
      });
      resetModalState();
    } catch (err) {
      setModalError(err.message || "No se pudieron guardar los horarios");
    } finally {
      setBusy(false);
    }
  };

  const removeRoom = async (room) => {
    const ok = window.confirm(`¿Eliminar el consultorio ${room.code}?`);
    if (!ok) return;
    setError("");
    try {
      await apiRequestWithRefresh(`/consulting-rooms/${room.id}`, { method: "DELETE" });
      if (activeRoom?.id === room.id) closeModal();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo eliminar");
    }
  };

  const filteredRooms = rooms.filter((r) => !filterLocationId || String(r.location_id) === filterLocationId);
  const weekdayLabel = (n) => WEEKDAYS.find(([v]) => v === String(n))?.[1] ?? n;

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Consultorios</h1>
      <p style={uiStyles.helpText}>
        Salas por ubicación. Editá datos, asociá agendas y definí horarios desde cada fila.
      </p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

      <div
        style={{
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
          marginBottom: 16,
          alignItems: "flex-end",
        }}
      >
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem", minWidth: 200 }}>
          Filtrar por ubicación
          <select
            value={filterLocationId}
            onChange={(e) => setFilterLocationId(e.target.value)}
            style={uiStyles.formControl}
          >
            <option value="">Todas</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" style={uiStyles.buttonPrimary} onClick={openAdd}>
          Agregar
        </button>
      </div>

      <div style={{ overflowX: "auto", border: `1px solid ${uiTheme.colors.border}`, borderRadius: uiTheme.radius.md }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ background: uiTheme.colors.primarySoft || "#f3f6f5", textAlign: "left" }}>
              <th style={{ padding: "10px 12px" }}>Ubicación</th>
              <th style={{ padding: "10px 12px" }}>Nombre</th>
              <th style={{ padding: "10px 12px" }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredRooms.length === 0 ? (
              <tr>
                <td colSpan={3} style={{ padding: 16, color: uiTheme.colors.textMuted }}>
                  No hay consultorios para mostrar.
                </td>
              </tr>
            ) : (
              filteredRooms.map((room) => (
                <tr key={room.id} style={{ borderTop: `1px solid ${uiTheme.colors.border}` }}>
                  <td style={{ padding: "10px 12px" }}>{locationName(room.location_id)}</td>
                  <td style={{ padding: "10px 12px", fontWeight: 600 }}>{room.code}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      <button type="button" style={uiStyles.buttonSecondary} onClick={() => openEdit(room)}>
                        Editar
                      </button>
                      <button type="button" style={uiStyles.buttonSecondary} onClick={() => openAgendas(room)}>
                        Agendas
                      </button>
                      <button type="button" style={uiStyles.buttonSecondary} onClick={() => openHours(room)}>
                        Horarios
                      </button>
                      <button type="button" style={uiStyles.buttonDanger} onClick={() => removeRoom(room)}>
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {(modal === "add" || modal === "edit") && (
        <ModalShell
          title={modal === "add" ? "Agregar consultorio" : `Editar ${activeRoom?.code || ""}`}
          error={modalError}
          onCancel={closeModal}
          onAccept={acceptAddOrEdit}
          busy={busy}
        >
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem", marginBottom: 10 }}>
            Ubicación
            <select
              value={formLocationId}
              onChange={(e) => setFormLocationId(e.target.value)}
              required
              style={uiStyles.formControl}
            >
              <option value="">Elegir…</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
            Código
            <input
              value={formCode}
              onChange={(e) => setFormCode(e.target.value)}
              placeholder="Código"
              required
              style={uiStyles.formControl}
            />
          </label>
        </ModalShell>
      )}

      {modal === "agendas" && activeRoom && (
        <ModalShell
          title={`Agendas — ${activeRoom.code}`}
          error={modalError}
          onCancel={closeModal}
          onAccept={acceptAgendas}
          busy={busy}
        >
          <p style={{ margin: "0 0 10px", fontSize: 13, color: uiTheme.colors.textMuted }}>
            Buscá el médico, asociá o quitá agendas. Los cambios se guardan al Aceptar.
          </p>
          <AgendaTypeahead onSelect={onSelectAgenda} roomId={activeRoom.id} />
          <ul style={{ listStyle: "none", margin: "12px 0 0", padding: 0 }}>
            {agendaDraft.length === 0 ? (
              <li style={{ color: uiTheme.colors.textMuted, fontSize: 13 }}>Sin agendas en el borrador.</li>
            ) : (
              agendaDraft.map((a) => (
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
                  <span>
                    {a.label}
                    {a.confirm_move ? (
                      <span style={{ color: uiTheme.colors.textMuted }}> (mover)</span>
                    ) : null}
                  </span>
                  <button
                    type="button"
                    style={uiStyles.buttonSecondary}
                    onClick={() => setAgendaDraft((prev) => prev.filter((x) => x.id_agenda !== a.id_agenda))}
                  >
                    Quitar
                  </button>
                </li>
              ))
            )}
          </ul>
        </ModalShell>
      )}

      {modal === "hours" && activeRoom && (
        <ModalShell
          title={`Horarios — ${activeRoom.code}`}
          error={modalError}
          onCancel={closeModal}
          onAccept={acceptHours}
          busy={busy}
        >
          <p style={{ margin: "0 0 10px", fontSize: 13, color: uiTheme.colors.textMuted }}>
            {editingHourKey
              ? "Modificá día y horario de la franja. Guardá la franja y luego Aceptar para persistir."
              : "Elegí uno o más días y la misma franja horaria. Los cambios se guardan al Aceptar."}
          </p>
          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: "0.85rem", marginBottom: 6 }}>
              {editingHourKey ? "Día" : "Días"}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 12px" }}>
              {WEEKDAYS.map(([value, label]) => {
                const checked = hourWeekdays.includes(value);
                return (
                  <label
                    key={value}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 4,
                      fontSize: 13,
                      cursor: "pointer",
                      fontWeight: checked ? 600 : 400,
                    }}
                  >
                    <input
                      type={editingHourKey ? "radio" : "checkbox"}
                      name={editingHourKey ? "edit-weekday" : undefined}
                      checked={checked}
                      onChange={() => toggleHourWeekday(value)}
                    />
                    {label}
                  </label>
                );
              })}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-end", marginBottom: 12 }}>
            <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
              Desde
              <input
                type="time"
                value={hourStart}
                onChange={(e) => setHourStart(e.target.value)}
                style={uiStyles.formControl}
              />
            </label>
            <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
              Hasta
              <input type="time" value={hourEnd} onChange={(e) => setHourEnd(e.target.value)} style={uiStyles.formControl} />
            </label>
            <button type="button" style={uiStyles.buttonSecondary} onClick={saveHourDraft}>
              {editingHourKey ? "Guardar franja" : "Agregar franja"}
            </button>
            {editingHourKey ? (
              <button type="button" style={uiStyles.buttonSecondary} onClick={cancelEditHour}>
                Cancelar edición
              </button>
            ) : null}
          </div>
          <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
            {hoursDraft.length === 0 ? (
              <li style={{ color: uiTheme.colors.textMuted, fontSize: 13 }}>Sin franjas en el borrador.</li>
            ) : (
              hoursDraft.map((h) => (
                <li
                  key={h.key}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 8,
                    padding: "8px 0",
                    borderBottom: `1px solid ${uiTheme.colors.border}`,
                    fontSize: 13,
                    background: editingHourKey === h.key ? uiTheme.colors.primarySoft || "transparent" : "transparent",
                  }}
                >
                  <span>
                    {weekdayLabel(h.weekday)} — {h.start_time} a {h.end_time}
                  </span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => startEditHour(h)}>
                      Modificar
                    </button>
                    <button
                      type="button"
                      style={uiStyles.buttonDanger}
                      onClick={() => {
                        setHoursDraft((prev) => prev.filter((x) => x.key !== h.key));
                        if (editingHourKey === h.key) resetHourForm();
                      }}
                    >
                      Eliminar
                    </button>
                  </div>
                </li>
              ))
            )}
          </ul>
        </ModalShell>
      )}
    </section>
  );
}
