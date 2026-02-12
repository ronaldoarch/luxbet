"""
Módulo para integração com a API Gatebox.

Tokens (sistema → Gatebox):
- Obtenção: POST /v1/customers/auth/sign-in → resposta: { "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }
- Uso: header Authorization: Bearer <token> em todas as requisições (PIX, saldo, etc.)
- Cache em memória até expirar (~1h); nova autenticação automática quando necessário

Webhooks (Gatebox → sistema):
- Uma única URL para todos os eventos: POST /api/webhooks/gatebox (depósito e saque)
- Gatebox não envia token; payload JSON direto

Endpoints:
- Auth: POST /v1/customers/auth/sign-in
- Cash-In: POST /v1/customers/pix/create-immediate-qrcode
- Status: GET /v1/customers/pix/status
- Cash-Out: POST /v1/customers/pix/withdraw
- Saldo: POST /v1/customers/account/balance
"""
import httpx
from typing import Optional, Dict, Any


class GateboxAPI:
    def __init__(self, username: str, password: str, api_url: str = "https://api.gatebox.com.br"):
        """
        Inicializa a API Gatebox.

        Args:
            username: Usuário (ex: CNPJ 93892492000158)
            password: Senha de acesso
            api_url: URL base da API (ex: https://api.gatebox.com.br)
        """
        self.username = username
        self.password = password
        self.base_url = api_url.rstrip("/")
        self._token: Optional[str] = None

    async def _get_token(self) -> Optional[str]:
        """
        Obtém token de acesso via sign-in. Cache em memória até expirar (~1h).
        Resposta oficial Gatebox: { "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }.
        """
        if self._token:
            return self._token
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/customers/auth/sign-in",
                    json={"username": self.username, "password": self.password},
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                body = response.json()
                if not isinstance(body, dict):
                    self._token = None
                    print(f"[Gatebox] Resposta do sign-in não é objeto: {type(body).__name__}")
                    return None

                def _token_from_obj(obj):
                    if not isinstance(obj, dict):
                        return None
                    return (
                        obj.get("access_token") or obj.get("token") or obj.get("accessToken")
                        or obj.get("value") or obj.get("jwt") or obj.get("bearer") or obj.get("Bearer")
                        or obj.get("credentials") or obj.get("authorization")
                    )

                # 1) Formato oficial Gatebox: { "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }
                self._token = _token_from_obj(body)
                if self._token:
                    return self._token
                if body.get("access_token"):
                    self._token = body["access_token"]
                    return self._token
                if body.get("token"):
                    self._token = body["token"]
                    return self._token
                if body.get("accessToken"):
                    self._token = body["accessToken"]
                    return self._token

                # 2) Token dentro de data (ex.: { "data": { "access_token": "..." } })
                data = body.get("data") if body.get("data") is not None else body
                if data is not body and isinstance(data, dict):
                    self._token = _token_from_obj(data)
                    if self._token:
                        return self._token
                if isinstance(data, dict):
                    self._token = (
                        data.get("access_token") or data.get("token") or data.get("accessToken")
                    )
                if self._token:
                    return self._token

                # 3) Token em stackAuth (string, objeto ou lista; quando stackAuth não é bool)
                if isinstance(data, dict):
                    stack = data.get("stackAuth")
                    if isinstance(stack, str) and stack.strip():
                        self._token = stack.strip()
                    elif isinstance(stack, dict):
                        self._token = _token_from_obj(stack)
                    elif isinstance(stack, list):
                        for item in stack:
                            if isinstance(item, str) and item.strip():
                                self._token = item.strip()
                                break
                            if isinstance(item, dict):
                                self._token = _token_from_obj(item)
                                if self._token:
                                    break

                # 4) Verificar headers da resposta (algumas APIs devolvem token no header)
                if not self._token:
                    auth_header = response.headers.get("Authorization") or response.headers.get("X-Auth-Token") or response.headers.get("X-Token")
                    if auth_header:
                        self._token = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else auth_header.strip()

                if not self._token:
                    keys = list(data.keys()) if isinstance(data, dict) else "n/a"
                    stack = data.get("stackAuth") if isinstance(data, dict) else None
                    stack_info = "n/a"
                    if stack is not None:
                        if isinstance(stack, dict):
                            stack_info = f"dict keys: {list(stack.keys())}"
                        elif isinstance(stack, list):
                            stack_info = f"list len={len(stack)}"
                            if len(stack) > 0 and isinstance(stack[0], dict):
                                stack_info += f" first keys: {list(stack[0].keys())}"
                            elif len(stack) > 0:
                                stack_info += f" first type: {type(stack[0]).__name__}"
                        else:
                            stack_info = f"type: {type(stack).__name__}"
                    print(f"[Gatebox] Token não encontrado. data keys: {keys} | stackAuth: {stack_info}")
                return self._token
        except Exception as e:
            print(f"[Gatebox] Erro ao obter token: {e}")
            return None

    def _auth_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Headers com Bearer token (para uso após _get_token)."""
        t = token or self._token
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {t}" if t else "",
        }

    async def create_pix_deposit(
        self,
        external_id: str,
        amount: float,
        document: str,
        name: str,
        expire_seconds: int = 3600,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        identification: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Cria PIX imediato (Cash-In).
        POST /v1/customers/pix/create-immediate-qrcode
        """
        token = await self._get_token()
        if not token:
            return None
        payload = {
            "externalId": external_id,
            "amount": amount,
            "document": document,
            "name": name,
            "expire": expire_seconds,
        }
        if email is not None:
            payload["email"] = email
        if phone is not None:
            payload["phone"] = phone
        if identification is not None:
            payload["identification"] = identification
        if description is not None:
            payload["description"] = description
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/customers/pix/create-immediate-qrcode",
                    json=payload,
                    headers=self._auth_headers(token),
                )
                print(f"[Gatebox] create-immediate-qrcode Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"[Gatebox] Response: {response.text[:500]}")
                if response.status_code == 422:
                    try:
                        body = response.json()
                        msg = body.get("message")
                        if isinstance(msg, list):
                            msg = "; ".join(str(m) for m in msg)
                        return {"_error": "VALIDATION", "message": msg or "Dados inválidos (ex.: telefone)"}
                    except Exception:
                        return {"_error": "VALIDATION", "message": response.text[:200] or "Dados inválidos"}
                response.raise_for_status()
                body = response.json()
                # Gatebox retorna { "statusCode": 200, "data": { "key": "...", "uuid": "...", ... } }
                if isinstance(body, dict) and "data" in body:
                    return body["data"]
                return body
        except httpx.HTTPStatusError as e:
            print(f"[Gatebox] Erro create_pix_deposit HTTP: {e}")
            return None
        except Exception as e:
            print(f"[Gatebox] Erro create_pix_deposit: {e}")
            return None

    async def get_pix_status(
        self,
        transaction_id: Optional[str] = None,
        external_id: Optional[str] = None,
        end_to_end: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Consulta status de transação PIX.
        GET /v1/customers/pix/status?transactionId=&externalId=&endToEnd=
        """
        token = await self._get_token()
        if not token:
            return None
        params = {}
        if transaction_id:
            params["transactionId"] = transaction_id
        if external_id:
            params["externalId"] = external_id
        if end_to_end:
            params["endToEnd"] = end_to_end
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/customers/pix/status",
                    params=params,
                    headers=self._auth_headers(token),
                )
                response.raise_for_status()
                body = response.json()
                if isinstance(body, dict) and "data" in body:
                    return body["data"]
                return body
        except Exception as e:
            print(f"[Gatebox] Erro get_pix_status: {e}")
            return None

    async def withdraw_pix(
        self,
        external_id: str,
        key: str,
        name: str,
        amount: float,
        document_number: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Saque PIX (Cash-Out).
        POST /v1/customers/pix/withdraw
        """
        token = await self._get_token()
        if not token:
            return None
        payload = {
            "externalId": external_id,
            "key": key,
            "name": name,
            "amount": amount,
        }
        if document_number is not None:
            payload["documentNumber"] = document_number
        if description is not None:
            payload["description"] = description
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/customers/pix/withdraw",
                    json=payload,
                    headers=self._auth_headers(token),
                )
                print(f"[Gatebox] withdraw Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"[Gatebox] Response: {response.text[:500]}")
                response.raise_for_status()
                body = response.json()
                if isinstance(body, dict) and "data" in body:
                    return body["data"]
                return body
        except Exception as e:
            print(f"[Gatebox] Erro withdraw_pix: {e}")
            return None

    async def get_balance(self) -> Optional[Dict[str, Any]]:
        """Consulta saldo da conta. POST /v1/customers/account/balance"""
        token = await self._get_token()
        if not token:
            return None
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/customers/account/balance",
                    json={},
                    headers=self._auth_headers(token),
                )
                response.raise_for_status()
                body = response.json()
                if isinstance(body, dict) and "data" in body:
                    return body["data"]
                return body
        except Exception as e:
            print(f"[Gatebox] Erro get_balance: {e}")
            return None

    async def validate_pix_key(self, pix_key: str) -> Optional[Dict[str, Any]]:
        """Valida chave PIX. GET /v1/customers/pix/pix-search?dict=..."""
        token = await self._get_token()
        if not token:
            return None
        # Remover pontuação
        dict_val = "".join(c for c in pix_key if c.isalnum())
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/customers/pix/pix-search",
                    params={"dict": dict_val},
                    headers=self._auth_headers(token),
                )
                response.raise_for_status()
                body = response.json()
                if isinstance(body, dict) and "data" in body:
                    return body["data"]
                return body
        except Exception as e:
            print(f"[Gatebox] Erro validate_pix_key: {e}")
            return None
