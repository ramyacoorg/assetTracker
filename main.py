# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os
from routers import authentication, assets, users, profile, issues, dashboard, assignments, reports, audit, qr, hr

app = FastAPI(title="Assentra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/profiles", exist_ok=True)
os.makedirs("uploads/issues", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(authentication.router, prefix="/api/auth",          tags=["auth"])
app.include_router(assets.router,         prefix="/api/assets",        tags=["assets"])
app.include_router(users.router,          prefix="/api/users",         tags=["users"])
app.include_router(profile.router,        prefix="/api/profile",       tags=["profile"])
app.include_router(issues.router,         prefix="/api/issues",        tags=["issues"])
app.include_router(dashboard.router,      prefix="/api/dashboard",     tags=["dashboard"])
app.include_router(assignments.router,    prefix="/api/assignments",   tags=["assignments"])
app.include_router(reports.router,        prefix="/api/reports",       tags=["reports"])
app.include_router(audit.router,          prefix="/api/audit",         tags=["audit"])
app.include_router(qr.router,             prefix="/api/qr",            tags=["qr"])
app.include_router(hr.router,             prefix="/api/hr",            tags=["hr"])

@app.get("/")
def root():
    return {"message": "Assentra API running", "status": "healthy"}

@app.get("/api/health")
def health_check(db = Depends(authentication.get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
