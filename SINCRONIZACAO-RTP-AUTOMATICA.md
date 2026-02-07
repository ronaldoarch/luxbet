# ✅ Sincronização Automática de RTP

## 🎯 Como Funciona

### Quando Você Atualiza RTP no Admin da Plataforma:

1. ✅ Você atualiza o RTP no admin (ex: muda de 26% para 94%)
2. ✅ O sistema **automaticamente** chama `control_rtp` na API do IGameWin
3. ✅ O RTP é sincronizado com o IGameWin
4. ✅ O novo RTP é aplicado em todos os jogos

**Não precisa fazer nada manualmente!** A sincronização acontece automaticamente.

---

## 🔄 Fluxo de Sincronização

### Quando Cria um Agente:

```
1. Você cria agente no admin com RTP 26%
   ↓
2. Sistema salva no banco de dados
   ↓
3. Sistema automaticamente chama control_rtp(rtp=26) no IGameWin
   ↓
4. RTP 26% configurado no IGameWin ✅
```

### Quando Atualiza RTP do Agente:

```
1. Você atualiza RTP no admin (ex: 26% → 94%)
   ↓
2. Sistema detecta que campo 'rtp' foi atualizado
   ↓
3. Sistema salva no banco de dados
   ↓
4. Sistema automaticamente chama control_rtp(rtp=94) no IGameWin
   ↓
5. RTP 94% configurado no IGameWin ✅
```

---

## ✅ Confirmação

**Se você já deixou RTP 26% no painel do IGameWin**:
- ✅ Está configurado no IGameWin
- ✅ Está aplicado nos jogos

**Se você atualizar no admin da plataforma**:
- ✅ Vai sincronizar automaticamente
- ✅ Vai atualizar o RTP no IGameWin
- ✅ Vai aplicar o novo RTP nos jogos

---

## 🧪 Como Testar

### Teste 1: Atualizar RTP no Admin

1. **Acesse o admin** da plataforma
2. **Vá em IGameWin Agents**
3. **Edite o agente**
4. **Mude o RTP** (ex: de 26 para 94)
5. **Salve**

**O que acontece**:
- Sistema salva no banco
- Sistema automaticamente chama `control_rtp` no IGameWin
- RTP é sincronizado

### Teste 2: Verificar Logs

**No console do backend**, você deve ver:
```
[IGameWin Agent] RTP atualizado e sincronizado: 26.0% → 94.0%
[IGameWin] Controlling RTP for agent - rtp=94
[IGameWin] RTP controlled successfully - changed_rtp=94
```

---

## ⚠️ Validações Automáticas

### Antes de Sincronizar:

- ✅ Valida se agente está ativo (`is_active == True`)
- ✅ Valida se tem credenciais (`agent_code` e `agent_key`)
- ✅ Valida se RTP <= 95 (conforme documentação IGameWin)

### Se Validação Falhar:

- ⚠️ Apenas loga aviso (não bloqueia atualização)
- ✅ Agente ainda é atualizado no banco
- ⚠️ RTP não é sincronizado com IGameWin

---

## 📊 Situação Atual

### Se RTP já está 26% no Painel IGameWin:

**Status**: ✅ RTP 26% já está aplicado nos jogos

**Se você atualizar no admin**:
- ✅ Vai sincronizar automaticamente
- ✅ Vai atualizar o RTP no IGameWin
- ✅ Vai aplicar o novo RTP nos jogos

---

## 🎯 Resposta à Sua Pergunta

**"Se eu atualizar no admin da plataforma vai sincronizar?"**

**Resposta**: 
- ✅ **SIM!** Vai sincronizar automaticamente
- ✅ Quando você atualizar o RTP no admin, o sistema automaticamente chama `control_rtp` no IGameWin
- ✅ Não precisa fazer nada manualmente

**Como funciona**:
1. Você atualiza RTP no admin (ex: 26% → 94%)
2. Sistema detecta mudança no campo `rtp`
3. Sistema salva no banco
4. Sistema automaticamente sincroniza com IGameWin
5. RTP atualizado nos jogos ✅

---

## 💡 Dica

**Se você já configurou RTP 26% no painel do IGameWin**:
- Está tudo certo! RTP 26% já está aplicado
- Se atualizar no admin, vai sincronizar automaticamente
- Se quiser mudar para outro valor, só atualizar no admin

**Sincronização funciona em ambos os sentidos**:
- ✅ Admin → IGameWin (automático quando atualiza no admin)
- ✅ IGameWin → Admin (manual, você precisa atualizar no admin)

---

**Status**: ✅ Sincronização automática implementada e funcional!

**Ação**: Simplesmente atualize o RTP no admin quando quiser mudar - vai sincronizar automaticamente! 🚀
