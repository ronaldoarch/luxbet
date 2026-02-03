from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json
import time

from database import get_db
from dependencies import get_current_admin_user, get_current_user
from models import (
    User, Deposit, Withdrawal, FTD, Gateway, IGameWinAgent, FTDSettings,
    TransactionStatus, UserRole, Bet, BetStatus, Notification, NotificationType,
    Affiliate, Manager, Theme, ProviderOrder, TrackingConfig, SupportConfig, GameCustomization,
    Coupon
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
    ManagerResponse, ManagerCreate, ManagerUpdate, ManagerCreateSubAffiliate,
    ThemeResponse, ThemeCreate, ThemeUpdate,
    ProviderOrderResponse, ProviderOrderCreate, ProviderOrderUpdate,
    TrackingConfigResponse, TrackingConfigCreate, TrackingConfigUpdate,
    SupportConfigResponse, SupportConfigCreate, SupportConfigUpdate,
    GameCustomizationResponse, GameCustomizationCreate, GameCustomizationUpdate,
    CouponResponse, CouponCreate, CouponUpdate
)
from auth import get_password_hash
from igamewin_api import get_igamewin_api

router = APIRouter(prefix="/api/admin", tags=["admin"])
public_router = APIRouter(prefix="/api/public", tags=["public"])
# Router sem prefixo para endpoints que precisam estar na raiz (como /gold_api para IGameWin)
root_router = APIRouter(tags=["root"])

# Cache em memória para providers e games da API IGameWin
# Formato: {chave: {"data": dados, "expires_at": timestamp}}
_igamewin_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutos de cache


def _get_cache_key(prefix: str, *args) -> str:
    """Gera uma chave de cache única"""
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"


def _get_cached(key: str) -> Optional[Any]:
    """Obtém dados do cache se ainda válidos"""
    if key not in _igamewin_cache:
        return None
    cache_entry = _igamewin_cache[key]
    if time.time() > cache_entry["expires_at"]:
        del _igamewin_cache[key]
        return None
    return cache_entry["data"]


def _set_cache(key: str, data: Any, ttl: int = CACHE_TTL_SECONDS):
    """Armazena dados no cache com TTL"""
    _igamewin_cache[key] = {
        "data": data,
        "expires_at": time.time() + ttl
    }


def _clear_cache(pattern: Optional[str] = None):
    """Limpa o cache. Se pattern fornecido, limpa apenas chaves que começam com pattern"""
    if pattern:
        keys_to_delete = [k for k in _igamewin_cache.keys() if k.startswith(pattern)]
        for k in keys_to_delete:
            del _igamewin_cache[k]
    else:
        _igamewin_cache.clear()


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
        settings = FTDSettings(pass_rate=0.0, min_amount=2.0, min_withdrawal=10.0, is_active=True)
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
def _apply_game_customizations(games: list, db: Session) -> list:
    """Aplica customizações de jogos aos dados retornados"""
    if not games:
        return games
    
    # Buscar todas as customizações de uma vez
    game_codes = [g.get("game_code") or g.get("code") or g.get("game_id") or g.get("id") or g.get("slug") for g in games]
    game_codes = [code for code in game_codes if code]
    
    if not game_codes:
        return games
    
    # Dividir em lotes para evitar problemas com muitos parâmetros (limite de 1000 por lote)
    BATCH_SIZE = 1000
    customization_map = {}
    
    for i in range(0, len(game_codes), BATCH_SIZE):
        batch = game_codes[i:i + BATCH_SIZE]
        customizations = db.query(GameCustomization).filter(GameCustomization.game_code.in_(batch)).all()
        for c in customizations:
            customization_map[c.game_code] = c
    
    # Aplicar customizações
    for game in games:
        game_code = game.get("game_code") or game.get("code") or game.get("game_id") or game.get("id") or game.get("slug")
        if game_code and game_code in customization_map:
            custom = customization_map[game_code]
            if custom.custom_name:
                game["name"] = custom.custom_name
                game["game_name"] = custom.custom_name
                game["title"] = custom.custom_name
                game["gameTitle"] = custom.custom_name
            if custom.custom_provider:
                game["provider"] = custom.custom_provider
                game["provider_code"] = custom.custom_provider
                game["provider_name"] = custom.custom_provider
                game["vendor"] = custom.custom_provider
                game["vendor_name"] = custom.custom_provider
    
    return games


def _choose_provider(providers: list, provider_code: Optional[str]) -> Optional[str]:
    chosen = provider_code
    if not chosen:
        active = [p for p in providers if str(p.get("status", 1)) in ["1", "true", "True"]]
        if active:
            chosen = active[0].get("code") or active[0].get("provider_code")
        elif providers:
            chosen = providers[0].get("code") or providers[0].get("provider_code")
    return chosen


def _extract_game_code(game: Dict[str, Any]) -> Optional[str]:
    """Extrai o código do jogo de forma consistente"""
    return (
        game.get("game_code") or 
        game.get("code") or 
        game.get("game_id") or 
        game.get("id") or 
        game.get("slug")
    )


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
    games = _apply_game_customizations(games, db)

    return {
        "providers": providers[:3],  # Limitar a 3 provedores
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

    # Verificar cache para providers
    cache_key_providers = _get_cache_key("providers", api.agent_code)
    cached_providers = _get_cached(cache_key_providers)
    
    if cached_providers is not None:
        providers = cached_providers
    else:
        providers = await api.get_providers()
        if providers is None:
            raise HTTPException(
                status_code=502,
                detail=f"Não foi possível obter provedores da IGameWin ({api.last_error or 'erro desconhecido'})"
            )
        _set_cache(cache_key_providers, providers)
    
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
    
    # Filtrar apenas os 3 provedores prioritários (is_priority = True)
    priority_providers_list = []
    for p in providers:
        code = (p.get("code") or p.get("provider_code") or "").upper().strip()
        if code in normalized_priority_providers:
            priority_providers_list.append(p)
            if len(priority_providers_list) >= 3:
                break
    
    # Se não há provedores prioritários configurados, usar os 3 primeiros da lista ordenada
    if not priority_providers_list:
        priority_providers_list = providers[:3]
    
    # Usar apenas os provedores prioritários para a home
    providers = priority_providers_list
    
    # Se provider_code foi especificado, retorna apenas jogos desse provedor
    if provider_code:
        chosen_provider = _choose_provider(providers, provider_code)
        
        # Verificar cache para games deste provedor
        cache_key_games = _get_cache_key("games", api.agent_code, chosen_provider)
        cached_games = _get_cached(cache_key_games)
        
        if cached_games is not None:
            games = cached_games
        else:
            games = await api.get_games(provider_code=chosen_provider)
            if games is None:
                raise HTTPException(
                    status_code=502,
                    detail=f"Não foi possível obter jogos da IGameWin (verifique provider_code e credenciais do agente). {api.last_error or ''}".strip()
                )
            games = _normalize_games(games, chosen_provider)
            _set_cache(cache_key_games, games)
        
        games = _apply_game_customizations(games, db)
        public_games = []
        game_count = 0
        for g in games:
            if game_count >= 20:  # Limitar a 20 jogos por provedor
                break
            status_val = g.get("status")
            is_active = (status_val == 1) or (status_val is True) or (str(status_val).lower() == "active")
            if not is_active:
                continue
            game_code = _extract_game_code(g)
            if not game_code:
                continue  # Pular jogos sem código válido
            public_games.append({
                "name": g.get("game_name") or g.get("name") or g.get("title") or g.get("gameTitle"),
                "code": game_code,
                "provider": g.get("provider_code") or g.get("provider") or g.get("provider_name") or g.get("vendor") or g.get("vendor_name") or chosen_provider,
                "banner": g.get("banner") or g.get("image") or g.get("icon"),
                "status": "active"
            })
            game_count += 1
        return {
            "providers": providers,  # Apenas os provedores prioritários (máximo 3)
            "provider_code": chosen_provider,
            "games": public_games
        }
    
    # Se não há provider_code, busca jogos de TODOS os provedores
    # Verificar cache para todos os games
    cache_key_all_games = _get_cache_key("all_games", api.agent_code)
    cached_all_games = _get_cached(cache_key_all_games)
    
    if cached_all_games is not None:
        all_games = cached_all_games
    else:
        all_games = []
        all_raw_games = []  # Coletar todos os jogos brutos primeiro
        active_providers = [p for p in providers if str(p.get("status", 1)) in ["1", "true", "True"]] or providers
        
        # Ordenar provedores pela ordem definida no banco (já ordenado acima, mas garantir)
        active_providers = sorted(active_providers, key=sort_providers)
        
        # Filtrar apenas os provedores prioritários (máximo 3)
        priority_active_providers = []
        for p in active_providers:
            code = (p.get("code") or p.get("provider_code") or "").upper().strip()
            if code in normalized_priority_providers:
                priority_active_providers.append(p)
                if len(priority_active_providers) >= 3:
                    break
        
        # Se não há provedores prioritários, usar os 3 primeiros
        if not priority_active_providers:
            priority_active_providers = active_providers[:3]
        
        # Primeiro, coletar todos os jogos brutos apenas dos provedores prioritários
        for provider in priority_active_providers:
            prov_code = provider.get("code") or provider.get("provider_code")
            if not prov_code:
                continue
            
            # Verificar cache para games deste provedor específico
            cache_key_provider_games = _get_cache_key("games", api.agent_code, prov_code)
            cached_provider_games = _get_cached(cache_key_provider_games)
            
            if cached_provider_games is not None:
                games = cached_provider_games
            else:
                games = await api.get_games(provider_code=prov_code)
                if games is None:
                    continue
                games = _normalize_games(games, prov_code)
                _set_cache(cache_key_provider_games, games)
            
            # Adicionar provedor_code a cada jogo para referência posterior
            for g in games:
                g["provider_code"] = prov_code
            
            all_raw_games.extend(games)
        
        # Aplicar customizações UMA VEZ para todos os jogos coletados
        all_raw_games = _apply_game_customizations(all_raw_games, db)
        
        # Agora processar os jogos customizados, limitando a 20 jogos por provedor
        games_per_provider = {}
        for g in all_raw_games:
            status_val = g.get("status")
            is_active = (status_val == 1) or (status_val is True) or (str(status_val).lower() == "active")
            if not is_active:
                continue
            # Usar o código do provedor diretamente para garantir correspondência com a ordenação
            game_code = _extract_game_code(g)
            if not game_code:
                continue  # Pular jogos sem código válido
            prov_code = g.get("provider_code")
            
            # Contar jogos por provedor
            if prov_code not in games_per_provider:
                games_per_provider[prov_code] = 0
            
            # Limitar a 20 jogos por provedor
            if games_per_provider[prov_code] >= 20:
                continue
            
            all_games.append({
                "name": g.get("game_name") or g.get("name") or g.get("title") or g.get("gameTitle"),
                "code": game_code,
                "provider": prov_code,  # Usar o código do provedor diretamente
                "provider_code": prov_code,  # Adicionar também como provider_code para referência
                "banner": g.get("banner") or g.get("image") or g.get("icon"),
                "status": "active"
            })
            games_per_provider[prov_code] += 1
        
        # Cachear resultado final
        _set_cache(cache_key_all_games, all_games)

    return {
        "providers": providers,  # Apenas os provedores prioritários (máximo 3)
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
                    game_code_from_api = _extract_game_code(game)
                    if game_code_from_api and game_code_from_api == game_code:
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
    
    # Variável para controlar o modo de operação
    is_seamless_mode = False
    
    # Detectar modo de operação ANTES de fazer transferências
    print("\n" + "="*80)
    print(f"[Launch Game] 🔍 Detectando modo de operação do IGameWin")
    print(f"[Launch Game] 👤 Usuário: {current_user.username}")
    print(f"[Launch Game] 💰 Saldo no nosso banco: R$ {current_user.balance}")
    print("="*80 + "\n")
    
    # 1. Garantir que o usuário existe no IGameWin
    print(f"[Launch Game] Criando/verificando usuário no IGameWin...")
    user_created = await api.create_user(current_user.username, is_demo=False)
    if not user_created:
        # Se o erro for DUPLICATED_USER, o usuário já existe - continuar normalmente
        if api.last_error and "DUPLICATED_USER" not in api.last_error:
            print(f"[Launch Game] Warning: Could not create user: {api.last_error}")
            # Não bloquear - tentar lançar mesmo assim (usuário pode já existir)
    
    # 2. Tentar verificar saldo para detectar o modo
    print(f"[Launch Game] Verificando saldo do usuário no IGameWin para detectar modo...")
    igamewin_balance = await api.get_user_balance(current_user.username)
    is_seamless_mode = False
    
    if igamewin_balance is None:
        # Verificar se o erro indica Seamless Mode
        if api.last_error and "ERROR_GET_BALANCE_END_POINT" in api.last_error:
            print(f"\n[Launch Game] ✅ DETECTADO: Modo Seamless (Seamless Mode)")
            print(f"[Launch Game] O IGameWin está configurado para chamar nosso /gold_api")
            print(f"[Launch Game] Não faremos transferências - o saldo fica no nosso banco")
            is_seamless_mode = True
            igamewin_balance = 0.0  # Em Seamless Mode, assumimos 0 no IGameWin
        else:
            print(f"[Launch Game] Warning: Não foi possível obter saldo do IGameWin")
            print(f"[Launch Game] Assumindo Transfer Mode e continuando...")
            igamewin_balance = 0.0
    else:
        print(f"[Launch Game] ✅ DETECTADO: Modo Transfer (Transfer Mode)")
        print(f"[Launch Game] Saldo no IGameWin: R$ {igamewin_balance}")
    
    # 3. Se estiver em Seamless Mode, pular todas as transferências
    if is_seamless_mode:
        print(f"\n[Launch Game] ⚡ Modo Seamless detectado - pulando transferências")
        print(f"[Launch Game] O IGameWin vai chamar nosso /gold_api para buscar saldo")
        print(f"[Launch Game] Saldo permanece no nosso banco: R$ {current_user.balance:.2f}")
    else:
        # MODO TRANSFER: Sincronizar saldo antes de lançar
        print(f"\n[Launch Game] 🔄 Modo Transfer - Sincronizando saldo")
        our_balance = float(current_user.balance)
        balance_diff = our_balance - igamewin_balance
    
        print(f"\n[Launch Game] 📊 Análise de saldo:")
        print(f"[Launch Game]   - Nosso banco: R$ {our_balance:.2f}")
        print(f"[Launch Game]   - IGameWin: R$ {igamewin_balance:.2f}")
        print(f"[Launch Game]   - Diferença: R$ {balance_diff:.2f}")
        
        if balance_diff > 0.01:  # Transferir se diferença > 1 centavo (nosso banco tem mais)
            print(f"\n[Launch Game] 💸 Transferindo R$ {balance_diff:.2f} para o IGameWin...")
            transfer_result = await api.transfer_in(current_user.username, balance_diff)
            if transfer_result:
                # Deduzir do nosso banco
                current_user.balance -= balance_diff
                db.flush()
                db.commit()
                db.refresh(current_user)
                print(f"[Launch Game] ✅ Transferência concluída!")
                print(f"[Launch Game] Novo saldo no nosso banco: R$ {current_user.balance:.2f}")
            else:
                print(f"[Launch Game] ❌ Erro na transferência: {api.last_error}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Erro ao transferir saldo para IGameWin: {api.last_error or 'Erro desconhecido'}"
                )
        elif balance_diff < -0.01:  # Se IGameWin tem mais saldo, SINCRONIZAR de volta primeiro
            # IMPORTANTE: Em Transfer Mode, sempre sincronizar saldo do IGameWin para nosso banco primeiro
            # Isso garante que o jogo sempre use apenas o saldo do nosso banco
            print(f"\n[Launch Game] ⚠️  IGameWin tem mais saldo (R$ {abs(balance_diff):.2f} a mais)")
            print(f"[Launch Game] 🔄 Sincronizando saldo do IGameWin para nosso banco primeiro...")
            
            transfer_back_result = await api.transfer_out(current_user.username, abs(balance_diff))
            if transfer_back_result:
                # Adicionar ao nosso banco
                db.refresh(current_user)
                our_balance_before = float(current_user.balance)
                current_user.balance += abs(balance_diff)
                db.flush()
                db.commit()
                db.refresh(current_user)
                our_balance_after_sync = float(current_user.balance)
                print(f"[Launch Game] ✅ Saldo sincronizado!")
                print(f"[Launch Game] Saldo antes: R$ {our_balance_before:.2f}")
                print(f"[Launch Game] Saldo após sincronização: R$ {our_balance_after_sync:.2f}")
                
                # Agora transferir de volta para IGameWin apenas o que temos no nosso banco
                print(f"[Launch Game] 💸 Transferindo R$ {our_balance_after_sync:.2f} para o IGameWin...")
                transfer_result = await api.transfer_in(current_user.username, our_balance_after_sync)
                if transfer_result:
                    current_user.balance = 0.0
                    db.flush()
                    db.commit()
                    db.refresh(current_user)
                    print(f"[Launch Game] ✅ Transferência concluída!")
                    print(f"[Launch Game] Saldo no nosso banco após transferência: R$ {current_user.balance:.2f}")
                else:
                    print(f"[Launch Game] ❌ Erro ao transferir para IGameWin: {api.last_error}")
                    raise HTTPException(
                        status_code=502,
                        detail=f"Erro ao transferir saldo para IGameWin: {api.last_error or 'Erro desconhecido'}"
                    )
            else:
                print(f"[Launch Game] ⚠️  Não foi possível sincronizar saldo do IGameWin: {api.last_error}")
                print(f"[Launch Game] Tentando continuar com o saldo atual...")
                # Tentar transferir apenas o que temos no nosso banco mesmo assim
                if our_balance > 0.01:
                    print(f"[Launch Game] 💸 Transferindo R$ {our_balance:.2f} do nosso banco para IGameWin...")
                    transfer_result = await api.transfer_in(current_user.username, our_balance)
                    if transfer_result:
                        current_user.balance = 0.0
                        db.flush()
                        db.commit()
                        db.refresh(current_user)
                        print(f"[Launch Game] ✅ Transferência parcial concluída!")
        else:
            print(f"\n[Launch Game] ✅ Saldos já estão sincronizados!")
        
        # 4. Verificar saldo final no IGameWin para confirmar (apenas em Transfer Mode)
        final_igamewin_balance = await api.get_user_balance(current_user.username)
        if final_igamewin_balance is not None:
            print(f"[Launch Game] Saldo final no IGameWin: R$ {final_igamewin_balance:.2f}")
        
        print("\n" + "="*80)
        print(f"[Launch Game] ✅ Saldo sincronizado! Pronto para lançar o jogo.")
        print("="*80 + "\n")
    
    # Em Seamless Mode, não verificamos saldo final - o IGameWin vai chamar /gold_api
    # (O código acima já trata isso no bloco if/else do is_seamless_mode)
    
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
                    "Verifique se o campo 'Ponto final do site' está configurado como 'https://api.luxbet.site' "
                    "(URL do backend, não do frontend) no painel administrativo do IGameWin (Agente de atualização). "
                    "Aguarde 2-5 minutos após salvar as configurações."
                )
            )
        
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível iniciar o jogo. {error_detail}"
        )
    
    print(f"[Launch Game] Success - URL length: {len(launch_url)}, starts with: {launch_url[:100]}...")
    print(f"[Launch Game] Full URL: {launch_url}")
    
    # Aviso sobre o modo usado
    if is_seamless_mode:
        print("\n" + "="*80)
        print("[Launch Game] ✅ JOGO LANÇADO EM MODO SEAMLESS")
        print("[Launch Game] ")
        print("[Launch Game] O saldo permanece no nosso banco.")
        print("[Launch Game] O IGameWin vai chamar nosso /gold_api para buscar saldo e processar transações.")
        print("[Launch Game] Não é necessário sincronizar manualmente após jogar.")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("[Launch Game] ✅ JOGO LANÇADO EM MODO TRANSFER")
        print("[Launch Game] ")
        print("[Launch Game] O saldo foi transferido para o IGameWin antes de lançar o jogo.")
        print("[Launch Game] Após jogar, use o endpoint /api/public/games/sync-balance para")
        print("[Launch Game] sincronizar o saldo de volta do IGameWin para nosso banco.")
        print("="*80 + "\n")
    
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


# Cache para evitar sincronizações simultâneas do mesmo usuário
_sync_locks: Dict[str, bool] = {}

@public_router.post("/games/sync-balance")
async def sync_balance_from_igamewin(
    for_withdrawal: bool = Query(False, description="Se True, não transfere saldo de volta para IGameWin (para saque)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sincroniza o saldo do IGameWin de volta para nosso banco de dados.
    Use este endpoint após jogar para atualizar o saldo do usuário.
    Protegido contra chamadas simultâneas para evitar race conditions.
    
    Args:
        for_withdrawal: Se True, apenas sincroniza do IGameWin para nosso banco,
                       sem transferir de volta. Use quando o usuário vai sacar.
    """
    # Verificar se já está sincronizando para este usuário
    lock_key = f"sync_{current_user.username}"
    if _sync_locks.get(lock_key, False):
        print(f"[Sync Balance] ⚠️  Sincronização já em andamento para {current_user.username}. Ignorando chamada duplicada.")
        return {
            "status": "pending",
            "message": "Sincronização já em andamento. Aguarde alguns segundos."
        }
    
    # Bloquear sincronização para este usuário
    _sync_locks[lock_key] = True
    
    try:
        api = get_igamewin_api(db)
        if not api:
            raise HTTPException(
                status_code=400,
                detail="Nenhum agente IGameWin ativo configurado"
            )
        
        print("\n" + "="*80)
        print(f"[Sync Balance] 🔄 Sincronizando saldo do IGameWin")
        print(f"[Sync Balance] 👤 Usuário: {current_user.username}")
        print("="*80 + "\n")
        
        # 1. Obter saldo atual do nosso banco (refresh para garantir dados atualizados)
        db.refresh(current_user)
        our_balance = float(current_user.balance)
        print(f"[Sync Balance] Saldo no nosso banco: R$ {our_balance:.2f}")
        
        # 2. Obter saldo atual do IGameWin
        igamewin_balance = await api.get_user_balance(current_user.username)
        if igamewin_balance is None:
            raise HTTPException(
                status_code=502,
                detail=f"Não foi possível obter saldo do IGameWin: {api.last_error or 'Erro desconhecido'}"
            )
        
        # Garantir que o saldo do IGameWin é um número válido
        try:
            igamewin_balance = float(igamewin_balance)
        except (ValueError, TypeError):
            print(f"[Sync Balance] ⚠️  Saldo do IGameWin inválido: {igamewin_balance}")
            raise HTTPException(
                status_code=502,
                detail=f"Saldo inválido retornado pelo IGameWin: {igamewin_balance}"
            )
        
        print(f"[Sync Balance] Saldo no IGameWin: R$ {igamewin_balance:.2f}")
        
        # 3. Calcular diferença
        balance_diff = igamewin_balance - our_balance
        
        print(f"\n[Sync Balance] 📊 Análise:")
        print(f"[Sync Balance]   - Nosso banco: R$ {our_balance:.2f}")
        print(f"[Sync Balance]   - IGameWin: R$ {igamewin_balance:.2f}")
        print(f"[Sync Balance]   - Diferença: R$ {balance_diff:.2f}")
        print(f"[Sync Balance]   - balance_diff > 0? {balance_diff > 0}")
        print(f"[Sync Balance]   - balance_diff < 0? {balance_diff < 0}")
        
        # 4. Validar diferença - ignorar diferenças muito pequenas (menos de 5 centavos)
        # EXCETO se nosso banco está zerado e IGameWin tem saldo - nesse caso sincronizar sempre
        if abs(balance_diff) < 0.05 and not (igamewin_balance > 0 and our_balance == 0):
            # Diferença menor que 5 centavos E não é caso de banco zerado com saldo no IGameWin
            print(f"\n[Sync Balance] ✅ Saldos já estão sincronizados! (diferença de R$ {abs(balance_diff):.2f} é muito pequena)")
            return {
                "status": "ok",
                "message": "Saldos já estão sincronizados",
                "our_balance": our_balance,
                "igamewin_balance": igamewin_balance,
                "difference": balance_diff
            }
        
        # Se nosso banco está zerado mas IGameWin tem saldo, garantir sincronização
        if igamewin_balance > 0 and our_balance == 0:
            print(f"[Sync Balance] ⚠️  Aviso: IGameWin tem saldo (R$ {igamewin_balance:.2f}) mas nosso banco está zerado. Sincronizando...")
            # Forçar balance_diff positivo para entrar no fluxo correto
            if balance_diff <= 0:
                balance_diff = igamewin_balance
                print(f"[Sync Balance] Corrigindo balance_diff para: R$ {balance_diff:.2f}")
        
        # 5. Transferir diferença
        if balance_diff > 0:  # IGameWin tem mais saldo - transferir para nosso banco
            print(f"\n[Sync Balance] 💸 Transferindo R$ {balance_diff:.2f} do IGameWin para nosso banco...")
            print(f"[Sync Balance] Saldo antes da transferência: R$ {our_balance:.2f}")
            print(f"[Sync Balance] Saldo esperado após transferência: R$ {our_balance + balance_diff:.2f}")
            
            transfer_result = await api.transfer_out(current_user.username, balance_diff)
            if transfer_result:
                # Refresh antes de modificar para garantir dados atualizados
                db.refresh(current_user)
                our_balance_before_update = float(current_user.balance)
                
                # Adicionar ao nosso banco
                current_user.balance += balance_diff
                db.flush()  # Garantir que as mudanças são enviadas ao banco antes do commit
                db.commit()
                db.refresh(current_user)  # Atualizar objeto com dados do banco após commit
                
                print(f"[Sync Balance] ✅ Transferência concluída!")
                print(f"[Sync Balance] Saldo antes da atualização: R$ {our_balance_before_update:.2f}")
                print(f"[Sync Balance] Novo saldo no nosso banco: R$ {current_user.balance:.2f}")
                
                # Verificar se o saldo foi atualizado corretamente
                if abs(current_user.balance - (our_balance_before_update + balance_diff)) > 0.01:
                    print(f"[Sync Balance] ⚠️  AVISO: Saldo não corresponde ao esperado!")
                    print(f"[Sync Balance] Esperado: R$ {our_balance_before_update + balance_diff:.2f}")
                    print(f"[Sync Balance] Atual: R$ {current_user.balance:.2f}")
                
                result = {
                    "status": "ok",
                    "message": f"Saldo sincronizado com sucesso. Transferidos R$ {balance_diff:.2f} do IGameWin.",
                    "our_balance_before": our_balance,
                    "our_balance_after": float(current_user.balance),
                    "igamewin_balance": igamewin_balance,
                    "transferred": balance_diff
                }
                # Garantir que o commit foi persistido antes de retornar
                return result
            else:
                print(f"[Sync Balance] ❌ Erro na transferência: {api.last_error}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Erro ao transferir saldo do IGameWin: {api.last_error or 'Erro desconhecido'}"
                )
        else:  # Nosso banco tem mais saldo - transferir para IGameWin (caso raro, mas pode acontecer)
            # IMPORTANTE: Se for para saque, NÃO transferir de volta para IGameWin
            # O saldo deve ficar no nosso banco para poder sacar
            if for_withdrawal:
                print(f"\n[Sync Balance] ⚠️  Sincronização para saque: Nosso banco tem mais saldo (R$ {our_balance:.2f})")
                print(f"[Sync Balance] IGameWin tem: R$ {igamewin_balance:.2f}")
                print(f"[Sync Balance] ✅ Mantendo saldo no nosso banco para saque. Não transferindo de volta para IGameWin.")
                return {
                    "status": "ok",
                    "message": "Saldo já está no nosso banco. Pronto para saque.",
                    "our_balance_before": our_balance,
                    "our_balance_after": our_balance,
                    "igamewin_balance": igamewin_balance,
                    "difference": balance_diff,
                    "for_withdrawal": True
                }
            
            # PROTEÇÃO: Não zerar saldo se nosso banco tem saldo e IGameWin está zerado
            # Isso pode indicar um problema - melhor sincronizar do IGameWin para nosso banco
            if our_balance > 0 and igamewin_balance == 0:
                print(f"\n[Sync Balance] ⚠️  ATENÇÃO: Nosso banco tem saldo (R$ {our_balance:.2f}) mas IGameWin está zerado.")
                print(f"[Sync Balance] Isso pode indicar que o saldo deveria estar no IGameWin.")
                print(f"[Sync Balance] Transferindo saldo do nosso banco para IGameWin...")
            
            print(f"\n[Sync Balance] 💸 Transferindo R$ {abs(balance_diff):.2f} do nosso banco para IGameWin...")
            print(f"[Sync Balance] Saldo antes da transferência: R$ {our_balance:.2f}")
            print(f"[Sync Balance] Saldo esperado após transferência: R$ {our_balance + balance_diff:.2f}")
            
            # Verificar se a transferência não vai zerar incorretamente o saldo
            expected_balance = our_balance + balance_diff  # balance_diff é negativo
            if expected_balance < 0:
                print(f"[Sync Balance] ❌ ERRO: Transferência resultaria em saldo negativo! Abortando.")
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro: Transferência resultaria em saldo negativo. Saldo atual: R$ {our_balance:.2f}, Transferência: R$ {abs(balance_diff):.2f}"
                )
            
            transfer_result = await api.transfer_in(current_user.username, abs(balance_diff))
            if transfer_result:
                # Refresh antes de modificar para garantir dados atualizados
                db.refresh(current_user)
                our_balance_before_update = float(current_user.balance)
                
                # Deduzir do nosso banco
                current_user.balance += balance_diff  # balance_diff é negativo aqui
                db.flush()  # Garantir que as mudanças são enviadas ao banco antes do commit
                db.commit()
                db.refresh(current_user)  # Atualizar objeto com dados do banco após commit
                
                print(f"[Sync Balance] ✅ Transferência concluída!")
                print(f"[Sync Balance] Saldo antes da atualização: R$ {our_balance_before_update:.2f}")
                print(f"[Sync Balance] Novo saldo no nosso banco: R$ {current_user.balance:.2f}")
                
                # Verificar se o saldo foi atualizado corretamente
                expected_balance_after = our_balance_before_update + balance_diff
                if abs(current_user.balance - expected_balance_after) > 0.01:
                    print(f"[Sync Balance] ⚠️  AVISO: Saldo não corresponde ao esperado!")
                    print(f"[Sync Balance] Esperado: R$ {expected_balance_after:.2f}")
                    print(f"[Sync Balance] Atual: R$ {current_user.balance:.2f}")
                
                # Verificar se o saldo está correto após o commit
                if current_user.balance < 0:
                    print(f"[Sync Balance] ❌ ERRO CRÍTICO: Saldo ficou negativo após commit! Revertendo...")
                    db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail="Erro crítico: Saldo ficou negativo após sincronização"
                    )
                
                result = {
                    "status": "ok",
                    "message": f"Saldo sincronizado com sucesso. Transferidos R$ {abs(balance_diff):.2f} para IGameWin.",
                    "our_balance_before": our_balance,
                    "our_balance_after": float(current_user.balance),
                    "igamewin_balance": igamewin_balance,
                    "transferred": balance_diff
                }
                # Garantir que o commit foi persistido antes de retornar
                return result
            else:
                print(f"[Sync Balance] ❌ Erro na transferência: {api.last_error}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Erro ao transferir saldo para IGameWin: {api.last_error or 'Erro desconhecido'}"
                )
    finally:
        # Sempre liberar o lock, mesmo em caso de erro
        _sync_locks[lock_key] = False


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
        s = start_date.replace('Z', '+00:00').strip()
        start = datetime.fromisoformat(s) if 'T' in s else datetime.combine(datetime.strptime(s[:10], '%Y-%m-%d').date(), datetime.min.time())
    else:
        start = datetime.combine(date.today(), datetime.min.time())
    
    if end_date:
        e = end_date.replace('Z', '+00:00').strip()
        if 'T' in e:
            end = datetime.fromisoformat(e)
        else:
            from datetime import time as dt_time
            end = datetime.combine(datetime.strptime(e[:10], '%Y-%m-%d').date(), dt_time(23, 59, 59))
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
    
    if user_id is not None:
        query = query.filter(Notification.user_id == user_id)
    
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


# ========== COUPONS ==========
@router.get("/coupons", response_model=List[CouponResponse])
async def get_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Listar cupons"""
    query = db.query(Coupon)
    if is_active is not None:
        query = query.filter(Coupon.is_active == is_active)
    coupons = query.order_by(desc(Coupon.created_at)).offset(skip).limit(limit).all()
    return coupons


@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Criar cupom"""
    existing = db.query(Coupon).filter(Coupon.code == coupon_data.code.strip().upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de cupom já existe")
    coupon = Coupon(**coupon_data.model_dump())
    coupon.code = coupon.code.strip().upper()
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.put("/coupons/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int,
    coupon_data: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualizar cupom"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    update_data = coupon_data.model_dump(exclude_unset=True)
    if "code" in update_data and update_data["code"]:
        update_data["code"] = update_data["code"].strip().upper()
    for field, value in update_data.items():
        setattr(coupon, field, value)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deletar cupom"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    db.delete(coupon)
    db.commit()


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
        revshare_percentage=affiliate_data.revshare_percentage,
        manager_id=affiliate_data.manager_id
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


# ========== MANAGERS (GERENTES) ==========
@router.get("/managers", response_model=List[ManagerResponse])
async def get_managers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lista todos os gerentes"""
    managers = db.query(Manager).offset(skip).limit(limit).all()
    return managers


@router.get("/managers/{manager_id}", response_model=ManagerResponse)
async def get_manager(
    manager_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Busca um gerente específico"""
    manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Gerente não encontrado")
    return manager


@router.post("/managers", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
async def create_manager(
    manager_data: ManagerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cria um novo gerente"""
    user = db.query(User).filter(User.id == manager_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    existing = db.query(Manager).filter(Manager.user_id == manager_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este usuário já é um gerente")
    manager = Manager(
        user_id=manager_data.user_id,
        cpa_pool=manager_data.cpa_pool,
        revshare_percentage=manager_data.revshare_percentage
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager


@router.put("/managers/{manager_id}", response_model=ManagerResponse)
async def update_manager(
    manager_id: int,
    manager_data: ManagerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualiza um gerente"""
    manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Gerente não encontrado")
    if manager_data.cpa_pool is not None:
        manager.cpa_pool = manager_data.cpa_pool
    if manager_data.revshare_percentage is not None:
        manager.revshare_percentage = manager_data.revshare_percentage
    if manager_data.is_active is not None:
        manager.is_active = manager_data.is_active
    db.commit()
    db.refresh(manager)
    return manager


@router.delete("/managers/{manager_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manager(
    manager_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deleta um gerente"""
    manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Gerente não encontrado")
    db.delete(manager)
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


@public_router.get("/minimums")
async def get_minimums(db: Session = Depends(get_db)):
    """Depósito mínimo e saque mínimo (público, para validação no frontend)"""
    settings = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
    if not settings:
        return {"min_deposit": 2.0, "min_withdrawal": 10.0}
    return {
        "min_deposit": getattr(settings, "min_amount", 2.0) or 2.0,
        "min_withdrawal": getattr(settings, "min_withdrawal", 10.0) or 10.0,
    }


@public_router.get("/notifications")
async def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter notificações do usuário: próprias ou globais (user_id = null)"""
    notifications = db.query(Notification).filter(
        Notification.is_active == True,
        or_(
            Notification.user_id == current_user.id,
            Notification.user_id.is_(None)
        )
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
    """Marcar notificação como lida (apenas notificações do usuário; globais não são alteradas no DB)"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    if notification.user_id is not None and notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    # Só atualiza is_read se for notificação do usuário (globais ficam "não lidas" no DB para outros)
    if notification.user_id == current_user.id:
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

# Endpoint de diagnóstico para verificar configuração do Seamless Mode
@public_router.get("/diagnostics/seamless")
async def seamless_diagnostics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint de diagnóstico para verificar configuração do Seamless Mode"""
    agent = db.query(IGameWinAgent).filter(IGameWinAgent.is_active == True).first()
    
    if not agent:
        return {
            "status": "error",
            "message": "Nenhum agente IGameWin ativo encontrado",
            "user_balance": float(current_user.balance),
            "username": current_user.username
        }
    
    return {
        "status": "ok",
        "user": {
            "username": current_user.username,
            "balance": float(current_user.balance),
            "balance_formatted": f"R$ {current_user.balance:.2f}"
        },
        "igamewin_agent": {
            "agent_code": agent.agent_code,
            "api_url": agent.api_url,
            "is_active": agent.is_active
        },
        "gold_api_endpoints": [
            "https://luxbet.site/gold_api",
            "https://api.luxbet.site/gold_api",
            "https://luxbet.site/api/public/gold_api",
            "https://api.luxbet.site/api/admin/gold_api"
        ],
        "configuration_checklist": {
            "site_endpoint": "Configure no painel IGameWin: 'Ponto final do site' = https://api.luxbet.site (URL do backend)",
            "mode": "Configure como 'Seamless Mode' (não Transfer ou Continuous)",
            "wait_time": "Aguarde 2-5 minutos após salvar as configurações",
            "test_endpoint": "Teste acessando: https://api.luxbet.site/gold_api (deve retornar JSON)"
        },
        "what_to_look_for": {
            "in_logs": "Procure por: '⚡⚡⚡ CHAMADA RECEBIDA NO /gold_api ⚡⚡⚡'",
            "when_playing": "Quando você jogar, o IGameWin DEVE chamar /gold_api para obter saldo e processar transações",
            "if_not_working": "Se não aparecer chamadas ao /gold_api nos logs, o IGameWin não está configurado corretamente"
        }
    }

# Endpoint também em /api/gold_api para garantir compatibilidade
@public_router.post("/gold_api")
async def igamewin_gold_api_public(request: Request, db: Session = Depends(get_db)):
    """Endpoint /api/public/gold_api para compatibilidade"""
    print(f"[Gold API Public] ===== REQUEST RECEIVED AT /api/public/gold_api =====")
    return await igamewin_gold_api(request, db)

# Endpoint também em /api/admin/gold_api para garantir acesso via api.luxbet.site
@router.post("/gold_api")
async def igamewin_gold_api_admin(request: Request, db: Session = Depends(get_db)):
    """Endpoint /api/admin/gold_api - redireciona para função principal"""
    print(f"[Gold API Admin] ===== REQUEST RECEIVED AT /api/admin/gold_api =====")
    return await igamewin_gold_api(request, db)

# Função principal que contém a lógica do endpoint /gold_api
# Esta função NÃO tem decorador - ela é chamada pelos endpoints acima
async def igamewin_gold_api(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para modo Seamless do IGameWin.
    Implementa os métodos: user_balance e transaction
    """
    # Log MUITO VISÍVEL no início para garantir que capturamos todas as chamadas
    print("\n" + "="*80)
    print("[Gold API] ⚡⚡⚡ CHAMADA RECEBIDA NO /gold_api ⚡⚡⚡")
    print("="*80 + "\n")
    
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
    """Handle user_balance method - retorna saldo do usuário
    
    IMPORTANTE: Em Seamless Mode, o IGameWin usa este saldo como fonte da verdade.
    O saldo retornado aqui é o que aparece no jogo.
    """
    print("\n" + "="*80)
    print("[Gold API] 💰💰💰 USER_BALANCE REQUEST 💰💰💰")
    print("="*80 + "\n")
    
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
    
    # IMPORTANTE: Em Seamless Mode, sempre retornamos o saldo do nosso banco
    # O IGameWin usa este valor como fonte da verdade para o jogo
    # NOTA: IGameWin pode esperar valores em centavos (multiplicar por 100) ou reais
    # Verificar documentação: se espera centavos, fazer: balance = float(user.balance) * 100
    balance = float(user.balance)
    
    # Log detalhado para debug
    print(f"[Gold API] ===== USER BALANCE REQUEST =====")
    print(f"[Gold API] User: {user_code}")
    print(f"[Gold API] Balance in DB (reais): {user.balance}")
    print(f"[Gold API] Balance being returned: {balance}")
    print(f"[Gold API] This balance will be used by IGameWin as the game balance")
    print(f"[Gold API] =================================")
    
    return {
        "status": 1,
        "user_balance": balance
    }


async def _handle_transaction(data: Dict[str, Any], agent: IGameWinAgent, db: Session) -> Dict[str, Any]:
    """Handle transaction method - registra transação de jogo"""
    print("\n" + "="*80)
    print("[Gold API] 💸💸💸 TRANSACTION REQUEST 💸💸💸")
    print("="*80 + "\n")
    
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
        print(f"[Gold API] Current balance before transaction: {user.balance}")
        
        # Calcular novo saldo baseado no tipo de transação
        if txn_type == "debit":
            # Apenas aposta (debitar)
            new_balance = user.balance - bet_money
            if new_balance < 0:
                print(f"[Gold API] Insufficient funds - current: {user.balance}, bet: {bet_money}")
                return {
                    "status": 0,
                    "user_balance": user.balance,
                    "msg": "INSUFFICIENT_USER_FUNDS"
                }
            user.balance = new_balance
            print(f"[Gold API] Debit applied - bet: {bet_money}, new balance: {user.balance}")
            
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
            print(f"[Gold API] Credit applied - win: {win_money}, new balance: {user.balance}")
            
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
                print(f"[Gold API] Insufficient funds - current: {user.balance}, bet: {bet_money}")
                return {
                    "status": 0,
                    "user_balance": user.balance,
                    "msg": "INSUFFICIENT_USER_FUNDS"
                }
            
            user.balance = new_balance
            print(f"[Gold API] Debit+Credit applied - bet: {bet_money}, win: {win_money}, net_change: {net_change}, new balance: {user.balance}")
            
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
        db.refresh(user)  # Garantir que temos o valor atualizado
        
        final_balance = float(user.balance)
        
        # Log detalhado para debug
        print(f"[Gold API] ===== TRANSACTION PROCESSED =====")
        print(f"[Gold API] User: {user_code}")
        print(f"[Gold API] Transaction type: {txn_type}")
        print(f"[Gold API] Bet: {bet_money}, Win: {win_money}")
        print(f"[Gold API] Final balance in DB (reais): {user.balance}")
        print(f"[Gold API] Final balance being returned: {final_balance}")
        print(f"[Gold API] This balance ({final_balance}) is now the source of truth for the game")
        print(f"[Gold API] ===================================")
        
        return {
            "status": 1,
            "user_balance": final_balance
        }
    
    else:
        # Outros tipos de jogo (pode ser expandido)
        return {
            "status": 0,
            "msg": "UNSUPPORTED_GAME_TYPE"
        }


# ========== SINCRONIZAÇÃO DE SALDO ==========
@public_router.post("/sync-balance")
async def sync_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para forçar sincronização do saldo.
    Útil quando há dessincronização entre jogo e carteira.
    """
    # Buscar saldo atual do banco
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.refresh(user)  # Garantir dados atualizados
    
    print(f"[Sync Balance] Forcing balance sync for user: {current_user.username}, balance: {user.balance}")
    
    return {
        "status": "success",
        "balance": float(user.balance),
        "message": "Saldo sincronizado"
    }


# ========== GAME CUSTOMIZATION ==========
@router.get("/game-customizations", response_model=List[GameCustomizationResponse])
async def get_game_customizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lista todas as customizações de jogos"""
    customizations = db.query(GameCustomization).all()
    return customizations


@router.get("/game-customizations/{game_code}", response_model=GameCustomizationResponse)
async def get_game_customization(
    game_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtém customização de um jogo específico"""
    customization = db.query(GameCustomization).filter(GameCustomization.game_code == game_code).first()
    if not customization:
        raise HTTPException(status_code=404, detail="Customização não encontrada")
    return customization


@router.post("/game-customizations", response_model=GameCustomizationResponse, status_code=status.HTTP_201_CREATED)
async def create_game_customization(
    customization_data: GameCustomizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cria ou atualiza customização de um jogo"""
    existing = db.query(GameCustomization).filter(GameCustomization.game_code == customization_data.game_code).first()
    
    if existing:
        # Atualizar existente
        if customization_data.custom_name is not None:
            existing.custom_name = customization_data.custom_name
        if customization_data.custom_provider is not None:
            existing.custom_provider = customization_data.custom_provider
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        # Limpar cache de games para refletir mudanças
        _clear_cache("games")
        _clear_cache("all_games")
        return existing
    else:
        # Criar novo
        customization = GameCustomization(**customization_data.dict())
        db.add(customization)
        db.commit()
        db.refresh(customization)
        # Limpar cache de games para refletir mudanças
        _clear_cache("games")
        _clear_cache("all_games")
        return customization


@router.put("/game-customizations/{game_code}", response_model=GameCustomizationResponse)
async def update_game_customization(
    game_code: str,
    customization_data: GameCustomizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualiza customização de um jogo"""
    customization = db.query(GameCustomization).filter(GameCustomization.game_code == game_code).first()
    if not customization:
        raise HTTPException(status_code=404, detail="Customização não encontrada")
    
    if customization_data.custom_name is not None:
        customization.custom_name = customization_data.custom_name
    if customization_data.custom_provider is not None:
        customization.custom_provider = customization_data.custom_provider
    customization.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(customization)
    # Limpar cache de games para refletir mudanças
    _clear_cache("games")
    _clear_cache("all_games")
    return customization


@router.delete("/game-customizations/{game_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_customization(
    game_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Remove customização de um jogo"""
    customization = db.query(GameCustomization).filter(GameCustomization.game_code == game_code).first()
    if not customization:
        raise HTTPException(status_code=404, detail="Customização não encontrada")
    
    db.delete(customization)
    db.commit()
    # Limpar cache de games para refletir mudanças
    _clear_cache("games")
    _clear_cache("all_games")
    return None
