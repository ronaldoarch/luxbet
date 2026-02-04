# ✅ DNS Configurado - Próximos Passos

## 🎉 Status Atual

✅ **DNS Configurado Corretamente na Contabo**
- Registro A para `luxbet.site` ✅
- Registro A para `www.luxbet.site` ✅
- Registro A para `api.luxbet.site` ✅
- Registro wildcard `*.luxbet.site` ✅
- Nameservers corretos ✅
- Sem duplicados ✅

---

## ⏱️ Passo 1: Aguardar Propagação DNS

**Tempo estimado**: 1-2 horas (pode levar até 48h)

### Verificar Propagação:

1. Acesse: https://dnschecker.org
2. Digite: `luxbet.site`
3. Verifique se o IP `147.93.147.33` aparece em todos os servidores
4. Repita para `www.luxbet.site` e `api.luxbet.site`

---

## 🔧 Passo 2: Configurar Domínios no Coolify

### Frontend:

1. Acesse o Coolify
2. Vá na aplicação **Frontend**
3. Clique em **Domains** ou **Settings** → **Domains**
4. Adicione:
   - `luxbet.site`
   - `www.luxbet.site` (opcional)

### Backend:

1. Acesse o Coolify
2. Vá na aplicação **Backend**
3. Clique em **Domains**
4. Adicione:
   - `api.luxbet.site`

**⚠️ IMPORTANTE**: O Coolify deve gerar certificados SSL automaticamente via Let's Encrypt após o DNS propagar.

---

## 🔧 Passo 3: Verificar Variáveis de Ambiente

### Frontend (Coolify):

Verifique se está configurado:
```env
VITE_API_URL=https://api.luxbet.site
```

**Se não estiver configurado:**
1. Vá em **Environment Variables**
2. Adicione: `VITE_API_URL=https://api.luxbet.site`
3. **Faça REDEPLOY** (crucial!)

### Backend (Coolify):

Verifique CORS (opcional, já está configurado para permitir tudo):
```env
CORS_ORIGINS=https://luxbet.site,https://www.luxbet.site
```

Ou mantenha como está (já permite todas as origens).

---

## 🚀 Passo 4: Fazer Redeploy

### Frontend:

1. Coolify → Frontend → **Redeploy**
2. Aguarde build completar
3. Verifique se não há erros nos logs

### Backend:

1. Coolify → Backend → **Redeploy** (se necessário)
2. Aguarde build completar

---

## 🧪 Passo 5: Testar Após Propagação DNS

### Teste 1: Backend (Após 1-2 horas)

No celular (4G), acesse:
```
https://api.luxbet.site/api/health
```

**Esperado**: `{"status": "healthy"}`

### Teste 2: Frontend (Após 1-2 horas)

No celular (4G), acesse:
```
https://luxbet.site
```

**Esperado**: Site carrega normalmente

### Teste 3: Console do Navegador

No celular (4G), abra o site e console (F12):
```javascript
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
```

**Esperado**: `https://api.luxbet.site` (NÃO `undefined` ou `localhost`)

---

## 📋 Checklist Completo

### DNS:
- [x] Registros A configurados na Contabo
- [x] Nameservers alterados para Contabo
- [ ] DNS propagado (verificar em dnschecker.org)
- [ ] Todos os domínios resolvendo corretamente

### Coolify - Frontend:
- [ ] Domínio `luxbet.site` adicionado
- [ ] Domínio `www.luxbet.site` adicionado (opcional)
- [ ] Variável `VITE_API_URL=https://api.luxbet.site` configurada
- [ ] REDEPLOY feito após configurar variável
- [ ] SSL gerado automaticamente
- [ ] Status: Running

### Coolify - Backend:
- [ ] Domínio `api.luxbet.site` adicionado
- [ ] SSL gerado automaticamente
- [ ] Status: Running
- [ ] Health check funcionando

### Testes:
- [ ] Backend acessível via `https://api.luxbet.site/api/health`
- [ ] Frontend acessível via `https://luxbet.site`
- [ ] Console mostra `VITE_API_URL` corretamente
- [ ] Testado no 4G e funcionando

---

## ⏱️ Timeline Esperada

1. **Agora**: DNS configurado ✅
2. **1-2 horas**: DNS propagado globalmente
3. **Após propagação**: Adicionar domínios no Coolify
4. **5-10 minutos**: SSL gerado automaticamente
5. **Após SSL**: Fazer redeploy do frontend
6. **Teste final**: Testar no 4G

**Total**: ~2-3 horas para tudo funcionar

---

## 🚨 Se Ainda Não Funcionar Após Propagação

### Verificar Logs do Coolify:
- Frontend → Logs → Procure erros
- Backend → Logs → Procure erros

### Verificar SSL:
- Domains → SSL → Verifique se certificados foram gerados
- Se não, force regeneração

### Verificar Status das Aplicações:
- Frontend: Deve estar "Running"
- Backend: Deve estar "Running"

### Testar Endpoints:
```bash
# Backend
curl https://api.luxbet.site/api/health

# Frontend
curl https://luxbet.site
```

---

## 📝 Resumo

✅ **DNS**: Configurado corretamente na Contabo
⏳ **Próximo**: Aguardar propagação (1-2h)
🔧 **Depois**: Adicionar domínios no Coolify
🚀 **Final**: Fazer redeploy e testar no 4G

**Ação imediata**: Aguarde 1-2 horas para DNS propagar, depois adicione os domínios no Coolify!
