import { useEffect, useState } from "react";

import { useAuth } from "../auth/AuthContext";
import { apiRequestWithRefresh } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

const WEEKDAYS = [
  { value: 0, label: "Lunes" },
  { value: 1, label: "Martes" },
  { value: 2, label: "Miércoles" },
  { value: 3, label: "Jueves" },
  { value: 4, label: "Viernes" },
  { value: 5, label: "Sábado" },
  { value: 6, label: "Domingo" },
];

function formatBytes(bytes) {
  if (bytes === null || bytes === undefined || bytes === 0) return "—";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleString("es-AR", { dateStyle: "short", timeStyle: "medium" });
  } catch {
    return String(dateStr);
  }
}

export function SettingsBackupPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [runningManual, setRunningManual] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [statusInfo, setStatusInfo] = useState(null);
  const [logs, setLogs] = useState([]);

  const [enabled, setEnabled] = useState(false);
  const [scheduleType, setScheduleType] = useState("daily");
  const [scheduleTime, setScheduleTime] = useState("03:00");
  const [scheduleDayOfWeek, setScheduleDayOfWeek] = useState(0);
  const [s3EndpointUrl, setS3EndpointUrl] = useState("");
  const [s3BucketName, setS3BucketName] = useState("");
  const [s3RegionName, setS3RegionName] = useState("auto");
  const [s3AccessKeyId, setS3AccessKeyId] = useState("");
  const [s3SecretAccessKey, setS3SecretAccessKey] = useState("");
  const [hasSecret, setHasSecret] = useState(false);
  const [s3Prefix, setS3Prefix] = useState("clinica-backups/");
  const [retentionCount, setRetentionCount] = useState(15);

  const loadData = async () => {
    setError("");
    try {
      const [cfg, stat, logList] = await Promise.all([
        apiRequestWithRefresh("/backups/config"),
        apiRequestWithRefresh("/backups/status"),
        apiRequestWithRefresh("/backups/logs?limit=50"),
      ]);
      setEnabled(Boolean(cfg.enabled));
      setScheduleType(cfg.schedule_type || "daily");
      setScheduleTime(cfg.schedule_time || "03:00");
      setScheduleDayOfWeek(cfg.schedule_day_of_week ?? 0);
      setS3EndpointUrl(cfg.s3_endpoint_url || "");
      setS3BucketName(cfg.s3_bucket_name || "");
      setS3RegionName(cfg.s3_region_name || "auto");
      setS3AccessKeyId(cfg.s3_access_key_id || "");
      setS3SecretAccessKey("");
      setHasSecret(Boolean(cfg.has_secret_access_key));
      setS3Prefix(cfg.s3_prefix || "clinica-backups/");
      setRetentionCount(cfg.retention_count || 15);
      setStatusInfo(stat);
      setLogs(Array.isArray(logList) ? logList : []);
    } catch (err) {
      setError(err.message || "No se pudo cargar la configuración de backups");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const body = {
        enabled,
        schedule_type: scheduleType,
        schedule_time: scheduleTime,
        schedule_day_of_week: scheduleType === "weekly" ? Number(scheduleDayOfWeek) : null,
        s3_endpoint_url: s3EndpointUrl.trim() || null,
        s3_bucket_name: s3BucketName.trim(),
        s3_region_name: s3RegionName.trim() || "auto",
        s3_access_key_id: s3AccessKeyId.trim(),
        s3_prefix: s3Prefix.trim() || "clinica-backups/",
        retention_count: Number(retentionCount) || 15,
      };
      if (s3SecretAccessKey.trim()) {
        body.s3_secret_access_key = s3SecretAccessKey.trim();
      }
      const updated = await apiRequestWithRefresh("/backups/config", {
        method: "PUT",
        body: JSON.stringify(body),
      });
      setHasSecret(Boolean(updated.has_secret_access_key));
      setS3SecretAccessKey("");
      setNotice("Configuración guardada.");
      const stat = await apiRequestWithRefresh("/backups/status");
      setStatusInfo(stat);
    } catch (err) {
      setError(err.message || "No se pudo guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleTriggerManual = async () => {
    if (runningManual) return;
    setRunningManual(true);
    setError("");
    setNotice("");
    try {
      const res = await apiRequestWithRefresh("/backups/run", { method: "POST" });
      if (res.success) setNotice(res.message);
      else setError(res.message || "Backup falló");
      const [stat, logList] = await Promise.all([
        apiRequestWithRefresh("/backups/status"),
        apiRequestWithRefresh("/backups/logs?limit=50"),
      ]);
      setStatusInfo(stat);
      setLogs(Array.isArray(logList) ? logList : []);
    } catch (err) {
      setError(err.message || "Error al ejecutar backup");
    } finally {
      setRunningManual(false);
    }
  };

  if (user?.role !== "admin") {
    return <p style={{ color: uiTheme.colors.danger }}>Solo administradores.</p>;
  }

  if (loading) {
    return <p style={{ color: uiTheme.colors.textMuted }}>Cargando configuración…</p>;
  }

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.35rem" }}>Configuración</h1>
          <p style={{ margin: "6px 0 0", color: uiTheme.colors.textMuted, fontSize: 14 }}>
            Backups de base de datos hacia almacenamiento S3-compatible.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" onClick={loadData} style={uiStyles.buttonSecondary}>
            Actualizar
          </button>
          <button
            type="button"
            onClick={handleTriggerManual}
            style={uiStyles.buttonPrimary}
            disabled={runningManual || statusInfo?.is_running}
          >
            {runningManual || statusInfo?.is_running ? "Generando backup…" : "Realizar backup ahora"}
          </button>
        </div>
      </div>

      {notice ? <div style={{ ...uiStyles.kpiCard, color: uiTheme.colors.success || "#0f766e" }}>{notice}</div> : null}
      {error ? <div style={{ ...uiStyles.kpiCard, borderColor: "#fca5a5", color: "#b91c1c" }}>{error}</div> : null}

      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Scheduler</div>
          <div style={{ fontWeight: 600 }}>{enabled ? "Habilitado" : "Deshabilitado"}</div>
        </div>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Próxima ejecución</div>
          <div style={{ fontWeight: 600 }}>{formatDate(statusInfo?.next_run_at)}</div>
        </div>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Último backup</div>
          <div style={{ fontWeight: 600 }}>
            {statusInfo?.last_log ? `${statusInfo.last_log.status} · ${formatDate(statusInfo.last_log.started_at)}` : "—"}
          </div>
        </div>
      </div>

      <form onSubmit={handleSave} style={{ ...uiStyles.kpiCard, display: "grid", gap: 14 }}>
        <h2 style={{ margin: 0, fontSize: "1.05rem" }}>Programación y S3</h2>
        <label style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
          <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} disabled={saving} />
          Habilitar backups programados
        </label>
        <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Frecuencia</span>
            <select value={scheduleType} onChange={(e) => setScheduleType(e.target.value)} style={uiStyles.formControl} disabled={saving}>
              <option value="daily">Diario</option>
              <option value="weekly">Semanal</option>
            </select>
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Hora (HH:MM)</span>
            <input value={scheduleTime} onChange={(e) => setScheduleTime(e.target.value)} style={uiStyles.formControl} disabled={saving} />
          </label>
          {scheduleType === "weekly" ? (
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Día</span>
              <select
                value={scheduleDayOfWeek}
                onChange={(e) => setScheduleDayOfWeek(Number(e.target.value))}
                style={uiStyles.formControl}
                disabled={saving}
              >
                {WEEKDAYS.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Retención (cantidad)</span>
            <input
              type="number"
              min={1}
              max={365}
              value={retentionCount}
              onChange={(e) => setRetentionCount(e.target.value)}
              style={uiStyles.formControl}
              disabled={saving}
            />
          </label>
        </div>

        <label style={{ display: "grid", gap: 4 }}>
          <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Endpoint S3 (R2/MinIO; vacío = AWS)</span>
          <input value={s3EndpointUrl} onChange={(e) => setS3EndpointUrl(e.target.value)} style={uiStyles.formControl} disabled={saving} />
        </label>
        <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Bucket</span>
            <input value={s3BucketName} onChange={(e) => setS3BucketName(e.target.value)} style={uiStyles.formControl} disabled={saving} required />
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Region</span>
            <input value={s3RegionName} onChange={(e) => setS3RegionName(e.target.value)} style={uiStyles.formControl} disabled={saving} />
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Prefix</span>
            <input value={s3Prefix} onChange={(e) => setS3Prefix(e.target.value)} style={uiStyles.formControl} disabled={saving} />
          </label>
        </div>
        <label style={{ display: "grid", gap: 4 }}>
          <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Access Key ID</span>
          <input value={s3AccessKeyId} onChange={(e) => setS3AccessKeyId(e.target.value)} style={uiStyles.formControl} disabled={saving} autoComplete="off" />
        </label>
        <label style={{ display: "grid", gap: 4 }}>
          <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>
            Secret Access Key {hasSecret ? "(guardado; dejar vacío para no cambiar)" : ""}
          </span>
          <input
            type="password"
            value={s3SecretAccessKey}
            onChange={(e) => setS3SecretAccessKey(e.target.value)}
            style={uiStyles.formControl}
            disabled={saving}
            autoComplete="new-password"
            placeholder={hasSecret ? "••••••••" : ""}
          />
        </label>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button type="submit" style={uiStyles.buttonPrimary} disabled={saving}>
            {saving ? "Guardando…" : "Guardar"}
          </button>
        </div>
      </form>

      <div style={uiStyles.kpiCard}>
        <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Historial</h2>
        {!logs.length ? (
          <p style={{ color: uiTheme.colors.textMuted, margin: 0 }}>Sin ejecuciones aún.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
              <thead>
                <tr style={{ textAlign: "left", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                  <th style={{ padding: "8px 6px" }}>Inicio</th>
                  <th style={{ padding: "8px 6px" }}>Trigger</th>
                  <th style={{ padding: "8px 6px" }}>Estado</th>
                  <th style={{ padding: "8px 6px" }}>Archivo</th>
                  <th style={{ padding: "8px 6px" }}>Tamaño</th>
                  <th style={{ padding: "8px 6px" }}>Duración</th>
                  <th style={{ padding: "8px 6px" }}>Error</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                    <td style={{ padding: "8px 6px" }}>{formatDate(log.started_at)}</td>
                    <td style={{ padding: "8px 6px" }}>{log.trigger_type}</td>
                    <td style={{ padding: "8px 6px" }}>{log.status}</td>
                    <td style={{ padding: "8px 6px" }}>{log.file_name}</td>
                    <td style={{ padding: "8px 6px" }}>{formatBytes(log.file_size_bytes)}</td>
                    <td style={{ padding: "8px 6px" }}>{log.duration_seconds != null ? `${log.duration_seconds}s` : "—"}</td>
                    <td style={{ padding: "8px 6px", maxWidth: 220 }}>{log.error_message || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
