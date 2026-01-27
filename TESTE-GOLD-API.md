# 🧪 Como Testar se o Endpoint /gold_api Está Acessível

## ✅ Endpoint Implementado

O endpoint `/gold_api` está implementado e disponível em:
- `https://luxbet.site/gold_api` (raiz - esperado pelo IGameWin)
- `https://luxbet.site/api/public/gold_api` (compatibilidade)

---

## 🧪 Teste 1: Verificar se o Endpoint Está Acessível

### Via Navegador (GET)
Abra no navegador:
```
https://luxbet.site/gold_api
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "message": "Endpoint /gold_api está acessível",
  "endpoint": "/gold_api",
  "methods": ["POST"],
  "expected_methods": ["user_balance", "transaction"]
}
```

Se você receber esta resposta, o endpoint está **acessível publicamente** ✅

---

## 🧪 Teste 2: Testar Método user_balance (POST)

### Via curl:
```bash
curl -X POST https://luxbet.site/gold_api \
  -H "Content-Type: application/json" \
  -d '{
    "method": "user_balance",
    "agent_code": "welisson4916",
    "agent_secret": "SEU_AGENT_SECRET_AQUI",
    "user_code": "ronaldo_dias_de_sousa"
  }'
```

**Resposta esperada (sucesso):**
```json
{
  "status": 1,
  "user_balance": 2.0
}
```

**Resposta esperada (erro de autenticação):**
```json
{
  "status": 0,
  "msg": "INVALID_SECRET"
}
```

---

## 🔍 Verificar Logs do Backend

Quando o IGameWin tentar acessar o endpoint, você deve ver nos logs:

```
[Gold API Root] ===== REQUEST RECEIVED AT /gold_api =====
[Gold API] ===== REQUEST RECEIVED =====
[Gold API] Client IP: ...
[Gold API] Headers: {...}
[Gold API] Method: user_balance, Agent Code: welisson4916
```

**Se você NÃO vê esses logs**, significa que:
- O IGameWin não está conseguindo acessar o endpoint
- Pode ser problema de DNS, firewall ou configuração no painel IGameWin

---

## ⚠️ Problemas Comuns

### 1. Endpoint Retorna 404
**Causa:** Endpoint não está acessível ou URL incorreta
**Solução:** 
- Verifique se o backend está rodando
- Verifique se o endpoint está em `/gold_api` (não `/api/public/gold_api`)

### 2. Endpoint Retorna 500
**Causa:** Erro interno no servidor
**Solução:**
- Verifique os logs do backend
- Verifique se o banco de dados está acessível
- Verifique se as credenciais do agente estão corretas

### 3. IGameWin Não Consegue Acessar
**Causa:** Campo "Ponto final do site" não configurado ou incorreto
**Solução:**
- Configure como `https://luxbet.site` (sem `/gold_api`)
- Aguarde 2-5 minutos após salvar
- Verifique se não há firewall bloqueando

---

## 📋 Checklist de Verificação

- [ ] Endpoint `/gold_api` retorna resposta de teste (GET)
- [ ] Endpoint `/gold_api` aceita requisições POST
- [ ] Campo "Ponto final do site" configurado como `https://luxbet.site`
- [ ] Aguardou 2-5 minutos após configurar
- [ ] Logs do backend mostram requisições chegando
- [ ] Não há firewall bloqueando requisições do IGameWin

---

## 🔧 Se o Problema Persistir

1. **Teste o endpoint manualmente** usando curl ou Postman
2. **Verifique os logs do backend** para ver se há requisições chegando
3. **Verifique o campo "Ponto final do site"** no painel IGameWin
4. **Contate o suporte do IGameWin** com:
   - URL do endpoint: `https://luxbet.site/gold_api`
   - Agent Code: `welisson4916`
   - Erro específico: `ERROR_GET_BALANCE_END_POINT`
