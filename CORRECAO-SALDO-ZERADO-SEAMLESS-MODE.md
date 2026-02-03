# Correção: Saldo Zerado ao Entrar em Jogo (Seamless Mode)

## 🐛 Problema Identificado

O saldo do usuário estava sendo zerado quando ele entrava em um jogo, mesmo estando configurado em **Seamless Mode**.

### Causa Raiz

O sistema estava detectando incorretamente o modo de operação:
- Quando o IGameWin retornava saldo `0`, o sistema assumia **Transfer Mode**
- Em Transfer Mode, o sistema transfere o saldo para o IGameWin e zera nosso banco
- Isso causava perda de saldo mesmo em Seamless Mode

## ✅ Correções Implementadas

### 1. Detecção Melhorada de Seamless Mode

**Antes:**
```python
if igamewin_balance is None:
    if api.last_error and "ERROR_GET_BALANCE_END_POINT" in api.last_error:
        is_seamless_mode = True
    else:
        # Assumia Transfer Mode mesmo em caso de erro
        igamewin_balance = 0.0
else:
    # Se retornou valor, sempre assumia Transfer Mode
    is_seamless_mode = False
```

**Depois:**
```python
if igamewin_balance is None:
    if api.last_error and "ERROR_GET_BALANCE_END_POINT" in api.last_error:
        is_seamless_mode = True  # Seamless Mode detectado
    else:
        # Por segurança, assumir Seamless Mode se não conseguir verificar
        is_seamless_mode = True
else:
    # Se retornou 0 E nosso banco tem saldo, assumir Seamless Mode por segurança
    if igamewin_balance == 0.0 and our_balance_before_check > 0.01:
        is_seamless_mode = True
    else:
        is_seamless_mode = False  # Transfer Mode
```

### 2. Logs Detalhados Adicionados

Agora o sistema mostra claramente:
- Saldo antes de verificar IGameWin
- Modo detectado (Seamless ou Transfer)
- Se está pulando transferências (Seamless Mode)
- Saldo permanece no banco

### 3. Proteção Contra Perda de Saldo

- Se a transferência falhar, o saldo **NÃO** é zerado
- Logs mostram claramente quando o saldo não foi modificado devido a erro
- Refresh do banco antes de cada operação para garantir dados atualizados

### 4. Correção nos Webhooks de Saque

- Uso de `old_status` em vez de `withdrawal.status` para reverter saldo corretamente
- Logs detalhados mostrando saldo antes/depois da reversão

## 🔍 Como Verificar se Está Funcionando

### Nos Logs ao Entrar em um Jogo:

**Se estiver em Seamless Mode (correto):**
```
[Launch Game] 🔍 Detectando modo de operação do IGameWin
[Launch Game] Saldo no nosso banco ANTES de verificar IGameWin: R$ 2.40
[Launch Game] ✅ DETECTADO: Modo Seamless (Seamless Mode)
[Launch Game] ⚡ Modo Seamless detectado - pulando transferências
[Launch Game] Saldo permanece no nosso banco: R$ 2.40
[Launch Game] ✅ JOGO LANÇADO EM MODO SEAMLESS
```

**Se estiver em Transfer Mode (incorreto para Seamless):**
```
[Launch Game] ✅ DETECTADO: Modo Transfer (Transfer Mode)
[Launch Game] ⚠️  ATENÇÃO: Se você configurou Seamless Mode, verifique:
[Launch Game]   1. Campo 'Tipo de API' está como 'Seamless' no painel IGameWin
[Launch Game]   2. Campo 'Ponto final do site' está como 'https://api.luxbet.site'
[Launch Game]   3. Aguardou 2-5 minutos após salvar as configurações
```

## 📋 Checklist de Configuração Seamless Mode

Para garantir que está em Seamless Mode:

- [ ] Acessou painel IGameWin → "Agente de atualização"
- [ ] Campo "Tipo de API" está como **"Seamless"** (não "Contínuo" ou "Transfer")
- [ ] Campo "Ponto final do site" está como **`https://api.luxbet.site`** (URL do backend)
- [ ] Salvou as configurações
- [ ] Aguardou **2-5 minutos** para a configuração ser aplicada
- [ ] Testou iniciando um jogo e verificou os logs

## 🎯 Comportamento Esperado em Seamless Mode

1. **Ao entrar no jogo:**
   - ✅ Saldo **NÃO** é transferido para IGameWin
   - ✅ Saldo **NÃO** é zerado
   - ✅ Saldo permanece no nosso banco

2. **Durante o jogo:**
   - ✅ IGameWin chama nosso `/gold_api` para buscar saldo
   - ✅ IGameWin chama nosso `/gold_api` para processar transações
   - ✅ Saldo é atualizado diretamente no nosso banco

3. **Ao sair do jogo:**
   - ✅ Saldo já está atualizado (não precisa sincronizar)
   - ✅ Pode sacar imediatamente

## ⚠️ Se o Saldo Ainda Estiver Zerando

1. **Verifique os logs** ao entrar no jogo:
   - Procure por `[Launch Game]` nos logs
   - Verifique qual modo foi detectado
   - Verifique se há mensagens de transferência

2. **Verifique a configuração do IGameWin:**
   - Confirme que "Tipo de API" está como "Seamless"
   - Confirme que "Ponto final do site" está correto
   - Aguarde mais tempo (pode levar até 5 minutos)

3. **Se necessário, force Seamless Mode:**
   - O código agora assume Seamless Mode por segurança quando:
     - Não consegue verificar saldo do IGameWin
     - IGameWin retorna 0 e nosso banco tem saldo

## 📝 Arquivos Modificados

- `backend/routes/admin.py`:
  - Função `launch_game`: Melhorada detecção de Seamless Mode
  - Logs detalhados adicionados
  - Proteção contra zerar saldo incorretamente

- `backend/routes/payments.py`:
  - Função `create_pix_withdrawal`: Logs detalhados de dedução de saldo
  - Função `webhook_nxgate_pix_cashout`: Correção na reversão de saldo
  - Função `webhook_pix_cashout`: Correção na reversão de saldo

## ✅ Resultado Esperado

Com essas correções, o saldo **NÃO** deve mais ser zerado ao entrar em um jogo quando estiver em Seamless Mode. O sistema agora:

1. Detecta Seamless Mode corretamente
2. Pula todas as transferências em Seamless Mode
3. Mantém o saldo no nosso banco
4. Permite que o IGameWin chame nosso `/gold_api` para buscar saldo e processar transações
