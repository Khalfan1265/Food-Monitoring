# app/main.py

import os
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv


from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


from app import models, database
from app.routes import (
    student, device, health, food, drink,
    allergy, food_suggestion, auth, secure, password_reset
)

# Load environment variables from .env file
load_dotenv()

# Initialize DB
models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI
app = FastAPI(
    title="Food Monitoring API",
    version="1.0.0",
    description="Monitoring API with JWT Authentication"
)

# Global Rate Limiter Setup (e.g., 10 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Rate limit error response
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again in a moment."}
    )

# CORS setup (allow everything for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 token endpoint for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Swagger security customization
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Include routes
app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(device.router, prefix="/device", tags=["Device"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(food.router, prefix="/food", tags=["Food"])
app.include_router(drink.router, prefix="/drink", tags=["Drink"])
app.include_router(allergy.router, prefix="/allergy", tags=["Allergy"])
app.include_router(food_suggestion.router, prefix="/suggestions", tags=["Suggestions"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(secure.router, prefix="/secure", tags=["Secure"])
app.include_router(password_reset.router, prefix="/password-reset", tags=["Password Reset"])

# Root route
@app.get("/")
async def read_root(request: Request):
    return {"message": "Backend is running"}

