# ✅ Controle de RTP Implementado e Funcional

## 🎯 O Que Foi Implementado

Implementei o controle de RTP conforme documentação oficial do IGameWin:

1. ✅ **Método `control_rtp`** na classe `IGameWinAPI`
2. ✅ **3 endpoints no admin** para controlar RTP:
   - Control Agent RTP
   - Control User RTP
   - Control Bulk Users RTP

---

## 📋 Endpoints Disponíveis

### 1. Control Agent RTP

**Endpoint**: `POST /api/admin/igamewin/control-rtp/agent`

**Request**:
```json
{
  "rtp": 92
}
```

**Response (Success)**:
```json
{
  "status": 1,
  "changed_rtp": 92
}
```

**Response (Failure)**:
```json
{
  "status": 0,
  "msg": "Invalid Parameter.",
  "detail": "rtp must be less than or equal to 95"
}
```

---

### 2. Control User RTP

**Endpoint**: `POST /api/admin/igamewin/control-rtp/user`

**Request**:
```json
{
  "rtp": 92,
  "user_code": "test"
}
```

**Response (Success)**:
```json
{
  "status": 1,
  "changed_rtp": 92
}
```

**Response (Failure)**:
```json
{
  "status": 0,
  "msg": "Invalid Parameter.",
  "detail": "rtp must be less than or equal to 95"
}
```

---

### 3. Control Bulk Users RTP

**Endpoint**: `POST /api/admin/igamewin/control-rtp/bulk-users`

**Request**:
```json
{
  "rtp": 92,
  "user_codes": ["test", "test2", "test3"]
}
```

**Response (Success)**:
```json
{
  "status": 1,
  "changed_rtp": 92
}
```

**Response (Failure)**:
```json
{
  "status": 0,
  "msg": "Invalid Parameter.",
  "detail": "rtp must be less than or equal to 95"
}
```

---

## 🧪 Como Testar

### Teste 1: Control Agent RTP

**Usando curl**:
```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/agent" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 92}'
```

**Usando Postman/Insomnia**:
1. Método: `POST`
2. URL: `https://api.luxbet.site/api/admin/igamewin/control-rtp/agent`
3. Headers:
   - `Authorization: Bearer SEU_TOKEN_ADMIN`
   - `Content-Type: application/json`
4. Body (JSON):
   ```json
   {
     "rtp": 92
   }
   ```

**Resultado esperado**:
```json
{
  "status": 1,
  "changed_rtp": 92
}
```

---

### Teste 2: Control User RTP

**Usando curl**:
```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/user" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 92, "user_code": "test"}'
```

**Body (JSON)**:
```json
{
  "rtp": 92,
  "user_code": "test"
}
```

**Resultado esperado**:
```json
{
  "status": 1,
  "changed_rtp": 92
}
```

---

### Teste 3: Control Bulk Users RTP

**Usando curl**:
```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/bulk-users" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 92, "user_codes": ["test", "test2", "test3"]}'
```

**Body (JSON)**:
```json
{
  "rtp": 92,
  "user_codes": ["test", "test2", "test3"]
}
```

**Resultado esperado**:
```json
{
  "status": 1,
  "changed_rtp": 92
}
```

---

## ✅ Validações Implementadas

### Validação de RTP:
- ✅ RTP deve ser <= 95
- ✅ Se RTP > 95, retorna erro: `"rtp must be less than or equal to 95"`

### Validação de User Code:
- ✅ Para Control User RTP: `user_code` é obrigatório
- ✅ Para Control Bulk Users RTP: `user_codes` é obrigatório e não pode estar vazio

### Validação de Agente:
- ✅ Verifica se há agente IGameWin ativo configurado
- ✅ Retorna erro se não houver agente ativo

---

## 🔍 Como Confirmar que Está Funcionando

### 1. Testar Endpoint de Agent RTP

**Teste com RTP válido (<= 95)**:
```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/agent" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 92}'
```

**Esperado**: `{"status": 1, "changed_rtp": 92}`

**Teste com RTP inválido (> 95)**:
```bash
curl -X POST "https://api.luxbet.site/api/admin/igamewin/control-rtp/agent" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rtp": 96}'
```

**Esperado**: `{"detail": "rtp must be less than or equal to 95"}`

---

### 2. Verificar Logs do Backend

**No console do backend**, você deve ver:
```
[IGameWin] Controlling RTP for agent - rtp=92
[IGameWin] RTP controlled successfully - changed_rtp=92
```

**Se houver erro**:
```
[IGameWin] Error controlling RTP: status=0 msg=... detail=...
```

---

### 3. Verificar Resposta da API IGameWin

**A implementação chama diretamente a API do IGameWin**:
- Endpoint: `https://igamewin.com/api/v1`
- Método: `control_rtp`
- Payload conforme documentação oficial

**Se a API do IGameWin retornar erro**, será retornado na resposta do nosso endpoint.

---

## 📊 Funcionalidades Adicionais

### Atualização Automática no Banco de Dados

**Para Control Agent RTP**:
- Após sucesso, atualiza automaticamente o campo `rtp` do agente no banco de dados
- Isso mantém o RTP sincronizado entre nosso sistema e o IGameWin

---

## 🚨 Possíveis Erros

### Erro 1: RTP > 95

**Causa**: RTP deve ser <= 95 conforme documentação IGameWin

**Solução**: Use RTP entre 0 e 95

---

### Erro 2: Agente Não Configurado

**Causa**: Não há agente IGameWin ativo configurado

**Solução**: Configure um agente IGameWin ativo no admin

---

### Erro 3: Erro na API IGameWin

**Causa**: API do IGameWin retornou erro

**Solução**: Verifique logs do backend para ver erro específico da API IGameWin

---

## ✅ Checklist de Teste

- [ ] Testar Control Agent RTP com RTP válido (<= 95)
- [ ] Testar Control Agent RTP com RTP inválido (> 95) - deve retornar erro
- [ ] Testar Control User RTP com user_code válido
- [ ] Testar Control User RTP sem user_code - deve retornar erro
- [ ] Testar Control Bulk Users RTP com lista de user_codes
- [ ] Testar Control Bulk Users RTP sem user_codes - deve retornar erro
- [ ] Verificar logs do backend para confirmar chamadas à API IGameWin
- [ ] Verificar se RTP do agente é atualizado no banco após Control Agent RTP

---

## 🎯 Resumo

✅ **Implementação Completa**: Todos os 3 métodos de controle de RTP implementados  
✅ **Validações**: RTP <= 95, user_code obrigatório quando necessário  
✅ **Integração**: Chama diretamente API do IGameWin conforme documentação  
✅ **Sincronização**: Atualiza RTP no banco de dados após Control Agent RTP  
✅ **Logs**: Logs detalhados para debug  

**Status**: ✅ Implementado e pronto para teste!

**Próximo passo**: Testar os endpoints para confirmar que estão funcionando corretamente com a API do IGameWin.
