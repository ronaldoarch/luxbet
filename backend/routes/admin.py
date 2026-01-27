from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from database import get_db
from dependencies import get_current_admin_user, get_current_user
from models import (
    User, Deposit, Withdrawal, FTD, Gateway, IGameWinAgent, FTDSettings,
    TransactionStatus, UserRole, Bet, BetStatus, Notification, NotificationType,
    Affiliate, Theme, ProviderOrder, TrackingConfig, SupportConfig
)
from schemas import (
    UserResponse, UserCreate, UserUpdate,
    DepositResponse, DepositCreate, DepositUpdate,
    WithdrawalResponse, WithdrawalCreate, WithdrawalUpdate,
    FTDResponse, FTDCreate, FTDUpdate,
    GatewayResponse, GatewayCreate, GatewayUpdate,
    IGameWinAgentResponse, IGameWinAgentCreate, IGameWinAgentUpdate,
    FTDSettingsResponse, FTDSettingsCreate, FTDSettingsUpdate,
    AffiliateResponse, AffiliateCreate, AffiliateUpdate,
    ThemeResponse, ThemeCreate, ThemeUpdate,
    ProviderOrderResponse, ProviderOrderCreate, ProviderOrderUpdate,
    TrackingConfigResponse, TrackingConfigCreate, TrackingConfigUpdate,
    SupportConfigResponse, SupportConfigCreate, SupportConfigUpdate
)
from auth import get_password_hash
from igamewin_api import get_igamewin_api

router = APIRouter(prefix="/api/admin", tags=["admin"])
public_router = APIRouter(prefix="/api/public", tags=["public"])
# Router sem prefixo para endpoints que precisam estar na raiz (como /gold_api para IGameWin)
root_router = APIRouter(tags=["root"])


# ========== USERS ==========
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        cpf=user_data.cpf,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.USER,
        balance=0.0,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None


# ========== DEPOSITS ==========
@router.get("/deposits", response_model=List[DepositResponse])
async def get_deposits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[TransactionStatus] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    query = db.query(Deposit)
    if status_filter:
        query = query.filter(Deposit.status == status_filter)
    if user_id:
        query = query.filter(Deposit.user_id == user_id)
    deposits = query.order_by(desc(Deposit.created_at)).offset(skip).limit(limit).all()
    return deposits


@router.get("/deposits/{deposit_id}", response_model=DepositResponse)
async def get_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return deposit


@router.post("/deposits", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: DepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == deposit_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transaction_id = f"DEP_{uuid.uuid4().hex[:16].upper()}"
    deposit = Deposit(
        user_id=deposit_data.user_id,
        gateway_id=deposit_data.gateway_id,
        amount=deposit_data.amount,
        status=TransactionStatus.PENDING,
        transaction_id=transaction_id,
        metadata_json=deposit_data.metadata_json
    )
    db.add(deposit)
    db.commit()
    db.refresh(deposit)
    return deposit


@router.put("/deposits/{deposit_id}", response_model=DepositResponse)
async def update_deposit(
    deposit_id: int,
    deposit_data: DepositUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    
    update_data = deposit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deposit, field, value)
    
    # If approved, update user balance
    if deposit_data.status == TransactionStatus.APPROVED and deposit.status != TransactionStatus.APPROVED:
        user = db.query(User).filter(User.id == deposit.user_id).first()
        user.balance += deposit.amount
        
        # Check if this is first deposit (FTD)
        existing_ftd = db.query(FTD).filter(FTD.user_id == deposit.user_id).first()
        if not existing_ftd:
            # Create FTD
            ftd_settings = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
            pass_rate = ftd_settings.pass_rate if ftd_settings else 0.0
            
            ftd = FTD(
                user_id=deposit.user_id,
                deposit_id=deposit.id,
                amount=deposit.amount,
                is_first_deposit=True,
                pass_rate=pass_rate,
                status=TransactionStatus.APPROVED
            )
            db.add(ftd)
    
    db.commit()
    db.refresh(deposit)
    return deposit


# ========== WITHDRAWALS ==========
@router.get("/withdrawals", response_model=List[WithdrawalResponse])
async def get_withdrawals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[TransactionStatus] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    query = db.query(Withdrawal)
    if status_filter:
        query = query.filter(Withdrawal.status == status_filter)
    if user_id:
        query = query.filter(Withdrawal.user_id == user_id)
    withdrawals = query.order_by(desc(Withdrawal.created_at)).offset(skip).limit(limit).all()
    return withdrawals


@router.get("/withdrawals/{withdrawal_id}", response_model=WithdrawalResponse)
async def get_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return withdrawal


@router.post("/withdrawals", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    withdrawal_data: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == withdrawal_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.balance < withdrawal_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    transaction_id = f"WD_{uuid.uuid4().hex[:16].upper()}"
    withdrawal = Withdrawal(
        user_id=withdrawal_data.user_id,
        gateway_id=withdrawal_data.gateway_id,
        amount=withdrawal_data.amount,
        status=TransactionStatus.PENDING,
        transaction_id=transaction_id,
        metadata_json=withdrawal_data.metadata_json
    )
    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)
    return withdrawal


@router.put("/withdrawals/{withdrawal_id}", response_model=WithdrawalResponse)
async def update_withdrawal(
    withdrawal_id: int,
    withdrawal_data: WithdrawalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    
    update_data = withdrawal_data.model_dump(exclude_unset=True)
    
    # If approved, deduct from user balance
    if withdrawal_data.status == TransactionStatus.APPROVED and withdrawal.status != TransactionStatus.APPROVED:
        user = db.query(User).filter(User.id == withdrawal.user_id).first()
        if user.balance < withdrawal.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        user.balance -= withdrawal.amount
    # If rejected or cancelled and was approved, refund
    elif withdrawal_data.status in [TransactionStatus.REJECTED, TransactionStatus.CANCELLED] and withdrawal.status == TransactionStatus.APPROVED:
        user = db.query(User).filter(User.id == withdrawal.user_id).first()
        user.balance += withdrawal.amount
    
    for field, value in update_data.items():
        setattr(withdrawal, field, value)
    
    db.commit()
    db.refresh(withdrawal)
    return withdrawal


# ========== FTDs ==========
@router.get("/ftds", response_model=List[FTDResponse])
async def get_ftds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    query = db.query(FTD)
    if user_id:
        query = query.filter(FTD.user_id == user_id)
    ftds = query.order_by(desc(FTD.created_at)).offset(skip).limit(limit).all()
    return ftds


@router.get("/ftds/{ftd_id}", response_model=FTDResponse)
async def get_ftd(
    ftd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    ftd = db.query(FTD).filter(FTD.id == ftd_id).first()
    if not ftd:
        raise HTTPException(status_code=404, detail="FTD not found")
    return ftd


@router.put("/ftds/{ftd_id}", response_model=FTDResponse)
async def update_ftd(
    ftd_id: int,
    ftd_data: FTDUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    ftd = db.query(FTD).filter(FTD.id == ftd_id).first()
    if not ftd:
        raise HTTPException(status_code=404, detail="FTD not found")
    
    update_data = ftd_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ftd, field, value)
    
    db.commit()
    db.refresh(ftd)
    return ftd


@router.get("/ftd-settings", response_model=FTDSettingsResponse)
async def get_ftd_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    settings = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
    if not settings:
        # Create default settings
        settings = FTDSettings(pass_rate=0.0, min_amount=0.0, is_active=True)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/ftd-settings", response_model=FTDSettingsResponse)
async def update_ftd_settings(
    settings_data: FTDSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    settings = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
    if not settings:
        settings = FTDSettings(**settings_data.model_dump())
        db.add(settings)
    else:
        update_data = settings_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    return settings


# ========== GATEWAYS ==========
@router.get("/gateways", response_model=List[GatewayResponse])
async def get_gateways(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    gateways = db.query(Gateway).all()
    return gateways


@router.get("/gateways/{gateway_id}", response_model=GatewayResponse)
async def get_gateway(
    gateway_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")
    return gateway


@router.post("/gateways", response_model=GatewayResponse, status_code=status.HTTP_201_CREATED)
async def create_gateway(
    gateway_data: GatewayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    existing = db.query(Gateway).filter(Gateway.name == gateway_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Gateway name already exists")
    
    gateway = Gateway(**gateway_data.model_dump())
    db.add(gateway)
    db.commit()
    db.refresh(gateway)
    return gateway


@router.put("/gateways/{gateway_id}", response_model=GatewayResponse)
async def update_gateway(
    gateway_id: int,
    gateway_data: GatewayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")
    
    update_data = gateway_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gateway, field, value)
    
    db.commit()
    db.refresh(gateway)
    return gateway


@router.delete("/gateways/{gateway_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gateway(
    gateway_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")
    db.delete(gateway)
    db.commit()
    return None


# ========== IGAMEWIN AGENTS ==========
@router.get("/igamewin-agents", response_model=List[IGameWinAgentResponse])
async def get_igamewin_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    agents = db.query(IGameWinAgent).all()
    return agents


@router.get("/igamewin-agents/{agent_id}", response_model=IGameWinAgentResponse)
async def get_igamewin_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    agent = db.query(IGameWinAgent).filter(IGameWinAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="IGameWin agent not found")
    return agent


@router.post("/igamewin-agents", response_model=IGameWinAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_igamewin_agent(
    agent_data: IGameWinAgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    existing = db.query(IGameWinAgent).filter(IGameWinAgent.agent_code == agent_data.agent_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent code already exists")
    
    agent = IGameWinAgent(**agent_data.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.put("/igamewin-agents/{agent_id}", response_model=IGameWinAgentResponse)
async def update_igamewin_agent(
    agent_id: int,
    agent_data: IGameWinAgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    agent = db.query(IGameWinAgent).filter(IGameWinAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="IGameWin agent not found")
    
    update_data = agent_data.model_dump(exclude_unset=True)
    
    # Verificar se agent_code está sendo atualizado e se já existe em outro registro
    if 'agent_code' in update_data:
        existing_agent = db.query(IGameWinAgent).filter(
            IGameWinAgent.agent_code == update_data['agent_code'],
            IGameWinAgent.id != agent_id
        ).first()
        if existing_agent:
            raise HTTPException(status_code=400, detail="Agent code already exists")
    
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/igamewin-agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_igamewin_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    agent = db.query(IGameWinAgent).filter(IGameWinAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="IGameWin agent not found")
    db.delete(agent)
    db.commit()
    return None


# ========== IGAMEWIN GAMES ==========
def _choose_provider(providers: list, provider_code: Optional[str]) -> Optional[str]:
    chosen = provider_code
    if not chosen:
        active = [p for p in providers if str(p.get("status", 1)) in ["1", "true", "True"]]
        if active:
            chosen = active[0].get("code") or active[0].get("provider_code")
        elif providers:
            chosen = providers[0].get("code") or providers[0].get("provider_code")
    return chosen


def _normalize_games(games: list, chosen_provider: Optional[str]) -> list:
    if chosen_provider:
        for g in games:
            if not g.get("provider_code"):
                g["provider_code"] = chosen_provider
    return games


@router.get("/igamewin/agent-balance")
async def get_igamewin_agent_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get IGameWin agent balance - Cannot deposit via API, must use IGameWin admin"""
    api = get_igamewin_api(db)
    if not api:
        raise HTTPException(
            status_code=400, 
            detail="Nenhum agente IGameWin ativo configurado ou credenciais incompletas (agent_code/agent_key vazios)"
        )

    balance = await api.get_agent_balance()
    if balance is None:
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível obter saldo do agente da IGameWin ({api.last_error or 'erro desconhecido'})"
        )

    return {
        "agent_code": api.agent_code,
        "balance": balance,
        "note": "Para adicionar saldo ao agente, utilize o painel administrativo da IGameWin. Esta API permite apenas consultar o saldo."
    }


@router.get("/igamewin/games")
async def list_igamewin_games(
    provider_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    api = get_igamewin_api(db)
    if not api:
        raise HTTPException(
            status_code=400, 
            detail="Nenhum agente IGameWin ativo configurado ou credenciais incompletas (agent_code/agent_key vazios)"
        )

    providers = await api.get_providers()
    if providers is None:
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível obter provedores da IGameWin ({api.last_error or 'erro desconhecido'})"
        )
    
    # Ordenar provedores pela ordem definida no banco
    provider_orders = db.query(ProviderOrder).all()
    order_map = {po.provider_code: po.display_order for po in provider_orders}
    priority_providers = {po.provider_code for po in provider_orders if po.is_priority}
    
    # Normalizar códigos dos provedores para comparação (uppercase, sem espaços)
    normalized_order_map = {k.upper().strip(): v for k, v in order_map.items()}
    normalized_priority_providers = {p.upper().strip() for p in priority_providers}
    
    # Ordenar: primeiro os prioritários por display_order (menor primeiro), depois os outros por display_order
    def sort_providers(p):
        code = (p.get("code") or p.get("provider_code") or "").upper().strip()
        is_priority = code in normalized_priority_providers
        order = normalized_order_map.get(code, 999)
        # Retorna: (0 se prioritário, 1 se não), depois a ordem específica
        return (0 if is_priority else 1, order)
    
    providers = sorted(providers, key=sort_providers)

    chosen_provider = _choose_provider(providers, provider_code)

    games = await api.get_games(provider_code=chosen_provider)
    if games is None:
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível obter jogos da IGameWin (verifique provider_code e credenciais do agente). {api.last_error or ''}".strip()
        )

    games = _normalize_games(games, chosen_provider)

    return {
        "providers": providers,
        "provider_code": chosen_provider,
        "games": games
    }


@public_router.get("/games")
async def public_games(
    provider_code: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    api = get_igamewin_api(db)
    if not api:
        raise HTTPException(
            status_code=400, 
            detail="Nenhum agente IGameWin ativo configurado ou credenciais incompletas (agent_code/agent_key vazios)"
        )

    providers = await api.get_providers()
    if providers is None:
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível obter provedores da IGameWin ({api.last_error or 'erro desconhecido'})"
        )
    
    # Ordenar provedores pela ordem definida no banco
    provider_orders = db.query(ProviderOrder).all()
    order_map = {po.provider_code: po.display_order for po in provider_orders}
    priority_providers = {po.provider_code for po in provider_orders if po.is_priority}
    
    # Normalizar códigos dos provedores para comparação (uppercase, sem espaços)
    normalized_order_map = {k.upper().strip(): v for k, v in order_map.items()}
    normalized_priority_providers = {p.upper().strip() for p in priority_providers}
    
    # Ordenar: primeiro os prioritários por display_order (menor primeiro), depois os outros por display_order
    def sort_providers(p):
        code = (p.get("code") or p.get("provider_code") or "").upper().strip()
        is_priority = code in normalized_priority_providers
        order = normalized_order_map.get(code, 999)
        # Retorna: (0 se prioritário, 1 se não), depois a ordem específica
        return (0 if is_priority else 1, order)
    
    providers = sorted(providers, key=sort_providers)
    
    # Se provider_code foi especificado, retorna apenas jogos desse provedor
    if provider_code:
        chosen_provider = _choose_provider(providers, provider_code)
        games = await api.get_games(provider_code=chosen_provider)
        if games is None:
            raise HTTPException(
                status_code=502,
                detail=f"Não foi possível obter jogos da IGameWin (verifique provider_code e credenciais do agente). {api.last_error or ''}".strip()
            )
        games = _normalize_games(games, chosen_provider)
        public_games = []
        for g in games:
            status_val = g.get("status")
            is_active = (status_val == 1) or (status_val is True) or (str(status_val).lower() == "active")
            if not is_active:
                continue
            public_games.append({
                "name": g.get("game_name") or g.get("name") or g.get("title") or g.get("gameTitle"),
                "code": g.get("game_code") or g.get("code") or g.get("game_id") or g.get("id") or g.get("slug"),
                "provider": g.get("provider_code") or g.get("provider") or g.get("provider_name") or g.get("vendor") or g.get("vendor_name") or chosen_provider,
                "banner": g.get("banner") or g.get("image") or g.get("icon"),
                "status": "active"
            })
        return {
            "providers": providers,
            "provider_code": chosen_provider,
            "games": public_games
        }
    
    # Se não há provider_code, busca jogos de TODOS os provedores
    all_games = []
    active_providers = [p for p in providers if str(p.get("status", 1)) in ["1", "true", "True"]] or providers
    
    # Ordenar provedores pela ordem definida no banco (já ordenado acima, mas garantir)
    active_providers = sorted(active_providers, key=sort_providers)
    
    for provider in active_providers:
        prov_code = provider.get("code") or provider.get("provider_code")
        if not prov_code:
            continue
        
        games = await api.get_games(provider_code=prov_code)
        if games is None:
            continue
        
        games = _normalize_games(games, prov_code)
        
        for g in games:
            status_val = g.get("status")
            is_active = (status_val == 1) or (status_val is True) or (str(status_val).lower() == "active")
            if not is_active:
                continue
            # Usar o código do provedor diretamente para garantir correspondência com a ordenação
            all_games.append({
                "name": g.get("game_name") or g.get("name") or g.get("title") or g.get("gameTitle"),
                "code": g.get("game_code") or g.get("code") or g.get("game_id") or g.get("id") or g.get("slug"),
                "provider": prov_code,  # Usar o código do provedor diretamente
                "provider_code": prov_code,  # Adicionar também como provider_code para referência
                "banner": g.get("banner") or g.get("image") or g.get("icon"),
                "status": "active"
            })

    return {
        "providers": providers,
        "provider_code": None,
        "games": all_games
    }


@public_router.get("/games/{game_code}/launch")
async def launch_game(
    game_code: str,
    provider_code: Optional[str] = Query(None),
    lang: str = Query("pt", description="Language code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Launch a game - requires user authentication
    
    Follows IGameWin API documentation:
    - Uses user_code (username) to launch game
    - Returns launch_url from API response
    - If provider_code is not provided, searches for the game in the game list to find its provider
    """
    api = get_igamewin_api(db)
    if not api:
        raise HTTPException(
            status_code=400, 
            detail="Nenhum agente IGameWin ativo configurado ou credenciais incompletas (agent_code/agent_key vazios)"
        )
    
    # Se provider_code não foi fornecido, buscar na lista de jogos
    if not provider_code:
        providers = await api.get_providers()
        if providers is None:
            raise HTTPException(
                status_code=502,
                detail=f"Não foi possível obter provedores da IGameWin ({api.last_error or 'erro desconhecido'})"
            )
        
        # Tentar encontrar o jogo em cada provider
        found_provider = None
        for provider in providers:
            provider_code_to_try = provider.get("code") or provider.get("provider_code")
            if not provider_code_to_try:
                continue
            
            games = await api.get_games(provider_code=provider_code_to_try)
            if games:
                for game in games:
                    game_code_from_api = game.get("game_code") or game.get("code") or game.get("game_id") or game.get("id")
                    if game_code_from_api == game_code:
                        found_provider = provider_code_to_try
                        break
                if found_provider:
                    break
        
        if found_provider:
            provider_code = found_provider
        else:
            # Se não encontrou, usar o primeiro provider ativo como fallback
            active_providers = [p for p in providers if str(p.get("status", 1)) in ["1", "true", "True"]]
            if active_providers:
                provider_code = active_providers[0].get("code") or active_providers[0].get("provider_code")
            elif providers:
                provider_code = providers[0].get("code") or providers[0].get("provider_code")
    
    # Se ainda não tem provider_code, retornar erro
    if not provider_code:
        raise HTTPException(
            status_code=400,
            detail="provider_code é obrigatório. Não foi possível determinar o provider do jogo."
        )
    
    # IMPORTANTE: Verificar modo de operação do IGameWin
    # Se estiver em modo Seamless, o IGameWin vai chamar nosso /gold_api para buscar saldo
    # Se estiver em modo Transferência, precisamos sincronizar saldo manualmente
    
    print(f"[Launch Game] Checking IGameWin mode for user: {current_user.username}")
    igamewin_balance = await api.get_user_balance(current_user.username)
    
    # Se get_user_balance retornou None, pode ser erro na API ou usuário não existe
    if igamewin_balance is None:
        # Verificar se foi um erro específico indicando modo Seamless
        if api.last_error and "ERROR_GET_BALANCE_END_POINT" in api.last_error:
            print(f"[Launch Game] Detected Seamless mode (ERROR_GET_BALANCE_END_POINT). Skipping balance sync.")
            print(f"[Launch Game] IGameWin will call /gold_api to get balance. Ensuring user exists...")
            
            # Em modo Seamless, apenas garantir que o usuário existe no IGameWin
            # Não precisamos sincronizar saldo - o IGameWin vai buscar via /gold_api
            user_created = await api.create_user(current_user.username, is_demo=False)
            if not user_created:
                # Se já existe, tudo bem - continuar
                if api.last_error and "DUPLICATED_USER" not in api.last_error:
                    print(f"[Launch Game] Warning: Could not create user: {api.last_error}")
                    # Não bloquear - tentar lançar mesmo assim
            # Não fazer transferência de saldo em modo Seamless
        else:
            print(f"[Launch Game] Transfer mode detected. User balance is None, creating user...")
            # Modo Transferência: criar usuário e transferir saldo
            user_created = await api.create_user(current_user.username, is_demo=False)
            if not user_created:
                raise HTTPException(
                    status_code=502,
                    detail=f"Erro ao criar usuário no IGameWin. {api.last_error or 'Erro desconhecido'}"
                )
            # Transferir todo o saldo do jogador para o IGameWin
            if current_user.balance > 0:
                transfer_result = await api.transfer_in(current_user.username, current_user.balance)
                if not transfer_result:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Erro ao transferir saldo para IGameWin. {api.last_error or 'Erro desconhecido'}"
                    )
    else:
        # Modo Transferência: saldo foi retornado, sincronizar se necessário
        print(f"[Launch Game] Transfer mode detected. IGameWin balance: {igamewin_balance}, Local balance: {current_user.balance}")
        if igamewin_balance != current_user.balance:
            # Saldos diferentes, sincronizar
            balance_diff = current_user.balance - igamewin_balance
            if balance_diff > 0:
                # Saldo local maior, transferir diferença para IGameWin
                transfer_result = await api.transfer_in(current_user.username, balance_diff)
                if not transfer_result:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Erro ao transferir saldo para IGameWin. {api.last_error or 'Erro desconhecido'}"
                    )
            elif balance_diff < 0:
                # Saldo IGameWin maior, transferir diferença de volta (caso o jogador tenha ganhado)
                transfer_result = await api.transfer_out(current_user.username, abs(balance_diff))
                if transfer_result:
                    # Atualizar saldo local
                    current_user.balance = igamewin_balance
                    db.commit()
    
    # Gerar URL de lançamento do jogo usando user_code (username)
    print(f"[Launch Game] Request - game_code={game_code}, provider_code={provider_code}, user={current_user.username}")
    launch_url = await api.launch_game(
        user_code=current_user.username,
        game_code=game_code,
        provider_code=provider_code,
        lang=lang
    )
    
    if not launch_url:
        error_detail = api.last_error or 'Erro desconhecido'
        print(f"[Launch Game] Failed - {error_detail}")
        
        # Se o erro for ERROR_GET_BALANCE_END_POINT, significa que o IGameWin está tentando chamar nosso /gold_api
        # mas não consegue acessá-lo. Isso pode ser porque:
        # 1. O campo "Ponto final do site" não está configurado no painel IGameWin
        # 2. O endpoint /gold_api não está acessível publicamente
        if "ERROR_GET_BALANCE_END_POINT" in error_detail:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Erro ao iniciar jogo: {error_detail}. "
                    "O IGameWin está tentando acessar nosso endpoint /gold_api mas não consegue. "
                    "Verifique se o campo 'Ponto final do site' está configurado como 'https://luxbet.site' "
                    "no painel administrativo do IGameWin (Agente de atualização). "
                    "Aguarde 2-5 minutos após salvar as configurações."
                )
            )
        
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível iniciar o jogo. {error_detail}"
        )
    
    print(f"[Launch Game] Success - URL length: {len(launch_url)}, starts with: {launch_url[:100]}...")
    print(f"[Launch Game] Full URL: {launch_url}")
    
    # Validar URL antes de retornar
    if not launch_url.startswith(('http://', 'https://')):
        print(f"[Launch Game] WARNING: URL inválida - não começa com http:// ou https://")
        raise HTTPException(
            status_code=502,
            detail=f"URL de lançamento inválida retornada pela API IGameWin"
        )
    
    return {
        "game_url": launch_url,
        "launch_url": launch_url,  # Mantém compatibilidade
        "game_code": game_code,
        "provider_code": provider_code,
        "username": current_user.username,
        "user_code": current_user.username
    }


# ========== STATS ==========
@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    from datetime import date, timedelta
    
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    
    # Total de usuários
    total_users = db.query(User).count()
    
    # Usuários registrados hoje
    usuarios_registrados_hoje = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    # Balanço total dos jogadores com saldo
    users_with_balance = db.query(User).filter(User.balance > 0).all()
    balanco_jogador_total = sum(u.balance for u in users_with_balance)
    jogadores_com_saldo = len(users_with_balance)
    
    # Depósitos
    total_deposits = db.query(Deposit).filter(Deposit.status == TransactionStatus.APPROVED).count()
    total_deposit_amount = db.query(Deposit).filter(Deposit.status == TransactionStatus.APPROVED).with_entities(
        func.sum(Deposit.amount)
    ).scalar() or 0.0
    pending_deposits = db.query(Deposit).filter(Deposit.status == TransactionStatus.PENDING).count()
    
    # Depósitos recebidos (aprovados) hoje
    pagamentos_recebidos_hoje = db.query(Deposit).filter(
        Deposit.status == TransactionStatus.APPROVED,
        func.date(Deposit.created_at) == today
    ).count()
    valor_pagamentos_recebidos_hoje = db.query(Deposit).filter(
        Deposit.status == TransactionStatus.APPROVED,
        func.date(Deposit.created_at) == today
    ).with_entities(func.sum(Deposit.amount)).scalar() or 0.0
    
    # PIX recebido hoje (depósitos PIX aprovados hoje)
    pix_recebido_hoje = db.query(Deposit).join(Gateway).filter(
        Deposit.status == TransactionStatus.APPROVED,
        Gateway.type == "pix",
        func.date(Deposit.created_at) == today
    ).with_entities(func.sum(Deposit.amount)).scalar() or 0.0
    pix_recebido_count_hoje = db.query(Deposit).join(Gateway).filter(
        Deposit.status == TransactionStatus.APPROVED,
        Gateway.type == "pix",
        func.date(Deposit.created_at) == today
    ).count()
    
    # Saques
    total_withdrawals = db.query(Withdrawal).filter(Withdrawal.status == TransactionStatus.APPROVED).count()
    total_withdrawal_amount = db.query(Withdrawal).filter(Withdrawal.status == TransactionStatus.APPROVED).with_entities(
        func.sum(Withdrawal.amount)
    ).scalar() or 0.0
    pending_withdrawals = db.query(Withdrawal).filter(Withdrawal.status == TransactionStatus.PENDING).count()
    
    # Pagamentos feitos (saques aprovados) hoje
    pagamentos_feitos_hoje = db.query(Withdrawal).filter(
        Withdrawal.status == TransactionStatus.APPROVED,
        func.date(Withdrawal.created_at) == today
    ).count()
    valor_pagamentos_feitos_hoje = db.query(Withdrawal).filter(
        Withdrawal.status == TransactionStatus.APPROVED,
        func.date(Withdrawal.created_at) == today
    ).with_entities(func.sum(Withdrawal.amount)).scalar() or 0.0
    
    # PIX feito hoje (saques PIX aprovados hoje)
    pix_feito_hoje = db.query(Withdrawal).join(Gateway).filter(
        Withdrawal.status == TransactionStatus.APPROVED,
        Gateway.type == "pix",
        func.date(Withdrawal.created_at) == today
    ).with_entities(func.sum(Withdrawal.amount)).scalar() or 0.0
    pix_feito_count_hoje = db.query(Withdrawal).join(Gateway).filter(
        Withdrawal.status == TransactionStatus.APPROVED,
        Gateway.type == "pix",
        func.date(Withdrawal.created_at) == today
    ).count()
    
    # PIX gerado hoje (pendentes ou aprovados)
    pix_gerado_hoje = db.query(Deposit).join(Gateway).filter(
        Gateway.type == "pix",
        func.date(Deposit.created_at) == today
    ).count()
    pix_gerado_pago_hoje = db.query(Deposit).join(Gateway).filter(
        Gateway.type == "pix",
        Deposit.status == TransactionStatus.APPROVED,
        func.date(Deposit.created_at) == today
    ).count()
    pix_percentual_pago = (pix_gerado_pago_hoje / pix_gerado_hoje * 100) if pix_gerado_hoje > 0 else 0
    
    # FTDs
    total_ftds = db.query(FTD).count()
    ftd_hoje = db.query(FTD).filter(func.date(FTD.created_at) == today).count()
    
    # GGR (Gross Gaming Revenue) - receita bruta de jogos
    # Simplificado: diferença entre depósitos e saques aprovados
    ggr_gerado = total_deposit_amount - total_withdrawal_amount
    ggr_taxa = 17.0  # Taxa padrão de 17% (pode ser configurável)
    
    # Total pago em GGR (assumindo que GGR pago = saques aprovados)
    total_pago_ggr = total_withdrawal_amount
    pagamentos_feitos_total = total_withdrawals
    
    # Receita líquida / Lucro total
    net_revenue = total_deposit_amount - total_withdrawal_amount
    
    # Depósitos hoje
    depositos_hoje = db.query(Deposit).filter(func.date(Deposit.created_at) == today).count()
    
    return {
        # Métricas básicas
        "total_users": total_users,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_ftds": total_ftds,
        "total_deposit_amount": total_deposit_amount,
        "total_withdrawal_amount": total_withdrawal_amount,
        "pending_deposits": pending_deposits,
        "pending_withdrawals": pending_withdrawals,
        "net_revenue": net_revenue,
        
        # Métricas expandidas
        "usuarios_na_casa": total_users,
        "usuarios_registrados_hoje": usuarios_registrados_hoje,
        "balanco_jogador_total": balanco_jogador_total,
        "jogadores_com_saldo": jogadores_com_saldo,
        "ggr_gerado": ggr_gerado,
        "ggr_taxa": ggr_taxa,
        "total_pago_ggr": total_pago_ggr,
        "pix_recebido_hoje": pix_recebido_hoje,
        "pix_recebido_count_hoje": pix_recebido_count_hoje,
        "pix_feito_hoje": pix_feito_hoje,
        "pix_feito_count_hoje": pix_feito_count_hoje,
        "pix_gerado_hoje": pix_gerado_hoje,
        "pix_percentual_pago": pix_percentual_pago,
        "pagamentos_recebidos_hoje": pagamentos_recebidos_hoje,
        "valor_pagamentos_recebidos_hoje": valor_pagamentos_recebidos_hoje,
        "pagamentos_feitos_hoje": pagamentos_feitos_hoje,
        "valor_pagamentos_feitos_hoje": valor_pagamentos_feitos_hoje,
        "pagamentos_feitos_total": pagamentos_feitos_total,
        "ftd_hoje": ftd_hoje,
        "depositos_hoje": depositos_hoje,
        "total_lucro": net_revenue,
    }


# ========== GGR REPORT ==========
@router.get("/ggr/report")
async def get_ggr_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Relatório de GGR (Gross Gaming Revenue)"""
    from datetime import datetime, date
    
    # Parse dates or use defaults
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    else:
        start = datetime.combine(date.today(), datetime.min.time())
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    else:
        end = datetime.utcnow()
    
    # Total de depósitos aprovados no período
    total_deposits = db.query(Deposit).filter(
        Deposit.status == TransactionStatus.APPROVED,
        Deposit.created_at >= start,
        Deposit.created_at <= end
    ).with_entities(func.sum(Deposit.amount)).scalar() or 0.0
    
    # Total de saques aprovados no período
    total_withdrawals = db.query(Withdrawal).filter(
        Withdrawal.status == TransactionStatus.APPROVED,
        Withdrawal.created_at >= start,
        Withdrawal.created_at <= end
    ).with_entities(func.sum(Withdrawal.amount)).scalar() or 0.0
    
    # Total de apostas no período
    total_bets = db.query(Bet).filter(
        Bet.created_at >= start,
        Bet.created_at <= end
    ).with_entities(func.sum(Bet.amount)).scalar() or 0.0
    
    # Total ganho em apostas
    total_wins = db.query(Bet).filter(
        Bet.status == BetStatus.WON,
        Bet.created_at >= start,
        Bet.created_at <= end
    ).with_entities(func.sum(Bet.win_amount)).scalar() or 0.0
    
    # GGR = Total Apostado - Total Ganho
    ggr = total_bets - total_wins
    
    # NGR (Net Gaming Revenue) = GGR - Bonuses (simplificado, pode incluir bônus depois)
    ngr = ggr
    
    return {
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "deposits": {
            "total": total_deposits,
            "count": db.query(Deposit).filter(
                Deposit.status == TransactionStatus.APPROVED,
                Deposit.created_at >= start,
                Deposit.created_at <= end
            ).count()
        },
        "withdrawals": {
            "total": total_withdrawals,
            "count": db.query(Withdrawal).filter(
                Withdrawal.status == TransactionStatus.APPROVED,
                Withdrawal.created_at >= start,
                Withdrawal.created_at <= end
            ).count()
        },
        "bets": {
            "total_amount": total_bets,
            "total_wins": total_wins,
            "count": db.query(Bet).filter(
                Bet.created_at >= start,
                Bet.created_at <= end
            ).count()
        },
        "ggr": ggr,
        "ngr": ngr,
        "ggr_rate": (ggr / total_bets * 100) if total_bets > 0 else 0.0,
    }


# ========== BETS ==========
@router.get("/bets")
async def get_bets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    status: Optional[BetStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Listar apostas"""
    query = db.query(Bet)
    
    if user_id:
        query = query.filter(Bet.user_id == user_id)
    if status:
        query = query.filter(Bet.status == status)
    
    bets = query.order_by(desc(Bet.created_at)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": bet.id,
            "user_id": bet.user_id,
            "username": bet.user.username if bet.user else None,
            "game_id": bet.game_id,
            "game_name": bet.game_name,
            "provider": bet.provider,
            "amount": bet.amount,
            "win_amount": bet.win_amount,
            "status": bet.status.value,
            "transaction_id": bet.transaction_id,
            "created_at": bet.created_at.isoformat(),
        }
        for bet in bets
    ]


@router.get("/bets/{bet_id}")
async def get_bet(
    bet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obter aposta específica"""
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Aposta não encontrada")
    
    return {
        "id": bet.id,
        "user_id": bet.user_id,
        "username": bet.user.username if bet.user else None,
        "game_id": bet.game_id,
        "game_name": bet.game_name,
        "provider": bet.provider,
        "amount": bet.amount,
        "win_amount": bet.win_amount,
        "status": bet.status.value,
        "transaction_id": bet.transaction_id,
        "external_id": bet.external_id,
        "metadata": json.loads(bet.metadata_json) if bet.metadata_json else None,
        "created_at": bet.created_at.isoformat(),
        "updated_at": bet.updated_at.isoformat(),
    }


# ========== NOTIFICATIONS ==========
@router.get("/notifications")
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Listar notificações"""
    query = db.query(Notification)
    
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    else:
        # Admin vê apenas notificações globais (user_id = null)
        query = query.filter(Notification.user_id == None)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    if is_active is not None:
        query = query.filter(Notification.is_active == is_active)
    
    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "type": notif.type.value,
            "user_id": notif.user_id,
            "username": notif.user.username if notif.user else None,
            "is_read": notif.is_read,
            "is_active": notif.is_active,
            "link": notif.link,
            "created_at": notif.created_at.isoformat(),
        }
        for notif in notifications
    ]


@router.post("/notifications")
async def create_notification(
    title: str,
    message: str,
    type: NotificationType = NotificationType.INFO,
    user_id: Optional[int] = None,
    link: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Criar notificação"""
    notification = Notification(
        title=title,
        message=message,
        type=type,
        user_id=user_id,  # null = notificação global
        link=link,
        is_active=True,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type.value,
        "user_id": notification.user_id,
        "is_read": notification.is_read,
        "is_active": notification.is_active,
        "link": notification.link,
        "created_at": notification.created_at.isoformat(),
    }


@router.put("/notifications/{notification_id}")
async def update_notification(
    notification_id: int,
    title: Optional[str] = None,
    message: Optional[str] = None,
    type: Optional[NotificationType] = None,
    is_active: Optional[bool] = None,
    link: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualizar notificação"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    if title is not None:
        notification.title = title
    if message is not None:
        notification.message = message
    if type is not None:
        notification.type = type
    if is_active is not None:
        notification.is_active = is_active
    if link is not None:
        notification.link = link
    
    db.commit()
    db.refresh(notification)
    
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type.value,
        "is_active": notification.is_active,
        "link": notification.link,
    }


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deletar notificação"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    db.delete(notification)
    db.commit()
    
    return {"success": True, "message": "Notificação deletada com sucesso"}


# ========== AFFILIATES ==========
@router.get("/affiliates", response_model=List[AffiliateResponse])
async def get_affiliates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lista todos os afiliados"""
    affiliates = db.query(Affiliate).offset(skip).limit(limit).all()
    return affiliates


@router.get("/affiliates/{affiliate_id}", response_model=AffiliateResponse)
async def get_affiliate(
    affiliate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Busca um afiliado específico"""
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Afiliado não encontrado")
    return affiliate


@router.post("/affiliates", response_model=AffiliateResponse, status_code=status.HTTP_201_CREATED)
async def create_affiliate(
    affiliate_data: AffiliateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cria um novo afiliado"""
    # Verificar se o usuário existe
    user = db.query(User).filter(User.id == affiliate_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se já existe afiliado para este usuário
    existing = db.query(Affiliate).filter(Affiliate.user_id == affiliate_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este usuário já é um afiliado")
    
    # Verificar se o código já existe
    existing_code = db.query(Affiliate).filter(Affiliate.affiliate_code == affiliate_data.affiliate_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Código de afiliado já existe")
    
    affiliate = Affiliate(
        user_id=affiliate_data.user_id,
        affiliate_code=affiliate_data.affiliate_code,
        cpa_amount=affiliate_data.cpa_amount,
        revshare_percentage=affiliate_data.revshare_percentage
    )
    
    db.add(affiliate)
    db.commit()
    db.refresh(affiliate)
    
    return affiliate


@router.put("/affiliates/{affiliate_id}", response_model=AffiliateResponse)
async def update_affiliate(
    affiliate_id: int,
    affiliate_data: AffiliateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualiza um afiliado (CPA e revshare)"""
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Afiliado não encontrado")
    
    if affiliate_data.cpa_amount is not None:
        affiliate.cpa_amount = affiliate_data.cpa_amount
    
    if affiliate_data.revshare_percentage is not None:
        if affiliate_data.revshare_percentage < 0 or affiliate_data.revshare_percentage > 100:
            raise HTTPException(status_code=400, detail="Revshare deve estar entre 0 e 100")
        affiliate.revshare_percentage = affiliate_data.revshare_percentage
    
    if affiliate_data.is_active is not None:
        affiliate.is_active = affiliate_data.is_active
    
    db.commit()
    db.refresh(affiliate)
    
    return affiliate


@router.delete("/affiliates/{affiliate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_affiliate(
    affiliate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deleta um afiliado"""
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Afiliado não encontrado")
    
    db.delete(affiliate)
    db.commit()


# ========== THEMES ==========
@router.get("/themes", response_model=List[ThemeResponse])
async def get_themes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lista todos os temas"""
    themes = db.query(Theme).all()
    return themes


@router.get("/themes/active", response_model=ThemeResponse)
async def get_active_theme(
    db: Session = Depends(get_db)
):
    """Retorna o tema ativo (público, não requer autenticação)"""
    theme = db.query(Theme).filter(Theme.is_active == True).first()
    if not theme:
        # Retornar tema padrão se não houver tema ativo
        default_colors = {
            "primary": "#0a4d3e",
            "secondary": "#0d5d4b",
            "accent": "#d4af37",
            "background": "#0a0e0f",
            "text": "#ffffff",
            "textSecondary": "#9ca3af",
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b"
        }
        return {
            "id": 0,
            "name": "Default",
            "colors_json": json.dumps(default_colors),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    return theme


@public_router.get("/themes/active", response_model=ThemeResponse)
async def get_active_theme_public(
    db: Session = Depends(get_db)
):
    """Retorna o tema ativo (público)"""
    return await get_active_theme(db)


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Busca um tema específico"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    return theme


@router.post("/themes", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    theme_data: ThemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cria um novo tema"""
    # Verificar se o nome já existe
    existing = db.query(Theme).filter(Theme.name == theme_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tema com este nome já existe")
    
    # Validar JSON de cores
    try:
        colors = json.loads(theme_data.colors_json)
        required_colors = ["primary", "secondary", "accent", "background", "text"]
        for color in required_colors:
            if color not in colors:
                raise HTTPException(status_code=400, detail=f"Cor '{color}' é obrigatória")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="colors_json deve ser um JSON válido")
    
    # Se este tema será ativo, desativar outros
    if theme_data.is_active:
        db.query(Theme).update({Theme.is_active: False})
    
    theme = Theme(
        name=theme_data.name,
        colors_json=theme_data.colors_json,
        is_active=theme_data.is_active
    )
    
    db.add(theme)
    db.commit()
    db.refresh(theme)
    
    return theme


@router.put("/themes/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: int,
    theme_data: ThemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualiza um tema"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    
    if theme_data.name is not None:
        # Verificar se o nome já existe em outro tema
        existing = db.query(Theme).filter(Theme.name == theme_data.name, Theme.id != theme_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tema com este nome já existe")
        theme.name = theme_data.name
    
    if theme_data.colors_json is not None:
        # Validar JSON de cores
        try:
            colors = json.loads(theme_data.colors_json)
            required_colors = ["primary", "secondary", "accent", "background", "text"]
            for color in required_colors:
                if color not in colors:
                    raise HTTPException(status_code=400, detail=f"Cor '{color}' é obrigatória")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="colors_json deve ser um JSON válido")
        theme.colors_json = theme_data.colors_json
    
    if theme_data.is_active is not None:
        # Se ativando este tema, desativar outros
        if theme_data.is_active:
            db.query(Theme).filter(Theme.id != theme_id).update({Theme.is_active: False})
        theme.is_active = theme_data.is_active
    
    db.commit()
    db.refresh(theme)
    
    return theme


@router.delete("/themes/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deleta um tema"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    
    # Não permitir deletar tema ativo
    if theme.is_active:
        raise HTTPException(status_code=400, detail="Não é possível deletar o tema ativo")
    
    db.delete(theme)
    db.commit()


# ========== PROVIDER ORDER ==========
@router.get("/provider-orders", response_model=List[ProviderOrderResponse])
async def get_provider_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lista todas as ordens de provedores"""
    orders = db.query(ProviderOrder).order_by(ProviderOrder.display_order.asc()).all()
    return orders


@router.post("/provider-orders", response_model=ProviderOrderResponse)
async def create_provider_order(
    order_data: ProviderOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cria ou atualiza ordem de um provedor"""
    existing = db.query(ProviderOrder).filter(ProviderOrder.provider_code == order_data.provider_code).first()
    if existing:
        existing.display_order = order_data.display_order
        existing.is_priority = order_data.is_priority
        db.commit()
        db.refresh(existing)
        return existing
    
    order = ProviderOrder(**order_data.dict())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/provider-orders/bulk", response_model=List[ProviderOrderResponse])
async def update_provider_orders_bulk(
    orders: List[ProviderOrderCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualiza múltiplas ordens de provedores de uma vez"""
    updated = []
    for order_data in orders:
        existing = db.query(ProviderOrder).filter(ProviderOrder.provider_code == order_data.provider_code).first()
        if existing:
            existing.display_order = order_data.display_order
            existing.is_priority = order_data.is_priority
            updated.append(existing)
        else:
            new_order = ProviderOrder(**order_data.dict())
            db.add(new_order)
            updated.append(new_order)
    db.commit()
    for order in updated:
        db.refresh(order)
    return updated


@router.delete("/provider-orders/{provider_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider_order(
    provider_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Remove ordem de um provedor"""
    order = db.query(ProviderOrder).filter(ProviderOrder.provider_code == provider_code).first()
    if order:
        db.delete(order)
        db.commit()


# ========== TRACKING CONFIG ==========
@router.get("/tracking-configs", response_model=List[TrackingConfigResponse])
async def get_tracking_configs(
    platform: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lista configurações de tracking"""
    query = db.query(TrackingConfig)
    if platform:
        query = query.filter(TrackingConfig.platform == platform)
    configs = query.all()
    return configs


@router.get("/tracking-configs/{config_id}", response_model=TrackingConfigResponse)
async def get_tracking_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtém uma configuração de tracking específica"""
    config = db.query(TrackingConfig).filter(TrackingConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração de tracking não encontrada")
    return config


@router.post("/tracking-configs", response_model=TrackingConfigResponse)
async def create_tracking_config(
    config_data: TrackingConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cria uma nova configuração de tracking"""
    config = TrackingConfig(**config_data.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/tracking-configs/{config_id}", response_model=TrackingConfigResponse)
async def update_tracking_config(
    config_id: int,
    config_data: TrackingConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualiza uma configuração de tracking"""
    config = db.query(TrackingConfig).filter(TrackingConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração de tracking não encontrada")
    
    update_data = config_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    return config


@router.delete("/tracking-configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracking_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deleta uma configuração de tracking"""
    config = db.query(TrackingConfig).filter(TrackingConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração de tracking não encontrada")
    
    db.delete(config)
    db.commit()


# ========== SUPPORT CONFIG ==========

@router.get("/support-config", response_model=SupportConfigResponse)
async def get_support_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obter configuração de suporte (admin)"""
    config = db.query(SupportConfig).filter(SupportConfig.is_active == True).first()
    if not config:
        # Criar configuração padrão se não existir
        config = SupportConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.post("/support-config", response_model=SupportConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_support_config(
    config_data: SupportConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Criar configuração de suporte"""
    # Desativar outras configurações se esta for ativa
    if config_data.is_active:
        db.query(SupportConfig).filter(SupportConfig.is_active == True).update({"is_active": False})
    
    config = SupportConfig(**config_data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/support-config/{config_id}", response_model=SupportConfigResponse)
async def update_support_config(
    config_id: int,
    config_data: SupportConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualizar configuração de suporte"""
    config = db.query(SupportConfig).filter(SupportConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração de suporte não encontrada")
    
    update_data = config_data.model_dump(exclude_unset=True)
    
    # Se estiver ativando esta configuração, desativar outras
    if update_data.get("is_active") is True:
        db.query(SupportConfig).filter(
            SupportConfig.is_active == True,
            SupportConfig.id != config_id
        ).update({"is_active": False})
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return config


@public_router.get("/support-config", response_model=SupportConfigResponse)
async def get_support_config(db: Session = Depends(get_db)):
    """Obter configuração de suporte ativa"""
    config = db.query(SupportConfig).filter(SupportConfig.is_active == True).first()
    if not config:
        # Retornar valores padrão se não houver configuração
        return {
            "id": 0,
            "whatsapp_number": "",
            "whatsapp_link": "",
            "phone_number": "",
            "email": "",
            "chat_link": "",
            "welcome_message": "",
            "working_hours": "",
            "is_active": False,
            "metadata_json": "{}"
        }
    return config


@public_router.get("/notifications")
async def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter notificações do usuário logado"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True
    ).order_by(desc(Notification.created_at)).limit(50).all()
    
    return [
        {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "type": notif.type.value,
            "is_read": notif.is_read,
            "link": notif.link,
            "created_at": notif.created_at.isoformat(),
        }
        for notif in notifications
    ]


@public_router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar notificação como lida"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    notification.is_read = True
    db.commit()
    
    return {"status": "success", "message": "Notificação marcada como lida"}


# ========== IGameWin Seamless API (Gold API) ==========
# Este endpoint é chamado pelo IGameWin quando está em modo Seamless
# Documentação: https://igamewin.com/docs (API integrada - API do site)

# Endpoint também na raiz (/gold_api) - IGameWin espera neste caminho
@root_router.post("/gold_api")
async def igamewin_gold_api_root(request: Request, db: Session = Depends(get_db)):
    """Endpoint /gold_api na raiz para IGameWin"""
    print(f"[Gold API Root] ===== REQUEST RECEIVED AT /gold_api =====")
    return await igamewin_gold_api(request, db)

# Endpoint GET para testar se /gold_api está acessível
@root_router.get("/gold_api")
async def test_gold_api():
    """Endpoint de teste para verificar se /gold_api está acessível"""
    return {
        "status": "ok",
        "message": "Endpoint /gold_api está acessível",
        "endpoint": "/gold_api",
        "methods": ["POST"],
        "expected_methods": ["user_balance", "transaction"]
    }

# Endpoint também em /api/gold_api para garantir compatibilidade
@public_router.post("/gold_api")
async def igamewin_gold_api_public(request: Request, db: Session = Depends(get_db)):
    """Endpoint /api/public/gold_api para compatibilidade"""
    print(f"[Gold API Public] ===== REQUEST RECEIVED AT /api/public/gold_api =====")
    return await igamewin_gold_api(request, db)

# Endpoint também em /api/gold_api (sem /public) para garantir acesso via api.luxbet.site
@router.post("/gold_api")
async def igamewin_gold_api_admin(request: Request, db: Session = Depends(get_db)):
    """Endpoint /api/admin/gold_api - redireciona para função principal"""
    print(f"[Gold API Admin] ===== REQUEST RECEIVED AT /api/admin/gold_api =====")
    return await igamewin_gold_api(request, db)

# Endpoint também em /api/public/gold_api para compatibilidade
@public_router.post("/gold_api")
async def igamewin_gold_api(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para modo Seamless do IGameWin.
    Implementa os métodos: user_balance e transaction
    """
    try:
        # Log da requisição recebida
        client_host = request.client.host if request.client else "unknown"
        print(f"[Gold API] ===== REQUEST RECEIVED =====")
        print(f"[Gold API] Client IP: {client_host}")
        print(f"[Gold API] Headers: {dict(request.headers)}")
        
        data = await request.json()
        method = data.get("method")
        agent_code = data.get("agent_code")
        agent_secret = data.get("agent_secret")
        
        print(f"[Gold API] Method: {method}, Agent Code: {agent_code}")
        print(f"[Gold API] Full payload: {json.dumps({**data, 'agent_secret': '***' if agent_secret else None})}")
        
        # Validar credenciais do agente
        agent = db.query(IGameWinAgent).filter(
            IGameWinAgent.agent_code == agent_code,
            IGameWinAgent.is_active == True
        ).first()
        
        if not agent:
            print(f"[Gold API] Agent not found: {agent_code}")
            return {
                "status": 0,
                "msg": "INVALID_AGENT"
            }
        
        # Verificar agent_secret
        # O agent_secret pode estar em credentials ou ser o mesmo que agent_key
        credentials_dict = {}
        if agent.credentials:
            try:
                credentials_dict = json.loads(agent.credentials)
            except Exception:
                pass
        
        # agent_secret pode estar em credentials ou ser o mesmo que agent_key
        expected_secret = credentials_dict.get("agent_secret") or agent.agent_key
        
        if agent_secret != expected_secret:
            print(f"[Gold API] Invalid agent_secret for agent: {agent_code}")
            return {
                "status": 0,
                "msg": "INVALID_SECRET"
            }
        
        # Processar métodos
        if method == "user_balance":
            return await _handle_user_balance(data, agent, db)
        elif method == "transaction":
            return await _handle_transaction(data, agent, db)
        else:
            return {
                "status": 0,
                "msg": "INVALID_METHOD"
            }
            
    except Exception as e:
        print(f"[Gold API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": 0,
            "msg": "INTERNAL_ERROR",
            "error": str(e)
        }


async def _handle_user_balance(data: Dict[str, Any], agent: IGameWinAgent, db: Session) -> Dict[str, Any]:
    """Handle user_balance method - retorna saldo do usuário"""
    user_code = data.get("user_code")
    
    if not user_code:
        return {
            "status": 0,
            "user_balance": 0,
            "msg": "INVALID_PARAMETER"
        }
    
    print(f"[Gold API] Getting balance for user: {user_code}")
    
    # Buscar usuário pelo username (user_code)
    user = db.query(User).filter(User.username == user_code).first()
    
    if not user:
        print(f"[Gold API] User not found: {user_code}")
        return {
            "status": 0,
            "user_balance": 0,
            "msg": "INVALID_USER"
        }
    
    balance = float(user.balance)
    print(f"[Gold API] User balance: {balance}")
    
    return {
        "status": 1,
        "user_balance": balance
    }


async def _handle_transaction(data: Dict[str, Any], agent: IGameWinAgent, db: Session) -> Dict[str, Any]:
    """Handle transaction method - registra transação de jogo"""
    user_code = data.get("user_code")
    user_balance = data.get("user_balance")
    agent_balance = data.get("agent_balance")
    game_type = data.get("game_type")
    
    if not user_code:
        return {
            "status": 0,
            "msg": "INVALID_PARAMETER"
        }
    
    print(f"[Gold API] Processing transaction - user={user_code}, game_type={game_type}")
    
    # Buscar usuário
    user = db.query(User).filter(User.username == user_code).first()
    
    if not user:
        return {
            "status": 0,
            "msg": "INVALID_USER"
        }
    
    # Processar transação baseado no tipo de jogo
    if game_type == "slot":
        slot_data = data.get("slot", {})
        txn_type = slot_data.get("txn_type", "debit_credit")
        bet_money = float(slot_data.get("bet_money", slot_data.get("bet", 0)))
        win_money = float(slot_data.get("win_money", slot_data.get("win", 0)))
        txn_id = slot_data.get("txn_id")
        provider_code = slot_data.get("provider_code")
        game_code = slot_data.get("game_code")
        game_type_detail = slot_data.get("type", "BASE")
        
        print(f"[Gold API] Slot transaction - txn_type={txn_type}, bet={bet_money}, win={win_money}, txn_id={txn_id}")
        
        # Calcular novo saldo baseado no tipo de transação
        if txn_type == "debit":
            # Apenas aposta (debitar)
            new_balance = user.balance - bet_money
            if new_balance < 0:
                return {
                    "status": 0,
                    "user_balance": user.balance,
                    "msg": "INSUFFICIENT_USER_FUNDS"
                }
            user.balance = new_balance
            
            # Criar registro de aposta
            bet = Bet(
                user_id=user.id,
                game_id=game_code,
                game_name=game_code,  # Pode ser melhorado buscando nome do jogo
                provider=provider_code or "IGameWin",
                amount=bet_money,
                win_amount=0.0,
                status=BetStatus.PENDING,
                transaction_id=txn_id or str(uuid.uuid4()),
                external_id=txn_id,
                metadata_json=json.dumps({
                    "txn_type": txn_type,
                    "game_type": game_type_detail,
                    "provider_code": provider_code,
                    "game_code": game_code
                })
            )
            db.add(bet)
            
        elif txn_type == "credit":
            # Apenas ganho (creditar)
            new_balance = user.balance + win_money
            user.balance = new_balance
            
            # Atualizar aposta existente se houver
            if txn_id:
                bet = db.query(Bet).filter(Bet.external_id == txn_id).first()
                if bet:
                    bet.win_amount = win_money
                    bet.status = BetStatus.WON if win_money > 0 else BetStatus.LOST
                    bet.updated_at = datetime.utcnow()
            
        elif txn_type == "debit_credit":
            # Aposta e ganho juntos
            net_change = win_money - bet_money
            new_balance = user.balance + net_change
            
            if user.balance < bet_money:
                return {
                    "status": 0,
                    "user_balance": user.balance,
                    "msg": "INSUFFICIENT_USER_FUNDS"
                }
            
            user.balance = new_balance
            
            # Criar ou atualizar registro de aposta
            if txn_id:
                bet = db.query(Bet).filter(Bet.external_id == txn_id).first()
                if bet:
                    bet.win_amount = win_money
                    bet.status = BetStatus.WON if win_money > bet_money else BetStatus.LOST
                    bet.updated_at = datetime.utcnow()
                else:
                    bet = Bet(
                        user_id=user.id,
                        game_id=game_code,
                        game_name=game_code,
                        provider=provider_code or "IGameWin",
                        amount=bet_money,
                        win_amount=win_money,
                        status=BetStatus.WON if win_money > bet_money else BetStatus.LOST,
                        transaction_id=txn_id or str(uuid.uuid4()),
                        external_id=txn_id,
                        metadata_json=json.dumps({
                            "txn_type": txn_type,
                            "game_type": game_type_detail,
                            "provider_code": provider_code,
                            "game_code": game_code
                        })
                    )
                    db.add(bet)
        
        db.commit()
        
        print(f"[Gold API] Transaction processed - new balance: {user.balance}")
        
        return {
            "status": 1,
            "user_balance": float(user.balance)
        }
    
    else:
        # Outros tipos de jogo (pode ser expandido)
        return {
            "status": 0,
            "msg": "UNSUPPORTED_GAME_TYPE"
        }
