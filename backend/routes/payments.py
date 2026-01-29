"""
Rotas públicas para pagamentos (depósitos e saques) usando SuitPay
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User, Deposit, Withdrawal, Gateway, TransactionStatus, Bet, BetStatus, Affiliate, Notification, NotificationType
from suitpay_api import SuitPayAPI
from nxgate_api import NXGateAPI
from schemas import DepositResponse, WithdrawalResponse, DepositPixRequest, WithdrawalPixRequest, AffiliateResponse
from dependencies import get_current_user
from igamewin_api import get_igamewin_api
from utils import generate_fake_cpf, clean_cpf
from datetime import datetime, timedelta
import json
import uuid
import os

router = APIRouter(prefix="/api/public/payments", tags=["payments"])
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
affiliate_router = APIRouter(prefix="/api/public/affiliate", tags=["affiliate"])


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
        
        if "nxgate" in gateway_name or "nx" in gateway_name:
            # NXGATE usa apenas api_key
            api_key = credentials.get("api_key")
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="API Key do gateway NXGATE não configurada"
                )
            return NXGateAPI(api_key)
        
        elif "suitpay" in gateway_name or "suit" in gateway_name:
            # SuitPay usa client_id e client_secret
            client_id = credentials.get("client_id") or credentials.get("ci")
            client_secret = credentials.get("client_secret") or credentials.get("cs")
            sandbox = credentials.get("sandbox", True)
            
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
    
    # Criar registro de depósito
    deposit = Deposit(
        user_id=user.id,
        gateway_id=gateway.id,
        amount=request.amount,
        status=TransactionStatus.APPROVED,  # Aprovar automaticamente
        transaction_id=str(uuid.uuid4()),
        external_id=id_transaction,
        metadata_json=json.dumps({
            "pix_code": pix_code,
            "pix_qr_code_base64": qr_code_base64,
            "gateway": gateway.name,
            "gateway_response": pix_response,
            "auto_approved": True,
            "approved_at": datetime.utcnow().isoformat()
        })
    )
    
    db.add(deposit)
    
    # Aprovar automaticamente e creditar saldo
    balance_before = float(user.balance)
    user.balance += deposit.amount
    balance_after = float(user.balance)
    
    print(f"[Deposit Auto-Approval] Depósito {deposit.id} aprovado automaticamente")
    print(f"[Deposit Auto-Approval] Usuário: {user.username}")
    print(f"[Deposit Auto-Approval] Valor: R$ {deposit.amount:.2f}")
    print(f"[Deposit Auto-Approval] Saldo atualizado - Antes: R$ {balance_before:.2f}, Depósito: R$ {deposit.amount:.2f}, Depois: R$ {balance_after:.2f}")
    
    # Criar notificação de sucesso
    notification = Notification(
        title="Depósito Aprovado",
        message=f"Seu depósito de R$ {deposit.amount:.2f} foi aprovado e creditado na sua conta.",
        type=NotificationType.SUCCESS,
        user_id=user.id,
        is_read=False,
        is_active=True
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
    
    # Verificar saldo
    if user.balance < request.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    
    # Validar tipo de chave
    valid_key_types = ["document", "phoneNumber", "email", "randomKey", "paymentCode"]
    if request.pix_key_type not in valid_key_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de chave inválido. Deve ser um dos: {', '.join(valid_key_types)}"
        )
    
    # Buscar gateway PIX ativo
    gateway = get_active_pix_gateway(db)
    
    # Criar cliente de pagamento (SuitPay ou NXGATE)
    payment_client = get_payment_client(gateway)
    
    # URL do webhook
    webhook_url = os.getenv("WEBHOOK_BASE_URL", "https://api.luxbet.site")
    
    # Gerar external_id único para controle de duplicidade
    external_id = f"WTH_{user.id}_{int(datetime.utcnow().timestamp())}"
    
    # Realizar transferência PIX conforme gateway
    transfer_response = None
    id_transaction = None
    
    gateway_name = gateway.name.lower()
    
    if isinstance(payment_client, NXGateAPI):
        # NXGATE - mapear tipos de chave
        tipo_chave_map = {
            "document": "CPF",
            "phoneNumber": "PHONE",
            "email": "EMAIL",
            "randomKey": "RANDOM"
        }
        tipo_chave_nxgate = tipo_chave_map.get(request.pix_key_type, "CPF")
        
        callback_url = f"{webhook_url}/api/webhooks/nxgate/pix-cashout"
        transfer_response = await payment_client.withdraw_pix(
            valor=request.amount,
            chave_pix=request.pix_key,
            tipo_chave=tipo_chave_nxgate,
            documento=request.document_validation or user.cpf or "",
            webhook=callback_url
        )
        
        if transfer_response:
            id_transaction = transfer_response.get("idTransaction")
    
    elif isinstance(payment_client, SuitPayAPI):
        # SuitPay
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
    
    if not transfer_response or not id_transaction:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao processar transferência PIX no gateway. Verifique as credenciais."
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
    user.balance -= request.amount
    
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
                print(f"[Webhook SuitPay] Processando depósito {deposit.id} - Status atual: {deposit.status}, Valor: R$ {deposit.amount:.2f}")
                deposit.status = TransactionStatus.APPROVED
                # Adicionar saldo ao usuário
                user = db.query(User).filter(User.id == deposit.user_id).first()
                if user:
                    balance_before = user.balance
                    user.balance += deposit.amount
                    balance_after = user.balance
                    print(f"[Webhook SuitPay] Saldo atualizado - Antes: R$ {balance_before:.2f}, Depósito: R$ {deposit.amount:.2f}, Depois: R$ {balance_after:.2f}")
                    
                    # Criar notificação de sucesso
                    notification = Notification(
                        title="Depósito Aprovado!",
                        message=f"Seu depósito de R$ {deposit.amount:.2f} foi aprovado e creditado na sua conta.",
                        type=NotificationType.SUCCESS,
                        user_id=user.id,
                        is_read=False,
                        is_active=True,
                        link="/conta"
                    )
                    db.add(notification)
            else:
                print(f"[Webhook SuitPay] Depósito {deposit.id} já foi processado anteriormente (status: {deposit.status}). Ignorando webhook duplicado.")
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
        deposit.metadata_json = json.dumps(metadata)
        
        db.commit()
        
        # Refresh para garantir que os dados estão atualizados
        db.refresh(deposit)
        if 'user' in locals() and user:
            db.refresh(user)
            print(f"[Webhook SuitPay] Saldo confirmado após commit - Usuário {user.username}: R$ {user.balance:.2f}")
        
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
                print(f"[Webhook NXGATE] Processando depósito {deposit.id} - Status atual: {old_status}, Valor: R$ {deposit.amount:.2f}")
                deposit.status = TransactionStatus.APPROVED
                # Adicionar saldo ao usuário
                user = db.query(User).filter(User.id == deposit.user_id).first()
                if user:
                    balance_before = user.balance
                    user.balance += deposit.amount
                    balance_after = user.balance
                    print(f"[Webhook NXGATE] Saldo atualizado - Antes: R$ {balance_before:.2f}, Depósito: R$ {deposit.amount:.2f}, Depois: R$ {balance_after:.2f}")
                    
                    # Criar notificação de sucesso (apenas uma vez)
                    notification = Notification(
                        title="Depósito Aprovado!",
                        message=f"Seu depósito de R$ {deposit.amount:.2f} foi aprovado e creditado na sua conta.",
                        type=NotificationType.SUCCESS,
                        user_id=user.id,
                        is_read=False,
                        is_active=True,
                        link="/conta"
                    )
                    db.add(notification)
            else:
                print(f"[Webhook NXGATE] Depósito {deposit.id} já foi processado anteriormente (status: {deposit.status}). Ignorando webhook duplicado.")
        
        # Atualizar metadata
        metadata = json.loads(deposit.metadata_json) if deposit.metadata_json else {}
        metadata["webhook_data"] = data
        metadata["webhook_parsed"] = parsed
        metadata["webhook_received_at"] = datetime.utcnow().isoformat()
        deposit.metadata_json = json.dumps(metadata)
        
        db.commit()
        
        # Refresh para garantir que os dados estão atualizados
        db.refresh(deposit)
        if 'user' in locals() and user:
            db.refresh(user)
            print(f"[Webhook NXGATE] Saldo confirmado após commit - Usuário {user.username}: R$ {user.balance:.2f}")
        
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
        
        # Parse do webhook NXGATE
        parsed = NXGateAPI.parse_webhook_withdrawal(data)
        id_transaction = parsed.get("idTransaction")
        status_withdrawal = parsed.get("status", "").upper()
        withdrawal_type = parsed.get("type", "")
        
        if not id_transaction:
            return {"status": "received", "message": "idTransaction não encontrado"}
        
        # Buscar saque pelo external_id
        withdrawal = db.query(Withdrawal).filter(Withdrawal.external_id == id_transaction).first()
        
        if not withdrawal:
            return {"status": "received", "message": "Saque não encontrado"}
        
        # Atualizar status do saque
        if withdrawal_type == "PIX_CASHOUT_SUCCESS" or status_withdrawal == "SUCCESS":
            withdrawal.status = TransactionStatus.APPROVED
        elif withdrawal_type == "PIX_CASHOUT_ERROR" or status_withdrawal == "ERROR":
            # Reverter saldo se foi cancelado
            if withdrawal.status == TransactionStatus.PENDING:
                user = db.query(User).filter(User.id == withdrawal.user_id).first()
                if user:
                    user.balance += withdrawal.amount
            withdrawal.status = TransactionStatus.REJECTED
        
        # Atualizar metadata
        metadata = json.loads(withdrawal.metadata_json) if withdrawal.metadata_json else {}
        metadata["webhook_data"] = data
        metadata["webhook_parsed"] = parsed
        metadata["webhook_received_at"] = datetime.utcnow().isoformat()
        withdrawal.metadata_json = json.dumps(metadata)
        
        db.commit()
        
        return {"status": "received"}
    
    except Exception as e:
        print(f"Erro ao processar webhook NXGATE PIX Cash-out: {str(e)}")
        import traceback
        traceback.print_exc()
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
        
        # Atualizar status do saque
        if status_transaction == "PAID_OUT":
            withdrawal.status = TransactionStatus.APPROVED
        elif status_transaction == "CANCELED":
            # Reverter saldo se foi cancelado
            if withdrawal.status == TransactionStatus.PENDING:
                user = db.query(User).filter(User.id == withdrawal.user_id).first()
                if user:
                    user.balance += withdrawal.amount
            withdrawal.status = TransactionStatus.CANCELLED
        
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
        
        # Buscar usuário pelo username (user_code)
        user = db.query(User).filter(User.username == user_code).first()
        if not user:
            return {"status": "error", "message": f"Usuário {user_code} não encontrado"}
        
        # Verificar se a aposta já foi processada
        existing_bet = db.query(Bet).filter(Bet.transaction_id == transaction_id).first()
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
            transaction_id=transaction_id,
            external_id=transaction_id,
            metadata_json=json.dumps(data)
        )
        
        db.add(bet)
        
        # NOTA: Em Seamless Mode, o saldo já está sendo atualizado pelo endpoint /gold_api
        # quando o IGameWin processa transações. Este webhook é apenas para registro.
        # Não precisamos atualizar saldo aqui para evitar duplicação.
        # 
        # Se você estiver usando Transfer Mode, descomente o código abaixo:
        # user.balance -= bet_amount
        # if win_amount > 0:
        #     user.balance += win_amount
        
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


@affiliate_router.get("/stats")
async def get_affiliate_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estatísticas do afiliado"""
    affiliate = db.query(Affiliate).filter(Affiliate.user_id == current_user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Você não é um afiliado")
    
    # Buscar usuários referenciados por este afiliado (via affiliate_code no metadata)
    # Isso depende de como você armazena a referência do afiliado nos usuários
    # Por enquanto, retornamos os dados do afiliado
    
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
