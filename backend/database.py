from sqlalchemy import create_engine, text
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
    echo=True,
    # Configurações do pool para evitar esgotamento de conexões
    pool_size=10,  # Aumentar de 5 para 10
    max_overflow=20,  # Aumentar de 10 para 20 (total máximo: 30 conexões)
    pool_pre_ping=True,  # Verificar conexões antes de usar
    pool_recycle=3600,  # Reciclar conexões após 1 hora
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables (only creates if they don't exist)"""
    # create_all() só cria tabelas que não existem, não deleta dados existentes
    Base.metadata.create_all(bind=engine)
    # Migração: adicionar coluna min_withdrawal em ftd_settings se não existir
    try:
        with engine.connect() as conn:
            if "sqlite" in DATABASE_URL:
                conn.execute(text("ALTER TABLE ftd_settings ADD COLUMN min_withdrawal REAL DEFAULT 10.0"))
            else:
                conn.execute(text("ALTER TABLE ftd_settings ADD COLUMN IF NOT EXISTS min_withdrawal DOUBLE PRECISION DEFAULT 10.0"))
            conn.commit()
    except Exception:
        pass  # Coluna já existe ou tabela não existe
    # Migração: adicionar coluna rtp em igamewin_agents se não existir
    try:
        with engine.connect() as conn:
            if "sqlite" in DATABASE_URL:
                conn.execute(text("ALTER TABLE igamewin_agents ADD COLUMN rtp REAL DEFAULT 96.0"))
            else:
                conn.execute(text("ALTER TABLE igamewin_agents ADD COLUMN IF NOT EXISTS rtp DOUBLE PRECISION DEFAULT 96.0"))
            conn.commit()
    except Exception:
        pass


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Em caso de erro, fazer rollback para liberar a transação
        db.rollback()
        raise
    finally:
        # Sempre fechar a conexão, mesmo em caso de erro
        db.close()
