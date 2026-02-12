# 🚨 Erro NXGate - Falha ao Autenticar na LottoPay

## 🎯 Erro Identificado

**Erro**: `{"error":"Erro interno","detalhe":"Falha ao autenticar na LottoPay"}`  
**Status**: HTTP 500  
**Endpoint**: `POST /pix/gerar`

---

## 🔍 Análise do Erro

### O Que Está Acontecendo:

1. **Requisição enviada corretamente**:
   - URL: `https://api.nxgate.com.br/pix/gerar`
   - Payload com `api_key` incluída
   - Headers corretos

2. **NXGate recebe a requisição**:
   - Processa a requisição
   - Tenta autenticar com LottoPay (provedor de pagamento)

3. **Falha na autenticação com LottoPay**:
   - NXGate não consegue autenticar na LottoPay
   - Retorna erro HTTP 500

---

## 🔍 Possíveis Causas

### Causa 1: API Key Inválida ou Expirada

**Sintoma**: API Key não está mais válida ou foi revogada

**Solução**:
1. Verificar API Key no painel NXGate
2. Gerar nova API Key se necessário
3. Atualizar API Key no admin da plataforma

---

### Causa 2: API Key Sem Permissão para LottoPay

**Sintoma**: API Key válida mas não tem permissão para usar LottoPay

**Solução**:
1. Verificar permissões da API Key no painel NXGate
2. Habilitar permissão para LottoPay
3. Ou usar outro provedor de pagamento

---

### Causa 3: Problema na Conta LottoPay

**Sintoma**: Conta LottoPay vinculada ao NXGate com problema

**Solução**:
1. Verificar status da conta LottoPay no painel NXGate
2. Verificar se há pendências ou bloqueios
3. Contatar suporte NXGate se necessário

---

### Causa 4: Credenciais LottoPay Não Configuradas no NXGate

**Sintoma**: NXGate não tem credenciais da LottoPay configuradas

**Solução**:
1. Acessar painel NXGate
2. Configurar credenciais da LottoPay
3. Verificar se integração LottoPay está ativa

---

## ✅ Soluções Práticas

### Solução 1: Verificar API Key no Admin

**No admin da plataforma**:
1. Vá em **Gateways**
2. Encontre o gateway NXGate
3. Verifique se API Key está configurada corretamente
4. Se necessário, atualize a API Key

---

### Solução 2: Verificar no Painel NXGate

**No painel NXGate**:
1. Acesse: https://nxgate.com.br (ou painel administrativo)
2. Verifique:
   - Status da API Key
   - Permissões da API Key
   - Status da integração LottoPay
   - Se há erros ou avisos

---

### Solução 3: Gerar Nova API Key

**Se API Key estiver inválida**:
1. No painel NXGate, gere nova API Key
2. Atualize no admin da plataforma:
   - Gateways → Editar NXGate
   - Cole nova API Key
   - Salve

---

### Solução 4: Verificar Integração LottoPay

**No painel NXGate**:
1. Verifique se integração LottoPay está ativa
2. Verifique se credenciais LottoPay estão configuradas
3. Verifique se há pendências ou bloqueios

---

### Solução 5: Contatar Suporte NXGate

**Se nada funcionar**:
1. Contate suporte NXGate
2. Informe o erro: "Falha ao autenticar na LottoPay"
3. Informe sua API Key (ou ID da conta)
4. Peça verificação da integração LottoPay

---

## 🧪 Como Diagnosticar

### Teste 1: Verificar API Key

**No admin da plataforma**:
- Confirme que API Key está configurada
- Confirme que API Key não está vazia
- Tente atualizar a API Key

### Teste 2: Verificar Logs

**No console do backend**, veja:
- Se API Key está sendo enviada no payload
- Se há outros erros antes do erro de autenticação
- Se há informações sobre a requisição

### Teste 3: Testar API Key Diretamente

**Usando curl**:
```bash
curl -X POST "https://api.nxgate.com.br/pix/gerar" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "nome_pagador": "Teste",
    "documento_pagador": "12345678900",
    "valor": 10.0,
    "api_key": "SUA_API_KEY_AQUI"
  }'
```

**Se retornar o mesmo erro**: Problema na API Key ou integração LottoPay

---

## 📊 Informações do Erro

### Payload Enviado:
```json
{
  "nome_pagador": "61996267042",
  "documento_pagador": "90906361290",
  "valor": 10.0,
  "api_key": "09bef9ee7893b2b25ed920d5d41bdf6a",
  "webhook": "https://api.luxbet.site/api/webhooks/nxgate/pix-cashin"
}
```

### Resposta Recebida:
```json
{
  "error": "Erro interno",
  "detalhe": "Falha ao autenticar na LottoPay"
}
```

**Status**: HTTP 500

---

## 🎯 Próximos Passos Recomendados

### 1. Verificar API Key (5 minutos)

**No admin da plataforma**:
- Confirme que API Key está correta
- Se necessário, gere nova API Key no painel NXGate

### 2. Verificar no Painel NXGate (10 minutos)

**No painel NXGate**:
- Verifique status da API Key
- Verifique integração LottoPay
- Verifique se há erros ou avisos

### 3. Contatar Suporte NXGate (se necessário)

**Se problema persistir**:
- Contate suporte NXGate
- Informe erro específico
- Peça verificação da integração LottoPay

---

## 💡 Nota Importante

**NXGate é um intermediário** que usa LottoPay como provedor de pagamento. O erro indica que:
- NXGate recebeu a requisição corretamente ✅
- NXGate tentou autenticar com LottoPay ❌
- LottoPay rejeitou a autenticação ❌

**Isso pode significar**:
- Problema nas credenciais LottoPay configuradas no NXGate
- Problema na conta LottoPay vinculada
- API Key sem permissão para usar LottoPay

---

## ✅ Checklist de Diagnóstico

- [ ] API Key está configurada no admin?
- [ ] API Key não está vazia?
- [ ] API Key está válida no painel NXGate?
- [ ] API Key tem permissão para LottoPay?
- [ ] Integração LottoPay está ativa no NXGate?
- [ ] Credenciais LottoPay estão configuradas no NXGate?
- [ ] Conta LottoPay está ativa e sem bloqueios?

---

**Status**: ⚠️ Erro de autenticação NXGate → LottoPay

**Ação**: Verificar API Key e integração LottoPay no painel NXGate
