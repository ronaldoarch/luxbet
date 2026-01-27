# Debug: Saldo Não Atualiza

## 🔍 Problema

O saldo na carteira não está atualizando mesmo após transações no jogo.

## 🔧 Melhorias Implementadas

### 1. Timestamp na Requisição

Adicionado timestamp (`?t=${Date.now()}`) na URL da requisição `/api/auth/me` para forçar atualização e evitar cache do navegador.

### 2. Logs de Debug

Adicionados logs detalhados para rastrear:
- Quando o saldo é atualizado no frontend
- Qual saldo está sendo retornado pelo backend
- Diferenças entre saldo antigo e novo

### 3. Verificação de Mudança

O frontend agora verifica se o saldo realmente mudou antes de logar, evitando logs desnecessários.

## 📊 Como Verificar

### 1. Abrir Console do Navegador (F12)

Você deve ver logs como:
```
[Balance Update] Saldo atualizado: R$ 2,00 → R$ 0,20
[Sync Balance] Atualizando saldo... Saldo atual: R$ 2,00
[Sync Balance] Saldo atualizado: R$ 0,20
```

### 2. Verificar Logs do Backend

No backend, você deve ver:
```
[Auth /me] User: username, Balance: 0.2
[Gold API] Transaction processed successfully - final balance: 0.2
```

### 3. Verificar Saldo no Banco

Execute no banco de dados:
```sql
SELECT username, balance FROM users WHERE username = 'seu_usuario';
```

## 🎯 Possíveis Causas

### Causa 1: Saldo no Banco Está Errado

**Sintoma:** Saldo no banco mostra R$ 2,00 mas deveria ser 0,20

**Solução:** 
- Verifique se as transações estão sendo processadas corretamente
- Verifique logs do `/gold_api` no backend
- Verifique se há erros nas transações

### Causa 2: Cache do Navegador

**Sintoma:** Requisições retornam dados antigos

**Solução:**
- Já implementado: timestamp na URL força atualização
- Já implementado: `cache: 'no-cache'` nas requisições

### Causa 3: Transações Não Estão Sendo Processadas

**Sintoma:** Logs do `/gold_api` não aparecem

**Solução:**
- Verifique se o endpoint `/gold_api` está acessível
- Verifique se o IGameWin está configurado corretamente
- Verifique se o "Ponto final do site" está configurado

## 🔍 Próximos Passos

1. **Teste o botão de refresh** na página "Minha Conta"
2. **Verifique o console** para ver os logs de atualização
3. **Verifique os logs do backend** para ver se as transações estão sendo processadas
4. **Verifique o saldo no banco** diretamente

## 📝 Logs Esperados

### Frontend (Console do Navegador)
```
[Sync Balance] Atualizando saldo... Saldo atual: R$ 2,00
[Balance Update] Saldo atualizado: R$ 2,00 → R$ 0,20
[Sync Balance] Saldo atualizado: R$ 0,20
```

### Backend (Logs do Servidor)
```
[Auth /me] User: username, Balance: 0.2
[Gold API] User balance requested - user=username, balance=0.2
[Gold API] Transaction processed successfully - final balance: 0.2
```

---

**Data:** 2026-01-27
**Status:** 🔍 Em Debug
