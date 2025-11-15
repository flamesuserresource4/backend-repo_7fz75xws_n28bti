import os
import time
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AFSA — Autonomous Financial Shield Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    scenario: Optional[str] = "upi_scam"
    speed: Optional[str] = "normal"  # slow | normal | fast


class SimulationEvent(BaseModel):
    t: str
    type: str
    message: str
    level: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/simulate", response_model=List[SimulationEvent])
def run_simulation(req: SimulationRequest):
    """
    Returns a deterministic sequence of events that the frontend can render
    as a step-by-step autonomous response. No delays here — the frontend
    animates timing. This keeps the API simple and reliable.
    """
    now = datetime.utcnow().strftime("%H:%M:%S")

    base = [
        {"type": "info", "message": "Monitoring… no threats detected.", "level": "info"},
        {"type": "ingest", "message": "New SMS analysed.", "level": "info"},
        {"type": "detect", "message": "Suspicious UPI intent detected.", "level": "warn"},
        {"type": "freeze", "message": "Auto-freeze triggered: UPI channel frozen.", "level": "critical"},
        {"type": "legal", "message": "Complaint drafted for cyber cell + RBI ombudsman.", "level": "success"},
        {"type": "recover", "message": "Recovery workflow initiated with bank dispute.", "level": "success"},
    ]

    events = [SimulationEvent(t=now, **e) for e in base]
    return events


@app.get("/api/timeline")
def get_timeline():
    base = [
        {"time": "12:00", "title": "Fraud request created", "data": {"channel": "UPI", "amount": "₹9,999", "upi_id": "abc@bank"}},
        {"time": "12:02", "title": "AFSA detected mismatch", "data": {"pattern": "merchant-risk-score>0.82", "device_ip": "103.25.*"}},
        {"time": "12:03", "title": "UPI frozen", "data": {"action": "temporary_freeze", "duration": "30 min"}},
        {"time": "12:05", "title": "Complaint drafted", "data": {"refs": ["Cyber Cell", "RBI Ombudsman"]}},
        {"time": "12:07", "title": "Evidence package created", "data": {"items": ["SMS", "UPI handle", "IP hash"]}},
        {"time": "12:10", "title": "Recovery workflow initiated", "data": {"ticket": "BK-34219", "priority": "P1"}},
    ]
    return {"items": base}


@app.get("/api/legal-docs")
def legal_documents():
    docs = [
        {"id": "cyber_complaint", "title": "Cyber Complaint Draft", "purpose": "Pre-filled FIR-style complaint", "actions": ["preview", "download", "send"]},
        {"id": "rbi_letter", "title": "RBI Ombudsman Letter", "purpose": "Escalation note with annexures", "actions": ["preview", "download", "send"]},
        {"id": "bank_dispute", "title": "Bank Dispute Form (Autofilled)", "purpose": "Card/UPI chargeback workflow", "actions": ["preview", "download", "send"]},
        {"id": "reconstruction", "title": "Fraud Reconstruction Summary", "purpose": "Timeline + evidence bundle", "actions": ["preview", "download", "send"]},
    ]
    return {"docs": docs}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
