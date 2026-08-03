import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.novedades import TieneProduccionResponse


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def parse_tiene_produccion_payload(payload) -> bool:
    if isinstance(payload, bool):
        return payload
    if isinstance(payload, (int, float)) and payload in (0, 1):
        return bool(payload)
    if isinstance(payload, str):
        s = payload.strip().lower()
        if s in ("true", "1", "yes", "si", "sí"):
            return True
        if s in ("false", "0", "no"):
            return False
    if isinstance(payload, dict):
        for key in ("tiene_produccion", "tieneProduccion", "result", "data", "value"):
            if key in payload:
                return parse_tiene_produccion_payload(payload[key])
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de tiene-produccion no reconocida",
    )


def check_tiene_produccion(*, fecha: str, codprof: str) -> TieneProduccionResponse:
    fecha_s = _as_str(fecha)
    codprof_s = _as_str(codprof)
    if not fecha_s or not codprof_s:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fecha y codprof son obligatorios",
        )

    url = (settings.novedades_bonos_tiene_produccion_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url or not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verificación de producción no configurada (URL/TOKEN)",
        )

    try:
        with httpx.Client(timeout=settings.novedades_bonos_tiene_produccion_timeout) as client:
            response = client.get(
                url,
                params={"fecha": fecha_s, "codprof": codprof_s},
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            response.raise_for_status()
            # Algunos APIs devuelven JSON boolean puro; otros body texto.
            try:
                payload = response.json()
            except Exception:
                payload = response.text
            tiene = parse_tiene_produccion_payload(payload)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar tiene-produccion: {exc}",
        ) from exc

    return TieneProduccionResponse(tiene_produccion=tiene)
