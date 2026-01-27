# Sincronização de Saldo entre Jogo e Carteira

## 🎯 Problema Identificado

O saldo no jogo estava diferente do saldo na carteira:
- **Jogo:** 0.20 BRL (20 centavos) ✅ **CORRETO**
- **Carteira:** R$ 2,00 ❌ **INCORRETO**

## ✅ Solução

Em **Seamless Mode**, o saldo do jogo é a **fonte da verdade**. O IGameWin usa nosso `/gold_api` para:
1. Obter o saldo inicial (`user_balance`)
2. Processar transações (`transaction`)

### Como Funciona

```
1. Usuário lança jogo
   ↓
2. IGameWin chama /gold_api com método "user_balance"
   ↓
3. Retornamos saldo atual do banco (user.balance)
   ↓
4. IGameWin usa este saldo como saldo inicial do jogo
   ↓
5. Durante o jogo, IGameWin chama /gold_api com método "transaction"
   ↓
6. Atualizamos user.balance no banco
   ↓
7. Retornamos novo saldo
   ↓
8. IGameWin atualiza saldo do jogo com este valor
```

## 🔄 Sincronização Automática

O sistema agora sincroniza automaticamente:

1. **Durante o jogo:**
   - Atualização a cada 3 segundos
   - Saldo da carteira sincroniza com transações processadas

2. **Ao voltar para a aba:**
   - Atualização imediata quando página ganha foco

3. **Ao sair do jogo:**
   - Atualização automática antes de sair da página
   - Saldo sincronizado quando volta para home

## 📊 Fluxo de Sincronização

```
Jogo mostra: 0.20 BRL
    ↓
IGameWin processou transações via /gold_api
    ↓
Nosso banco tem: user.balance = 0.20
    ↓
Frontend atualiza automaticamente (a cada 3-5 segundos)
    ↓
Carteira mostra: R$ 0,20 ✅
```

## ⚠️ Importante

**O saldo do jogo é sempre a fonte da verdade!**

- Se o jogo mostra 0.20 BRL, nosso banco deve ter 0.20
- Se há discrepância, significa que:
  - Alguma transação não foi processada corretamente
  - Ou houve um problema na sincronização inicial

## 🔍 Verificação

Para verificar se está sincronizado:

1. **Ver saldo no jogo** (dentro do jogo IGameWin)
2. **Ver saldo na carteira** (header do site)
3. **Comparar valores** - devem ser iguais

Se houver diferença:
- O sistema atualiza automaticamente em 3-5 segundos
- Ou ao voltar para a aba/página

## 🛠️ Logs para Debug

O sistema registra logs detalhados:

```
[Gold API] User balance requested - user=username, balance=0.20
[Gold API] This balance will be used by IGameWin as the game balance
[Gold API] Transaction processed successfully - final balance: 0.20
[Gold API] This balance (0.20) is now the source of truth for the game
```

## ✅ Resultado Esperado

Após as correções:
- ✅ Saldo no jogo = Saldo na carteira
- ✅ Sincronização automática a cada 3-5 segundos
- ✅ Atualização imediata ao voltar para a aba
- ✅ Saldo sempre sincronizado

---

**Data:** 2026-01-27
**Status:** ✅ Implementado
