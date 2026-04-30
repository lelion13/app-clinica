from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.api.routers.auth import router as auth_router
from app.api.routers.bookings import router as bookings_router
from app.api.routers.consulting_rooms import router as consulting_rooms_router
from app.api.routers.locations import router as locations_router
from app.api.routers.professionals import router as professionals_router
from app.api.routers.setup import router as setup_router
from app.api.routers.users import router as users_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(setup_router, prefix="/api/v1/setup", tags=["setup"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(locations_router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(consulting_rooms_router, prefix="/api/v1/consulting-rooms", tags=["consulting-rooms"])
app.include_router(professionals_router, prefix="/api/v1/professionals", tags=["professionals"])
app.include_router(bookings_router, prefix="/api/v1/bookings", tags=["bookings"])
