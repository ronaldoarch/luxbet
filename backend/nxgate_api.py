"""
Módulo para integração com a API NXGATE
Documentação: https://api.nxgate.com.br
"""
import httpx
import json
from typing import Optional, Dict, Any
import socket


class NXGateAPI:
    def __init__(self, api_key: str):
        """
        Inicializa a API NXGATE
        
        Args:
            api_key: Chave secreta (api_key) da NXGATE
        """
        self.api_key = api_key
        # Endpoint correto conforme documentação: https://nxgate.com.br/api/pix/sacar
        self.base_url = "https://nxgate.com.br/api"
        self.headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }
    
    async def _get_server_ip(self) -> Optional[str]:
        """Tenta obter o IP público do servidor"""
        try:
            # Tentar obter IP público usando serviço externo
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Tentar múltiplos serviços
                services = [
                    "https://api.ipify.org?format=json",
                    "https://ifconfig.me/ip",
                    "https://icanhazip.com"
                ]
                for service_url in services:
                    try:
                        if "ipify" in service_url:
                            response = await client.get(service_url)
                            if response.status_code == 200:
                                data = response.json()
                                return data.get("ip")
                        else:
                            response = await client.get(service_url)
                            if response.status_code == 200:
                                return response.text.strip()
                    except:
                        continue
        except Exception as e:
            print(f"[NXGate] Erro ao obter IP público: {e}")
        return None
    
    async def _post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Faz requisição POST para a API NXGATE"""
        try:
            # Tentar obter IP do servidor para diagnóstico
            server_ip = await self._get_server_ip()
            if server_ip:
                print(f"[NXGate] IP público do servidor detectado: {server_ip}")
            
            # Headers conforme documentação
            headers = {
                "Content-Type": "application/json",
                "accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                url = f"{self.base_url}{endpoint}"
                print(f"\n{'='*80}")
                print(f"NXGATE Request - URL: {url}")
                print(f"NXGATE Request - Headers: {headers}")
                if server_ip:
                    print(f"NXGATE Request - Server IP: {server_ip}")
                print(f"NXGATE Request - Payload: {json.dumps(payload, indent=2)}")
                print(f"{'='*80}\n")
                
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload
                )
                
                print(f"NXGATE {endpoint} - Status: {response.status_code}")
                print(f"NXGATE {endpoint} - Headers: {dict(response.headers)}")
                print(f"NXGATE {endpoint} - Response: {response.text[:1000]}")
                
                # Verificar se a resposta é HTML (pode ser Cloudflare ou erro de rota)
                content_type = response.headers.get("content-type", "")
                if content_type.startswith("text/html"):
                    print(f"\n{'='*80}")
                    print(f"NXGATE {endpoint} - ⚠️  ERRO: Resposta é HTML, não JSON!")
                    print(f"NXGATE {endpoint} - Content-Type: {content_type}")
                    print(f"NXGATE {endpoint} - Possíveis causas:")
                    print(f"  - Endpoint incorreto ou mudou")
                    print(f"  - API Key inválida ou não autorizada")
                    print(f"  - Cloudflare bloqueando requisição")
                    print(f"NXGATE {endpoint} - HTML Response (primeiros 500 chars):")
                    print(f"{response.text[:500]}")
                    print(f"{'='*80}\n")
                    return None
                
                # Tentar fazer parse do JSON mesmo se status não for 2xx
                try:
                    response_data = response.json()
                except:
                    response_data = None
                
                # Verificar erros específicos antes de fazer raise_for_status
                if response.status_code == 403:
                    # Tentar obter mensagem de erro de várias formas
                    error_message = ""
                    if response_data:
                        error_message = response_data.get("message", "") or response_data.get("error", "") or str(response_data)
                    else:
                        # Se não conseguiu parsear JSON, tentar ler o texto da resposta
                        try:
                            response_text = response.text.lower()
                            if "ip" in response_text and ("não autorizado" in response_text or "nao autorizado" in response_text or "nao autorizado" in response_text):
                                error_message = "IP não autorizado"
                        except:
                            pass
                    
                    # Verificar se é erro de IP não autorizado (várias formas de verificar)
                    is_ip_error = (
                        response_data and (
                            "IP" in str(response_data).upper() and ("não autorizado" in str(response_data).lower() or "nao autorizado" in str(response_data).lower() or "autorizado" in str(response_data).lower())
                        )
                    ) or (
                        "IP" in error_message.upper() and ("não autorizado" in error_message.lower() or "nao autorizado" in error_message.lower() or "autorizado" in error_message.lower())
                    )
                    
                    if is_ip_error:
                        print(f"\n{'='*80}")
                        print(f"NXGATE {endpoint} - ⚠️  ERRO 403: IP não autorizado")
                        print(f"NXGATE {endpoint} - Response: {response_data}")
                        if server_ip:
                            print(f"NXGATE {endpoint} - ⚠️  IP detectado do servidor: {server_ip}")
                            print(f"NXGATE {endpoint} - ⚠️  Verifique se este IP está autorizado na conta NXGate")
                        print(f"{'='*80}\n")
                        # Retornar um dict especial para identificar o erro de IP
                        return {"_error": "IP_NOT_AUTHORIZED", "message": error_message or "IP não autorizado", "detected_ip": server_ip}
                
                response.raise_for_status()
                return response_data
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if e.response else "Sem resposta"
            
            # Verificar se é erro 403 de IP não autorizado
            if e.response and e.response.status_code == 403:
                error_message = ""
                error_json = None
                
                # Tentar parsear JSON do erro
                try:
                    error_json = e.response.json() if e.response else {}
                    error_message = error_json.get("message", "") or error_json.get("error", "") or str(error_json)
                except:
                    # Se não conseguiu parsear JSON, verificar o texto da resposta
                    error_text_lower = error_text.lower()
                    if "ip" in error_text_lower and ("não autorizado" in error_text_lower or "nao autorizado" in error_text_lower):
                        error_message = "IP não autorizado"
                
                # Verificar se é erro de IP não autorizado (várias formas)
                is_ip_error = (
                    error_json and (
                        "IP" in str(error_json).upper() and ("não autorizado" in str(error_json).lower() or "nao autorizado" in str(error_json).lower() or "autorizado" in str(error_json).lower())
                    )
                ) or (
                    "IP" in error_message.upper() and ("não autorizado" in error_message.lower() or "nao autorizado" in error_message.lower() or "autorizado" in error_message.lower())
                ) or (
                    "ip" in error_text.lower() and ("não autorizado" in error_text.lower() or "nao autorizado" in error_text.lower())
                )
                
                if is_ip_error:
                    # Obter IP do servidor se ainda não foi obtido
                    if not server_ip:
                        server_ip = await self._get_server_ip()
                    print(f"\n{'='*80}")
                    print(f"NXGATE {endpoint} - ⚠️  ERRO 403: IP não autorizado")
                    print(f"NXGATE {endpoint} - Response: {error_json or error_text[:500]}")
                    if server_ip:
                        print(f"NXGATE {endpoint} - ⚠️  IP detectado do servidor: {server_ip}")
                        print(f"NXGATE {endpoint} - ⚠️  Verifique se este IP está autorizado na conta NXGate")
                    print(f"{'='*80}\n")
                    return {"_error": "IP_NOT_AUTHORIZED", "message": error_message or "IP não autorizado", "detected_ip": server_ip}
            
            print(f"\n{'='*80}")
            print(f"NXGATE {endpoint} - ❌ ERRO HTTP {e.response.status_code}")
            print(f"NXGATE {endpoint} - Response: {error_text[:1000]}")
            print(f"{'='*80}\n")
            return None
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"NXGATE {endpoint} - ❌ ERRO: {str(e)}")
            print(f"{'='*80}\n")
            return None
    
    async def generate_pix_payment(
        self,
        nome_pagador: str,
        documento_pagador: str,
        valor: float,
        webhook: Optional[str] = None,
        split_users: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Gera código de pagamento PIX (Cash-in)
        Endpoint: POST /pix/gerar
        
        Args:
            nome_pagador: Nome do pagador
            documento_pagador: CPF/CNPJ do pagador (formato: 000.000.000-00)
            valor: Valor da transação
            webhook: URL do webhook para receber atualizações (opcional)
            split_users: Lista de objetos para split (opcional, máximo 2)
        
        Returns:
            Dict com dados do PIX ou None em caso de erro
        """
        payload = {
            "nome_pagador": nome_pagador,
            "documento_pagador": documento_pagador,
            "valor": valor,
            "api_key": self.api_key
        }
        
        if webhook:
            payload["webhook"] = webhook
        
        if split_users:
            payload["split_users"] = split_users
        
        return await self._post("/pix/gerar", payload)
    
    async def withdraw_pix(
        self,
        valor: float,
        chave_pix: str,
        tipo_chave: str,
        documento: str,
        webhook: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Realiza saque via PIX (Cash-out)
        Endpoint: POST /pix/sacar
        URL completa: https://nxgate.com.br/api/pix/sacar
        
        Args:
            valor: Valor da transação
            chave_pix: Chave PIX que irá receber o saque
            tipo_chave: Tipo da chave (CPF, CNPJ, PHONE, EMAIL, RANDOM)
            documento: CPF/CNPJ do recebedor
            webhook: URL do webhook para receber atualizações (opcional)
        
        Returns:
            Dict com dados do saque ou None em caso de erro
        """
        # Formatar valor como string com 2 casas decimais (conforme documentação)
        valor_str = f"{valor:.2f}"
        
        payload = {
            "api_key": self.api_key,
            "valor": valor_str,  # Enviar como string conforme documentação
            "chave_pix": chave_pix,
            "tipo_chave": tipo_chave.upper(),  # Garantir maiúsculas
            "documento": documento
        }
        
        if webhook:
            payload["webhook"] = webhook
        
        return await self._post("/pix/sacar", payload)
    
    @staticmethod
    def parse_webhook_payment(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse do webhook de pagamento (depósito)
        
        Formato esperado:
        - Simples: {"status": "paid", "idTransaction": "..."}
        - Completo: {"type": "QR_CODE_COPY_AND_PASTE_PAID", "data": {...}}
        
        Returns:
            Dict padronizado com: idTransaction, status, amount, payment_date
        """
        result = {
            "idTransaction": None,
            "status": None,
            "amount": None,
            "payment_date": None
        }
        
        # Formato simples
        if "status" in data and "idTransaction" in data:
            result["idTransaction"] = data.get("idTransaction")
            result["status"] = data.get("status")
            if "documento_pagador" in data:
                result["documento_pagador"] = data.get("documento_pagador")
        
        # Formato completo
        if "type" in data and "data" in data:
            data_obj = data.get("data", {})
            result["idTransaction"] = data_obj.get("tx_id") or data_obj.get("qr_code_id")
            result["status"] = data_obj.get("status", "").upper()
            result["amount"] = data_obj.get("amount")
            result["payment_date"] = data_obj.get("payment_date")
            result["end_to_end"] = data_obj.get("end_to_end")
            result["pix_copy_and_paste"] = data_obj.get("pix_copy_and_paste")
        
        return result
    
    @staticmethod
    def parse_webhook_withdrawal(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse do webhook de saque
        
        Formato esperado:
        {
            "type": "PIX_CASHOUT_SUCCESS" ou "PIX_CASHOUT_ERROR",
            "idTransaction": "...",
            "internalreference": "...",  # Pode vir ao invés de idTransaction
            "status": "SUCCESS" ou "ERROR",
            "amount": 0.96,
            ...
        }
        
        Returns:
            Dict padronizado com: idTransaction, status, amount, payment_date
        """
        # NXGate pode enviar idTransaction ou internalreference
        transaction_id = data.get("idTransaction") or data.get("internalreference") or data.get("id")
        
        result = {
            "idTransaction": transaction_id,
            "status": data.get("status", "").upper(),
            "type": data.get("type", ""),
            "amount": data.get("amount"),
            "payment_date": data.get("payment_date"),
            "end_to_end": data.get("end_to_end"),
            "worked": data.get("worked", False),
            "internalreference": data.get("internalreference")  # Manter também o internalreference original
        }
        
        return result
