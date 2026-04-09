import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models
from database import engine
from routers import users, assets, authentication, profile, issues, dashboard

try:
    models.Base.metadata.create_all(bind=engine)
    print("Database connected successfully!")
except Exception as e:
    print(f"Database warning: {e}")

app = FastAPI(title="OptiAsset API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(authentication.router, prefix="/api/auth",      tags=["Auth"])
app.include_router(users.router,          prefix="/api/users",     tags=["Users"])
app.include_router(assets.router,         prefix="/api/assets",    tags=["Assets"])
app.include_router(profile.router,        prefix="/api/profile",   tags=["Profile"])
app.include_router(issues.router,         prefix="/api/issues",    tags=["Issues"])
app.include_router(dashboard.router,      prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "OptiAsset API is running!"}
