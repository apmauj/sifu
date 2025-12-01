"""BROU router endpoints."""

from fastapi import APIRouter
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


# Note: /api/brou/current is defined in main.py BEFORE including this router
# to ensure mocks in tests work correctly (they patch main._update_brou_cache)
