# 🔍 Diagnóstico - Plataforma não abre no 4G (Variável já configurada)

## ✅ Situação Atual

- `VITE_API_URL=https://api.luxbet.site` ✅ **Configurada**
- Status: "Running (unknown)" ⚠️ **Possível problema**

---

## 🔍 Próximos Passos de Diagnóstico

### 1. **Verificar se o Backend está Acessível**

Teste no celular (4G):

1. Abra o navegador no celular
2. Desative WiFi (use apenas 4G)
3. Acesse: `https://api.luxbet.site/api/health`
4. **O que deve aparecer**: `{"status": "healthy"}`

**Se não funcionar:**
- ❌ Problema de DNS ou rede
- ❌ Backend não está acessível publicamente
- ❌ Certificado SSL inválido

**Se funcionar:**
- ✅ Backend está OK, problema pode ser no frontend

---

### 2. **Verificar DNS**

No celular (4G), teste:

```
https://api.luxbet.site
```

**Possíveis problemas:**
- DNS não está propagado para redes móveis
- DNS bloqueado pelo provedor
- Domínio não configurado corretamente

**Solução temporária:**
- Use IP direto do servidor (se disponível)
- Ou aguarde propagação DNS (pode levar até 48h)

---

### 3. **Verificar Certificado SSL**

No navegador do celular (4G):

1. Acesse `https://api.luxbet.site`
2. Clique no cadeado ao lado da URL
3. Verifique se o certificado é válido

**Se houver aviso:**
- Certificado expirado ou inválido
- Certificado auto-assinado
- Navegadores móveis podem bloquear

---

### 4. **Verificar Logs do Frontend**

No Coolify:

1. Vá em **Frontend → Logs**
2. Procure por erros relacionados a:
   - `Failed to fetch`
   - `NetworkError`
   - `CORS`
   - `localhost`

---

### 5. **Verificar Build do Frontend**

O frontend pode não ter sido rebuildado após configurar a variável.

**Solução:**
1. No Coolify, clique em **"Redeploy"**
2. Aguarde o build completar
3. Verifique se a variável foi incluída no build

**Como verificar:**
- Após redeploy, acesse o site
- Abra console (F12)
- Digite: `console.log(import.meta.env.VITE_API_URL)`
- Deve mostrar: `https://api.luxbet.site`

---

### 6. **Testar no Console do Navegador**

No celular (4G), abra o site e console:

```javascript
// Verificar variável
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);

// Testar conexão
fetch('https://api.luxbet.site/api/health')
  .then(r => r.json())
  .then(d => console.log('✅ Backend OK:', d))
  .catch(e => console.error('❌ Backend ERRO:', e));
```

**Erros comuns:**

- `Failed to fetch` → Backend não acessível
- `NetworkError` → Problema de rede/DNS
- `undefined` → Variável não foi incluída no build (precisa redeploy)

---

### 7. **Verificar Status "Running (unknown)"**

O status "Running (unknown)" pode indicar:

- Health check não está funcionando
- Aplicação pode estar com problemas
- Monitoramento não está configurado

**Solução:**
1. Verifique se há health check endpoint configurado
2. Verifique logs do backend
3. Tente reiniciar a aplicação

---

## 🎯 Checklist de Diagnóstico

- [ ] Backend acessível via `https://api.luxbet.site/api/health` no 4G
- [ ] Certificado SSL válido
- [ ] DNS resolvendo corretamente no 4G
- [ ] Frontend fez redeploy após configurar variável
- [ ] Console mostra `VITE_API_URL` corretamente
- [ ] Logs do frontend não mostram erros
- [ ] Status da aplicação não é "unknown"

---

## 🔧 Soluções Rápidas

### Solução 1: Redeploy do Frontend

1. Coolify → Frontend → **Redeploy**
2. Aguarde build completar
3. Teste no 4G novamente

### Solução 2: Verificar DNS

Se `api.luxbet.site` não resolve no 4G:

1. Verifique configuração DNS no provedor
2. Use ferramenta: https://dnschecker.org
3. Verifique se todos os servidores DNS retornam o mesmo IP

### Solução 3: Testar com IP Direto

Se tiver IP do servidor:

1. Configure temporariamente: `VITE_API_URL=https://IP_DO_SERVIDOR`
2. Faça redeploy
3. Teste no 4G
4. Se funcionar, problema é DNS

---

## 📞 Informações Necessárias para Diagnóstico

Para ajudar melhor, preciso saber:

1. **Backend acessível no 4G?**
   - Teste: `https://api.luxbet.site/api/health` no celular (4G)
   - Funciona? Sim/Não

2. **Console do navegador mostra erros?**
   - Abra F12 no celular
   - Quais erros aparecem?

3. **Frontend fez redeploy após configurar variável?**
   - Sim/Não

4. **DNS está resolvendo?**
   - Teste: `nslookup api.luxbet.site` no celular
   - Retorna IP? Sim/Não

---

## 🚨 Problemas Mais Comuns

### Problema 1: DNS não propagado
**Sintoma**: Site não carrega no 4G, mas funciona no WiFi
**Solução**: Aguardar propagação DNS (24-48h) ou usar IP direto

### Problema 2: Certificado SSL inválido
**Sintoma**: Navegador mostra aviso de segurança
**Solução**: Renovar certificado no Coolify

### Problema 3: Variável não incluída no build
**Sintoma**: Console mostra `undefined` para `VITE_API_URL`
**Solução**: Fazer redeploy do frontend

### Problema 4: Backend bloqueando IPs móveis
**Sintoma**: Backend funciona no WiFi mas não no 4G
**Solução**: Verificar firewall/configurações de rede
