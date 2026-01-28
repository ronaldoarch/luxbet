from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from database import get_db
from schemas import LoginRequest, Token, UserResponse, UserCreate
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, get_user_by_username
from dependencies import get_current_user
from models import User, UserRole
from igamewin_api import get_igamewin_api

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limiter será injetado via app.state.limiter
def get_limiter(request: Request):
    """Helper para obter o limiter do app"""
    return request.app.state.limiter


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar se username já existe
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Verificar se email já existe (apenas se fornecido)
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Gerar email temporário se não fornecido (baseado no telefone ou username)
    import re
    email = user_data.email
    if not email:
        # Usar telefone ou username para gerar email temporário único
        identifier = user_data.phone or user_data.username
        # Remove caracteres não numéricos do telefone
        clean_identifier = re.sub(r'\D', '', identifier) if identifier else user_data.username
        # Garantir que o email seja único adicionando timestamp se necessário
        import time
        email = f"{clean_identifier}_{int(time.time())}@luxbet.temp"
        
        # Verificar se o email temporário já existe (improvável, mas verificar)
        existing_temp_email = db.query(User).filter(User.email == email).first()
        if existing_temp_email:
            email = f"{clean_identifier}_{int(time.time() * 1000)}@luxbet.temp"
    
    # Criar novo usuário
    new_user = User(
        username=user_data.username,
        email=email,
        cpf=user_data.cpf,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.USER,
        balance=0.0,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    # Rate limit temporariamente desativado para debug/testes
    # limiter = request.app.state.limiter
    
    # try:
    #     limit_key = f"login:{login_data.username}"
    #     limiter.hit(limit_key, "100/minute")
    # except Exception:
    #     pass
    
    # authenticate_user já tenta por username e email
    user = authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna informações do usuário logado.
    Sempre retorna os dados mais atualizados do banco de dados.
    """
    # Garantir que temos os dados mais atualizados do banco
    db.refresh(current_user)
    
    # Log para debug - verificar saldo retornado
    print(f"[Auth /me] User: {current_user.username}, Balance: {current_user.balance}")
    
    return current_user


@router.get("/available-balance")
async def get_available_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna o saldo disponível para saque, considerando saldo no nosso banco e no IGameWin.
    Em Transfer Mode, o saldo pode estar no IGameWin e precisa ser sincronizado antes do saque.
    """
    our_balance = float(current_user.balance)
    
    # Tentar obter saldo do IGameWin
    api = get_igamewin_api(db)
    igamewin_balance = None
    if api:
        try:
            igamewin_balance = await api.get_user_balance(current_user.username)
        except Exception as e:
            print(f"[Available Balance] Erro ao obter saldo do IGameWin: {e}")
            # Continuar mesmo se não conseguir obter saldo do IGameWin
    
    # Calcular saldo disponível
    # Se há saldo no IGameWin maior que no nosso banco, precisamos sincronizar primeiro
    if igamewin_balance is not None and igamewin_balance > our_balance:
        # Saldo está no IGameWin - precisa sincronizar antes de sacar
        available_balance = our_balance  # Só pode sacar o que está no nosso banco
        needs_sync = True
        total_balance = igamewin_balance  # Saldo total (nosso + IGameWin)
    else:
        # Saldo está sincronizado ou não há saldo no IGameWin
        available_balance = our_balance
        needs_sync = False
        total_balance = our_balance
    
    return {
        "available_balance": round(available_balance, 2),
        "our_balance": round(our_balance, 2),
        "igamewin_balance": round(igamewin_balance, 2) if igamewin_balance is not None else None,
        "total_balance": round(total_balance, 2),
        "needs_sync": needs_sync,
        "message": "Sincronize o saldo do IGameWin antes de sacar" if needs_sync else "Saldo disponível para saque"
    }
