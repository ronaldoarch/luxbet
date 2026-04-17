"""
Integração com a API pública SarrixPay (Enterprise).
Base: https://apiv1.sarrixpay.com — autenticação OAuth2 client credentials + Bearer.
Documentação: PIX cash-in/out, transações e webhooks normalizados.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import httpx

from utils import normalize_phone_for_gatebox


class SarrixPayAPI:
    """Cliente async para SarrixPay (token curto + endpoints PIX)."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://apiv1.sarrixpay.com",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    async def _get_access_token(self) -> Optional[str]:
        """POST /auth/integrations/token — cache até ~1h (renova 60s antes)."""
        now = time.time()
        if self._access_token and now < self._token_expires_at - 60:
            return self._access_token
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    f"{self.base_url}/auth/integrations/token",
                    headers={"Content-Type": "application/json"},
                    json={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
                text = r.text
                print(f"[SarrixPay] token Status: {r.status_code} body[:300]={text[:300]}")
                if r.status_code != 200:
                    try:
                        err = r.json()
                        msg = err.get("message") or err.get("error") or text
                    except Exception:
                        msg = text[:500]
                    print(f"[SarrixPay] Falha no token: {msg}")
                    self._access_token = None
                    self._token_expires_at = 0
                    return None
                body = r.json()
                if not isinstance(body, dict):
                    return None
                token = body.get("access_token")
                if not token:
                    return None
                self._access_token = token
                expires_in = int(body.get("expires_in") or 3600)
                self._token_expires_at = now + max(expires_in, 60)
                return self._access_token
        except Exception as e:
            print(f"[SarrixPay] Erro ao obter token: {e}")
            self._access_token = None
            self._token_expires_at = 0
            return None

    def _bearer_headers(self, token: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        token = await self._get_access_token()
        if not token:
            return None
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.request(
                    method,
                    url,
                    headers=self._bearer_headers(token),
                    json=json_body,
                    params=params,
                )
                text = r.text
                print(f"[SarrixPay] {method} {path} -> {r.status_code} {text[:400]}")
                try:
                    data = r.json() if text else {}
                except json.JSONDecodeError:
                    data = {"_raw": text}
                if r.status_code >= 400:
                    if isinstance(data, dict):
                        data = dict(data)
                        data["_http_status"] = r.status_code
                        data["_error"] = "HTTP"
                        return data
                    return {"_error": "HTTP", "_http_status": r.status_code, "message": text[:500]}
                return data if isinstance(data, dict) else {"_error": "INVALID_JSON", "raw": data}
        except Exception as e:
            print(f"[SarrixPay] Erro em {method} {path}: {e}")
            return None

    async def create_pix_charge(
        self,
        amount: float,
        payer_name: str,
        payer_document: str,
        *,
        description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        POST /pix/in/charges — PIX cash-in (QR dinâmico).
        """
        doc = "".join(c for c in str(payer_document) if c.isdigit())
        payload: Dict[str, Any] = {
            "client_id": self.client_id,
            "amount": amount,
            "currency": "BRL",
            "payer": {
                "name": (payer_name or "Cliente").strip()[:120],
                "document": doc,
            },
        }
        if description:
            payload["description"] = description[:255]
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        return await self._request_json("POST", "/pix/in/charges", json_body=payload)

    async def create_pix_transfer(
        self,
        amount: float,
        beneficiary_name: str,
        pix_key: str,
        pix_key_type: str,
        *,
        beneficiary_document: Optional[str] = None,
        description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        POST /pix/out/transfers — PIX cash-out.
        pix_key_type: cpf | cnpj | email | phone | random
        """
        ben: Dict[str, Any] = {
            "name": (beneficiary_name or "Beneficiário").strip()[:120],
            "pix_key_type": pix_key_type,
            "pix_key": pix_key,
        }
        if beneficiary_document:
            ben["document"] = "".join(c for c in str(beneficiary_document) if c.isdigit())
        payload: Dict[str, Any] = {
            "client_id": self.client_id,
            "amount": amount,
            "currency": "BRL",
            "beneficiary": ben,
        }
        if description:
            payload["description"] = description[:255]
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        return await self._request_json("POST", "/pix/out/transfers", json_body=payload)

    async def get_transactions(
        self, transaction_id: str
    ) -> Optional[Dict[str, Any]]:
        """GET /transactions?client_id=&transaction_id="""
        return await self._request_json(
            "GET",
            "/transactions",
            params={"client_id": self.client_id, "transaction_id": transaction_id},
        )

    async def get_balance_summary(self) -> Optional[Dict[str, Any]]:
        """GET /clients/{client_id}/balance-summary"""
        return await self._request_json(
            "GET", f"/clients/{self.client_id}/balance-summary"
        )

    @staticmethod
    def map_frontend_pix_key_type_to_sarrix(
        frontend_type: str, pix_key: str
    ) -> tuple[str, str]:
        """
        Mapeia tipos do front (SuitPay-like) para SarrixPay
        (``cpf`` | ``cnpj`` | ``email`` | ``phone`` | ``random``).

        A documentação SarrixPay exige telefone em formato internacional ``+55...``.
        CPF/CNPJ: apenas dígitos, 11 ou 14 caracteres.

        Raises:
            ValueError: chave vazia, documento com tamanho inválido ou telefone inválido.
        """
        t = (frontend_type or "").strip().lower()
        key = (pix_key or "").strip()
        if not key:
            raise ValueError("Informe a chave PIX de destino.")

        if t in ("document",):
            digits = "".join(c for c in key if c.isdigit())
            if len(digits) == 14:
                return "cnpj", digits
            if len(digits) == 11:
                return "cpf", digits
            raise ValueError(
                "CPF deve ter 11 dígitos e CNPJ 14 dígitos (informe apenas números ou com máscara)."
            )

        if t in ("phonenumber", "phone"):
            normalized = normalize_phone_for_gatebox(key)
            if not normalized:
                digits = "".join(c for c in key if c.isdigit())
                if len(digits) == 11:
                    normalized = f"+55{digits}"
                elif len(digits) == 10:
                    normalized = f"+55{digits}"
                elif len(digits) >= 12 and digits.startswith("55"):
                    normalized = f"+{digits}"
            if not normalized or not normalized.startswith("+55"):
                raise ValueError(
                    "Telefone inválido para PIX. Use DDD + número (ex.: 62999999999) ou +5511999999999."
                )
            return "phone", normalized

        if t in ("email",):
            # PIX por e-mail costuma ser case-insensitive; provedores esperam string estável.
            return "email", key.strip().lower()

        if t in ("randomkey", "random"):
            return "random", key.strip()

        if t == "paymentcode":
            # PIX copia-e-cola (EMV): remover quebras de linha e espaços
            return "random", "".join(key.split())

        return "random", key.strip()

    @staticmethod
    def user_message_from_error(body: Optional[Dict[str, Any]]) -> str:
        if not body:
            return "Erro ao comunicar com SarrixPay."
        if body.get("_error") == "HTTP":
            msg = body.get("message") or body.get("error")
            if isinstance(msg, str) and msg.strip():
                return msg.strip()
            return f"Erro HTTP {body.get('_http_status', '')} no gateway."
        err = body.get("error")
        msg = body.get("message")
        if err == "insufficient_balance":
            return "Saldo insuficiente no provedor/gateway para esta operação."
        if msg:
            return str(msg)
        if err:
            return str(err)
        return "Resposta inválida do gateway SarrixPay."
