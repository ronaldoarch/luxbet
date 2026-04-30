"""
Cliente HTTP para Cyber Payment API (Escale Cyber).
Base: https://api.escalecyber.com/v1 — autenticação: header X-API-Key.

Documentação: PIX cash-in (POST /payments/transactions), cash-out (POST /payments/withdrawals),
webhooks com eventos pix.in.* / pix.out.* (payload { id, type, created_at, data }).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx


def normalize_phone_cyber(phone: Optional[str]) -> str:
    """Telefone em dígitos com prefixo 55 (Brasil) quando faltar."""
    if not phone or not str(phone).strip():
        return "5511999999999"
    digits = "".join(c for c in str(phone) if c.isdigit())
    if not digits:
        return "5511999999999"
    if len(digits) >= 10 and len(digits) <= 11 and not digits.startswith("55"):
        return "55" + digits
    if not digits.startswith("55") and len(digits) >= 12:
        return digits
    if digits.startswith("55"):
        return digits
    return "55" + digits


class CyberPayAPI:
    def __init__(self, api_key: str, base_url: str = "https://api.escalecyber.com/v1"):
        self.api_key = (api_key or "").strip()
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    @staticmethod
    def map_frontend_pix_key_type_to_cyber(frontend_type: str, pix_key: str) -> str:
        """Mapeia tipos do frontend LuxBet para pixKeyType da Cyber (CPF, CNPJ, EMAIL, PHONE, RANDOM)."""
        ft = (frontend_type or "").strip()
        if ft == "document":
            digits = "".join(c for c in str(pix_key) if c.isdigit())
            return "CNPJ" if len(digits) > 11 else "CPF"
        m = {
            "phoneNumber": "PHONE",
            "email": "EMAIL",
            "randomKey": "RANDOM",
            "paymentCode": "RANDOM",
        }
        return m.get(ft, "CPF")

    @staticmethod
    def user_message_from_error(body: Optional[Dict[str, Any]]) -> str:
        if not body:
            return "Resposta vazia da API Cyber."
        if body.get("_error") == "HTTP":
            msg = body.get("message") or body.get("error") or body.get("detail")
            if isinstance(msg, list) and msg:
                msg = msg[0]
            if isinstance(msg, dict):
                msg = msg.get("message") or json.dumps(msg, ensure_ascii=False)[:400]
            if msg:
                return str(msg)
            return f"Erro HTTP {body.get('_http_status', '')} na Cyber."
        msg = body.get("message") or body.get("error") or body.get("detail")
        if msg:
            return str(msg)[:500]
        return "Falha na API Cyber."

    async def create_pix_transaction(
        self,
        *,
        amount: float,
        customer_name: str,
        customer_phone: str,
        customer_document: str,
        customer_email: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        customer_document_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "amount": float(amount),
            "customerName": customer_name,
            "customerPhone": normalize_phone_cyber(customer_phone),
            "customerDocument": customer_document,
            "customerEmail": customer_email,
        }
        if description:
            payload["description"] = description
        if metadata:
            payload["metadata"] = metadata
        if customer_document_type in ("cpf", "cnpj"):
            payload["customerDocumentType"] = customer_document_type

        url = f"{self.base_url}/payments/transactions"
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.post(url, headers=self._headers(), json=payload)
                text = r.text or ""
                try:
                    data = r.json() if text else {}
                except json.JSONDecodeError:
                    data = {"_raw": text[:500]}
                if r.status_code >= 400:
                    if isinstance(data, dict):
                        data = dict(data)
                        data["_error"] = "HTTP"
                        data["_http_status"] = r.status_code
                        return data
                    return {"_error": "HTTP", "_http_status": r.status_code, "message": text[:500]}
                if not isinstance(data, dict):
                    return {"_error": "INVALID_JSON", "raw": data}
                if data.get("success") is False:
                    return {"_error": "API", **data}
                inner = data.get("data") or {}
                pix = inner.get("pix") or {}
                qr = pix.get("qrCode") or {}
                emv = qr.get("emv") or qr.get("copyPaste")
                img = qr.get("image")
                txn_id = inner.get("id")
                return {
                    "id": txn_id,
                    "status": inner.get("status"),
                    "paymentCode": emv,
                    "paymentCodeBase64": img,
                    "pix": pix,
                    "_raw": data,
                }
        except Exception as e:
            print(f"[CyberPay] create_pix_transaction erro: {e}")
            return {"_error": "NETWORK", "message": str(e)}

    async def create_pix_withdrawal(
        self,
        *,
        amount: float,
        pix_key: str,
        pix_key_type: str,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "amount": float(amount),
            "pixKey": pix_key,
            "pixKeyType": pix_key_type,
        }
        if description:
            payload["description"] = description

        url = f"{self.base_url}/payments/withdrawals"
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.post(url, headers=self._headers(), json=payload)
                text = r.text or ""
                try:
                    data = r.json() if text else {}
                except json.JSONDecodeError:
                    data = {"_raw": text[:500]}
                if r.status_code >= 400:
                    if isinstance(data, dict):
                        data = dict(data)
                        data["_error"] = "HTTP"
                        data["_http_status"] = r.status_code
                        return data
                    return {"_error": "HTTP", "_http_status": r.status_code, "message": text[:500]}
                if not isinstance(data, dict):
                    return {"_error": "INVALID_JSON", "raw": data}
                if data.get("success") is False:
                    return {"_error": "API", **data}
                inner = data.get("data") or {}
                wid = (
                    inner.get("id")
                    or inner.get("withdrawal_id")
                    or inner.get("withdrawalId")
                )
                if not wid:
                    wid = inner.get("transactionId") or inner.get("transaction_id")
                return {
                    "id": wid,
                    "withdrawal_id": inner.get("withdrawal_id") or inner.get("withdrawalId") or wid,
                    "transaction_id": inner.get("transactionId") or inner.get("transaction_id"),
                    "status": inner.get("status"),
                    "_raw": data,
                }
        except Exception as e:
            print(f"[CyberPay] create_pix_withdrawal erro: {e}")
            return {"_error": "NETWORK", "message": str(e)}
