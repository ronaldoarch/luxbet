from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
import os

# Obter DATABASE_URL e normalizar postgres:// para postgresql://
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fortunevegas.db")
# SQLAlchemy 2.0 requer postgresql:// em vez de postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Log de diagnóstico para identificar qual banco está sendo usado
if "sqlite" in DATABASE_URL:
    print("⚠️  WARNING: Using SQLite database! Data will be lost on container recreation.")
    print("⚠️  Set DATABASE_URL environment variable to use PostgreSQL for persistence.")
else:
    print(f"✅ Using PostgreSQL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables (only creates if they don't exist)"""
    # create_all() só cria tabelas que não existem, não deleta dados existentes
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
