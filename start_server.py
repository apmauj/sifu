#!/usr/bin/env python
import uvicorn
import os

# Set CORS environment variable
os.environ['ALLOW_ORIGINS'] = 'https://edition-snake-rehab-ca.trycloudflare.com,http://localhost:3000,http://localhost:5173'

from main import app

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False, log_level="debug")
