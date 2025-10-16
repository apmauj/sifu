"""
Utilities para unificación de terminología exchange (Punto 5)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from constants import (
    EXCHANGE_FIELD_CURRENCY,
    EXCHANGE_FIELD_BUY_RATE,
    EXCHANGE_FIELD_SELL_RATE,
    EXCHANGE_FIELD_AVERAGE_RATE,
    EXCHANGE_FIELD_DATE,
    EXCHANGE_FIELD_SOURCE,
    EXCHANGE_FIELD_SOURCE_TYPE,
    EXCHANGE_FIELD_TIMESTAMP,
    EXCHANGE_SOURCE_TYPE_LIVE,
    EXCHANGE_SOURCE_TYPE_HISTORICAL,
    EXCHANGE_SOURCE_TYPE_SAMPLE,
    EXCHANGE_SOURCE_TYPE_PERSISTED,
    EXCHANGE_SOURCE_BCU,
    EXCHANGE_SOURCE_INE,
    EXCHANGE_SOURCE_BROU,
    EXCHANGE_SOURCE_BROU_SAMPLE,
    EXCHANGE_SOURCE_BROU_PERSISTED,
    CURRENCY_NAMES,
    SOURCE_DESCRIPTIONS
)


def standardize_exchange_response(
    data: List[Dict[str, Any]],
    source: str,
    source_type: str = EXCHANGE_SOURCE_TYPE_LIVE,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Estandarizar respuesta de exchange con terminología unificada
    
    Args:
        data: Lista de datos de cotizaciones
        source: Fuente de datos (BCU, INE, BROU, etc.)
        source_type: Tipo de fuente (live, historical, sample, persisted)
        include_metadata: Incluir metadatos adicionales
    
    Returns:
        Respuesta estandarizada
    """
    standardized_data = []
    
    for item in data:
        standardized_item = {
            EXCHANGE_FIELD_CURRENCY: item.get("currency", item.get("currency", "")),
            EXCHANGE_FIELD_BUY_RATE: item.get("buy_rate", item.get("buy")),
            EXCHANGE_FIELD_SELL_RATE: item.get("sell_rate", item.get("sell")),
            EXCHANGE_FIELD_AVERAGE_RATE: item.get("average_rate", item.get("average")),
            EXCHANGE_FIELD_DATE: item.get("date", item.get("timestamp", "").split("T")[0] if item.get("timestamp") else ""),
            EXCHANGE_FIELD_SOURCE: source,
            EXCHANGE_FIELD_SOURCE_TYPE: source_type,
            EXCHANGE_FIELD_TIMESTAMP: item.get("timestamp", datetime.utcnow().isoformat())
        }
        
        # Agregar campos adicionales si existen
        if "preferential" in item:
            standardized_item["is_preferential"] = item["preferential"]
        
        if "arbitrage_buy" in item:
            standardized_item["arbitrage_buy"] = item["arbitrage_buy"]
            
        if "arbitrage_sell" in item:
            standardized_item["arbitrage_sell"] = item["arbitrage_sell"]
        
        standardized_data.append(standardized_item)
    
    response = {
        "success": True,
        "message": f"Exchange rates retrieved successfully from {source}",
        "data": standardized_data
    }
    
    if include_metadata:
        response["metadata"] = {
            "total_records": len(standardized_data),
            "source": source,
            "source_type": source_type,
            "source_description": SOURCE_DESCRIPTIONS.get(source, f"Unknown source: {source}"),
            "timestamp": datetime.utcnow().isoformat(),
            "currency_names": {curr: CURRENCY_NAMES.get(curr, curr) for curr in set(item[EXCHANGE_FIELD_CURRENCY] for item in standardized_data)}
        }
    
    return response


def standardize_brou_response(
    data: List[Dict[str, Any]],
    source_type: str = EXCHANGE_SOURCE_TYPE_LIVE,
    data_age_minutes: Optional[float] = None,
    is_fresh: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Estandarizar respuesta específica de BROU con terminología unificada
    
    Args:
        data: Lista de datos de cotizaciones BROU
        source_type: Tipo de fuente (live, historical, sample, persisted)
        data_age_minutes: Edad de los datos en minutos
        is_fresh: Si los datos son frescos
    
    Returns:
        Respuesta estandarizada
    """
    # Mapear source_type a source apropiado
    source_map = {
        EXCHANGE_SOURCE_TYPE_LIVE: EXCHANGE_SOURCE_BROU,
        EXCHANGE_SOURCE_TYPE_HISTORICAL: EXCHANGE_SOURCE_BROU_PERSISTED,
        EXCHANGE_SOURCE_TYPE_SAMPLE: EXCHANGE_SOURCE_BROU_SAMPLE,
        EXCHANGE_SOURCE_TYPE_PERSISTED: EXCHANGE_SOURCE_BROU_PERSISTED
    }
    
    source = source_map.get(source_type, EXCHANGE_SOURCE_BROU)
    
    response = standardize_exchange_response(data, source, source_type, include_metadata=True)
    
    # Agregar metadatos específicos de BROU
    if data_age_minutes is not None:
        response["metadata"]["data_age_minutes"] = data_age_minutes
    
    if is_fresh is not None:
        response["metadata"]["is_fresh"] = is_fresh
    
    # Agregar información de estado
    status_info = {
        EXCHANGE_SOURCE_TYPE_LIVE: {
            "label": "Datos en vivo",
            "color": "green",
            "description": "Cotizaciones obtenidas directamente del BROU"
        },
        EXCHANGE_SOURCE_TYPE_PERSISTED: {
            "label": "Datos históricos",
            "color": "yellow",
            "description": "Cotizaciones almacenadas de consultas anteriores"
        },
        EXCHANGE_SOURCE_TYPE_SAMPLE: {
            "label": "Datos de muestra",
            "color": "red",
            "description": "Datos de ejemplo - API no disponible"
        }
    }
    
    response["metadata"]["status"] = status_info.get(source_type, {
        "label": "Estado desconocido",
        "color": "gray",
        "description": "No se pudo determinar el estado de los datos"
    })
    
    return response


def standardize_bcu_response(
    data: List[Dict[str, Any]],
    source_type: str = EXCHANGE_SOURCE_TYPE_LIVE
) -> Dict[str, Any]:
    """
    Estandarizar respuesta específica de BCU con terminología unificada
    
    Args:
        data: Lista de datos de cotizaciones BCU
        source_type: Tipo de fuente (live, historical, sample)
    
    Returns:
        Respuesta estandarizada
    """
    return standardize_exchange_response(data, EXCHANGE_SOURCE_BCU, source_type, include_metadata=True)


def standardize_ine_response(
    data: List[Dict[str, Any]],
    source_type: str = EXCHANGE_SOURCE_TYPE_HISTORICAL
) -> Dict[str, Any]:
    """
    Estandarizar respuesta específica de INE con terminología unificada
    
    Args:
        data: Lista de datos de cotizaciones INE
        source_type: Tipo de fuente (historical)
    
    Returns:
        Respuesta estandarizada
    """
    return standardize_exchange_response(data, EXCHANGE_SOURCE_INE, source_type, include_metadata=True)


def get_currency_display_name(currency_code: str) -> str:
    """
    Obtener nombre de moneda para display
    
    Args:
        currency_code: Código de moneda (USD, EUR, etc.)
    
    Returns:
        Nombre de moneda para display
    """
    return CURRENCY_NAMES.get(currency_code, currency_code)


def get_source_description(source: str) -> str:
    """
    Obtener descripción de fuente
    
    Args:
        source: Código de fuente (BCU, INE, BROU, etc.)
    
    Returns:
        Descripción de la fuente
    """
    return SOURCE_DESCRIPTIONS.get(source, f"Unknown source: {source}")


def validate_exchange_data(data: Dict[str, Any]) -> bool:
    """
    Validar estructura de datos de exchange
    
    Args:
        data: Datos de cotización
    
    Returns:
        True si la estructura es válida
    """
    required_fields = [
        EXCHANGE_FIELD_CURRENCY,
        EXCHANGE_FIELD_BUY_RATE,
        EXCHANGE_FIELD_SELL_RATE
    ]
    
    return all(field in data for field in required_fields)


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crear respuesta de error estandarizada
    
    Args:
        message: Mensaje de error
        error_code: Código de error opcional
        details: Detalles adicionales del error
    
    Returns:
        Respuesta de error estandarizada
    """
    response = {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": error_code or "EXCHANGE_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response
