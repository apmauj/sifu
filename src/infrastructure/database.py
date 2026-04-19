from sqlalchemy import (
    create_engine,
    Column,
    Float,
    Date,
    Integer,
    DateTime,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.utils.constants import (
    DATABASE_URL,
    DATABASE_CONNECT_ARGS,
    TABLE_UI_RECORDS,
    TABLE_UR_RECORDS,
    TABLE_EXCHANGE_RATE_RECORDS,
    TABLE_BROU_RECORDS,
)

# Database configuration
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class UIRecord(Base):
    """UI (Unidad Indexada) record model"""

    __tablename__ = TABLE_UI_RECORDS

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)  # Date field
    value = Column(Float, nullable=False)  # Value field
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Update timestamp


class URRecord(Base):
    """UR (Unidad Reajustable) record model"""

    __tablename__ = TABLE_UR_RECORDS

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)  # Year field
    month = Column(Integer, nullable=False, index=True)  # Month field
    value = Column(Float, nullable=False)  # Value field
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Update timestamp

    # Make year-month combination unique
    __table_args__ = (
        UniqueConstraint("year", "month", name="uq_ur_year_month"),
        {"sqlite_autoincrement": True},
    )


class ExchangeRateRecord(Base):
    """Exchange rate record model"""

    __tablename__ = TABLE_EXCHANGE_RATE_RECORDS

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)  # Date field
    currency = Column(
        String(10), nullable=False, index=True
    )  # Currency code (USD, EUR, etc.)
    buy_rate = Column(Float, nullable=True)  # Buy rate
    sell_rate = Column(Float, nullable=True)  # Sell rate
    average_rate = Column(Float, nullable=True)  # Average rate
    arbitrage = Column(Float, nullable=True)  # Arbitrage
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Update timestamp

    # Make date-currency combination unique
    __table_args__ = (
        UniqueConstraint("date", "currency", name="uq_exchange_rate_date_currency"),
        {"sqlite_autoincrement": True},
    )


class BROURecord(Base):
    """BROU (Banco República Oriental del Uruguay) exchange rate record model"""

    __tablename__ = TABLE_BROU_RECORDS

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


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
Base.metadata.create_all(bind=engine)

