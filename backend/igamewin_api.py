import httpx
import json
from typing import Optional, Dict, Any, List
from models import IGameWinAgent
from sqlalchemy.orm import Session


class IGameWinAPI:
    def __init__(
        self,
        agent_code: str,
        agent_key: str,
        api_url: str = "https://igamewin.com",
        credentials: Optional[Dict[str, Any]] = None
    ):
        self.agent_code = agent_code
        self.agent_key = agent_key  # maps to agent_token in requests
        self.api_url = api_url.rstrip('/')
        # Detect base url for /api/v1 according to doc
        if self.api_url.endswith("/api/v1"):
            self.base_url = self.api_url
        elif self.api_url.endswith("/api"):
            self.base_url = f"{self.api_url}/v1"
        else:
            self.base_url = f"{self.api_url}/api/v1"
        self.credentials = credentials or {}
        self.last_error: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json"
        }
    
    async def create_user(self, user_code: str, is_demo: bool = False) -> Optional[Dict[str, Any]]:
        """Create user in igamewin system - follows IGameWin API documentation"""
        payload = {
            "method": "user_create",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key,
            "user_code": user_code
        }
        if is_demo:
            payload["is_demo"] = True
        
        data = await self._post(payload)
        if not data:
            return None
        
        # Verificar se status é 1 (sucesso)
        if data.get("status") == 1:
            return data
        
        return None
    
    async def get_agent_balance(self) -> Optional[float]:
        """Get agent balance from igamewin - follows IGameWin API documentation"""
        payload = {
            "method": "money_info",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key
        }
        
        data = await self._post(payload)
        if not data:
            return None
        
        # A resposta tem estrutura: {"status": 1, "agent": {"agent_code": "...", "balance": ...}}
        agent_info = data.get("agent")
        if agent_info:
            return agent_info.get("balance", 0.0)
        
        return None

    async def get_user_balance(self, user_code: str) -> Optional[float]:
        """Get user balance from igamewin - follows IGameWin API documentation"""
        payload = {
            "method": "money_info",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key,
            "user_code": user_code
        }
        
        print(f"[IGameWin] Getting user balance - user_code={user_code}")
        data = await self._post(payload)
        if not data:
            print(f"[IGameWin] Failed to get user balance: {self.last_error}")
            return None
        
        print(f"[IGameWin] Balance response: {json.dumps(data)}")
        
        # Verificar se status é 1 (sucesso)
        status = data.get("status")
        if status != 1:
            error_msg = data.get("msg", "Erro desconhecido")
            self.last_error = f"status={status} msg={error_msg}"
            print(f"[IGameWin] Error getting balance: {self.last_error}")
            return None
        
        # A resposta tem estrutura: {"status": 1, "agent": {...}, "user": {"user_code": "...", "balance": ...}}
        user_info = data.get("user")
        if user_info:
            balance = user_info.get("balance", 0.0)
            print(f"[IGameWin] User balance: {balance}")
            return balance
        
        # Se não tem user_info mas status é 1, pode ser que o usuário não existe ainda
        print(f"[IGameWin] No user info in response, user may not exist yet")
        return None
    
    async def transfer_in(self, user_code: str, amount: float) -> Optional[Dict[str, Any]]:
        """Transfer money into user account (deposit) - follows IGameWin API documentation"""
        payload = {
            "method": "user_deposit",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key,
            "user_code": user_code,
            "amount": amount
        }
        
        data = await self._post(payload)
        if not data:
            return None
        
        # Verificar se status é 1 (sucesso)
        if data.get("status") == 1:
            return data
        
        return None
    
    async def transfer_out(self, user_code: str, amount: float) -> Optional[Dict[str, Any]]:
        """Transfer money out of user account (withdraw) - follows IGameWin API documentation"""
        payload = {
            "method": "user_withdraw",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key,
            "user_code": user_code,
            "amount": amount
        }
        
        data = await self._post(payload)
        if not data:
            return None
        
        # Verificar se status é 1 (sucesso)
        if data.get("status") == 1:
            return data
        
        return None
    
    async def _post(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self.last_error = None
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # API retorna status 1 para sucesso, 0 para erro
                # Para métodos que não retornam status (como alguns endpoints), aceitar a resposta
                # Mas para métodos que devem retornar status, validar explicitamente
                if isinstance(data, dict):
                    status = data.get("status")
                    # Se status existe e não é 1, é um erro
                    if status is not None and status != 1:
                        error_msg = data.get("msg", "Erro desconhecido")
                        self.last_error = f"status={status} msg={error_msg}"
                        return None
                    # Se status é 1 ou None (alguns endpoints podem não retornar status), aceitar
                    return data
                
                return data
            except httpx.HTTPError as e:
                body_preview = ""
                try:
                    body_preview = e.response.text[:500] if hasattr(e, "response") and e.response else ""
                except Exception:
                    pass
                self.last_error = f"{e} {body_preview}"
                print(f"Error calling igamewin: {self.last_error}")
                return None

    async def get_providers(self) -> Optional[List[Dict[str, Any]]]:
        payload = {
            "method": "provider_list",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key
        }
        data = await self._post(payload)
        if not data:
            return None
        return data.get("providers")

    async def get_games(self, provider_code: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        payload: Dict[str, Any] = {
            "method": "game_list",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key
        }
        if provider_code:
            payload["provider_code"] = provider_code
        # Allow provider_code from credentials default
        if not provider_code and isinstance(self.credentials, dict):
            default_provider = self.credentials.get("provider_code")
            if default_provider:
                payload["provider_code"] = default_provider

        data = await self._post(payload)
        if not data:
            return None
        return data.get("games")

    async def launch_game(self, user_code: str, game_code: str, provider_code: Optional[str] = None, lang: str = "pt") -> Optional[str]:
        """Generate game launch URL for user - follows IGameWin API documentation"""
        payload: Dict[str, Any] = {
            "method": "game_launch",
            "agent_code": self.agent_code,
            "agent_token": self.agent_key,
            "user_code": user_code,
            "game_code": game_code,
            "lang": lang
        }
        if provider_code:
            payload["provider_code"] = provider_code
        
        print(f"[IGameWin] Launching game - user_code={user_code}, game_code={game_code}, provider_code={provider_code}, lang={lang}")
        print(f"[IGameWin] Payload: {json.dumps({**payload, 'agent_token': '***'})}")
        
        data = await self._post(payload)
        if not data:
            print(f"[IGameWin] Failed to get response: {self.last_error}")
            return None
        
        print(f"[IGameWin] Response received: {json.dumps(data)}")
        
        # Verificar se status é 1 (sucesso) conforme documentação
        status = data.get("status")
        if status != 1:
            error_msg = data.get("msg", "Erro desconhecido")
            self.last_error = f"status={status} msg={error_msg}"
            print(f"[IGameWin] Error status: {self.last_error}")
            return None
        
        # A resposta de sucesso tem "launch_url" conforme documentação
        launch_url = data.get("launch_url")
        if not launch_url:
            self.last_error = "Resposta de sucesso não contém launch_url"
            print(f"[IGameWin] Missing launch_url in response: {json.dumps(data)}")
            return None
        
        # Validar que a URL não está vazia
        if not launch_url.strip():
            self.last_error = "launch_url está vazio"
            print(f"[IGameWin] Empty launch_url")
            return None
        
        print(f"[IGameWin] Success! Launch URL: {launch_url[:100]}...")
        return launch_url


def get_igamewin_api(db: Session) -> Optional[IGameWinAPI]:
    """Get active igamewin agent and return API instance"""
    agent = db.query(IGameWinAgent).filter(IGameWinAgent.is_active == True).first()
    if not agent:
        return None
    
    # Validar que agent_code e agent_key não estão vazios
    if not agent.agent_code or not agent.agent_key:
        return None
    
    credentials_dict: Dict[str, Any] = {}
    if agent.credentials:
        try:
            credentials_dict = json.loads(agent.credentials)
        except Exception:
            credentials_dict = {}
    return IGameWinAPI(
        agent_code=agent.agent_code,
        agent_key=agent.agent_key,
        api_url=agent.api_url,
        credentials=credentials_dict
    )
