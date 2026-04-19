"""System router endpoints (health, info, metrics, debug)."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import uuid

from src.api.error_handling import log_and_raise_http_exception
from src.infrastructure.database import get_db
from src.utils.constants import ENDPOINT_HEALTH

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
    """Endpoint de health check basico - verifica que el servidor esta corriendo.
    
    Para health checks avanzados usar /api/health/detailed o /api/health/ready.
    """
    from datetime import datetime
    
    return {
        "status": "ok",
        "message": "Server is running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/api/info")
async def get_info_v2(db: Session = Depends(get_db)):
    """Informacion general del sistema (endpoint v2 - expandido)."""
    try:
        from src.domain.ui_service import UIService
        
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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error getting information",
            error=e,
        )


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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error generating Prometheus metrics",
            error=e,
        )


@router.get("/api/health/detailed")
async def get_detailed_health(db: Session = Depends(get_db)):
    """Detailed health check with extended diagnostics."""
    try:
        if not health_checker:
            raise RuntimeError("Health checker not initialized")

        result = health_checker.run_all_checks()
        status_str = "healthy" if result.get("status") == "healthy" else "unhealthy"
        return {
            "status": status_str,
            "timestamp": result.get("timestamp"),
            "checks": result.get("checks", {}),
            "system_info": result.get("system_info", {}),
        }

    except Exception as e:
        log_and_raise_http_exception(
            logger=logger,
            status_code=503,
            log_message="Error in detailed health check",
            error=e,
        )


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

        result = health_checker.run_all_checks()
        if result.get("status") == "healthy":
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")

    except Exception as e:
        log_and_raise_http_exception(
            logger=logger,
            status_code=503,
            log_message="Error in readiness probe",
            error=e,
        )

