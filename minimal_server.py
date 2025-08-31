#!/usr/bin/env python3
"""
Minimal SIFU server for debugging startup issues.
This version includes only essential components to isolate the problem.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Minimal lifespan without heavy initialization
@asynccontextmanager
async def minimal_lifespan(app: FastAPI):
    logger.info("Starting minimal SIFU server...")
    try:
        yield
    finally:
        logger.info("Shutting down minimal SIFU server...")

# Create minimal FastAPI app
app = FastAPI(
    title="SIFU Minimal",
    description="Minimal version for debugging",
    version="1.0.0",
    lifespan=minimal_lifespan
)

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Minimal SIFU server is running"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Minimal server healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting minimal server on port 8003...")
    uvicorn.run("minimal_server:app", host="127.0.0.1", port=8003, reload=False)
