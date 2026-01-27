# ✅ Endpoint `/gold_api` Implementado

## 📋 O que foi implementado

Implementei o endpoint `/gold_api` necessário para o modo **Seamless** do IGameWin. Este endpoint permite que o IGameWin chame nosso site para:

1. **Buscar saldo do usuário** (`user_balance`)
2. **Registrar transações de jogo** (`transaction`)

---

## 🔧 Configuração Necessária

### 1. Configurar `agent_secret` no IGameWinAgent

O `agent_secret` é diferente do `agent_token` e é usado pelo IGameWin para autenticar chamadas para nosso site.

**Opção 1: Usar o mesmo valor de `agent_key`**
- Se você não tem um `agent_secret` separado, o sistema usará o `agent_key` como `agent_secret`

**Opção 2: Configurar `agent_secret` separado**
- No campo `credentials` do IGameWinAgent, adicione:
```json
{
  "agent_secret": "seu_agent_secret_aqui"
}
```

### 2. Configurar "Ponto final do site" no painel IGameWin

No painel administrativo do IGameWin:

1. Vá em **"Agente de atualização"**
2. Localize o campo **"Ponto final do site (Site Endpoint)"**
3. Configure como: `https://luxbet.site`
   - ⚠️ **NÃO inclua** `/gold_api` no final
   - O IGameWin automaticamente adiciona `/gold_api` quando necessário

4. Salve as alterações

---

## 📍 Endpoint Implementado

### URL
```
POST https://luxbet.site/api/public/gold_api
```

### Métodos Suportados

#### 1. `user_balance` - Buscar Saldo

**Request:**
```json
{
  "method": "user_balance",
  "agent_code": "welisson4916",
  "agent_secret": "seu_agent_secret",
  "user_code": "test"
}
```

**Response (Success):**
```json
{
  "status": 1,
  "user_balance": 1000.0
}
```

**Response (Error):**
```json
{
  "status": 0,
  "user_balance": 0,
  "msg": "INVALID_USER"
}
```

#### 2. `transaction` - Registrar Transação

**Request:**
```json
{
  "method": "transaction",
  "agent_code": "welisson4916",
  "agent_secret": "seu_agent_secret",
  "agent_balance": 10000000,
  "user_code": "test",
  "user_balance": 99200,
  "game_type": "slot",
  "slot": {
    "provider_code": "PRAGMATIC",
    "game_code": "vs20doghouse",
    "type": "BASE",
    "bet_money": 1000,
    "win_money": 200,
    "txn_id": "MVGKE8FJE3838EFN378DF",
    "txn_type": "debit_credit"
  }
}
```

**Tipos de `txn_type`:**
- `"debit"` - Apenas aposta (debitar saldo)
- `"credit"` - Apenas ganho (creditar saldo)
- `"debit_credit"` - Aposta e ganho juntos (calcular diferença)

**Response (Success):**
```json
{
  "status": 1,
  "user_balance": 1000.0
}
```

**Response (Error - Saldo Insuficiente):**
```json
{
  "status": 0,
  "user_balance": 500.0,
  "msg": "INSUFFICIENT_USER_FUNDS"
}
```

---

## 🔐 Autenticação

O endpoint valida:
1. **agent_code** - Deve existir e estar ativo no banco de dados
2. **agent_secret** - Deve corresponder ao `agent_secret` em `credentials` ou ao `agent_key`

---

## 📊 Funcionalidades

### Registro de Apostas

Todas as transações são registradas na tabela `bets`:
- **Aposta criada** quando `txn_type` é `"debit"` ou `"debit_credit"`
- **Aposta atualizada** quando `txn_type` é `"credit"` (busca por `txn_id`)
- **Status da aposta**:
  - `WON` - Se ganho > aposta
  - `LOST` - Se ganho <= aposta
  - `PENDING` - Se apenas debit (aguardando resultado)

### Sincronização de Saldo

- O saldo do usuário é atualizado automaticamente
- Transações são registradas com `txn_id` para rastreamento
- Metadata completa é armazenada em `metadata_json`

---

## 🐛 Debugging

### Logs

O endpoint gera logs detalhados:
```
[Gold API] Received request - method=user_balance, agent_code=welisson4916
[Gold API] Getting balance for user: test
[Gold API] User balance: 1000.0
[Gold API] Processing transaction - user=test, game_type=slot
[Gold API] Slot transaction - txn_type=debit_credit, bet=1000, win=200, txn_id=...
[Gold API] Transaction processed - new balance: 9200.0
```

### Verificar se o endpoint está funcionando

1. **Teste manual com curl:**
```bash
curl -X POST https://luxbet.site/api/public/gold_api \
  -H "Content-Type: application/json" \
  -d '{
    "method": "user_balance",
    "agent_code": "welisson4916",
    "agent_secret": "seu_agent_secret",
    "user_code": "test"
  }'
```

2. **Verificar logs do backend** para ver se as requisições estão chegando

---

## ⚠️ Importante

### Modo Seamless vs Modo Transferência

- **Modo Seamless** (atual): IGameWin chama nosso site para buscar saldo e registrar transações
- **Modo Transferência**: Nós chamamos IGameWin para transferir saldo manualmente

O endpoint `/gold_api` é necessário **apenas** para o modo Seamless.

### Configuração no Painel IGameWin

Certifique-se de que:
- ✅ Campo "Ponto final do site" está configurado como `https://luxbet.site`
- ✅ Campo "Tipo de API" está como "Modo contínuo" ou "Seamless"
- ✅ `agent_secret` está configurado corretamente (se diferente de `agent_key`)

---

## ✅ Próximos Passos

1. **Configurar `agent_secret`** no banco de dados (se necessário)
2. **Configurar "Ponto final do site"** no painel IGameWin
3. **Testar** iniciando um jogo
4. **Verificar logs** para confirmar que as chamadas estão funcionando

---

## 🔄 Detecção Automática de Modo

O sistema agora detecta automaticamente se o IGameWin está em modo **Seamless** ou **Transferência**:

- **Se receber `ERROR_GET_BALANCE_END_POINT`**: Detecta modo Seamless e pula sincronização de saldo
- **Se conseguir buscar saldo**: Detecta modo Transferência e sincroniza saldo normalmente

Isso significa que você não precisa fazer nenhuma configuração adicional - o sistema se adapta automaticamente!

---

## 📞 Se o Erro Persistir

Se ainda receber `ERROR_GET_BALANCE_END_POINT`:

1. **Verifique os logs do backend** - procure por `[Gold API]`
2. **Teste o endpoint manualmente** com curl
3. **Verifique se o `agent_secret` está correto**
4. **Confirme que o campo "Ponto final do site" está salvo** no painel IGameWin
5. **Aguarde 2-5 minutos** após salvar as configurações

O endpoint está implementado e pronto para uso! 🎉
