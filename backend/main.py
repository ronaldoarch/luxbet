from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import init_db, get_db
from auth import create_admin_user
from sqlalchemy.orm import Session
import os

# Import routes
from routes import auth, admin, media, payments, promotions

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Lux Bet API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS - permite variáveis de ambiente para produção
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()] if cors_origins_env else []

# Se não houver variável, usa defaults de desenvolvimento
if not cors_origins:
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "https://luxbet.site",
        "https://www.luxbet.site",
        "https://api.luxbet.site",
        "http://luxbet.site",
        "http://www.luxbet.site",
        # Permite qualquer origem do domínio agenciamidas.com em produção
        "https://*.agenciamidas.com",
        "http://*.agenciamidas.com",
    ]

# Forçar logs para debug
print(f"CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for debugging
    # allow_origins=cors_origins,
    allow_origin_regex=r"https?://.*", # Allow all regex
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(admin.public_router)
app.include_router(admin.root_router)  # Router sem prefixo para /gold_api
app.include_router(media.router)
app.include_router(media.public_router)
app.include_router(payments.router)
app.include_router(payments.webhook_router)
app.include_router(payments.affiliate_router)
app.include_router(promotions.router)
app.include_router(promotions.public_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create admin user on startup"""
    init_db()
    # Create admin user
    db = next(get_db())
    try:
        create_admin_user(db)
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Lux Bet API", "status": "ok", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}
