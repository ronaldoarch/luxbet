"""
Módulo para integração com a API SuitPay
Documentação: https://sandbox.ws.suitpay.app (sandbox) ou https://ws.suitpay.app (produção)
"""
import httpx
import json
from typing import Optional, Dict, Any
import os


class SuitPayAPI:
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        """
        Inicializa a API SuitPay
        
        Args:
            client_id: Client ID (ci) da SuitPay
            client_secret: Client Secret (cs) da SuitPay
            sandbox: Se True, usa ambiente sandbox, senão usa produção
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://sandbox.ws.suitpay.app" if sandbox else "https://ws.suitpay.app"
        self.headers = {
            "ci": client_id,
            "cs": client_secret,
            "Content-Type": "application/json"
        }
    
    async def _post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Faz requisição POST para a API SuitPay"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    json=payload
                )
                # Log da resposta para debug
                response_text = response.text
                print(f"SuitPay {endpoint} - Status: {response.status_code}")
                print(f"SuitPay {endpoint} - Response: {response_text[:500]}")
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if e.response else "Sem resposta"
            print(f"Erro HTTP SuitPay {endpoint}: {e.response.status_code} - {error_text}")
            return None
        except Exception as e:
            print(f"Erro ao chamar SuitPay {endpoint}: {str(e)}")
            return None
    
    async def generate_pix_payment(
        self,
        value: float,
        payer_name: str,
        payer_tax_id: str,
        request_number: str,
        url_callback: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Gera código de pagamento PIX (Cash-in)
        
        Args:
            value: Valor do pagamento
            payer_name: Nome do pagador
            payer_tax_id: CPF/CNPJ do pagador
            request_number: Número único da requisição (para controle)
            url_callback: URL do webhook (opcional)
        
        Returns:
            Dict com dados do PIX ou None em caso de erro
        """
        payload = {
            "value": value,
            "payerName": payer_name,
            "payerTaxId": payer_tax_id,
            "requestNumber": request_number
        }
        
        if url_callback:
            payload["urlCallback"] = url_callback
        
        # Endpoint correto conforme documentação SuitPay
        # POST /api/v1/gateway/pix/create
        return await self._post("/api/v1/gateway/pix/create", payload)
    
    async def transfer_pix(
        self,
        value: float,
        destination_name: str,
        destination_tax_id: str,
        destination_bank: str,
        destination_account: str,
        destination_account_type: str = "CHECKING",  # CHECKING ou SAVINGS
        url_callback: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Realiza transferência via PIX (Cash-out)
        
        Args:
            value: Valor a transferir
            destination_name: Nome do destinatário
            destination_tax_id: CPF/CNPJ do destinatário
            destination_bank: Código do banco (ex: "001" para Banco do Brasil)
            destination_account: Número da conta
            destination_account_type: Tipo de conta (CHECKING ou SAVINGS)
            url_callback: URL do webhook (opcional)
        
        Returns:
            Dict com dados da transferência ou None em caso de erro
        """
        payload = {
            "value": value,
            "destinationName": destination_name,
            "destinationTaxId": destination_tax_id,
            "destinationBank": destination_bank,
            "destinationAccount": destination_account,
            "destinationAccountType": destination_account_type
        }
        
        if url_callback:
            payload["urlCallback"] = url_callback
        
        # Endpoint correto conforme documentação SuitPay
        # POST /api/v1/gateway/pix/transfer
        return await self._post("/api/v1/gateway/pix/transfer", payload)
    
    @staticmethod
    def validate_webhook_hash(data: Dict[str, Any], client_secret: str) -> bool:
        """
        Valida o hash do webhook recebido da SuitPay
        
        IMPORTANTE: Conforme documentação oficial da SuitPay:
        "Mantenha a ordem dos valores contidos consistente com a ordem dos valores recebidos no JSON"
        
        Args:
            data: Dados do webhook (JSON) - deve manter ordem original
            client_secret: Client Secret (cs) da SuitPay
        
        Returns:
            True se o hash for válido, False caso contrário
        """
        import hashlib
        import copy
        
        # Faz cópia para não modificar o original
        data_copy = copy.deepcopy(data)
        
        # Remove o hash do dict para calcular
        received_hash = data_copy.pop("hash", None)
        if not received_hash:
            return False
        
        # IMPORTANTE: Concatena valores na ORDEM ORIGINAL do JSON recebido
        # Não ordenar alfabeticamente! A documentação exige manter a ordem original
        values = []
        for key, value in data_copy.items():
            if value is not None:
                values.append(str(value))
        
        # Concatena com client_secret
        string_to_hash = "".join(values) + client_secret
        
        # Calcula SHA-256
        calculated_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
        
        # Compara hashes (case-insensitive conforme documentação)
        return calculated_hash.lower() == received_hash.lower()
