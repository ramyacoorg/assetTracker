import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models
from database import engine
from routers import users, assets, authentication, profile

try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database connection warning: {e}")

app = FastAPI(
    title="OptiAsset API",
    description="IT Asset Management System with RBAC",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://asset-frontend-six.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(authentication.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])

@app.get("/")
def root():
    return {"message": "OptiAsset API is running! Visit /docs to see all endpoints."}
