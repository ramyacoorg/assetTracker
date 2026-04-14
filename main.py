import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models
from database import engine

try:
    models.Base.metadata.create_all(bind=engine)
    print("Database connected!")
except Exception as e:
    print(f"DB warning: {e}")

app = FastAPI(title="OptiAsset API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except:
    pass

from routers import authentication, users, assets, profile, issues, dashboard 
try:
    from routers import dashboard
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
except Exception as e:
    print(f"Dashboard router error: {e}")
# In main.py — verify these lines exist

app.include_router(authentication.router, prefix="/api/auth", tags=["auth"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(issues.router, prefix="/api/issues", tags=["issues"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
def root():
    return {"message": "OptiAsset API is running! Visit /docs to see all endpoints."}
