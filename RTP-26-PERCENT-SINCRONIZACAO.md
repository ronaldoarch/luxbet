# ⚠️ RTP 26% - Sincronização Necessária

## 🎯 Situação Atual

**RTP do agente no banco de dados**: 26%  
**RTP configurado no IGameWin**: ❓ Desconhecido (pode ser diferente)

**⚠️ IMPORTANTE**: O RTP no banco de dados **NÃO é automaticamente aplicado** nos jogos. Ele precisa ser sincronizado com a API do IGameWin usando `control_rtp`.

---

## 🔍 Como o RTP Funciona

### 1. RTP no Banco de Dados

- O campo `rtp` na tabela `igamewin_agents` armazena o RTP configurado
- Atualmente está em **26%**
- Este valor é apenas para referência/controle interno

### 2. RTP no IGameWin

- O RTP **real** que afeta os jogos é o configurado na API do IGameWin
- Precisa ser configurado via método `control_rtp`
- O RTP no banco e no IGameWin podem estar **dessincronizados**

---

## ✅ Solução: Sincronizar RTP

### Opção 1: Sincronizar Manualmente (Rápido)

**Usando o endpoint de controle de RTP**:

```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/agent" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 26}'
```

**Resultado esperado**:
```json
{
  "status": 1,
  "changed_rtp": 26
}
```

**Isso vai**:
- Configurar RTP 26% no IGameWin
- Aplicar RTP 26% em todos os jogos do agente
- Sincronizar banco de dados com IGameWin

---

### Opção 2: Sincronização Automática (Implementada)

**Implementei sincronização automática** que:
- ✅ Sincroniza RTP automaticamente quando agente é **criado**
- ✅ Sincroniza RTP automaticamente quando RTP é **atualizado**
- ✅ Valida RTP <= 95 antes de sincronizar
- ✅ Não bloqueia criação/atualização se sincronização falhar

**Como funciona**:
1. Quando você cria um agente com RTP 26%, ele sincroniza automaticamente
2. Quando você atualiza o RTP do agente, ele sincroniza automaticamente
3. Se sincronização falhar, apenas loga aviso (não bloqueia operação)

---

## 🧪 Como Confirmar que RTP Está Sincronizado

### Teste 1: Verificar RTP no Banco

**No admin**, veja o RTP do agente:
- Deve mostrar: **26%**

### Teste 2: Sincronizar RTP Manualmente

**Execute o endpoint de controle de RTP**:
```bash
POST /api/admin/igamewin/control-rtp/agent
Body: {"rtp": 26}
```

**Se retornar sucesso**, RTP está sincronizado.

### Teste 3: Verificar Logs

**No console do backend**, você deve ver:
```
[IGameWin] Controlling RTP for agent - rtp=26
[IGameWin] RTP controlled successfully - changed_rtp=26
```

---

## ⚠️ Importante: RTP 26% é Muito Baixo

**RTP 26% significa**:
- Para cada R$ 100 apostados, apenas R$ 26 são retornados
- **74% de margem da casa** (muito alto)
- Jogadores vão perder muito rápido

**Recomendação**:
- RTP típico para cassinos: **94-96%**
- RTP mínimo recomendado: **90%**
- RTP 26% é extremamente baixo e pode afastar jogadores

**Se quiser aumentar o RTP**:
```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/agent" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 94}'
```

---

## 📊 Resumo

| Item | Status |
|------|--------|
| **RTP no banco** | ✅ 26% |
| **RTP no IGameWin** | ❓ Desconhecido (pode ser diferente) |
| **RTP aplicado nos jogos** | ❓ Depende do RTP configurado no IGameWin |
| **Sincronização automática** | ✅ Implementada (quando criar/atualizar agente) |
| **Sincronização manual** | ✅ Disponível via endpoint |

---

## 🎯 Próximos Passos

### 1. Sincronizar RTP Atual (26%)

**Execute**:
```bash
POST /api/admin/igamewin/control-rtp/agent
Body: {"rtp": 26}
```

**Isso vai garantir** que o RTP 26% está configurado no IGameWin e será aplicado nos jogos.

### 2. Considerar Aumentar RTP (Recomendado)

**Se quiser aumentar para RTP mais razoável**:
```bash
POST /api/admin/igamewin/control-rtp/agent
Body: {"rtp": 94}
```

**RTP recomendado**: 94-96%

---

## ✅ Resposta à Sua Pergunta

**"Atualmente o rtp do agente está em 26% isso vai ser refletido?"**

**Resposta**: 
- ❌ **NÃO automaticamente** - O RTP no banco não é aplicado automaticamente
- ✅ **SIM após sincronizar** - Você precisa sincronizar via `control_rtp` para aplicar
- ✅ **Sincronização automática implementada** - Agora sincroniza quando criar/atualizar agente

**Ação necessária**: 
1. Sincronizar RTP 26% manualmente agora (para garantir)
2. Ou atualizar o agente no admin (vai sincronizar automaticamente)

---

**Status**: ⚠️ RTP precisa ser sincronizado para ser aplicado nos jogos

**Ação**: Execute o endpoint de controle de RTP para sincronizar o RTP 26% com o IGameWin
