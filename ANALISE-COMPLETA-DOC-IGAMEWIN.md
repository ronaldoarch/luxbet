# Análise Completa da Documentação IGameWin API

## 📋 Resumo Executivo

Após análise detalhada da documentação oficial do IGameWin, identifiquei um **problema crítico** na implementação atual: estamos fazendo operações de saldo (`get_user_balance`, `transfer_in`) antes de lançar o jogo, o que pode estar **forçando o modo Transfer** quando deveríamos estar usando **modo Seamless**.

---

## 🔍 Análise Detalhada por Seção

### 1. API de Transferência (Transfer Mode / Continuous Mode)

**Endpoint:** `https://igamewin.com/api/v1`

#### 1.1 Criar Usuário (`user_create`)
- ✅ **Implementado corretamente**
- Retorna `DUPLICATED_USER` se usuário já existe (tratado corretamente)

#### 1.2 Depositar Saldo (`user_deposit`)
- ⚠️ **Usado incorretamente antes do lançamento**
- Deve ser usado apenas em **Transfer Mode**
- Transfere saldo do agente para o usuário no IGameWin

#### 1.3 Retirar Saldo (`user_withdraw`)
- ⚠️ **Usado incorretamente após o jogo**
- Deve ser usado apenas em **Transfer Mode**
- Transfere saldo do usuário de volta para o agente

#### 1.4 Obter Saldo (`money_info`)
- ⚠️ **Usado incorretamente antes do lançamento**
- Retorna saldo do agente e/ou usuário no IGameWin
- **Não deve ser usado em Seamless Mode**

#### 1.5 Lançar Jogo (`game_launch`)
- ✅ **Implementado corretamente**
- Retorna `launch_url` para o jogo
- **IMPORTANTE:** Não requer verificação de saldo antes em Seamless Mode

---

### 2. API Integrada (API do Site) - ⚠️ CRÍTICO

**Endpoint:** `https://fiverstest-site.com/gold_api` (nosso site)

**Nota da documentação:**
> "O site deve implementar esta API, usar somente no modo Seamless (Obrigatório)"

#### 2.1 Saldo do Usuário (`user_balance`)

**Quando é chamado:**
- IGameWin chama nosso `/gold_api` quando precisa verificar o saldo do usuário
- Chamado durante o jogo quando o usuário faz apostas

**Request esperado:**
```json
{
    "method": "user_balance",
    "agent_code": "Midaslabs",
    "agent_secret": "19e4c979a7a5a4f70ffc30b510312317",
    "user_code": "test"
}
```

**Response esperado:**
```json
{
    "status": 1,
    "user_balance": 1000
}
```

**Status da implementação:**
- ✅ Implementado em `/gold_api`
- ✅ Valida `agent_secret`
- ✅ Retorna saldo do nosso banco de dados

#### 2.2 Transação (`transaction`)

**Quando é chamado:**
- IGameWin chama nosso `/gold_api` quando o usuário faz uma aposta ou ganha
- Chamado automaticamente pelo jogo durante a partida

**Request esperado:**
```json
{
    "method": "transaction",
    "agent_code": "Midaslabs",
    "agent_secret": "19e4c979a7a5a4f70ffc30b510312317",
    "agent_balance": 10000000,
    "user_code": "test",
    "user_balance": 99200,
    "game_type": "slot",
    "slot": {
        "provider_code": "BOOONGO",
        "game_code": "sun_of_egypt",
        "type": "BASE",
        "bet_money": 1000,
        "win_money": 200,
        "txn_id": "MVGKE8FJE3838EFN378DF",
        "txn_type": "debit_credit"
    }
}
```

**Tipos de transação (`txn_type`):**
- `"debit"`: Apenas aposta (debitar saldo)
- `"credit"`: Apenas ganho (creditar saldo)
- `"debit_credit"`: Aposta e ganho juntos

**Response esperado:**
```json
{
    "status": 1,
    "user_balance": 1000
}
```

**Status da implementação:**
- ✅ Implementado em `/gold_api`
- ✅ Processa `debit`, `credit`, e `debit_credit`
- ✅ Atualiza saldo no nosso banco
- ✅ Cria registros de `Bet`

---

## 🚨 PROBLEMA IDENTIFICADO

### O que está acontecendo atualmente:

1. **Antes de lançar o jogo:**
   - Chamamos `get_user_balance` (money_info) ❌
   - Chamamos `transfer_in` (user_deposit) ❌
   - Depois chamamos `game_launch` ✅

2. **O que deveria acontecer em Seamless Mode:**

   - Apenas criar usuário se necessário (`user_create`) ✅
   - Chamar `game_launch` diretamente ✅
   - **NÃO fazer verificação de saldo** ❌
   - **NÃO fazer transferências** ❌

### Por que isso causa problemas:

1. **Força modo Transfer:**
   - Ao fazer `user_deposit` antes do jogo, estamos transferindo saldo para o IGameWin
   - Isso pode fazer o IGameWin pensar que estamos em Transfer Mode
   - O jogo pode ser configurado para usar saldo do IGameWin em vez de chamar nosso `/gold_api`

2. **Muda estado do usuário:**
   - Operações de transferência podem alterar o estado interno do usuário no IGameWin
   - Isso pode fazer o IGameWin retornar uma `launch_url` diferente
   - A URL pode apontar para recursos que têm problemas de CORS

3. **Conflito de modos:**
   - Estamos implementando `/gold_api` (Seamless Mode)
   - Mas também fazendo transferências (Transfer Mode)
   - Isso cria uma inconsistência que pode causar problemas

---

## ✅ SOLUÇÃO PROPOSTA

### Para Seamless Mode (recomendado):

1. **Remover todas as verificações de saldo antes do `game_launch`**
2. **Remover todas as transferências (`transfer_in`, `transfer_out`)**
3. **Apenas garantir que o usuário existe** (`user_create` se necessário)
4. **Chamar `game_launch` diretamente**
5. **Deixar o IGameWin chamar nosso `/gold_api` durante o jogo**

### Código atual (INCORRETO):
```python
# ❌ ERRADO para Seamless Mode
user_balance = await api.get_user_balance(current_user.username)
if user_balance is None:
    # Transferir saldo
    await api.transfer_in(current_user.username, amount)
launch_url = await api.launch_game(...)
```

### Código correto (SEAMLESS MODE):
```python
# ✅ CORRETO para Seamless Mode
# Apenas garantir que usuário existe
user_created = await api.create_user(current_user.username, is_demo=False)
# Se DUPLICATED_USER, tudo bem - usuário já existe

# Lançar jogo diretamente - IGameWin vai chamar nosso /gold_api
launch_url = await api.launch_game(
    user_code=current_user.username,
    game_code=game_code,
    provider_code=provider_code,
    lang="pt"
)
```

---

## 🔄 Modo Transfer (Continuous Mode) - Alternativa

Se preferirmos usar Transfer Mode:

1. **Remover implementação de `/gold_api`**
2. **Manter verificações de saldo e transferências**
3. **Fazer `transfer_in` antes do jogo**
4. **Fazer `transfer_out` após o jogo**

**Desvantagens:**
- Requer sincronização manual de saldo
- Mais chamadas de API
- Mais complexo de gerenciar

---

## 📊 Comparação dos Modos

| Aspecto | Seamless Mode | Transfer Mode |
|--------|---------------|---------------|
| **Saldo gerenciado** | Nosso banco | IGameWin |
| **Verificação antes do jogo** | ❌ Não precisa | ✅ Necessária |
| **Transferências** | ❌ Não precisa | ✅ Necessárias |
| **API do site (`/gold_api`)** | ✅ Obrigatória | ❌ Não usada |
| **Complexidade** | Baixa | Média |
| **Sincronização** | Automática | Manual |

---

## 🎯 RECOMENDAÇÃO FINAL

**Usar Seamless Mode** porque:

1. ✅ Já implementamos `/gold_api` corretamente
2. ✅ Menos complexo (sem transferências)
3. ✅ Sincronização automática de saldo
4. ✅ Menos chamadas de API
5. ✅ Saldo sempre sincronizado

**Ação imediata:**
- Remover `get_user_balance` e `transfer_in` do `launch_game`
- Manter apenas `user_create` (se necessário) e `game_launch`
- Deixar o IGameWin gerenciar saldo via `/gold_api`

---

## 🔗 Relação com Erros de CORS

Os erros de CORS que estamos vendo podem estar relacionados porque:

1. **URL diferente:** Ao fazer transferências, o IGameWin pode retornar uma `launch_url` diferente
2. **Configuração diferente:** O modo Transfer pode usar recursos diferentes que têm problemas de CORS
3. **Estado inconsistente:** Misturar modos pode deixar o usuário em estado inconsistente no IGameWin

**Teste sugerido:**
- Remover todas as operações de saldo antes do `game_launch`
- Testar se os erros de CORS desaparecem
- Se desaparecerem, confirma que o problema era a mistura de modos

---

## 📝 Checklist de Implementação

- [x] Implementar `/gold_api` com `user_balance` e `transaction`
- [x] Validar `agent_secret` corretamente
- [x] Processar todos os tipos de `txn_type` (debit, credit, debit_credit)
- [ ] **Remover `get_user_balance` antes de `game_launch`**
- [ ] **Remover `transfer_in` antes de `game_launch`**
- [ ] **Remover `transfer_out` após o jogo**
- [ ] Manter apenas `user_create` (se necessário) e `game_launch`
- [ ] Testar se erros de CORS desaparecem

---

## 📚 Referências

- Documentação oficial: `https://igamewin.com/docs`
- Endpoint API: `https://igamewin.com/api/v1`
- Endpoint nosso (Seamless): `https://api.luxbet.site/gold_api`

---

**Data da análise:** 2026-01-27
**Versão da documentação analisada:** Última disponível em igamewin.com/docs
