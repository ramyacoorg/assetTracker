# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from routers import authentication, assets, users, profile, issues, dashboard, assignments, reports

app = FastAPI()

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

app.include_router(authentication.router, prefix="/api/auth",        tags=["auth"])
app.include_router(assets.router,         prefix="/api/assets",      tags=["assets"])
app.include_router(users.router,          prefix="/api/users",       tags=["users"])
app.include_router(profile.router,        prefix="/api/profile",     tags=["profile"])
app.include_router(issues.router,         prefix="/api/issues",      tags=["issues"])
app.include_router(dashboard.router,      prefix="/api/dashboard",   tags=["dashboard"])
app.include_router(assignments.router,    prefix="/api/assignments", tags=["assignments"])
app.include_router(reports.router,        prefix="/api/reports",     tags=["reports"])

@app.get("/")
def root():
    return {"message": "OptiAsset API running"}
