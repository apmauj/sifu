"""BROU router endpoints."""

from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["BROU"])

# Shared instances from main.py
brou_cache = None
_cache_lock = None
brou_processor = None


def set_brou_cache_and_lock(cache, lock):
    """Set the BROU cache and lock instances."""
    global brou_cache, _cache_lock
    brou_cache = cache
    _cache_lock = lock


def set_brou_processor(processor):
    """Set the BROU processor instance."""
    global brou_processor
    brou_processor = processor


@router.get("/api/brou/current")
async def get_current_brou_rates(force_refresh: bool = False, full: bool = False):
    """Obtener cotizaciones actuales del BROU.

    Compatibilidad: versión anterior devolvía lista directamente. Ahora por defecto
    seguimos retornando únicamente la lista (para no romper frontend/tests existentes).
    Si se pasa ?full=true se entrega un envoltorio con metadatos.
    """
    try:
        if not _cache_lock:
            raise RuntimeError("Cache not initialized")

        global brou_cache
        with _cache_lock:
            cached = brou_cache
        need_update = False
        if not cached:
            need_update = True
        else:
            age = (
                datetime.utcnow() - cached.get("updated_at", datetime.utcnow())
            ).total_seconds()
            if age > 55 * 60:
                need_update = True
        if force_refresh or need_update:
            from main import _update_brou_cache
            _update_brou_cache()
            with _cache_lock:
                if brou_cache is None:  # mocked case
                    brou_cache = {
                        "data": [],
                        "updated_at": datetime.utcnow(),
                        "source": "BROU_SAMPLE",
                    }
                cached = brou_cache

        data_list = cached["data"] if cached else []
        source = cached.get("source", "BROU") if cached else "UNKNOWN"
        source_type = cached.get("source_type", "unknown") if cached else "unknown"

        if full:
            # Calcular edad de los datos
            data_age = None
            if cached and cached.get("updated_at"):
                data_age = (
                    datetime.utcnow() - cached["updated_at"]
                ).total_seconds() / 60  # en minutos

            # Información de estado para el frontend
            status_info = {
                "live": {
                    "label": "Datos en vivo",
                    "color": "green",
                    "description": "Cotizaciones obtenidas directamente del BROU",
                },
                "persisted": {
                    "label": "Datos históricos",
                    "color": "yellow",
                    "description": "Cotizaciones almacenadas de consultas anteriores",
                },
                "sample": {
                    "label": "Datos de muestra",
                    "color": "red",
                    "description": "Datos de ejemplo - API no disponible",
                },
            }

            current_status = status_info.get(
                source_type,
                {
                    "label": "Estado desconocido",
                    "color": "gray",
                    "description": "No se pudo determinar el estado de los datos",
                },
            )

            return {
                "success": True if data_list else False,
                "message": f"Cotizaciones BROU obtenidas ({len(data_list)} monedas)"
                if data_list
                else "Sin datos BROU",
                "data": data_list,
                "source": source,
                "source_type": source_type,
                "status": current_status,
                "timestamp": cached.get("updated_at").isoformat()
                if cached and cached.get("updated_at")
                else None,
                "data_age_minutes": round(data_age, 1)
                if data_age is not None
                else None,
                "is_fresh": data_age is not None
                and data_age < 60,  # Consideramos frescos datos de menos de 1 hora
                "frontend_display": {
                    "status_label": current_status["label"],
                    "status_color": current_status["color"],
                    "warning_message": current_status["description"]
                    if source_type in ["persisted", "sample"]
                    else None,
                },
            }
        return data_list
    except Exception as e:
        logger.error(f"Error getting current BROU rates: {e}")
        if full:
            return {
                "success": False,
                "message": f"Error interno: {str(e)}",
                "data": None,
            }
        return []
