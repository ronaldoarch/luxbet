# 🔧 Como Configurar para Continuous Mode (Modo Contínuo)

## ✅ Vantagens do Continuous Mode

- ✅ **Mais simples** - não precisa implementar endpoint `/gold_api`
- ✅ **IGameWin gerencia** o saldo internamente
- ✅ **Menos dependência** do nosso servidor durante o jogo
- ✅ **Já está funcionando** - nosso código detecta automaticamente

---

## 🔧 Configuração no Painel IGameWin

### Passo 1: Configurar Tipo de API

1. **Acesse** o painel administrativo do IGameWin
2. **Vá em** "Agente de atualização"
3. **Localize** o campo **"Tipo de API"** ou **"API Type"**
4. **Selecione:** "Contínuo" ou "Transfer" ou "Continuous"
   - ⚠️ **NÃO selecione** "Seamless" ou "Modo Seamless"

### Passo 2: Campo "Ponto final do site" (Opcional)

- Pode deixar **vazio** ou configurar como `https://api.luxbet.site`
- Não é obrigatório para Continuous Mode
- O endpoint `/gold_api` não será usado

### Passo 3: Salvar e Aguardar

1. **Salve** as alterações
2. **Aguarde** 2-5 minutos para a configuração ser aplicada

---

## 🔍 Como Verificar se Está em Continuous Mode

### Nos Logs do Backend:

Quando você tentar iniciar um jogo, deve ver:

```
[Launch Game] Checking IGameWin mode for user: ...
[IGameWin] Getting user balance - user_code=...
[IGameWin] Balance response: {"status": 1, "user": {"balance": ...}}
[IGameWin] User balance: ...
[Launch Game] Transfer mode detected. IGameWin balance: ..., Local balance: ...
```

**Se você vê "Transfer mode detected"** → Está em Continuous Mode ✅

**Se você vê "Detected Seamless mode"** → Está em Seamless Mode ⚠️

---

## 📋 Como Funciona no Continuous Mode

### Fluxo Automático:

1. **Usuário clica** para iniciar jogo
2. **Backend busca saldo** no IGameWin usando `money_info`
3. **Se saldo diferente** → transfere diferença automaticamente:
   - Se nosso saldo > IGameWin → `user_deposit` (deposita diferença)
   - Se IGameWin > nosso saldo → `user_withdraw` (retira diferença)
4. **Backend chama** `game_launch` no IGameWin
5. **IGameWin retorna** URL do jogo
6. **Jogo carrega** e usa saldo do IGameWin diretamente

### Após o Jogo:

- **Saldo fica no IGameWin**
- **Precisa sincronizar** quando o usuário sair do jogo ou antes do próximo jogo
- **Nosso código sincroniza automaticamente** antes de cada lançamento

---

## ⚠️ Importante: Sincronização de Saldo

No Continuous Mode, o saldo fica no IGameWin durante o jogo. Após o jogo terminar:

### Opção 1: Sincronização Automática (Recomendado)

Nosso código já faz isso automaticamente antes de cada lançamento:
- Busca saldo no IGameWin
- Compara com nosso banco
- Sincroniza se necessário

### Opção 2: Sincronização Manual

Você pode criar um endpoint para sincronizar saldo manualmente:

```python
# Exemplo de endpoint para sincronizar saldo
@router.post("/igamewin/sync-balance/{username}")
async def sync_user_balance(username: str, db: Session = Depends(get_db)):
    api = get_igamewin_api(db)
    user = db.query(User).filter(User.username == username).first()
    
    igamewin_balance = await api.get_user_balance(username)
    if igamewin_balance is not None:
        balance_diff = user.balance - igamewin_balance
        if balance_diff > 0:
            await api.transfer_in(username, balance_diff)
        elif balance_diff < 0:
            await api.transfer_out(username, abs(balance_diff))
            user.balance = igamewin_balance
            db.commit()
```

---

## ✅ Checklist de Configuração

- [ ] Campo "Tipo de API" configurado como "Contínuo" ou "Transfer"
- [ ] Campo "Ponto final do site" pode ficar vazio (ou configurado opcionalmente)
- [ ] Aguardou 2-5 minutos após salvar
- [ ] Testou iniciar um jogo
- [ ] Verificou logs - deve mostrar "Transfer mode detected"
- [ ] Saldo está sincronizando corretamente

---

## 🎯 Vantagens para Seu Caso

Como você está usando Continuous Mode:

1. ✅ **Não precisa** do endpoint `/gold_api` funcionando
2. ✅ **Menos complexidade** - IGameWin gerencia tudo
3. ✅ **Código já está pronto** - detecta automaticamente e sincroniza
4. ✅ **Funciona imediatamente** - sem configuração adicional

---

## 📝 Notas Importantes

- O código **detecta automaticamente** qual modo está ativo
- **Funciona em ambos os modos** sem mudanças no código
- Se mudar de Continuous para Seamless, o código se adapta automaticamente
- A sincronização de saldo acontece **antes de cada lançamento** automaticamente

---

## 🔄 Se Quiser Mudar para Seamless Mode Depois

Se no futuro quiser usar Seamless Mode:

1. Configure "Tipo de API" como "Seamless"
2. Configure "Ponto final do site" como `https://api.luxbet.site`
3. O código detectará automaticamente e usará Seamless Mode
4. O endpoint `/gold_api` já está implementado e pronto!
