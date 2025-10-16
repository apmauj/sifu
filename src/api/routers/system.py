"""System router endpoints (health, info, metrics, debug)."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import uuid
from typing import Optional

from src.infrastructure.database import get_db
from src.utils.constants import ENDPOINT_HEALTH, MSG_LATEST_UI_SUCCESS

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Sistema"])

# Shared instances from main.py
health_checker = None


def set_health_checker(checker):
    """Set the health checker instance."""
    global health_checker
    health_checker = checker


@router.get("/api/debug/correlation")
async def get_correlation_id():
    """Debug endpoint to show current correlation ID."""
    return {"correlation_id": str(uuid.uuid4())}


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint for basic connectivity."""
    return {"status": "ok", "message": "SIFU API is running"}


@router.get(ENDPOINT_HEALTH)
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de health check (verifica conexion BD y status general)."""
    try:
        if not health_checker:
            raise RuntimeError("Health checker not initialized")

        status = health_checker.check_all()
        status_code = 200 if status.is_healthy else 503
        return status.to_dict()

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": None,
            "checks": {"database": {"status": "error", "error": str(e)}},
        }


@router.get("/api/info")
async def get_info_v2(db: Session = Depends(get_db)):
    """Informacion general del sistema (endpoint v2 - expandido)."""
    try:
        from src.domain.services import UIService
        from src.domain.models import HealthResponse
        
        service = UIService(db)
        total_records = service.get_total_records()
        min_date, max_date = service.get_date_range_available()
        latest_ui = service.get_latest_ui()

        return {
            "total_records": total_records,
            "date_range": {
                "min_date": min_date.isoformat() if min_date else None,
                "max_date": max_date.isoformat() if max_date else None,
            },
            "latest_ui": latest_ui.dict() if latest_ui else None,
            "data_source": "National Institute of Statistics (INE) - Uruguay",
        }

    except Exception as e:
        logger.error(f"Error getting information: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/metrics/prometheus")
async def get_prometheus_metrics():
    """Prometheus /metrics endpoint for scraping (OSS OpenTelemetry + Prometheus client)."""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        
        metrics_data = generate_latest()
        return (
            metrics_data.decode("utf-8"),
            200,
            {"Content-Type": CONTENT_TYPE_LATEST},
        )
    except ImportError:
        logger.warning("Prometheus client not available")
        return {"message": "Prometheus metrics not available"}, 503
    except Exception as e:
        logger.error(f"Error generating Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/health/detailed")
async def get_detailed_health(db: Session = Depends(get_db)):
    """Detailed health check with extended diagnostics."""
    try:
        if not health_checker:
            raise RuntimeError("Health checker not initialized")

        status = health_checker.check_all()
        return {
            "status": "healthy" if status.is_healthy else "unhealthy",
            "timestamp": status.timestamp.isoformat() if status.timestamp else None,
            "checks": {
                name: check.to_dict() for name, check in status.checks.items()
            },
        }

    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/health/live")
async def liveness_probe():
    """Kubernetes liveness probe - app is running."""
    return {"status": "alive"}


@router.get("/api/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """Kubernetes readiness probe - app is ready for traffic."""
    try:
        if not health_checker:
            raise RuntimeError("Health checker not initialized")

        status = health_checker.check_all()
        if status.is_healthy:
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")

    except Exception as e:
        logger.error(f"Error in readiness probe: {e}")
        raise HTTPException(status_code=503, detail=str(e))

