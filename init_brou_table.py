#!/usr/bin/env python3
"""
Script para inicializar la tabla BROU en la base de datos existente
"""

import os
from sqlalchemy import (
    create_engine,
    Column,
    Float,
    Integer,
    DateTime,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration (copied from constants to avoid import issues)
DATABASE_PATH = os.getenv("DATABASE_PATH", "./ui_data.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
DATABASE_CONNECT_ARGS = {"check_same_thread": False}

# Database setup
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# BROU Record model (copied from database.py to avoid import issues)
class BROURecord(Base):
    """BROU (Banco República Oriental del Uruguay) exchange rate record model"""

    __tablename__ = "brou_records"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(
        String(20), nullable=False, index=True
    )  # USD, EUR, ARS, BRL, USD_EBROU
    name = Column(String(50), nullable=False)  # Nombre completo de la moneda
    buy_rate = Column(Float, nullable=True)  # Tasa de compra
    sell_rate = Column(Float, nullable=True)  # Tasa de venta
    average_rate = Column(Float, nullable=True)  # Tasa promedio
    arbitrage_buy = Column(Float, nullable=True)  # Arbitraje compra vs USD
    arbitrage_sell = Column(Float, nullable=True)  # Arbitraje venta vs USD
    source = Column(String(20), nullable=False, default="BROU")  # BROU o BROU_SAMPLE
    timestamp = Column(DateTime, nullable=False, index=True)  # Timestamp de los datos
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Update timestamp

    # Make currency-timestamp combination unique (solo guardamos el más reciente por moneda)
    __table_args__ = (
        UniqueConstraint("currency", "timestamp", name="uq_brou_currency_timestamp"),
        {"sqlite_autoincrement": True},
    )


def init_brou_table():
    """Inicializa la tabla BROU si no existe"""
    try:
        # Verificar si la tabla ya existe
        inspector = inspect(engine)
        if "brou_records" in inspector.get_table_names():
            logger.info("Tabla BROU ya existe")
            return

        # Crear la tabla BROU
        BROURecord.__table__.create(engine)
        logger.info("Tabla BROU creada exitosamente")

    except Exception as e:
        logger.error(f"Error creando tabla BROU: {e}")
        raise


if __name__ == "__main__":
    init_brou_table()
