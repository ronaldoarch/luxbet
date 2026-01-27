# 🔄 Diferença: Seamless Mode vs Continuous Mode (Modo Contínuo)

## 📋 Resumo Executivo

**Seamless Mode** e **Continuous Mode** são dois modos de operação diferentes do IGameWin para gerenciar saldo e transações de jogos.

---

## 🔵 Seamless Mode (Modo Seamless)

### Como Funciona:

1. **IGameWin chama nosso site** para buscar saldo e registrar transações
2. **Nosso site implementa** o endpoint `/gold_api` que o IGameWin chama
3. **Saldo fica no nosso banco** - IGameWin apenas consulta quando necessário
4. **Transações são registradas** em tempo real via `/gold_api`

### Fluxo:

```
1. Usuário clica para iniciar jogo
2. Nosso backend chama game_launch no IGameWin
3. IGameWin retorna URL do jogo
4. Jogo carrega no iframe
5. Quando jogo precisa de saldo → IGameWin chama nosso /gold_api
6. Quando há transação → IGameWin chama nosso /gold_api
```

### Requisitos:

- ✅ Endpoint `/gold_api` implementado no nosso site
- ✅ Campo "Ponto final do site" configurado no painel IGameWin
- ✅ `agent_secret` configurado para autenticação

### Vantagens:

- ✅ **Saldo único** - fica apenas no nosso banco
- ✅ **Sincronização automática** - IGameWin busca quando precisa
- ✅ **Menos transferências** - não precisa transferir saldo manualmente
- ✅ **Mais controle** - temos controle total sobre o saldo

### Desvantagens:

- ⚠️ Precisa implementar endpoint `/gold_api`
- ⚠️ Depende de nosso servidor estar online
- ⚠️ Requer configuração adicional no painel IGameWin

---

## 🟢 Continuous Mode (Modo Contínuo / Transfer Mode)

### Como Funciona:

1. **Nós chamamos IGameWin** para transferir saldo quando necessário
2. **Saldo fica no IGameWin** - precisamos sincronizar manualmente
3. **Transferências manuais** usando `user_deposit` e `user_withdraw`
4. **IGameWin gerencia** o saldo internamente

### Fluxo:

```
1. Usuário clica para iniciar jogo
2. Nosso backend busca saldo no IGameWin (money_info)
3. Se saldo diferente → transfere diferença (user_deposit/user_withdraw)
4. Nosso backend chama game_launch no IGameWin
5. IGameWin retorna URL do jogo
6. Jogo carrega e usa saldo do IGameWin diretamente
```

### Requisitos:

- ✅ APIs `money_info`, `user_deposit`, `user_withdraw` funcionando
- ✅ Sincronização manual de saldo antes de lançar jogo
- ❌ **NÃO precisa** de endpoint `/gold_api`

### Vantagens:

- ✅ **Mais simples** - não precisa implementar endpoint
- ✅ **IGameWin gerencia** tudo internamente
- ✅ **Menos dependência** do nosso servidor durante o jogo

### Desvantagens:

- ⚠️ **Dois saldos** - um no nosso banco, outro no IGameWin
- ⚠️ **Sincronização manual** - precisa transferir antes de cada jogo
- ⚠️ **Mais chamadas API** - precisa fazer transferências manualmente
- ⚠️ **Risco de dessincronização** - saldos podem ficar diferentes

---

## 📊 Comparação Direta

| Característica | Seamless Mode | Continuous Mode |
|----------------|---------------|------------------|
| **Onde fica o saldo?** | No nosso banco | No IGameWin |
| **Quem busca saldo?** | IGameWin chama nosso site | Nós chamamos IGameWin |
| **Endpoint necessário?** | Sim (`/gold_api`) | Não |
| **Sincronização** | Automática | Manual |
| **Transferências** | Não precisa | Precisa fazer manualmente |
| **Complexidade** | Maior (precisa endpoint) | Menor |
| **Controle** | Total sobre saldo | IGameWin gerencia |
| **Dependência** | Nosso servidor deve estar online | Menor dependência |

---

## 🔍 Como Identificar Qual Modo Está Ativo

### Seamless Mode:
- Quando chamamos `money_info` → retorna `ERROR_GET_BALANCE_END_POINT`
- IGameWin tenta chamar nosso `/gold_api`
- Logs mostram: `[Launch Game] Detected Seamless mode`

### Continuous Mode:
- Quando chamamos `money_info` → retorna saldo normalmente
- Não há chamadas ao `/gold_api`
- Logs mostram: `[Launch Game] Transfer mode detected`

---

## 🎯 Qual Modo Usar?

### Use Seamless Mode se:
- ✅ Quer controle total sobre o saldo
- ✅ Quer saldo único (apenas no seu banco)
- ✅ Pode implementar o endpoint `/gold_api`
- ✅ Seu servidor tem boa disponibilidade

### Use Continuous Mode se:
- ✅ Quer simplicidade (sem endpoint adicional)
- ✅ Prefere que IGameWin gerencie o saldo
- ✅ Não quer depender do seu servidor durante o jogo
- ✅ Aceita sincronização manual de saldo

---

## 🔧 Configuração no Painel IGameWin

### Para Seamless Mode:
1. Campo **"Tipo de API"** → "Seamless" ou "Modo Seamless"
2. Campo **"Ponto final do site"** → `https://api.luxbet.site`
3. Endpoint `/gold_api` deve estar implementado

### Para Continuous Mode:
1. Campo **"Tipo de API"** → "Contínuo" ou "Transfer"
2. Campo **"Ponto final do site"** → Não necessário (ou pode deixar vazio)
3. Endpoint `/gold_api` não é necessário

---

## 📝 Nota Importante

Nosso código detecta automaticamente qual modo está ativo:
- Se receber `ERROR_GET_BALANCE_END_POINT` → detecta Seamless e pula sincronização
- Se conseguir buscar saldo → detecta Continuous e sincroniza normalmente

Isso significa que **funciona em ambos os modos** sem configuração adicional! 🎉
