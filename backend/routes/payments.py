"""
Rotas públicas para pagamentos (depósitos e saques) usando SuitPay
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import timezone
from database import get_db
from models import User, Deposit, Withdrawal, Gateway, TransactionStatus, Bet, BetStatus, Affiliate, Manager, FTD, Notification, NotificationType, FTDSettings, UserRole, Promotion, PromotionType
from suitpay_api import SuitPayAPI
from nxgate_api import NXGateAPI
from schemas import DepositResponse, WithdrawalResponse, DepositPixRequest, WithdrawalPixRequest, AffiliateResponse, ManagerCreateSubAffiliate
from dependencies import get_current_user
from auth import get_password_hash
from igamewin_api import get_igamewin_api
from utils import generate_fake_cpf, clean_cpf
from datetime import datetime, timedelta
import json
import uuid
import os

router = APIRouter(prefix="/api/public/payments", tags=["payments"])
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
affiliate_router = APIRouter(prefix="/api/public/affiliate", tags=["affiliate"])
manager_router = APIRouter(prefix="/api/public/manager", tags=["manager"])


def get_active_pix_gateway(db: Session) -> Gateway:
    """Busca gateway PIX ativo"""
    gateway = db.query(Gateway).filter(
        Gateway.type == "pix",
        Gateway.is_active == True
    ).first()
    
    if not gateway:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gateway PIX não configurado ou inativo"
        )
    
    return gateway


def get_payment_client(gateway: Gateway):
    """
    Cria cliente de pagamento baseado no nome do gateway
    Suporta: SuitPay e NXGATE
    """
    try:
        credentials = json.loads(gateway.credentials) if gateway.credentials else {}
        gateway_name = gateway.name.lower()
        print(f"[Payment Client] Criando cliente para gateway: {gateway.name} (nome normalizado: {gateway_name})")
        
        if "nxgate" in gateway_name or "nx" in gateway_name:
            print(f"[Payment Client] Detectado como NXGATE")
            # NXGATE usa apenas api_key
            api_key = credentials.get("api_key")
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="API Key do gateway NXGATE não configurada"
                )
            return NXGateAPI(api_key)
        
        elif "suitpay" in gateway_name or "suit" in gateway_name:
            print(f"[Payment Client] Detectado como SuitPay")
            # SuitPay usa client_id e client_secret
            client_id = credentials.get("client_id") or credentials.get("ci")
            client_secret = credentials.get("client_secret") or credentials.get("cs")
            sandbox = credentials.get("sandbox", True)
            print(f"[Payment Client] SuitPay - Sandbox: {sandbox}, Client ID: {client_id[:10] if client_id else 'None'}...")
            
            if not client_id or not client_secret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Credenciais do gateway SuitPay não configuradas"
                )
            
            return SuitPayAPI(client_id, client_secret, sandbox=sandbox)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gateway '{gateway.name}' não suportado. Use 'NXGATE' ou 'SuitPay'"
            )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credenciais do gateway inválidas"
        )


def apply_promotion_bonus(db: Session, user: User, deposit: Deposit) -> Optional[float]:
    """
    Aplica bônus de promoção quando um depósito é aprovado.
    Retorna o valor do bônus aplicado (ou None se nenhuma promoção aplicável foi encontrada).
    """
    now_utc = datetime.utcnow()
    
    # Buscar promoções ativas e válidas
    promotions = db.query(Promotion).filter(
        Promotion.is_active == True,
        Promotion.start_date <= now_utc,
        Promotion.end_date >= now_utc,
        Promotion.bonus_percentage > 0  # Apenas promoções com bônus
    ).order_by(Promotion.position.desc(), Promotion.created_at.desc()).all()
    
    # Encontrar a primeira promoção aplicável
    for promo in promotions:
        # Verificar se o depósito atende ao mínimo
        if deposit.amount < promo.min_deposit:
            continue
        
        # Calcular bônus
        bonus_amount = (deposit.amount * promo.bonus_percentage) / 100.0
        
        # Aplicar limite máximo se existir
        if promo.max_bonus > 0 and bonus_amount > promo.max_bonus:
            bonus_amount = promo.max_bonus
        
        if bonus_amount > 0:
            # Aplicar bônus ao saldo do usuário (tanto balance quanto bonus_balance)
            db.refresh(user)
            balance_before_bonus = float(user.balance)
            bonus_balance_before = float(user.bonus_balance) if hasattr(user, 'bonus_balance') else 0.0
            user.balance += bonus_amount
            user.bonus_balance += bonus_amount  # Rastrear bônus separadamente (não sacável)
            db.flush()  # Garantir que o bônus seja persistido imediatamente antes do commit
            balance_after_bonus = float(user.balance)
            bonus_balance_after = float(user.bonus_balance) if hasattr(user, 'bonus_balance') else 0.0
            
            print(f"\n{'='*80}")
            print(f"[Promotion] 🎁 BÔNUS APLICADO!")
            print(f"[Promotion] Promoção: {promo.title}")
            print(f"[Promotion] Depósito: R$ {deposit.amount:.2f}")
            print(f"[Promotion] Bônus ({promo.bonus_percentage}%): R$ {bonus_amount:.2f}")
            print(f"[Promotion] Saldo antes do bônus: R$ {balance_before_bonus:.2f}")
            print(f"[Promotion] Saldo após bônus: R$ {balance_after_bonus:.2f}")
            print(f"[Promotion] Bônus não sacável antes: R$ {bonus_balance_before:.2f}")
            print(f"[Promotion] Bônus não sacável após: R$ {bonus_balance_after:.2f}")
            print(f"[Promotion] Saldo sacável: R$ {balance_after_bonus - bonus_balance_after:.2f}")
            print(f"{'='*80}\n")
            
            # Criar notificação sobre o bônus
            notification = Notification(
                title="🎁 Bônus Aplicado!",
                message=f"Você recebeu um bônus de R$ {bonus_amount:.2f} da promoção '{promo.title}'! Seu saldo foi atualizado.",
                type=NotificationType.SUCCESS,
                user_id=user.id,
                is_read=False,
                is_active=True,
                link="/promocoes"
            )
            db.add(notification)
            db.flush()  # Garantir que a notificação também seja persistida
            
            # Refresh do usuário para garantir que o saldo está atualizado no objeto
            db.refresh(user)
            
            # Verificar se o bônus foi aplicado corretamente
            final_balance = float(user.balance)
            expected_balance = balance_before_bonus + bonus_amount
            if abs(final_balance - expected_balance) > 0.01:
                print(f"[Promotion] ⚠️  AVISO: Saldo não corresponde ao esperado após aplicar bônus!")
                print(f"[Promotion] Esperado: R$ {expected_balance:.2f}")
                print(f"[Promotion] Atual: R$ {final_balance:.2f}")
            
            return bonus_amount
    
    return None


def update_affiliate_on_deposit_approved(db: Session, user: User, deposit: Deposit) -> None:
    """
    Chamado quando um depósito é aprovado.
    Atualiza totais do afiliado (total_deposits, FTD/CPA, revshare) e credita o saldo sacável
    do usuário afiliado (CPA e revshare são sacáveis).
    Se o afiliado for sub-afiliado (manager_id preenchido), o gerente também recebe comissão = CPA do sub.
    """
    if not getattr(user, "referred_by_affiliate_id", None):
        return
    affiliate = db.query(Affiliate).filter(Affiliate.id == user.referred_by_affiliate_id).first()
    if not affiliate or not affiliate.is_active:
        return
    affiliate_user = db.query(User).filter(User.id == affiliate.user_id).first()
    if not affiliate_user:
        return
    # Total depositado pelos indicados
    affiliate.total_deposits = (affiliate.total_deposits or 0) + float(deposit.amount)
    # Revshare sobre este depósito → credita no saldo do afiliado (sacável)
    revshare_pct = (affiliate.revshare_percentage or 0) / 100.0
    revshare_amount = float(deposit.amount) * revshare_pct
    affiliate.total_revshare_earned = (affiliate.total_revshare_earned or 0) + revshare_amount
    affiliate.total_earnings = (affiliate.total_earnings or 0) + revshare_amount
    affiliate_user.balance = (affiliate_user.balance or 0) + revshare_amount
    # Revshare do gerente (se sub-afiliado): gerente ganha revshare sobre depósitos dos indicados do sub
    if affiliate.manager_id:
        manager = db.query(Manager).filter(Manager.id == affiliate.manager_id, Manager.is_active == True).first()
        if manager:
            manager_revshare_pct = (manager.revshare_percentage or 0) / 100.0
            manager_revshare = float(deposit.amount) * manager_revshare_pct
            manager.total_revshare_earned = (manager.total_revshare_earned or 0) + manager_revshare
            manager.total_earnings = (manager.total_earnings or 0) + manager_revshare
            manager_user = db.query(User).filter(User.id == manager.user_id).first()
            if manager_user:
                manager_user.balance = (manager_user.balance or 0) + manager_revshare
    # Primeiro depósito (FTD): criar FTD e creditar CPA → credita no saldo do afiliado (sacável)
    existing_ftd = db.query(FTD).filter(FTD.user_id == user.id).first()
    if not existing_ftd:
        ftd = FTD(
            user_id=user.id,
            deposit_id=deposit.id,
            amount=deposit.amount,
            is_first_deposit=True,
            pass_rate=0.0,
            status=TransactionStatus.APPROVED
        )
        db.add(ftd)
        cpa = float(affiliate.cpa_amount or 0)
        affiliate.total_cpa_earned = (affiliate.total_cpa_earned or 0) + cpa
        affiliate.total_earnings = (affiliate.total_earnings or 0) + cpa
        affiliate_user.balance = (affiliate_user.balance or 0) + cpa
        # Se sub-afiliado: gerente ganha comissão = CPA do sub (o que distribuiu)
        if affiliate.manager_id and cpa > 0:
            manager = db.query(Manager).filter(Manager.id == affiliate.manager_id, Manager.is_active == True).first()
            if manager:
                manager.total_cpa_earned = (manager.total_cpa_earned or 0) + cpa
                manager.total_earnings = (manager.total_earnings or 0) + cpa
                manager_user = db.query(User).filter(User.id == manager.user_id).first()
                if manager_user:
                    manager_user.balance = (manager_user.balance or 0) + cpa


@router.post("/deposit/pix", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_pix_deposit(
    request: DepositPixRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria depósito via PIX usando SuitPay
    Conforme documentação oficial: POST /api/v1/gateway/request-qrcode
    
    Args:
        request: Dados do depósito (amount, payer_name, payer_tax_id, payer_email, payer_phone)
    """
    # Usar usuário autenticado
    user = current_user
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    
    # Depósito mínimo (configuração FTD)
    settings = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
    min_deposit = getattr(settings, "min_amount", 2.0) if settings else 2.0
    if request.amount < min_deposit:
        raise HTTPException(
            status_code=400,
            detail=f"Valor mínimo de depósito é R$ {min_deposit:.2f}"
        )
    
    # Gerar CPF falso automaticamente se não fornecido
    payer_tax_id = request.payer_tax_id
    if not payer_tax_id or not payer_tax_id.strip():
        # Gerar CPF falso válido para o depósito
        fake_cpf = generate_fake_cpf()
        payer_tax_id = clean_cpf(fake_cpf)  # Remover formatação para enviar ao gateway
        print(f"[Deposit] CPF não fornecido. Gerando CPF falso para depósito: {fake_cpf}")
    
    # Buscar gateway PIX ativo
    gateway = get_active_pix_gateway(db)
    
    # Criar cliente de pagamento (SuitPay ou NXGATE)
    payment_client = get_payment_client(gateway)
    
    # URL do webhook
    webhook_url = os.getenv("WEBHOOK_BASE_URL", "https://api.luxbet.site")
    
    # Gerar código PIX conforme gateway
    pix_response = None
    id_transaction = None
    pix_code = None
    
    gateway_name = gateway.name.lower()
    
    if isinstance(payment_client, NXGateAPI):
        # NXGATE
        callback_url = f"{webhook_url}/api/webhooks/nxgate/pix-cashin"
        pix_response = await payment_client.generate_pix_payment(
            nome_pagador=request.payer_name,
            documento_pagador=payer_tax_id,
            valor=request.amount,
            webhook=callback_url
        )
        
        if pix_response:
            id_transaction = pix_response.get("idTransaction")
            pix_code = pix_response.get("pix_copy_and_paste") or pix_response.get("qr_code")
    
    elif isinstance(payment_client, SuitPayAPI):
        # SuitPay
        request_number = f"DEP_{user.id}_{int(datetime.utcnow().timestamp())}"
        due_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
        callback_url = f"{webhook_url}/api/webhooks/suitpay/pix-cashin"
        
        pix_response = await payment_client.generate_pix_payment(
            request_number=request_number,
            due_date=due_date,
            amount=request.amount,
            client_name=request.payer_name,
            client_document=payer_tax_id,
            client_email=request.payer_email,
            client_phone=request.payer_phone,
            callback_url=callback_url
        )
        
        if pix_response:
            # Garantir que pix_response é um dict
            if isinstance(pix_response, str):
                try:
                    pix_response = json.loads(pix_response)
                except:
                    pass
            
            if isinstance(pix_response, dict):
                id_transaction = pix_response.get("idTransaction")
                # SuitPay retorna paymentCode diretamente
                pix_code = pix_response.get("paymentCode")
                
                # Log para debug
                print(f"DEBUG SuitPay response type: {type(pix_response)}")
                print(f"DEBUG SuitPay response keys: {list(pix_response.keys())}")
                print(f"DEBUG paymentCode value: {pix_response.get('paymentCode')}")
                print(f"DEBUG paymentCode extracted: {pix_code}")
            else:
                print(f"ERROR: pix_response is not a dict: {type(pix_response)}")
                print(f"ERROR: pix_response value: {pix_response}")
    
    if not pix_response:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao gerar código PIX no gateway. Verifique as credenciais e se o gateway está ativo."
        )
    
    if not id_transaction:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao gerar código PIX: idTransaction não encontrado na resposta. Resposta: {pix_response}"
        )
    
    # Verificar se o status da resposta indica sucesso
    if isinstance(pix_response, dict):
        response_status = pix_response.get("status", "").lower()
        
        # Se status é success mas pix_code ainda está vazio, tentar extrair novamente
        if response_status == "success" and not pix_code:
            pix_code = pix_response.get("paymentCode")
            print(f"DEBUG Retry extraction after success check - paymentCode: {pix_code}")
    
    if not pix_code:
        # Log completo da resposta para debug
        print(f"ERROR: PIX code not found in response: {pix_response}")
        print(f"ERROR: Response type: {type(pix_response)}")
        if isinstance(pix_response, dict):
            print(f"ERROR: Response keys: {list(pix_response.keys())}")
            print(f"ERROR: paymentCode value: {pix_response.get('paymentCode')}")
            print(f"ERROR: status value: {pix_response.get('status')}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Resposta inválida do gateway. Código PIX não encontrado. Resposta: {pix_response}"
        )
    
    # Extrair QR code base64 da resposta
    qr_code_base64 = pix_response.get("paymentCodeBase64") or pix_response.get("base_64_image") or pix_response.get("qr_code_base64")
    
    # Log para debug
    print(f"DEBUG QR Code Base64 disponível: {bool(qr_code_base64)}")
    if qr_code_base64:
        print(f"DEBUG QR Code Base64 length: {len(qr_code_base64) if isinstance(qr_code_base64, str) else 'N/A'}")
    
    # Criar registro de depósito com status PENDING
    # IMPORTANTE: O saldo só será creditado quando o webhook confirmar o pagamento
    deposit = Deposit(
        user_id=user.id,
        gateway_id=gateway.id,
        amount=request.amount,
        status=TransactionStatus.PENDING,  # Aguardar confirmação do pagamento via webhook
        transaction_id=str(uuid.uuid4()),
        external_id=id_transaction,
        metadata_json=json.dumps({
            "pix_code": pix_code,
            "pix_qr_code_base64": qr_code_base64,
            "gateway": gateway.name,
            "gateway_response": pix_response,
            "created_at": datetime.utcnow().isoformat(),
            "waiting_payment": True
        })
    )
    
    db.add(deposit)
    
    # NÃO creditar saldo aqui - aguardar confirmação via webhook
    print(f"[Deposit] Depósito {deposit.id} criado com status PENDING")
    print(f"[Deposit] Usuário: {user.username}")
    print(f"[Deposit] Valor: R$ {deposit.amount:.2f}")
    print(f"[Deposit] ⚠️  Saldo NÃO será creditado até confirmação do pagamento via webhook")
    print(f"[Deposit] QR Code gerado. Aguardando pagamento...")
    
    # Criar notificação informando que o QR code foi gerado
    # A notificação de aprovação será criada pelo webhook quando o pagamento for confirmado
    notification = Notification(
        title="QR Code PIX Gerado",
        message=f"QR Code PIX de R$ {deposit.amount:.2f} gerado. Efetue o pagamento para creditar o saldo.",
        type=NotificationType.INFO,
        user_id=user.id,
        is_read=False,
        is_active=True,
        link="/deposito"
    )
    db.add(notification)
    
    db.commit()
    db.refresh(deposit)
    db.refresh(user)
    
    return deposit


@router.post("/withdrawal/pix", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_pix_withdrawal(
    request: WithdrawalPixRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria saque via PIX usando SuitPay
    Conforme documentação oficial: POST /api/v1/gateway/pix-payment
    
    IMPORTANTE: É necessário cadastrar o IP do servidor na SuitPay
    (GATEWAY/CHECKOUT -> GERENCIAMENTO DE IPs)
    
    Args:
        request: Dados do saque (amount, pix_key, pix_key_type, document_validation)
    """
    # Usar usuário autenticado
    user = current_user
    db.refresh(user)  # Garantir dados atualizados
    
    # Calcular saldo sacável (balance - bonus_balance)
    bonus_balance = float(user.bonus_balance) if hasattr(user, 'bonus_balance') else 0.0
    total_balance = float(user.balance)
    withdrawable_balance = total_balance - bonus_balance
    
    # Verificar saldo sacável
    if withdrawable_balance < request.amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Saldo sacável insuficiente. Saldo total: R$ {total_balance:.2f}, Bônus não sacável: R$ {bonus_balance:.2f}, Saldo sacável: R$ {withdrawable_balance:.2f}"
        )
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    
    # Saque mínimo (configuração FTD)
    settings = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
    min_withdrawal = getattr(settings, "min_withdrawal", 10.0) if settings else 10.0
    if request.amount < min_withdrawal:
        raise HTTPException(
            status_code=400,
            detail=f"Valor mínimo de saque é R$ {min_withdrawal:.2f}"
        )
    
    # Validar tipo de chave
    valid_key_types = ["document", "phoneNumber", "email", "randomKey", "paymentCode"]
    if request.pix_key_type not in valid_key_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de chave inválido. Deve ser um dos: {', '.join(valid_key_types)}"
        )
    
    # Buscar gateway PIX ativo
    gateway = get_active_pix_gateway(db)
    print(f"[Withdrawal] Gateway selecionado: {gateway.name} (ID: {gateway.id}, Tipo: {gateway.type}, Ativo: {gateway.is_active})")
    
    # Criar cliente de pagamento (SuitPay ou NXGATE)
    payment_client = get_payment_client(gateway)
    print(f"[Withdrawal] Cliente de pagamento criado: {type(payment_client).__name__}")
    
    # URL do webhook
    webhook_url = os.getenv("WEBHOOK_BASE_URL", "https://api.luxbet.site")
    
    # Gerar external_id único para controle de duplicidade
    external_id = f"WTH_{user.id}_{int(datetime.utcnow().timestamp())}"
    
    # Realizar transferência PIX conforme gateway
    transfer_response = None
    id_transaction = None
    
    gateway_name = gateway.name.lower()
    print(f"[Withdrawal] Processando saque via {gateway_name.upper()}")
    
    try:
        if isinstance(payment_client, NXGateAPI):
            print(f"[Withdrawal] Usando NXGATE para processar saque")
            # NXGATE - mapear tipos de chave
            tipo_chave_map = {
                "document": "CPF",
                "phoneNumber": "PHONE",
                "email": "EMAIL",
                "randomKey": "RANDOM"
            }
            tipo_chave_nxgate = tipo_chave_map.get(request.pix_key_type, "CPF")
            
            # Garantir que temos um documento válido (obrigatório para NXGate)
            documento = request.document_validation or user.cpf
            if not documento or documento.strip() == "":
                raise HTTPException(
                    status_code=400,
                    detail="Documento (CPF/CNPJ) é obrigatório para saque via NXGate. Por favor, preencha o campo de validação de CPF/CNPJ ou atualize seu CPF no perfil."
                )
            
            # Remover formatação do documento (pontos, traços, barras) para NXGate
            documento_limpo = documento.replace(".", "").replace("-", "").replace("/", "").strip()
            
            # Se o documento não tem 11 ou 14 dígitos, pode estar incorreto
            if len(documento_limpo) not in [11, 14]:
                print(f"[Withdrawal] ⚠️  Documento pode estar incorreto: {documento_limpo} (tamanho: {len(documento_limpo)})")
            
            callback_url = f"{webhook_url}/api/webhooks/nxgate/pix-cashout"
            transfer_response = await payment_client.withdraw_pix(
                valor=request.amount,
                chave_pix=request.pix_key,
                tipo_chave=tipo_chave_nxgate,
                documento=documento_limpo,  # Enviar documento limpo (sem formatação)
                webhook=callback_url
            )
            
            # Verificar se é erro de IP não autorizado
            if transfer_response and transfer_response.get("_error") == "IP_NOT_AUTHORIZED":
                error_message = transfer_response.get("message", "")
                detected_ip = transfer_response.get("detected_ip", "não detectado")
                
                if detected_ip and detected_ip != "não detectado":
                    detail_msg = (
                        f"IP do servidor não autorizado na conta NXGate. "
                        f"IP detectado: {detected_ip}. "
                        f"Para autorizar este IP, acesse o painel da NXGate e adicione este IP na lista de IPs autorizados. "
                        f"Se você não tem acesso ao painel da NXGate, entre em contato com o suporte técnico."
                    )
                else:
                    detail_msg = (
                        f"IP do servidor não autorizado na conta NXGate. {error_message} "
                        f"Por favor, entre em contato com o suporte da NXGate para autorizar o IP do servidor onde a aplicação está hospedada. "
                        f"Você pode encontrar o IP do servidor nas configurações do Coolify ou consultando o provedor de hospedagem."
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=detail_msg
                )
            
            # Processar resposta da NXGate
            if transfer_response:
                # NXGate retorna "internalreference" ao invés de "idTransaction"
                # Também pode retornar "idTransaction" em alguns casos, então verificamos ambos
                id_transaction = transfer_response.get("internalreference") or transfer_response.get("idTransaction")
                
                print(f"[Withdrawal] NXGate Response - Status: {transfer_response.get('status')}, ID: {id_transaction}")
                print(f"[Withdrawal] NXGate Response completa: {transfer_response}")
                
                # Verificar status da resposta da NXGate
                response_status = transfer_response.get("status", "").lower()
                if response_status == "error":
                    error_message = transfer_response.get("message", "Erro desconhecido na API NXGate")
                    print(f"[Withdrawal] ❌ NXGate retornou erro: {error_message}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Erro ao processar saque: {error_message}"
                    )
                elif response_status == "sucesso" or response_status == "success":
                    if id_transaction:
                        print(f"[Withdrawal] ✅ NXGate processou saque com sucesso. ID: {id_transaction}")
                    else:
                        print(f"[Withdrawal] ⚠️  NXGate retornou sucesso mas sem ID de transação")
                else:
                    # Se não tem status claro mas tem internalreference, assumimos sucesso
                    if id_transaction:
                        print(f"[Withdrawal] ✅ NXGate processou saque (status não claro mas tem ID). ID: {id_transaction}")
                    else:
                        print(f"[Withdrawal] ⚠️  Resposta da NXGate sem ID de transação: {transfer_response}")
        
        elif isinstance(payment_client, SuitPayAPI):
            # SuitPay
            print(f"[Withdrawal] Usando SuitPay para processar saque")
            callback_url = f"{webhook_url}/api/webhooks/suitpay/pix-cashout"
            transfer_response = await payment_client.transfer_pix(
                key=request.pix_key,
                type_key=request.pix_key_type,
                value=request.amount,
                callback_url=callback_url,
                document_validation=request.document_validation,
                external_id=external_id
            )
            
            if transfer_response:
                id_transaction = transfer_response.get("idTransaction")
                # Verificar resposta da API SuitPay
                response_status = transfer_response.get("response", "").upper()
                if response_status != "OK":
                    error_messages = {
                        "ACCOUNT_DOCUMENTS_NOT_VALIDATED": "Conta não validada",
                        "NO_FUNDS": "Saldo insuficiente no gateway",
                        "PIX_KEY_NOT_FOUND": "Chave PIX não encontrada",
                        "UNAUTHORIZED_IP": "IP não autorizado. Cadastre o IP do servidor na SuitPay.",
                        "DOCUMENT_VALIDATE": "A chave PIX não pertence ao documento informado",
                        "DUPLICATE_EXTERNAL_ID": "External ID já foi utilizado",
                        "ERROR": "Erro interno no gateway"
                    }
                    error_msg = error_messages.get(response_status, f"Erro: {response_status}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg
                    )
        
        # Validar resposta do gateway
        if not transfer_response:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Erro ao processar transferência PIX no gateway. Nenhuma resposta recebida. Verifique as credenciais e tente novamente."
            )
        
        if not id_transaction:
            # Log detalhado para debug
            print(f"[Withdrawal] ⚠️  Resposta do gateway sem ID de transação:")
            print(f"[Withdrawal] Gateway: {gateway.name}")
            print(f"[Withdrawal] Resposta completa: {transfer_response}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro ao processar transferência PIX: resposta do gateway não contém ID de transação. Resposta: {transfer_response}"
            )
    
    except HTTPException:
        # Re-raise HTTPExceptions (já tratadas)
        raise
    except Exception as e:
        # Tratar outros erros (timeout, conexão, etc.)
        print(f"[Withdrawal] Erro ao processar saque: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com o gateway de pagamento: {str(e)}. Tente novamente em alguns instantes."
        )
    
    # Criar registro de saque
    withdrawal = Withdrawal(
        user_id=user.id,
        gateway_id=gateway.id,
        amount=request.amount,
        status=TransactionStatus.PENDING,
        transaction_id=str(uuid.uuid4()),
        external_id=id_transaction or external_id,
        metadata_json=json.dumps({
            "pix_key": request.pix_key,
            "pix_key_type": request.pix_key_type,
            "document_validation": request.document_validation,
            "external_id": external_id,
            "gateway": gateway.name,
            "gateway_response": transfer_response
        })
    )
    
    # Bloquear saldo do usuário
    db.refresh(user)  # Garantir dados atualizados
    balance_before = float(user.balance)
    bonus_balance_before = float(user.bonus_balance) if hasattr(user, 'bonus_balance') else 0.0
    withdrawable_before = balance_before - bonus_balance_before
    
    # Deduzir apenas do balance (bonus_balance permanece intacto)
    user.balance -= request.amount
    balance_after = float(user.balance)
    bonus_balance_after = float(user.bonus_balance) if hasattr(user, 'bonus_balance') else 0.0
    withdrawable_after = balance_after - bonus_balance_after
    
    print(f"\n{'='*80}")
    print(f"[Withdrawal] 💰 SALDO SENDO DEDUZIDO:")
    print(f"[Withdrawal]   - Usuário: {user.username} (ID: {user.id})")
    print(f"[Withdrawal]   - Saldo total anterior: R$ {balance_before:.2f}")
    print(f"[Withdrawal]   - Bônus não sacável: R$ {bonus_balance_before:.2f}")
    print(f"[Withdrawal]   - Saldo sacável anterior: R$ {withdrawable_before:.2f}")
    print(f"[Withdrawal]   - Valor do saque: R$ {request.amount:.2f}")
    print(f"[Withdrawal]   - Saldo total após dedução: R$ {balance_after:.2f}")
    print(f"[Withdrawal]   - Bônus não sacável (inalterado): R$ {bonus_balance_after:.2f}")
    print(f"[Withdrawal]   - Saldo sacável após dedução: R$ {withdrawable_after:.2f}")
    print(f"{'='*80}\n")
    
    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)
    
    return withdrawal


# ========== WEBHOOKS ==========

@webhook_router.post("/suitpay/pix-cashin")
async def webhook_pix_cashin(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber notificações de PIX Cash-in (depósitos) da SuitPay
    """
    try:
        data = await request.json()
        
        # Buscar gateway PIX ativo para validar hash
        gateway = get_active_pix_gateway(db)
        credentials = json.loads(gateway.credentials) if gateway.credentials else {}
        client_secret = credentials.get("client_secret") or credentials.get("cs")
        
        if not client_secret:
            raise HTTPException(status_code=500, detail="Credenciais do gateway não configuradas")
        
        # Validar hash
        if not SuitPayAPI.validate_webhook_hash(data.copy(), client_secret):
            raise HTTPException(status_code=401, detail="Hash inválido")
        
        # Processar webhook conforme documentação oficial SuitPay
        # Campos esperados: idTransaction, typeTransaction, statusTransaction, 
        # value, payerName, payerTaxId, paymentDate, paymentCode, requestNumber, hash
        id_transaction = data.get("idTransaction")
        status_transaction = data.get("statusTransaction")
        type_transaction = data.get("typeTransaction")  # Deve ser "PIX"
        value = data.get("value")
        request_number = data.get("requestNumber")
        payment_date = data.get("paymentDate")  # Formato: dd/MM/yyyy HH:mm:ss
        payment_code = data.get("paymentCode")
        
        # Buscar depósito pelo external_id ou request_number
        deposit = None
        if id_transaction:
            deposit = db.query(Deposit).filter(Deposit.external_id == id_transaction).first()
        
        if not deposit and request_number:
            # Tentar buscar pelo request_number no metadata
            deposits = db.query(Deposit).filter(
                Deposit.status == TransactionStatus.PENDING
            ).all()
            for d in deposits:
                metadata = json.loads(d.metadata_json) if d.metadata_json else {}
                if metadata.get("request_number") == request_number:
                    deposit = d
                    break
        
        if not deposit:
            return {"status": "ok", "message": "Depósito não encontrado"}
        
        # Atualizar status do depósito
        if status_transaction == "PAID_OUT":
            # Verificar se já foi processado para evitar duplicação
            if deposit.status != TransactionStatus.APPROVED:
                print(f"\n{'='*80}")
                print(f"[Webhook SuitPay] ✅ PAGAMENTO CONFIRMADO!")
                print(f"[Webhook SuitPay] Depósito ID: {deposit.id}")
                print(f"[Webhook SuitPay] Status anterior: {deposit.status}")
                print(f"[Webhook SuitPay] Valor: R$ {deposit.amount:.2f}")
                print(f"{'='*80}\n")
                
                deposit.status = TransactionStatus.APPROVED
                
                # Adicionar saldo ao usuário
                user = db.query(User).filter(User.id == deposit.user_id).first()
                if user:
                    db.refresh(user)  # Garantir dados atualizados
                    balance_before = float(user.balance)
                    user.balance += deposit.amount
                    db.flush()  # Garantir que a mudança é enviada antes do commit
                    balance_after_deposit = float(user.balance)
                    
                    print(f"[Webhook SuitPay] 💰 SALDO ATUALIZADO (DEPÓSITO):")
                    print(f"[Webhook SuitPay]   - Saldo anterior: R$ {balance_before:.2f}")
                    print(f"[Webhook SuitPay]   - Depósito: R$ {deposit.amount:.2f}")
                    print(f"[Webhook SuitPay]   - Saldo após depósito: R$ {balance_after_deposit:.2f}")
                    
                    # Aplicar bônus de promoção se houver
                    bonus_amount = apply_promotion_bonus(db, user, deposit)
                    balance_after_bonus = float(user.balance)
                    
                    # Criar notificação de sucesso
                    message = f"Seu depósito de R$ {deposit.amount:.2f} foi confirmado e creditado na sua conta."
                    if bonus_amount:
                        message += f" Você também recebeu um bônus de R$ {bonus_amount:.2f}!"
                    message += f" Saldo atual: R$ {balance_after_bonus:.2f}"
                    
                    notification = Notification(
                        title="✅ Depósito Aprovado!",
                        message=message,
                        type=NotificationType.SUCCESS,
                        user_id=user.id,
                        is_read=False,
                        is_active=True,
                        link="/conta"
                    )
                    db.add(notification)
                    # Afiliado: atualizar totais e FTD/CPA/revshare
                    update_affiliate_on_deposit_approved(db, user, deposit)
                    print(f"[Webhook SuitPay] 📧 Notificação criada para o usuário")
            else:
                print(f"[Webhook SuitPay] ⚠️  Depósito {deposit.id} já foi processado anteriormente (status: {deposit.status}). Ignorando webhook duplicado.")
        elif status_transaction == "CHARGEBACK":
            if deposit.status == TransactionStatus.APPROVED:
                # Reverter saldo se já foi aprovado
                user = db.query(User).filter(User.id == deposit.user_id).first()
                if user and user.balance >= deposit.amount:
                    user.balance -= deposit.amount
            deposit.status = TransactionStatus.CANCELLED
        
        # Atualizar metadata
        metadata = json.loads(deposit.metadata_json) if deposit.metadata_json else {}
        metadata["webhook_data"] = data
        metadata["webhook_received_at"] = datetime.utcnow().isoformat()
        if status_transaction == "PAID_OUT":
            metadata["approved_at"] = datetime.utcnow().isoformat()
        deposit.metadata_json = json.dumps(metadata)
        
        db.commit()
        
        # Refresh para garantir que os dados estão atualizados
        db.refresh(deposit)
        if 'user' in locals() and user:
            db.refresh(user)
            final_balance_after_commit = float(user.balance)
            print(f"[Webhook SuitPay] ✅ CONFIRMAÇÃO FINAL:")
            print(f"[Webhook SuitPay]   - Depósito {deposit.id} status: {deposit.status}")
            print(f"[Webhook SuitPay]   - Usuário {user.username}")
            print(f"[Webhook SuitPay]   - Saldo confirmado após commit: R$ {final_balance_after_commit:.2f}")
            if deposit.status == TransactionStatus.APPROVED and 'balance_after_bonus' in locals():
                expected_balance = balance_after_bonus
                if abs(final_balance_after_commit - expected_balance) > 0.01:
                    print(f"[Webhook SuitPay] ⚠️  AVISO: Saldo após commit não corresponde ao esperado!")
                    print(f"[Webhook SuitPay]   - Esperado: R$ {expected_balance:.2f}")
                    print(f"[Webhook SuitPay]   - Atual: R$ {final_balance_after_commit:.2f}")
            print(f"[Webhook SuitPay] ✅ Processamento concluído com sucesso!\n")
        
        return {"status": "ok", "message": "Webhook processado com sucesso"}
    
    except Exception as e:
        print(f"Erro ao processar webhook PIX Cash-in: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")


@webhook_router.post("/nxgate/pix-cashin")
async def webhook_nxgate_pix_cashin(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber notificações de PIX Cash-in (depósitos) da NXGATE
    """
    try:
        data = await request.json()
        
        # Parse do webhook NXGATE
        parsed = NXGateAPI.parse_webhook_payment(data)
        id_transaction = parsed.get("idTransaction")
        status_payment = (parsed.get("status") or "").lower() if parsed.get("status") is not None else ""
        
        if not id_transaction:
            return {"status": "received", "message": "idTransaction não encontrado"}
        
        # Buscar depósito pelo external_id
        deposit = db.query(Deposit).filter(Deposit.external_id == id_transaction).first()
        
        if not deposit:
            return {"status": "received", "message": "Depósito não encontrado"}
        
        # Atualizar status do depósito
        if status_payment == "paid":
            # Verificar se já foi processado para evitar duplicação
            old_status = deposit.status
            if old_status != TransactionStatus.APPROVED:
                print(f"\n{'='*80}")
                print(f"[Webhook NXGATE] ✅ PAGAMENTO CONFIRMADO!")
                print(f"[Webhook NXGATE] Depósito ID: {deposit.id}")
                print(f"[Webhook NXGATE] Status anterior: {old_status}")
                print(f"[Webhook NXGATE] Valor: R$ {deposit.amount:.2f}")
                print(f"{'='*80}\n")
                
                deposit.status = TransactionStatus.APPROVED
                
                # Adicionar saldo ao usuário
                user = db.query(User).filter(User.id == deposit.user_id).first()
                if user:
                    db.refresh(user)  # Garantir dados atualizados
                    balance_before = float(user.balance)
                    user.balance += deposit.amount
                    db.flush()  # Garantir que a mudança é enviada antes do commit
                    balance_after_deposit = float(user.balance)
                    
                    print(f"[Webhook NXGATE] 💰 SALDO ATUALIZADO (DEPÓSITO):")
                    print(f"[Webhook NXGATE]   - Saldo anterior: R$ {balance_before:.2f}")
                    print(f"[Webhook NXGATE]   - Depósito: R$ {deposit.amount:.2f}")
                    print(f"[Webhook NXGATE]   - Saldo após depósito: R$ {balance_after_deposit:.2f}")
                    
                    # Aplicar bônus de promoção se houver
                    bonus_amount = apply_promotion_bonus(db, user, deposit)
                    balance_after_bonus = float(user.balance)
                    
                    # Criar notificação de sucesso (apenas uma vez)
                    message = f"Seu depósito de R$ {deposit.amount:.2f} foi confirmado e creditado na sua conta."
                    if bonus_amount:
                        message += f" Você também recebeu um bônus de R$ {bonus_amount:.2f}!"
                    message += f" Saldo atual: R$ {balance_after_bonus:.2f}"
                    
                    notification = Notification(
                        title="✅ Depósito Aprovado!",
                        message=message,
                        type=NotificationType.SUCCESS,
                        user_id=user.id,
                        is_read=False,
                        is_active=True,
                        link="/conta"
                    )
                    db.add(notification)
                    # Afiliado: atualizar totais e FTD/CPA/revshare
                    update_affiliate_on_deposit_approved(db, user, deposit)
                    print(f"[Webhook NXGATE] 📧 Notificação criada para o usuário")
            else:
                print(f"[Webhook NXGATE] ⚠️  Depósito {deposit.id} já foi processado anteriormente (status: {deposit.status}). Ignorando webhook duplicado.")
        
        # Atualizar metadata
        metadata = json.loads(deposit.metadata_json) if deposit.metadata_json else {}
        metadata["webhook_data"] = data
        metadata["webhook_parsed"] = parsed
        metadata["webhook_received_at"] = datetime.utcnow().isoformat()
        if status_payment == "paid":
            metadata["approved_at"] = datetime.utcnow().isoformat()
        deposit.metadata_json = json.dumps(metadata)
        
        db.commit()
        
        # Refresh para garantir que os dados estão atualizados
        db.refresh(deposit)
        if 'user' in locals() and user:
            db.refresh(user)
            final_balance_after_commit = float(user.balance)
            print(f"[Webhook NXGATE] ✅ CONFIRMAÇÃO FINAL:")
            print(f"[Webhook NXGATE]   - Depósito {deposit.id} status: {deposit.status}")
            print(f"[Webhook NXGATE]   - Usuário {user.username}")
            print(f"[Webhook NXGATE]   - Saldo confirmado após commit: R$ {final_balance_after_commit:.2f}")
            if deposit.status == TransactionStatus.APPROVED and 'balance_after_bonus' in locals():
                expected_balance = balance_after_bonus
                if abs(final_balance_after_commit - expected_balance) > 0.01:
                    print(f"[Webhook NXGATE] ⚠️  AVISO: Saldo após commit não corresponde ao esperado!")
                    print(f"[Webhook NXGATE]   - Esperado: R$ {expected_balance:.2f}")
                    print(f"[Webhook NXGATE]   - Atual: R$ {final_balance_after_commit:.2f}")
            print(f"[Webhook NXGATE] ✅ Processamento concluído com sucesso!\n")
        
        return {"status": "received"}
    
    except Exception as e:
        print(f"Erro ao processar webhook NXGATE PIX Cash-in: {str(e)}")
        import traceback
        traceback.print_exc()
        # Retornar 200 mesmo em erro para evitar retries desnecessários
        return {"status": "error", "message": str(e)}


@webhook_router.post("/nxgate/pix-cashout")
async def webhook_nxgate_pix_cashout(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber notificações de PIX Cash-out (saques) da NXGATE
    """
    try:
        data = await request.json()
        
        print(f"\n{'='*80}")
        print(f"[Webhook NXGATE PIX Cash-out] Webhook recebido")
        print(f"[Webhook NXGATE PIX Cash-out] Payload completo: {json.dumps(data, indent=2)}")
        print(f"{'='*80}\n")
        
        # Parse do webhook NXGATE
        parsed = NXGateAPI.parse_webhook_withdrawal(data)
        id_transaction = parsed.get("idTransaction")
        internalreference = parsed.get("internalreference")
        status_withdrawal = parsed.get("status", "").upper()
        withdrawal_type = parsed.get("type", "")
        
        print(f"[Webhook NXGATE PIX Cash-out] ID Transaction: {id_transaction}")
        print(f"[Webhook NXGATE PIX Cash-out] Internal Reference: {internalreference}")
        print(f"[Webhook NXGATE PIX Cash-out] Status: {status_withdrawal}")
        print(f"[Webhook NXGATE PIX Cash-out] Type: {withdrawal_type}")
        
        if not id_transaction and not internalreference:
            print(f"[Webhook NXGATE PIX Cash-out] ⚠️  Nenhum ID de transação encontrado no webhook")
            return {"status": "received", "message": "idTransaction ou internalreference não encontrado"}
        
        # Buscar saque pelo external_id (pode ser idTransaction ou internalreference)
        withdrawal = None
        search_ids = [id_transaction, internalreference]
        
        for search_id in search_ids:
            if search_id:
                withdrawal = db.query(Withdrawal).filter(Withdrawal.external_id == search_id).first()
                if withdrawal:
                    print(f"[Webhook NXGATE PIX Cash-out] ✅ Saque encontrado pelo ID: {search_id}")
                    break
        
        if not withdrawal:
            print(f"[Webhook NXGATE PIX Cash-out] ⚠️  Saque não encontrado com IDs: {search_ids}")
            # Tentar buscar pelo transaction_id também (caso tenha sido salvo diferente)
            if id_transaction:
                withdrawal = db.query(Withdrawal).filter(Withdrawal.transaction_id == id_transaction).first()
            if not withdrawal and internalreference:
                withdrawal = db.query(Withdrawal).filter(Withdrawal.transaction_id == internalreference).first()
            
            if not withdrawal:
                print(f"[Webhook NXGATE PIX Cash-out] ❌ Saque não encontrado após todas as tentativas")
                return {"status": "received", "message": "Saque não encontrado"}
        
        old_status = withdrawal.status
        print(f"[Webhook NXGATE PIX Cash-out] Saque ID: {withdrawal.id}, Status atual: {old_status}")
        
        # Atualizar status do saque
        if withdrawal_type == "PIX_CASHOUT_SUCCESS" or status_withdrawal == "SUCCESS":
            if old_status != TransactionStatus.APPROVED:
                withdrawal.status = TransactionStatus.APPROVED
                print(f"[Webhook NXGATE PIX Cash-out] ✅ Status atualizado para APPROVED")
            else:
                print(f"[Webhook NXGATE PIX Cash-out] ⚠️  Saque já estava aprovado, ignorando webhook duplicado")
        elif withdrawal_type == "PIX_CASHOUT_ERROR" or status_withdrawal == "ERROR":
            # Reverter saldo se foi cancelado (usar old_status para garantir que verificamos o status antes da atualização)
            if old_status == TransactionStatus.PENDING:
                user = db.query(User).filter(User.id == withdrawal.user_id).first()
                if user:
                    db.refresh(user)  # Garantir dados atualizados
                    balance_before = float(user.balance)
                    user.balance += withdrawal.amount
                    balance_after = float(user.balance)
                    print(f"[Webhook NXGATE PIX Cash-out] 💰 Saldo revertido para usuário:")
                    print(f"[Webhook NXGATE PIX Cash-out]   - Saldo anterior: R$ {balance_before:.2f}")
                    print(f"[Webhook NXGATE PIX Cash-out]   - Valor revertido: R$ {withdrawal.amount:.2f}")
                    print(f"[Webhook NXGATE PIX Cash-out]   - Saldo atual: R$ {balance_after:.2f}")
            withdrawal.status = TransactionStatus.REJECTED
            print(f"[Webhook NXGATE PIX Cash-out] ❌ Status atualizado para REJECTED")
        else:
            print(f"[Webhook NXGATE PIX Cash-out] ⚠️  Status não reconhecido: {status_withdrawal}, Type: {withdrawal_type}")
        
        # Atualizar metadata
        metadata = json.loads(withdrawal.metadata_json) if withdrawal.metadata_json else {}
        metadata["webhook_data"] = data
        metadata["webhook_parsed"] = parsed
        metadata["webhook_received_at"] = datetime.utcnow().isoformat()
        withdrawal.metadata_json = json.dumps(metadata)
        
        db.commit()
        db.refresh(withdrawal)
        
        print(f"[Webhook NXGATE PIX Cash-out] ✅ Webhook processado com sucesso. Status final: {withdrawal.status}")
        print(f"{'='*80}\n")
        
        return {"status": "received", "message": "Webhook processado com sucesso"}
    
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"[Webhook NXGATE PIX Cash-out] ❌ ERRO ao processar webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        return {"status": "error", "message": str(e)}


@webhook_router.post("/suitpay/pix-cashout")
async def webhook_pix_cashout(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber notificações de PIX Cash-out (saques) da SuitPay
    """
    try:
        data = await request.json()
        
        # Buscar gateway PIX ativo para validar hash
        gateway = get_active_pix_gateway(db)
        credentials = json.loads(gateway.credentials) if gateway.credentials else {}
        client_secret = credentials.get("client_secret") or credentials.get("cs")
        
        if not client_secret:
            raise HTTPException(status_code=500, detail="Credenciais do gateway não configuradas")
        
        # Validar hash
        if not SuitPayAPI.validate_webhook_hash(data.copy(), client_secret):
            raise HTTPException(status_code=401, detail="Hash inválido")
        
        # Processar webhook
        id_transaction = data.get("idTransaction")
        status_transaction = data.get("statusTransaction")
        
        # Buscar saque pelo external_id
        withdrawal = None
        if id_transaction:
            withdrawal = db.query(Withdrawal).filter(Withdrawal.external_id == id_transaction).first()
        
        if not withdrawal:
            return {"status": "ok", "message": "Saque não encontrado"}
        
        old_status = withdrawal.status
        print(f"[Webhook SuitPay PIX Cash-out] Saque ID: {withdrawal.id}, Status atual: {old_status}")
        
        # Atualizar status do saque
        if status_transaction == "PAID_OUT":
            if old_status != TransactionStatus.APPROVED:
                withdrawal.status = TransactionStatus.APPROVED
                print(f"[Webhook SuitPay PIX Cash-out] ✅ Status atualizado para APPROVED")
            else:
                print(f"[Webhook SuitPay PIX Cash-out] ⚠️  Saque já estava aprovado, ignorando webhook duplicado")
        elif status_transaction == "CANCELED":
            # Reverter saldo se foi cancelado (usar old_status para garantir que verificamos o status antes da atualização)
            if old_status == TransactionStatus.PENDING:
                user = db.query(User).filter(User.id == withdrawal.user_id).first()
                if user:
                    db.refresh(user)  # Garantir dados atualizados
                    balance_before = float(user.balance)
                    user.balance += withdrawal.amount
                    balance_after = float(user.balance)
                    print(f"[Webhook SuitPay PIX Cash-out] 💰 Saldo revertido para usuário:")
                    print(f"[Webhook SuitPay PIX Cash-out]   - Saldo anterior: R$ {balance_before:.2f}")
                    print(f"[Webhook SuitPay PIX Cash-out]   - Valor revertido: R$ {withdrawal.amount:.2f}")
                    print(f"[Webhook SuitPay PIX Cash-out]   - Saldo atual: R$ {balance_after:.2f}")
            withdrawal.status = TransactionStatus.CANCELLED
            print(f"[Webhook SuitPay PIX Cash-out] ❌ Status atualizado para CANCELLED")
        
        # Atualizar metadata
        metadata = json.loads(withdrawal.metadata_json) if withdrawal.metadata_json else {}
        metadata["webhook_data"] = data
        metadata["webhook_received_at"] = datetime.utcnow().isoformat()
        withdrawal.metadata_json = json.dumps(metadata)
        
        db.commit()
        
        return {"status": "ok", "message": "Webhook processado com sucesso"}
    
    except Exception as e:
        print(f"Erro ao processar webhook PIX Cash-out: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")


@webhook_router.post("/igamewin/bet")
async def webhook_igamewin_bet(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber notificações de apostas do IGameWin
    Processa apostas e atualiza saldo do jogador
    
    Campos esperados do IGameWin:
    - user_code: Código do usuário
    - game_code: Código do jogo
    - bet_amount: Valor da aposta
    - win_amount: Valor ganho (0 se perdeu)
    - transaction_id: ID único da transação
    - status: Status da aposta (win/lose)
    """
    try:
        data = await request.json()
        
        # Extrair dados do webhook
        user_code = data.get("user_code") or data.get("userCode")
        game_code = data.get("game_code") or data.get("gameCode")
        bet_amount = float(data.get("bet_amount") or data.get("betAmount") or 0)
        win_amount = float(data.get("win_amount") or data.get("winAmount") or 0)
        transaction_id = data.get("transaction_id") or data.get("transactionId")
        status = data.get("status", "").lower()
        
        if not user_code or not transaction_id:
            return {"status": "error", "message": "user_code e transaction_id são obrigatórios"}
        
        # Converter transaction_id para string (campos são VARCHAR no banco)
        transaction_id_str = str(transaction_id) if transaction_id else None
        
        # Buscar usuário pelo username (user_code)
        user = db.query(User).filter(User.username == user_code).first()
        if not user:
            return {"status": "error", "message": f"Usuário {user_code} não encontrado"}
        
        # Verificar se a aposta já foi processada
        if transaction_id_str:
            existing_bet = db.query(Bet).filter(Bet.transaction_id == transaction_id_str).first()
            if existing_bet:
                return {"status": "ok", "message": "Aposta já processada"}
        
        # Criar registro de aposta
        bet_status = BetStatus.WON if status == "win" else BetStatus.LOST
        if win_amount == 0:
            bet_status = BetStatus.LOST
        
        bet = Bet(
            user_id=user.id,
            game_id=game_code,
            game_name=data.get("game_name") or data.get("gameName") or "Unknown",
            provider="IGameWin",
            amount=bet_amount,
            win_amount=win_amount,
            status=bet_status,
            transaction_id=transaction_id_str,
            external_id=transaction_id_str,
            metadata_json=json.dumps(data)
        )
        
        db.add(bet)
        
        # NOTA: Em Seamless Mode, o saldo já está sendo atualizado pelo endpoint /gold_api
        # quando o IGameWin processa transações. Este webhook é apenas para registro.
        # Não precisamos atualizar saldo aqui para evitar duplicação.
        # O saldo é atualizado diretamente pelo /gold_api em Seamless Mode.
        
        db.commit()
        db.refresh(bet)
        
        return {"status": "ok", "message": "Aposta processada com sucesso", "bet_id": bet.id}
    
    except Exception as e:
        print(f"Erro ao processar webhook IGameWin bet: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")


# ========== AFFILIATE PANEL ==========
@affiliate_router.get("/dashboard", response_model=AffiliateResponse)
async def get_affiliate_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Painel do afiliado - retorna dados do afiliado logado
    
    Retorna 404 se o usuário não for afiliado (comportamento esperado).
    O frontend deve tratar 404 como "não é afiliado", não como erro.
    """
    affiliate = db.query(Affiliate).filter(Affiliate.user_id == current_user.id).first()
    if not affiliate:
        # 404 é esperado quando usuário não é afiliado - não é um erro crítico
        raise HTTPException(status_code=404, detail="Você não é um afiliado")
    
    return affiliate


def _affiliate_period_bounds(period: str):
    """Retorna (start_dt, end_dt) em UTC para o período. end_dt é inclusive (fim do dia)."""
    now = datetime.utcnow()
    today = now.date()
    if period == "this_week":
        # Segunda a hoje
        start = datetime.combine(today - timedelta(days=now.weekday()), datetime.min.time())
        end = now
    elif period == "last_week":
        start = datetime.combine(today - timedelta(days=now.weekday() + 7), datetime.min.time())
        end = datetime.combine(today - timedelta(days=now.weekday() + 1), datetime.min.time()) + timedelta(days=1) - timedelta(seconds=1)
    elif period == "this_month":
        start = datetime.combine(today.replace(day=1), datetime.min.time())
        end = now
    elif period == "last_month":
        first_this = today.replace(day=1)
        first_last = (first_this - timedelta(days=1)).replace(day=1)
        last_day_last = first_this - timedelta(days=1)
        start = datetime.combine(first_last, datetime.min.time())
        end = datetime.combine(last_day_last, datetime.max.time())
    else:
        # default this_month
        start = datetime.combine(today.replace(day=1), datetime.min.time())
        end = now
    return start, end


@affiliate_router.get("/meus-dados")
async def get_affiliate_meus_dados(
    period: str = "this_month",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dados do subordinado (métricas do afiliado) com filtro de período.
    period: this_week | last_week | this_month | last_month
    """
    affiliate = db.query(Affiliate).filter(Affiliate.user_id == current_user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Você não é um afiliado")
    start_dt, end_dt = _affiliate_period_bounds(period)

    # Subordinados = usuários com referred_by_affiliate_id = affiliate.id
    novos_subordinados = db.query(User).filter(
        User.referred_by_affiliate_id == affiliate.id,
        User.created_at >= start_dt,
        User.created_at <= end_dt
    ).count()

    # Depósitos (count e valor) dos subordinados no período
    q_dep = db.query(Deposit).join(User, Deposit.user_id == User.id).filter(
        User.referred_by_affiliate_id == affiliate.id,
        Deposit.status == TransactionStatus.APPROVED,
        Deposit.created_at >= start_dt,
        Deposit.created_at <= end_dt
    )
    depositos_count = q_dep.count()
    valor_deposito = q_dep.with_entities(func.coalesce(func.sum(Deposit.amount), 0)).scalar() or 0.0

    # Primeiros depósitos (FTD) dos subordinados no período
    q_ftd = db.query(FTD).join(User, FTD.user_id == User.id).filter(
        User.referred_by_affiliate_id == affiliate.id,
        FTD.created_at >= start_dt,
        FTD.created_at <= end_dt
    )
    primeiros_depositos_count = q_ftd.count()
    valor_primeiro_deposito = q_ftd.with_entities(func.coalesce(func.sum(FTD.amount), 0)).scalar() or 0.0

    # Usuários registrados com 1º depósito (no período) = quem fez FTD no período
    usuarios_com_1_deposito = primeiros_depositos_count  # mesmo que primeiros_depositos_count (um FTD por usuário)

    # Registro e 1º depósito (valor) - mesmo que valor do primeiro depósito
    registro_e_1_deposito = valor_primeiro_deposito

    # Saques dos subordinados no período
    q_w = db.query(Withdrawal).join(User, Withdrawal.user_id == User.id).filter(
        User.referred_by_affiliate_id == affiliate.id,
        Withdrawal.status == TransactionStatus.APPROVED,
        Withdrawal.created_at >= start_dt,
        Withdrawal.created_at <= end_dt
    )
    numero_saques = q_w.count()
    valor_saque = q_w.with_entities(func.coalesce(func.sum(Withdrawal.amount), 0)).scalar() or 0.0

    # Receber recompensas (CPA + Revshare no período)
    cpa_no_periodo = primeiros_depositos_count * float(affiliate.cpa_amount or 0)
    revshare_no_periodo = valor_deposito * (float(affiliate.revshare_percentage or 0) / 100.0)
    receber_recompensas = cpa_no_periodo + revshare_no_periodo

    # Apostas válidas (soma dos valores apostados pelos subordinados no período)
    apostas_validas = db.query(func.coalesce(func.sum(Bet.amount), 0)).join(User, Bet.user_id == User.id).filter(
        User.referred_by_affiliate_id == affiliate.id,
        Bet.status != BetStatus.CANCELLED,
        Bet.created_at >= start_dt,
        Bet.created_at <= end_dt
    ).scalar() or 0.0

    # V/D diretas = GGR (valor apostado - valor ganho) dos subordinados no período
    total_apostado = db.query(func.coalesce(func.sum(Bet.amount), 0)).join(User, Bet.user_id == User.id).filter(
        User.referred_by_affiliate_id == affiliate.id,
        Bet.status != BetStatus.CANCELLED,
        Bet.created_at >= start_dt,
        Bet.created_at <= end_dt
    ).scalar() or 0.0
    total_ganho = db.query(func.coalesce(func.sum(Bet.win_amount), 0)).join(User, Bet.user_id == User.id).filter(
        User.referred_by_affiliate_id == affiliate.id,
        Bet.status != BetStatus.CANCELLED,
        Bet.created_at >= start_dt,
        Bet.created_at <= end_dt
    ).scalar() or 0.0
    vd_diretas = float(total_apostado) - float(total_ganho)  # positivo = casa ganhou

    return {
        "period": period,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "novos_subordinados": novos_subordinados,
        "depositos": depositos_count,
        "primeiros_depositos": primeiros_depositos_count,
        "usuarios_registrados_com_1_deposito": usuarios_com_1_deposito,
        "valor_deposito": round(valor_deposito, 2),
        "valor_primeiro_deposito": round(valor_primeiro_deposito, 2),
        "registro_e_1_deposito": round(registro_e_1_deposito, 2),
        "valor_saque": round(valor_saque, 2),
        "numero_saques": numero_saques,
        "receber_recompensas": round(receber_recompensas, 2),
        "apostas_validas": round(apostas_validas, 2),
        "vd_diretas": round(vd_diretas, 2),
    }


@affiliate_router.get("/stats")
async def get_affiliate_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estatísticas do afiliado (totais gerais)"""
    affiliate = db.query(Affiliate).filter(Affiliate.user_id == current_user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Você não é um afiliado")
    return {
        "affiliate_code": affiliate.affiliate_code,
        "cpa_amount": affiliate.cpa_amount,
        "revshare_percentage": affiliate.revshare_percentage,
        "total_earnings": affiliate.total_earnings,
        "total_cpa_earned": affiliate.total_cpa_earned,
        "total_revshare_earned": affiliate.total_revshare_earned,
        "total_referrals": affiliate.total_referrals,
        "total_deposits": affiliate.total_deposits,
        "is_active": affiliate.is_active
    }


# ========== MANAGER PANEL ==========
@manager_router.get("/dashboard")
async def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Painel do gerente - retorna dados do gerente logado"""
    manager = db.query(Manager).filter(Manager.user_id == current_user.id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Você não é um gerente")
    subs = db.query(Affiliate).filter(Affiliate.manager_id == manager.id).all()
    return {
        "id": manager.id,
        "user_id": manager.user_id,
        "cpa_pool": manager.cpa_pool,
        "revshare_percentage": manager.revshare_percentage,
        "total_earnings": manager.total_earnings,
        "total_cpa_earned": manager.total_cpa_earned,
        "total_revshare_earned": manager.total_revshare_earned,
        "is_active": manager.is_active,
        "sub_affiliates_count": len(subs),
        "cpa_distributed": sum(float(a.cpa_amount or 0) for a in subs)
    }


@manager_router.get("/sub-affiliates")
async def get_manager_sub_affiliates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista sub-afiliados do gerente"""
    manager = db.query(Manager).filter(Manager.user_id == current_user.id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Você não é um gerente")
    subs = db.query(Affiliate).filter(Affiliate.manager_id == manager.id).all()
    result = []
    for a in subs:
        u = db.query(User).filter(User.id == a.user_id).first()
        result.append({
            "id": a.id,
            "user_id": a.user_id,
            "username": u.username if u else "",
            "email": u.email if u else "",
            "affiliate_code": a.affiliate_code,
            "cpa_amount": a.cpa_amount,
            "revshare_percentage": a.revshare_percentage,
            "total_referrals": a.total_referrals,
            "total_deposits": a.total_deposits,
            "total_earnings": a.total_earnings,
            "is_active": a.is_active
        })
    return result


@manager_router.post("/sub-affiliates", status_code=status.HTTP_201_CREATED)
async def create_manager_sub_affiliate(
    data: ManagerCreateSubAffiliate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Gerente cria um sub-afiliado (novo User + Affiliate)"""
    manager = db.query(Manager).filter(Manager.user_id == current_user.id).first()
    if not manager or not manager.is_active:
        raise HTTPException(status_code=404, detail="Você não é um gerente ativo")
    # Verificar se username/email já existe
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email já cadastrado")
    existing_code = db.query(Affiliate).filter(Affiliate.affiliate_code == data.affiliate_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Código de afiliado já existe")
    # Criar usuário
    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=UserRole.USER,
        balance=0.0
    )
    db.add(user)
    db.flush()
    # Criar afiliado (sub)
    affiliate = Affiliate(
        user_id=user.id,
        manager_id=manager.id,
        affiliate_code=data.affiliate_code,
        cpa_amount=data.cpa_amount,
        revshare_percentage=data.revshare_percentage
    )
    db.add(affiliate)
    db.commit()
    db.refresh(affiliate)
    return {
        "id": affiliate.id,
        "user_id": user.id,
        "affiliate_code": affiliate.affiliate_code,
        "cpa_amount": affiliate.cpa_amount,
        "revshare_percentage": affiliate.revshare_percentage,
        "message": "Sub-afiliado criado com sucesso"
    }
