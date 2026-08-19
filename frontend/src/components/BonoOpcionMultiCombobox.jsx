import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";

import { alignedNativeFormControlStyle } from "./ProfessionalCombobox";
import { uiTheme } from "../ui/theme";

function normalize(s) {
  return String(s || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

/**
 * Multi-select combobox: filtrar por texto y agregar/quitar opciones.
 */
export function BonoOpcionMultiCombobox({
  options,
  selectedIds,
  onChange,
  label = "Opciones de bono",
  placeholder = "Escribí para filtrar (centro, servicio, semana, horario)…",
  disabled = false,
}) {
  const listId = useId();
  const wrapRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);

  const selectedSet = useMemo(() => new Set(selectedIds.map(Number)), [selectedIds]);

  const selectedOptions = useMemo(
    () => options.filter((o) => selectedSet.has(Number(o.id))),
    [options, selectedSet]
  );

  const filtered = useMemo(() => {
    const q = normalize(query.trim());
    let list = options;
    if (q) {
      list = options.filter((o) => normalize(o.label).includes(q));
    }
    return list.slice(0, 100);
  }, [options, query]);

  useEffect(() => {
    setHighlight(0);
  }, [query, open, filtered.length]);

  const toggle = useCallback(
    (id) => {
      const numId = Number(id);
      if (selectedSet.has(numId)) {
        onChange(selectedIds.filter((x) => Number(x) !== numId));
      } else {
        onChange([...selectedIds, numId]);
      }
    },
    [onChange, selectedIds, selectedSet]
  );

  const remove = useCallback(
    (id) => {
      onChange(selectedIds.filter((x) => Number(x) !== Number(id)));
    },
    [onChange, selectedIds]
  );

  useEffect(() => {
    const onDocClick = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const onKeyDown = (e) => {
    if (disabled) return;
    if (!open && (e.key === "ArrowDown" || e.key === "Enter")) {
      setOpen(true);
      return;
    }
    if (!open) return;
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, Math.max(0, filtered.length - 1)));
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    }
    if (e.key === "Enter" && filtered.length) {
      e.preventDefault();
      toggle(filtered[highlight].id);
    }
  };

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <label style={{ display: "grid", gap: 4, position: "relative" }}>
        <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>{label}</span>
        <div ref={wrapRef} style={{ position: "relative" }}>
          <input
            type="text"
            inputMode="search"
            autoComplete="off"
            placeholder={placeholder}
            value={query}
            disabled={disabled}
            aria-expanded={open}
            aria-controls={listId}
            aria-autocomplete="list"
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            onKeyDown={onKeyDown}
            style={{ ...alignedNativeFormControlStyle, width: "100%" }}
          />
          {open && !disabled ? (
            <ul
              id={listId}
              role="listbox"
              aria-multiselectable="true"
              style={{
                position: "absolute",
                zIndex: 20,
                left: 0,
                right: 0,
                top: "100%",
                margin: "4px 0 0",
                padding: 0,
                listStyle: "none",
                maxHeight: 240,
                overflowY: "auto",
                background: "#fff",
                border: `1px solid ${uiTheme.colors.border}`,
                borderRadius: 8,
                boxShadow: "0 10px 30px rgba(15,23,42,0.12)",
              }}
            >
              {filtered.map((o, i) => {
                const picked = selectedSet.has(Number(o.id));
                const active = i === highlight;
                return (
                  <li key={o.id}>
                    <button
                      type="button"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => toggle(o.id)}
                      style={{
                        display: "flex",
                        width: "100%",
                        textAlign: "left",
                        gap: 8,
                        alignItems: "flex-start",
                        padding: "8px 12px",
                        border: "none",
                        borderTop: i === 0 ? "none" : "1px solid #f1f5f9",
                        background: active ? uiTheme.colors.primarySoft : picked ? "#f0fdf4" : "#fff",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                      }}
                    >
                      <span style={{ fontWeight: picked ? 600 : 400, color: picked ? uiTheme.colors.primary : "inherit" }}>
                        {picked ? "✓ " : ""}
                        {o.label}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          ) : null}
        </div>
        {open && query.trim() && filtered.length === 0 ? (
          <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Sin coincidencias</span>
        ) : null}
      </label>

      {selectedOptions.length ? (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {selectedOptions.map((o) => (
            <span
              key={o.id}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "4px 8px",
                borderRadius: uiTheme.radius.pill,
                background: uiTheme.colors.primarySoft,
                fontSize: 12,
                lineHeight: 1.3,
                maxWidth: "100%",
              }}
            >
              <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{o.label}</span>
              {!disabled ? (
                <button
                  type="button"
                  onClick={() => remove(o.id)}
                  aria-label={`Quitar ${o.label}`}
                  style={{
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                    padding: 0,
                    lineHeight: 1,
                    color: uiTheme.colors.textMuted,
                    fontSize: 14,
                  }}
                >
                  ×
                </button>
              ) : null}
            </span>
          ))}
        </div>
      ) : (
        <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>
          {options.length ? "Buscá y elegí una o más opciones con el mismo valor." : "No hay opciones sin tarifa."}
        </span>
      )}
    </div>
  );
}
