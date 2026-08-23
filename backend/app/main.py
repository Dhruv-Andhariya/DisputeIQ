import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.db import init_db
from app.database.seed import seed_database
from app.api.routes import router

app = FastAPI(
    title="DisputeIQ AI Risk Manager API",
    description="AI-Powered Dispute Investigation & Evidence Intelligence Layer for Razorpay",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("[DisputeIQ Startup] Initializing Database & Data Seeding...")
    init_db()
    # Check if database needs initial seeding
    db_file = settings.DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_file) and os.path.getsize(db_file) > 0:
        print("[DisputeIQ Startup] SQLite Database exists.")
    else:
        print("[DisputeIQ Startup] Seeding database with synthetic dataset...")
        seed_database()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
