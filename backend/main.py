from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import init_db, get_db
from auth import create_admin_user
from sqlalchemy.orm import Session
import os
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from routes import auth, admin, media, payments, promotions

# Função melhorada para obter IP do cliente (considera proxies e headers)
def get_client_ip(request: Request) -> str:
    """Obtém o IP real do cliente, considerando proxies e headers"""
    # Verificar headers de proxy primeiro
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Pegar o primeiro IP da lista (IP original do cliente)
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback para o método padrão
    return get_remote_address(request)

# Configurar rate limiter com função melhorada
limiter = Limiter(key_func=get_client_ip)

app = FastAPI(title="Lux Bet API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS - permite variáveis de ambiente para produção
# NOTA: Atualmente usando allow_origins=["*"] para máxima compatibilidade
# A variável CORS_ORIGINS é apenas para referência/logs, não é usada no middleware
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()] if cors_origins_env else []

# Filtrar localhost da lista (não faz sentido em produção)
cors_origins = [origin for origin in cors_origins if not origin.startswith(("http://localhost", "http://127.0.0.1"))]

# Se não houver variável, usa defaults de desenvolvimento (apenas para logs)
if not cors_origins:
    cors_origins = [
        "https://luxbet.site",
        "https://www.luxbet.site",
        "https://api.luxbet.site",
    ]

# Forçar logs para debug
print(f"CORS Origins from env (filtered): {cors_origins_env}")
print(f"CORS Origins configured (for reference only): {cors_origins}")
print(f"⚠️  CORS MODE: ALLOWING ALL ORIGINS (*) - Variável CORS_ORIGINS é apenas para referência")
print(f"⚠️  IMPORTANTE: localhost foi removido da lista - não afeta acessos via 4G/WiFi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir TODAS as origens para máxima compatibilidade entre dispositivos (WiFi, 4G, etc)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP
    allow_headers=["*"],  # Permitir todos os headers
    expose_headers=["*"],  # Expor todos os headers para compatibilidade
    max_age=3600,  # Cache preflight por 1 hora
)

# Middleware de logging e headers de compatibilidade
@app.middleware("http")
async def add_compatibility_headers(request: Request, call_next):
    """Adiciona headers de compatibilidade e logging"""
    start_time = time.time()
    
    # Log da requisição
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")
    origin = request.headers.get("Origin", "No Origin")
    
    # Log detalhado para debug de CORS
    logger.info(f"Request: {request.method} {request.url.path} - IP: {client_ip} - Origin: {origin} - UA: {user_agent[:100]}")
    
    try:
        response = await call_next(request)
        
        # Adicionar headers de compatibilidade
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        # Adicionar header de timing para debug
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log CORS headers na resposta para debug
        cors_origin = response.headers.get("Access-Control-Allow-Origin", "Not Set")
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s - CORS-Origin: {cors_origin}")
        
        return response
    except Exception as e:
        logger.error(f"Error processing request {request.method} {request.url.path}: {str(e)}", exc_info=True)
        raise

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
app.include_router(payments.manager_router)
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
async def health(request: Request):
    """Health check endpoint com informações de debug"""
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "client_ip": client_ip,
        "user_agent": user_agent[:100],
        "headers": dict(request.headers)
    }
