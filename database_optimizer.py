#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Optimization Module for SIFU
Implements database indexes, query optimization, and caching
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import date, datetime, timedelta
from functools import lru_cache
from sqlalchemy import Index, text, func
from sqlalchemy.orm import Session
from database import (
    engine, UIRecord, URRecord, ExchangeRateRecord, BROURecord,
    SessionLocal, Base
)

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database optimization and caching manager"""

    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = 300  # 5 minutes default TTL

    def create_optimized_indexes(self):
        """Create optimized indexes for better query performance"""
        logger.info("Creating optimized database indexes...")

        try:
            # UI Table optimizations
            # Composite index for date range queries
            try:
                ui_date_range_idx = Index('idx_ui_date_range', UIRecord.date, UIRecord.value)
                ui_date_range_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_ui_date_range already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_ui_date_range: {e}")

            # Covering index for latest queries
            try:
                ui_latest_idx = Index('idx_ui_latest', UIRecord.date.desc(), UIRecord.value)
                ui_latest_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_ui_latest already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_ui_latest: {e}")

            # UR Table optimizations
            # Composite index for year-month queries
            try:
                ur_year_month_idx = Index('idx_ur_year_month', URRecord.year, URRecord.month, URRecord.value)
                ur_year_month_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_ur_year_month already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_ur_year_month: {e}")

            # Index for year-based queries
            try:
                ur_year_idx = Index('idx_ur_year_only', URRecord.year)
                ur_year_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_ur_year_only already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_ur_year_only: {e}")

            # Composite index for range queries
            try:
                ur_range_idx = Index('idx_ur_range', URRecord.year, URRecord.month)
                ur_range_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_ur_range already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_ur_range: {e}")

            # Exchange Rate Table optimizations
            # Composite index for date-currency queries
            try:
                er_date_currency_idx = Index('idx_er_date_currency',
                                           ExchangeRateRecord.date,
                                           ExchangeRateRecord.currency,
                                           ExchangeRateRecord.buy_rate,
                                           ExchangeRateRecord.sell_rate,
                                           ExchangeRateRecord.average_rate)
                er_date_currency_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_er_date_currency already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_er_date_currency: {e}")

            # Index for currency-based queries
            try:
                er_currency_date_idx = Index('idx_er_currency_date',
                                           ExchangeRateRecord.currency,
                                           ExchangeRateRecord.date.desc())
                er_currency_date_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_er_currency_date already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_er_currency_date: {e}")

            # Covering index for latest queries
            try:
                er_latest_idx = Index('idx_er_latest',
                                    ExchangeRateRecord.date.desc(),
                                    ExchangeRateRecord.currency,
                                    ExchangeRateRecord.average_rate)
                er_latest_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_er_latest already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_er_latest: {e}")

            # BROU Table optimizations
            # Composite index for currency-timestamp queries
            try:
                brou_currency_time_idx = Index('idx_brou_currency_timestamp',
                                             BROURecord.currency,
                                             BROURecord.timestamp.desc(),
                                             BROURecord.buy_rate,
                                             BROURecord.sell_rate)
                brou_currency_time_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_brou_currency_timestamp already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_brou_currency_timestamp: {e}")

            # Index for timestamp-based queries
            try:
                brou_time_idx = Index('idx_brou_timestamp', BROURecord.timestamp.desc())
                brou_time_idx.create(bind=engine)
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Index idx_brou_timestamp already exists, skipping...")
                else:
                    logger.warning(f"Error creating idx_brou_timestamp: {e}")

            logger.info("Database indexes created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
            return False

    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze current query performance and suggest optimizations"""
        logger.info("Analyzing query performance...")

        results = {
            'table_stats': {},
            'index_stats': {},
            'query_patterns': {},
            'recommendations': []
        }

        try:
            with engine.connect() as conn:
                # Get table statistics
                for table_name in ['ui_records', 'ur_records', 'exchange_rate_records', 'brou_records']:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                        count = result.fetchone()[0]
                        results['table_stats'][table_name] = {'record_count': count}
                    except Exception as e:
                        logger.warning(f"Could not get stats for {table_name}: {e}")

                # Analyze index usage (SQLite specific)
                try:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
                    indexes = [row[0] for row in result.fetchall()]
                    results['index_stats']['existing_indexes'] = indexes
                except Exception as e:
                    logger.warning(f"Could not analyze indexes: {e}")

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []

        # Check table sizes
        for table, stats in analysis_results.get('table_stats', {}).items():
            count = stats.get('record_count', 0)
            if count > 10000:
                recommendations.append(f"Table {table} has {count} records - consider partitioning or archiving old data")
            elif count > 1000:
                recommendations.append(f"Table {table} has {count} records - ensure proper indexing is in place")

        # General recommendations
        recommendations.extend([
            "Implement application-level caching for frequently accessed data",
            "Consider using database connection pooling for high-traffic scenarios",
            "Monitor slow queries and add appropriate indexes",
            "Implement query result caching with TTL for expensive operations"
        ])

        return recommendations

    def optimize_query_execution(self, query_type: str, **kwargs) -> Any:
        """Execute optimized queries with caching"""
        cache_key = f"{query_type}:{str(kwargs)}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        # Execute query based on type
        result = self._execute_optimized_query(query_type, **kwargs)

        # Cache result
        if result is not None:
            self.cache[cache_key] = result
            self.cache_expiry[cache_key] = time.time() + self.cache_ttl

        return result

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache_expiry:
            return False
        return time.time() < self.cache_expiry[cache_key]

    def _execute_optimized_query(self, query_type: str, **kwargs) -> Any:
        """Execute specific optimized query"""
        db = SessionLocal()
        try:
            if query_type == "latest_ui":
                return self._get_latest_ui_optimized(db)
            elif query_type == "ui_date_range":
                return self._get_ui_date_range_optimized(db, kwargs.get('start_date'), kwargs.get('end_date'))
            elif query_type == "latest_exchange_rates":
                return self._get_latest_exchange_rates_optimized(db, kwargs.get('currencies'))
            elif query_type == "exchange_rate_history":
                return self._get_exchange_rate_history_optimized(db, kwargs.get('currency'), kwargs.get('limit', 30))
            else:
                logger.warning(f"Unknown query type: {query_type}")
                return None
        finally:
            db.close()

    def _get_latest_ui_optimized(self, db: Session):
        """Optimized query for latest UI value"""
        try:
            # Use indexed query with limit for better performance
            record = db.query(UIRecord).order_by(UIRecord.date.desc()).limit(1).first()
            return record.value if record else None
        except Exception as e:
            logger.error(f"Error in optimized latest UI query: {e}")
            return None

    def _get_ui_date_range_optimized(self, db: Session, start_date: date, end_date: date):
        """Optimized query for UI date range"""
        try:
            # Use indexed range query
            records = db.query(UIRecord.date, UIRecord.value).filter(
                UIRecord.date.between(start_date, end_date)
            ).order_by(UIRecord.date).all()

            return [{'date': r.date.isoformat(), 'value': r.value} for r in records]
        except Exception as e:
            logger.error(f"Error in optimized UI date range query: {e}")
            return []

    def _get_latest_exchange_rates_optimized(self, db: Session, currencies: Optional[List[str]] = None):
        """Optimized query for latest exchange rates"""
        try:
            # Get latest date first (using index)
            latest_date_result = db.query(func.max(ExchangeRateRecord.date)).first()
            if not latest_date_result or not latest_date_result[0]:
                return []

            latest_date = latest_date_result[0]

            # Get all rates for latest date (using composite index)
            query = db.query(ExchangeRateRecord).filter(ExchangeRateRecord.date == latest_date)

            if currencies:
                query = query.filter(ExchangeRateRecord.currency.in_([c.upper() for c in currencies]))

            records = query.order_by(ExchangeRateRecord.currency).all()

            return [{
                'date': r.date.isoformat(),
                'currency': r.currency,
                'buy_rate': r.buy_rate,
                'sell_rate': r.sell_rate,
                'average_rate': r.average_rate
            } for r in records]
        except Exception as e:
            logger.error(f"Error in optimized latest exchange rates query: {e}")
            return []

    def _get_exchange_rate_history_optimized(self, db: Session, currency: str, limit: int = 30):
        """Optimized query for exchange rate history"""
        try:
            # Use composite index for currency + date ordering
            records = db.query(ExchangeRateRecord).filter(
                ExchangeRateRecord.currency == currency.upper()
            ).order_by(ExchangeRateRecord.date.desc()).limit(limit).all()

            return [{
                'date': r.date.isoformat(),
                'currency': r.currency,
                'buy_rate': r.buy_rate,
                'sell_rate': r.sell_rate,
                'average_rate': r.average_rate
            } for r in records]
        except Exception as e:
            logger.error(f"Error in optimized exchange rate history query: {e}")
            return []

    def clear_cache(self):
        """Clear all cached query results"""
        self.cache.clear()
        self.cache_expiry.clear()
        logger.info("Database query cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'cached_queries': list(self.cache.keys())
        }


# Global optimizer instance
db_optimizer = DatabaseOptimizer()

# Convenience functions for easy access
def optimize_database():
    """Apply all database optimizations"""
    return db_optimizer.create_optimized_indexes()

def analyze_performance():
    """Analyze database performance"""
    return db_optimizer.analyze_query_performance()

def get_optimized_data(query_type: str, **kwargs):
    """Get optimized data with caching"""
    return db_optimizer.optimize_query_execution(query_type, **kwargs)

def clear_db_cache():
    """Clear database cache"""
    db_optimizer.clear_cache()

def get_db_cache_stats():
    """Get database cache statistics"""
    return db_optimizer.get_cache_stats()
