"""
OpenTelemetry instrumentation for SIFU backend.
Includes automatic instrumentation for FastAPI, requests, and SQLAlchemy.
Exports metrics and traces via OTLP exporter.
"""

import os
from typing import Optional

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Logger
import logging

logger = logging.getLogger(__name__)


def is_otel_enabled() -> bool:
    """Check if OpenTelemetry is enabled via environment."""
    return os.getenv("OTEL_ENABLED", "false").lower() in ("true", "1", "yes")


def get_otel_exporter_endpoint() -> str:
    """Get OTLP exporter endpoint from environment."""
    return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")


def init_otel_tracer_provider() -> Optional[TracerProvider]:
    """
    Initialize OpenTelemetry tracer provider with OTLP exporter.
    
    Returns:
        TracerProvider if OTEL_ENABLED=true, None otherwise.
    """
    if not is_otel_enabled():
        logger.info("OpenTelemetry disabled (OTEL_ENABLED not set or false)")
        return None
    
    try:
        endpoint = get_otel_exporter_endpoint()
        logger.info(f"Initializing OpenTelemetry tracer with endpoint: {endpoint}")
        
        resource = Resource.create({
            "service.name": "sifu-backend",
            "service.version": os.getenv("API_VERSION", "1.0.0"),
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        })
        
        # Create OTLP span exporter
        span_exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True,  # Set to False for production with TLS
        )
        
        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
        
        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        logger.info("OpenTelemetry tracer provider initialized successfully")
        return tracer_provider
    
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry tracer: {e}", exc_info=True)
        return None


def init_otel_meter_provider() -> Optional[MeterProvider]:
    """
    Initialize OpenTelemetry meter provider with OTLP exporter.
    
    Returns:
        MeterProvider if OTEL_ENABLED=true, None otherwise.
    """
    if not is_otel_enabled():
        return None
    
    try:
        endpoint = get_otel_exporter_endpoint()
        logger.info(f"Initializing OpenTelemetry meter with endpoint: {endpoint}")
        
        resource = Resource.create({
            "service.name": "sifu-backend",
            "service.version": os.getenv("API_VERSION", "1.0.0"),
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        })
        
        # Create OTLP metric exporter
        metric_exporter = OTLPMetricExporter(
            endpoint=endpoint,
            insecure=True,
        )
        
        # Create meter provider with periodic export
        metric_reader = PeriodicExportingMetricReader(metric_exporter)
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        
        # Set global meter provider
        metrics.set_meter_provider(meter_provider)
        
        logger.info("OpenTelemetry meter provider initialized successfully")
        return meter_provider
    
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry meter: {e}", exc_info=True)
        return None


def instrument_fastapi(app):
    """
    Instrument FastAPI application for tracing and metrics.
    
    Args:
        app: FastAPI application instance.
    """
    if not is_otel_enabled():
        logger.debug("Skipping FastAPI instrumentation (OTEL_ENABLED=false)")
        return
    
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}", exc_info=True)


def instrument_requests():
    """Instrument requests library for tracing outbound HTTP calls."""
    if not is_otel_enabled():
        logger.debug("Skipping requests instrumentation (OTEL_ENABLED=false)")
        return
    
    try:
        RequestsInstrumentor().instrument()
        logger.info("Requests library instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument requests: {e}", exc_info=True)


def instrument_sqlalchemy(engine):
    """
    Instrument SQLAlchemy engine for tracing database calls.
    
    Args:
        engine: SQLAlchemy engine instance.
    """
    if not is_otel_enabled():
        logger.debug("Skipping SQLAlchemy instrumentation (OTEL_ENABLED=false)")
        return
    
    try:
        SQLAlchemyInstrumentor().instrument(engine=engine)
        logger.info("SQLAlchemy instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument SQLAlchemy: {e}", exc_info=True)


def instrument_logging():
    """Enable logging instrumentation to capture logs in traces."""
    if not is_otel_enabled():
        logger.debug("Skipping logging instrumentation (OTEL_ENABLED=false)")
        return
    
    try:
        LoggingInstrumentor().instrument()
        logger.info("Logging instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument logging: {e}", exc_info=True)


def shutdown_otel():
    """Gracefully shutdown OpenTelemetry providers."""
    if not is_otel_enabled():
        return
    
    try:
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, "force_flush"):
            tracer_provider.force_flush()
        logger.info("OpenTelemetry tracer provider flushed")
    except Exception as e:
        logger.error(f"Error flushing tracer provider: {e}")
    
    try:
        meter_provider = metrics.get_meter_provider()
        if hasattr(meter_provider, "force_flush"):
            meter_provider.force_flush()
        logger.info("OpenTelemetry meter provider flushed")
    except Exception as e:
        logger.error(f"Error flushing meter provider: {e}")
