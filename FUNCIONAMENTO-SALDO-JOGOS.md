# Funcionamento do Saldo nos Jogos IGameWin

## ✅ Como Funciona

O sistema está configurado para usar **Seamless Mode**, onde:

1. **Saldo da Carteira = Saldo nos Jogos**
   - O saldo que aparece nos jogos é o mesmo saldo da carteira do usuário (`user.balance`)
   - Quando o IGameWin precisa verificar o saldo, ele chama nosso `/gold_api` com método `user_balance`
   - Retornamos o saldo atual da carteira

2. **Apostas Descontam do Saldo**
   - Quando o usuário aposta, o IGameWin chama nosso `/gold_api` com método `transaction`
   - O valor da aposta (`bet_money`) é **debitado** do saldo da carteira
   - O saldo é atualizado imediatamente no banco de dados

3. **Ganhos Creditam no Saldo**
   - Quando o usuário ganha, o IGameWin chama nosso `/gold_api` com método `transaction`
   - O valor do ganho (`win_money`) é **creditado** no saldo da carteira
   - O saldo é atualizado imediatamente no banco de dados

## 🔄 Fluxo Completo

### 1. Usuário Inicia um Jogo
```
Usuário clica em "Jogar" → Backend chama game_launch → IGameWin retorna launch_url
```

### 2. Durante o Jogo - Verificação de Saldo
```
Jogo precisa verificar saldo → IGameWin chama POST /gold_api
{
  "method": "user_balance",
  "agent_code": "...",
  "agent_secret": "...",
  "user_code": "username"
}
→ Retornamos: {"status": 1, "user_balance": 1000.00}
```

### 3. Durante o Jogo - Aposta (Debit)
```
Usuário aposta R$ 10 → IGameWin chama POST /gold_api
{
  "method": "transaction",
  "user_code": "username",
  "game_type": "slot",
  "slot": {
    "bet_money": 10.00,
    "win_money": 0,
    "txn_type": "debit",
    "txn_id": "..."
  }
}
→ Debitamos: user.balance = user.balance - 10.00
→ Retornamos: {"status": 1, "user_balance": 990.00}
```

### 4. Durante o Jogo - Ganho (Credit)
```
Usuário ganha R$ 50 → IGameWin chama POST /gold_api
{
  "method": "transaction",
  "user_code": "username",
  "game_type": "slot",
  "slot": {
    "bet_money": 0,
    "win_money": 50.00,
    "txn_type": "credit",
    "txn_id": "..."
  }
}
→ Creditamos: user.balance = user.balance + 50.00
→ Retornamos: {"status": 1, "user_balance": 1040.00}
```

### 5. Durante o Jogo - Aposta + Ganho Juntos (Debit+Credit)
```
Usuário aposta R$ 10 e ganha R$ 5 → IGameWin chama POST /gold_api
{
  "method": "transaction",
  "user_code": "username",
  "game_type": "slot",
  "slot": {
    "bet_money": 10.00,
    "win_money": 5.00,
    "txn_type": "debit_credit",
    "txn_id": "..."
  }
}
→ Calculamos: net_change = 5.00 - 10.00 = -5.00
→ Atualizamos: user.balance = user.balance + (-5.00)
→ Retornamos: {"status": 1, "user_balance": 995.00}
```

## 📊 Tipos de Transação

### `debit` - Apenas Aposta
- Usado quando o usuário apenas aposta (sem ganho ainda)
- Debitamos `bet_money` do saldo
- Criamos registro de `Bet` com status `PENDING`

### `credit` - Apenas Ganho
- Usado quando o usuário apenas recebe ganho (aposta já foi debitada)
- Creditamos `win_money` no saldo
- Atualizamos registro de `Bet` existente com `win_amount` e status

### `debit_credit` - Aposta + Ganho Juntos
- Usado quando aposta e ganho acontecem na mesma transação
- Calculamos `net_change = win_money - bet_money`
- Atualizamos saldo: `user.balance = user.balance + net_change`
- Criamos ou atualizamos registro de `Bet`

## 🔒 Validações de Segurança

1. **Saldo Insuficiente**
   - Se `user.balance < bet_money`, retornamos erro `INSUFFICIENT_USER_FUNDS`
   - Não debitamos nada
   - Retornamos saldo atual

2. **Usuário Não Encontrado**
   - Se `user_code` não existe, retornamos erro `INVALID_USER`
   - Não processamos transação

3. **Autenticação**
   - Validamos `agent_secret` antes de processar qualquer transação
   - Apenas agentes ativos podem fazer chamadas

## 📝 Registros Criados

Cada transação cria ou atualiza um registro na tabela `bets`:

- `user_id`: ID do usuário
- `game_id`: Código do jogo
- `game_name`: Nome do jogo
- `provider`: Código do provedor
- `amount`: Valor da aposta (`bet_money`)
- `win_amount`: Valor do ganho (`win_money`)
- `status`: `PENDING`, `WON`, ou `LOST`
- `transaction_id`: ID único da transação
- `external_id`: ID da transação do IGameWin (`txn_id`)
- `metadata_json`: Informações adicionais (txn_type, game_type, etc.)

## ✅ Status Atual

- ✅ `/gold_api` implementado corretamente
- ✅ `user_balance` retorna saldo da carteira
- ✅ `transaction` debita apostas e credita ganhos
- ✅ Validações de saldo insuficiente
- ✅ Registros de apostas criados/atualizados
- ✅ Logs detalhados para debug

## 🎯 Resultado

**O saldo da carteira do usuário é sincronizado automaticamente com os jogos!**

- Saldo na carteira = Saldo nos jogos ✅
- Apostas descontam automaticamente ✅
- Ganhos creditam automaticamente ✅
- Tudo sincronizado em tempo real ✅

---

**Data:** 2026-01-27
**Modo:** Seamless Mode (API do Site)
