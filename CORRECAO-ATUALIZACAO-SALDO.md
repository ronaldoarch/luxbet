# Correção: Atualização de Saldo na Carteira

## 🐛 Problema Identificado

O saldo estava funcionando dentro dos jogos (atualizando corretamente), mas não estava atualizando na carteira exibida no header do site.

## ✅ Correções Implementadas

### 1. Redução do Intervalo de Atualização

**Antes:**
- Atualização a cada 15 segundos (páginas gerais)
- Atualização a cada 10 segundos (página do jogo)

**Depois:**
- Atualização a cada **5 segundos** (páginas gerais)
- Atualização a cada **3 segundos** (página do jogo)

### 2. Garantir Dados Atualizados no Backend

Adicionado `db.refresh(current_user)` no endpoint `/api/auth/me` para garantir que sempre retorna os dados mais atualizados do banco de dados.

**Arquivo:** `backend/routes/auth.py`
```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Garantir que temos os dados mais atualizados do banco
    db.refresh(current_user)
    return current_user
```

## 🔄 Como Funciona Agora

1. **Usuário aposta no jogo**
   - IGameWin chama nosso `/gold_api`
   - Backend debita o saldo (`user.balance -= bet_money`)
   - `db.commit()` e `db.refresh(user)` são executados

2. **Frontend atualiza automaticamente**
   - A cada 5 segundos (páginas gerais)
   - A cada 3 segundos (página do jogo)
   - Quando volta para a aba
   - Quando página fica visível

3. **Backend retorna saldo atualizado**
   - Endpoint `/api/auth/me` faz `db.refresh(current_user)`
   - Garante que sempre retorna o valor mais recente do banco

4. **Frontend exibe saldo atualizado**
   - Header atualiza automaticamente
   - Página "Minha Conta" atualiza automaticamente

## 📊 Tempos de Atualização

| Situação | Intervalo | Observação |
|----------|-----------|------------|
| Páginas gerais | 5 segundos | Header, Home, etc. |
| Página do jogo | 3 segundos | Durante o jogo |
| Voltar para aba | Imediato | Evento `focus` |
| Página visível | Imediato | Evento `visibilitychange` |

## ✅ Resultado Esperado

Agora o saldo na carteira deve atualizar automaticamente:
- ✅ Máximo 5 segundos após apostar (páginas gerais)
- ✅ Máximo 3 segundos após apostar (página do jogo)
- ✅ Imediatamente ao voltar para a aba
- ✅ Imediatamente quando página fica visível

## 🔍 Debug

Se ainda não estiver atualizando, verifique:

1. **Console do navegador:**
   - Abra DevTools (F12)
   - Vá em "Network"
   - Verifique se há chamadas para `/api/auth/me` a cada 5 segundos
   - Verifique se a resposta contém o saldo atualizado

2. **Logs do backend:**
   - Verifique se `/gold_api` está sendo chamado
   - Verifique se `db.commit()` está sendo executado
   - Verifique se o saldo está sendo atualizado no banco

3. **Banco de dados:**
   - Verifique diretamente no banco se `user.balance` está sendo atualizado
   - Execute: `SELECT username, balance FROM users WHERE username = 'seu_usuario';`

---

**Data:** 2026-01-27
**Status:** ✅ Corrigido
