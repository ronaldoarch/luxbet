from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from typing import List, Optional
from database import get_db
from schemas import LoginRequest, Token, UserResponse, UserCreate
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, get_user_by_username
from dependencies import get_current_user
from models import User, UserRole, Affiliate, Deposit, Withdrawal, Bet, TransactionStatus, BetStatus
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
    
    # Afiliado: se veio com ref (affiliate_code), vincular ao afiliado
    referred_by_affiliate_id = None
    if getattr(user_data, "affiliate_code", None) and user_data.affiliate_code.strip():
        aff = db.query(Affiliate).filter(
            Affiliate.affiliate_code == user_data.affiliate_code.strip(),
            Affiliate.is_active == True
        ).first()
        if aff:
            referred_by_affiliate_id = aff.id

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
        is_verified=False,
        referred_by_affiliate_id=referred_by_affiliate_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Atualizar total de indicações do afiliado
    if referred_by_affiliate_id:
        aff = db.query(Affiliate).filter(Affiliate.id == referred_by_affiliate_id).first()
        if aff:
            aff.total_referrals = (aff.total_referrals or 0) + 1
            db.commit()
    
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
    Retorna o saldo disponível para saque.
    Sistema usa apenas Seamless Mode - o saldo sempre fica no nosso banco.
    """
    db.refresh(current_user)
    our_balance = float(current_user.balance)
    
    # Em Seamless Mode, o saldo sempre fica no nosso banco
    # Não é necessário verificar ou sincronizar com IGameWin
    print(f"[Available Balance] Seamless Mode - saldo disponível: R$ {our_balance:.2f}")
    
    return {
        "available_balance": round(our_balance, 2),
        "our_balance": round(our_balance, 2),
        "igamewin_balance": None,
        "total_balance": round(our_balance, 2),
        "needs_sync": False,
        "message": "Saldo disponível para saque"
    }


# ========== HISTÓRICO DE TRANSAÇÕES ==========

@router.get("/transactions")
async def get_my_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de transações do usuário (depósitos e saques)
    """
    # Buscar depósitos do usuário
    deposits = db.query(Deposit).filter(
        Deposit.user_id == current_user.id
    ).order_by(desc(Deposit.created_at)).offset(skip).limit(limit).all()
    
    # Buscar saques do usuário
    withdrawals = db.query(Withdrawal).filter(
        Withdrawal.user_id == current_user.id
    ).order_by(desc(Withdrawal.created_at)).offset(skip).limit(limit).all()
    
    # Combinar e ordenar por data
    transactions = []
    
    for deposit in deposits:
        transactions.append({
            "id": deposit.id,
            "type": "deposit",
            "amount": float(deposit.amount),
            "status": deposit.status.value,
            "transaction_id": deposit.transaction_id,
            "external_id": deposit.external_id,
            "created_at": deposit.created_at.isoformat(),
            "updated_at": deposit.updated_at.isoformat(),
        })
    
    for withdrawal in withdrawals:
        transactions.append({
            "id": withdrawal.id,
            "type": "withdrawal",
            "amount": float(withdrawal.amount),
            "status": withdrawal.status.value,
            "transaction_id": withdrawal.transaction_id,
            "external_id": withdrawal.external_id,
            "created_at": withdrawal.created_at.isoformat(),
            "updated_at": withdrawal.updated_at.isoformat(),
        })
    
    # Ordenar por data (mais recente primeiro)
    transactions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "transactions": transactions[:limit],
        "total": len(transactions)
    }


# ========== MINHAS APOSTAS ==========

@router.get("/bets")
async def get_my_bets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de apostas do usuário
    """
    query = db.query(Bet).filter(Bet.user_id == current_user.id)
    
    if status_filter:
        try:
            bet_status = BetStatus(status_filter.lower())
            query = query.filter(Bet.status == bet_status)
        except ValueError:
            pass  # Ignorar status inválido
    
    bets = query.order_by(desc(Bet.created_at)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": bet.id,
            "game_id": bet.game_id,
            "game_name": bet.game_name,
            "provider": bet.provider,
            "amount": float(bet.amount),
            "win_amount": float(bet.win_amount),
            "status": bet.status.value,
            "transaction_id": bet.transaction_id,
            "created_at": bet.created_at.isoformat(),
            "updated_at": bet.updated_at.isoformat(),
        }
        for bet in bets
    ]
