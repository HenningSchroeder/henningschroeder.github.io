from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Lab Baseline API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Lab Baseline API",
        "timestamp": datetime.now().isoformat(),
        "hostname": os.getenv("HOSTNAME", "unknown")
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/info")
async def info():
    return {
        "service": "FastAPI Demo",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
