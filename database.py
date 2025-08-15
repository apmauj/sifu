from sqlalchemy import create_engine, Column, Float, Date, Integer, DateTime, String, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from constants import (
    DATABASE_URL, DATABASE_CONNECT_ARGS, TABLE_UI_RECORDS, TABLE_UR_RECORDS, TABLE_EXCHANGE_RATE_RECORDS,
    COLUMN_UI_DATE, COLUMN_UI_VALUE, COLUMN_UR_YEAR, COLUMN_UR_MONTH, COLUMN_UR_VALUE,
    COLUMN_EXCHANGE_RATE_DATE, COLUMN_EXCHANGE_RATE_CURRENCY, COLUMN_EXCHANGE_RATE_BUY, 
    COLUMN_EXCHANGE_RATE_SELL, COLUMN_EXCHANGE_RATE_AVERAGE, COLUMN_EXCHANGE_RATE_ARBITRAGE,
    COLUMN_ID, COLUMN_CREATED_AT, COLUMN_UPDATED_AT
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp


class URRecord(Base):
    """UR (Unidad Reajustable) record model"""
    __tablename__ = TABLE_UR_RECORDS
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)  # Year field
    month = Column(Integer, nullable=False, index=True)  # Month field
    value = Column(Float, nullable=False)  # Value field
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp
    
    # Make year-month combination unique
    __table_args__ = (
        UniqueConstraint('year', 'month', name='uq_ur_year_month'),
        {'sqlite_autoincrement': True},
    )

    # Legacy Spanish alias properties (año/mes/valor)
    @property
    def año(self):  # type: ignore
        return self.year

    @año.setter
    def año(self, v):  # type: ignore
        self.year = v

    @property
    def mes(self):  # type: ignore
        return self.month

    @mes.setter
    def mes(self, v):  # type: ignore
        self.month = v

    @property
    def valor(self):  # type: ignore
        return self.value

    @valor.setter
    def valor(self, v):  # type: ignore
        self.value = v


class ExchangeRateRecord(Base):
    """Exchange Rate record model"""
    __tablename__ = TABLE_EXCHANGE_RATE_RECORDS
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)  # Exchange rate date
    currency = Column(String(10), nullable=False, index=True)  # USD, EUR, ARS, BRL, etc.
    buy_rate = Column(Float, nullable=False)  # Buy rate
    sell_rate = Column(Float, nullable=False)  # Sell rate
    average_rate = Column(Float, nullable=True)  # Average rate (optional)
    arbitrage = Column(String(50), nullable=True)  # Arbitrage information (optional)
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp
    
    # Make date-currency combination unique
    __table_args__ = (
        UniqueConstraint('date', 'currency', name='uq_exchange_date_currency'),
        {'sqlite_autoincrement': True},
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