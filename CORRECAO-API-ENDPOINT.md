# Correção do Endpoint da API IGameWin

## 🚨 Problema Identificado

O endpoint da API estava configurado incorretamente:

- ❌ **Incorreto:** `https://api.igamewin.com`
- ✅ **Correto:** `https://igamewin.com/api/v1`

## 📋 Documentação Oficial

Segundo a documentação oficial do IGameWin:
> **Ponto de extremidade da API:** `https://igamewin.com/api/v1`

## 🔧 Correções Realizadas

### 1. Modelo (`backend/models.py`)
```python
# ANTES (incorreto)
api_url = Column(String(255), default="https://api.igamewin.com", nullable=False)

# DEPOIS (correto)
api_url = Column(String(255), default="https://igamewin.com", nullable=False)
```

### 2. Schema (`backend/schemas.py`)
```python
# ANTES (incorreto)
api_url: str = "https://api.igamewin.com"

# DEPOIS (correto)
api_url: str = "https://igamewin.com"
```

### 3. Código (`backend/igamewin_api.py`)
O código já estava correto - ele recebe `https://igamewin.com` e adiciona `/api/v1` automaticamente:
```python
if self.api_url.endswith("/api/v1"):
    self.base_url = self.api_url
elif self.api_url.endswith("/api"):
    self.base_url = f"{self.api_url}/v1"
else:
    self.base_url = f"{self.api_url}/api/v1"  # Adiciona /api/v1 automaticamente
```

## ⚠️ Ação Necessária no Banco de Dados

Se você já tem agentes cadastrados com o valor antigo (`https://api.igamewin.com`), você precisa atualizar manualmente:

### Opção 1: Via SQL
```sql
UPDATE igamewin_agents 
SET api_url = 'https://igamewin.com' 
WHERE api_url = 'https://api.igamewin.com';
```

### Opção 2: Via Painel Administrativo
1. Acesse o painel administrativo
2. Vá em "IGameWin Agents"
3. Edite cada agente
4. Altere o campo "API Endpoint" de `https://api.igamewin.com` para `https://igamewin.com`
5. Salve

## ✅ Verificação

Após a correção, o código vai:
1. Receber `https://igamewin.com` do banco de dados
2. Adicionar `/api/v1` automaticamente
3. Fazer chamadas para `https://igamewin.com/api/v1` ✅

## 📝 Nota sobre o Painel IGameWin

No painel administrativo do IGameWin (que você mostrou na imagem), o campo "API Endpoint" provavelmente deve ser configurado como:
- `https://igamewin.com` (sem `/api/v1`)

O sistema deles deve adicionar `/api/v1` internamente, ou você pode tentar:
- `https://igamewin.com/api/v1` (completo)

Mas o importante é que **nosso código** agora usa `https://igamewin.com` como padrão, que é o correto.

---

**Data da correção:** 2026-01-27
