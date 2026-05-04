import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";

function normalize(s) {
  return String(s || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

function profHaystack(p) {
  return normalize(
    [p.full_name, p.external_document, p.license_number, p.email, String(p.id)].filter(Boolean).join(" ")
  );
}

/** Base visual compartida con `<select>` / `input[type=time]` en la misma fila de formulario. */
export const alignedNativeFormControlStyle = {
  boxSizing: "border-box",
  minHeight: 36,
  padding: "6px 8px",
  border: "1px solid #cbd5e1",
  borderRadius: 6,
  fontSize: 14,
  lineHeight: 1.25,
  backgroundColor: "#fff",
  color: "#0f172a",
};

export function formatProfessionalLabel(p) {
  if (!p) return "";
  const doc = p.external_document ? ` · DNI ${p.external_document}` : "";
  return `#${p.id} · ${p.full_name}${doc}`;
}

/**
 * Búsqueda tipo combobox sin dependencias extra.
 * @param {object} props
 * @param {Array} props.professionals
 * @param {string} props.value - id como string o ""
 * @param {(id: string) => void} props.onChange
 * @param {string} props.label
 * @param {string} [props.placeholder]
 * @param {boolean} [props.showAllEntry] - fila inicial "Todos" (value "")
 * @param {string} [props.allEntryLabel]
 * @param {boolean} [props.required] - validación visual solamente; el submit debe chequear igual
 */
export function ProfessionalCombobox({
  professionals,
  value,
  onChange,
  label,
  placeholder = "Escribí nombre, DNI, matrícula o #id…",
  showAllEntry = false,
  allEntryLabel = "Todos los profesionales",
  required = false,
}) {
  const listId = useId();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);
  const wrapRef = useRef(null);
  const blurTimer = useRef(null);

  const selected = useMemo(() => professionals.find((p) => String(p.id) === String(value)), [professionals, value]);

  useEffect(() => {
    if (showAllEntry && value === "") {
      setQuery("");
      return;
    }
    if (selected) {
      setQuery(formatProfessionalLabel(selected));
    } else if (!value) {
      setQuery("");
    }
  }, [value, selected, showAllEntry]);

  const filtered = useMemo(() => {
    const q = normalize(query.trim());
    let list = professionals;
    if (q) {
      list = professionals.filter((p) => profHaystack(p).includes(q));
    } else if (open) {
      list = [...professionals].sort((a, b) => a.full_name.localeCompare(b.full_name, "es")).slice(0, 50);
    } else {
      list = [];
    }
    return list.slice(0, 100);
  }, [professionals, query, open]);

  const options = useMemo(() => {
    const rows = [];
    if (showAllEntry && open) {
      rows.push({ kind: "all", key: "__all__" });
    }
    for (const p of filtered) {
      rows.push({ kind: "prof", key: String(p.id), prof: p });
    }
    return rows;
  }, [showAllEntry, open, filtered]);

  useEffect(() => {
    setHighlight(0);
  }, [query, open, options.length]);

  const pick = useCallback(
    (idStr) => {
      onChange(idStr);
      if (idStr === "") {
        setQuery("");
      } else {
        const p = professionals.find((x) => String(x.id) === idStr);
        setQuery(p ? formatProfessionalLabel(p) : "");
      }
      setOpen(false);
    },
    [onChange, professionals]
  );

  useEffect(() => {
    const onDocClick = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false);
        if (selected) setQuery(formatProfessionalLabel(selected));
        else if (showAllEntry && value === "") setQuery("");
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [selected, showAllEntry, value]);

  const onKeyDown = (e) => {
    if (!open && (e.key === "ArrowDown" || e.key === "Enter")) {
      setOpen(true);
      return;
    }
    if (!open) return;
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
      if (selected) setQuery(formatProfessionalLabel(selected));
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, Math.max(0, options.length - 1)));
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    }
    if (e.key === "Enter" && options.length) {
      e.preventDefault();
      const row = options[highlight];
      if (row?.kind === "all") pick("");
      if (row?.kind === "prof") pick(String(row.prof.id));
    }
  };

  return (
    <label
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 4,
        position: "relative",
        minWidth: 260,
        fontSize: 13,
        color: "#334155",
      }}
    >
      <span style={{ lineHeight: 1.2 }}>
        {label}
        {required ? <span style={{ color: "#b91c1c" }}> *</span> : null}
      </span>
      <div ref={wrapRef} style={{ position: "relative", width: "100%" }}>
        <input
          type="text"
          inputMode="search"
          autoComplete="off"
          placeholder={placeholder}
          value={query}
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          onChange={(e) => {
            const v = e.target.value;
            setQuery(v);
            setOpen(true);
            if (v.trim() === "") {
              onChange("");
              return;
            }
            if (selected && v.trim() !== formatProfessionalLabel(selected).trim()) {
              onChange("");
            }
          }}
          onFocus={() => {
            clearTimeout(blurTimer.current);
            setOpen(true);
          }}
          onBlur={() => {
            blurTimer.current = setTimeout(() => {
              setOpen(false);
              if (selected) setQuery(formatProfessionalLabel(selected));
              else if (showAllEntry && value === "") setQuery("");
            }, 120);
          }}
          onKeyDown={onKeyDown}
          style={{ ...alignedNativeFormControlStyle, width: "100%" }}
        />
        {open && options.length > 0 ? (
          <ul
            id={listId}
            role="listbox"
            style={{
              position: "absolute",
              zIndex: 20,
              left: 0,
              right: 0,
              top: "100%",
              margin: "4px 0 0",
              padding: 0,
              listStyle: "none",
              maxHeight: 280,
              overflowY: "auto",
              background: "#fff",
              border: "1px solid #e2e8f0",
              borderRadius: 8,
              boxShadow: "0 10px 30px rgba(15,23,42,0.12)",
            }}
          >
            {options.map((row, i) => {
              if (row.kind === "all") {
                return (
                  <li key={row.key}>
                    <button
                      type="button"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => pick("")}
                      style={{
                        display: "block",
                        width: "100%",
                        textAlign: "left",
                        padding: "10px 12px",
                        border: "none",
                        background: i === highlight ? "#e0f2f1" : "#f8fafc",
                        cursor: "pointer",
                        fontWeight: 600,
                        fontSize: "0.85rem",
                      }}
                    >
                      {allEntryLabel}
                    </button>
                  </li>
                );
              }
              const p = row.prof;
              const active = i === highlight;
              return (
                <li key={row.key}>
                  <button
                    type="button"
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => pick(String(p.id))}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 12px",
                      border: "none",
                      borderTop: "1px solid #f1f5f9",
                      background: active ? "#e0f2f1" : "#fff",
                      cursor: "pointer",
                      fontSize: "0.85rem",
                    }}
                  >
                    {formatProfessionalLabel(p)}
                  </button>
                </li>
              );
            })}
          </ul>
        ) : null}
      </div>
      {open && query.trim() && filtered.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>Sin coincidencias</div>
      ) : null}
    </label>
  );
}
