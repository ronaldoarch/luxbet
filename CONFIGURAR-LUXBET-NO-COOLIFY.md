# 🚀 Configurar luxbet.site no Coolify - Passo a Passo

## 📋 Checklist Pré-requisitos

- [x] DNS configurado na Hostinger
- [x] Nameservers da Hostinger configurados
- [x] Registros A para `luxbet.site`, `www.luxbet.site` e `api.luxbet.site`

---

## 🔧 Passo 1: Configurar Frontend no Coolify

### 1.1 Acessar Aplicação Frontend

1. Acesse o Coolify: `http://147.93.147.33:8000`
2. Vá em **Projects** → Selecione o projeto do luxbet
3. Abra a aplicação **Frontend** (ou crie uma nova se não existir)

### 1.2 Configuração Geral

Na aba **Configuration**, configure:

```
Name: luxbet-frontend (ou o nome que preferir)
Build Pack: Nixpacks (ou Dockerfile)
Base Directory: /frontend
```

### 1.3 Configuração de Porta

```
Ports Exposed: 80
Ports Mapping: (deixe vazio)
```

**⚠️ IMPORTANTE**: Use porta 80 (não vai conflitar com outros sites, Traefik roteia por domínio)

### 1.4 Configuração de Build

```
Build Command: npm ci && npm run build
Publish Directory: dist
Is Static Site: SIM ✓
```

### 1.5 Adicionar Domínios

1. Vá na aba **Domains** ou **Configuration** → **Custom Domain**
2. Adicione:
   - `luxbet.site`
   - `www.luxbet.site` (opcional)

3. O Coolify deve gerar SSL automaticamente via Let's Encrypt

### 1.6 Variáveis de Ambiente

Na aba **Environment Variables**, adicione:

```env
VITE_API_URL=https://api.luxbet.site
NIXPACKS_NODE_VERSION=22
```

**⚠️ CRÍTICO**: Após adicionar `VITE_API_URL`, você **DEVE fazer REDEPLOY**!

---

## 🔧 Passo 2: Configurar Backend no Coolify

### 2.1 Acessar Aplicação Backend

1. No mesmo projeto, abra a aplicação **Backend** (ou crie uma nova)

### 2.2 Configuração Geral

```
Name: luxbet-backend
Build Pack: Nixpacks (ou Dockerfile)
Base Directory: /backend
```

### 2.3 Configuração de Porta

```
Ports Exposed: 8000
Ports Mapping: 8000
```

### 2.4 Configuração de Build/Start

```
Build Command: (deixe vazio ou use: pip install -r requirements.txt)
Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2.5 Adicionar Domínio

1. Vá na aba **Domains**
2. Adicione:
   - `api.luxbet.site`

3. O Coolify deve gerar SSL automaticamente

### 2.6 Variáveis de Ambiente

Na aba **Environment Variables**, verifique se tem:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
CORS_ORIGINS=https://luxbet.site,https://www.luxbet.site
```

**Ou mantenha CORS permitindo tudo** (já está configurado assim no código)

---

## 🔧 Passo 3: Configurar Traefik Labels (Opcional)

Se precisar configurar manualmente, adicione em **Custom Labels**:

### Frontend:

```yaml
traefik.http.routers.luxbet-frontend.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`)
traefik.http.routers.luxbet-frontend.entrypoints=websecure
traefik.http.routers.luxbet-frontend.tls=true
traefik.http.services.luxbet-frontend.loadbalancer.server.port=80
```

### Backend:

```yaml
traefik.http.routers.luxbet-backend.rule=Host(`api.luxbet.site`)
traefik.http.routers.luxbet-backend.entrypoints=websecure
traefik.http.routers.luxbet-backend.tls=true
traefik.http.services.luxbet-backend.loadbalancer.server.port=8000
```

**Nota**: O Coolify geralmente configura isso automaticamente quando você adiciona os domínios.

---

## 🚀 Passo 4: Fazer Deploy

### 4.1 Frontend

1. Vá na aba **Deployments**
2. Clique em **Deploy** ou **Redeploy**
3. Aguarde build completar
4. Verifique logs se houver erros

### 4.2 Backend

1. Vá na aba **Deployments**
2. Clique em **Deploy** ou **Redeploy**
3. Aguarde build completar
4. Verifique logs se houver erros

---

## ✅ Passo 5: Verificar se Funcionou

### 5.1 Verificar Status

- Frontend: Status deve ser **"Running"**
- Backend: Status deve ser **"Running"**

### 5.2 Verificar SSL

- Frontend: SSL deve estar **"Active"** para `luxbet.site`
- Backend: SSL deve estar **"Active"** para `api.luxbet.site`

### 5.3 Testar Endpoints

#### Backend:
```bash
curl https://api.luxbet.site/api/health
# Deve retornar: {"status": "healthy"}
```

#### Frontend:
```bash
curl https://luxbet.site
# Deve retornar HTML do site
```

### 5.4 Verificar Variável de Ambiente no Build

Após deploy do frontend, verifique se a variável foi incluída:

1. Acesse o site: `https://luxbet.site`
2. Abra console (F12)
3. Digite:
   ```javascript
   console.log(import.meta.env.VITE_API_URL);
   ```
4. Deve mostrar: `https://api.luxbet.site` (NÃO `undefined`)

---

## 🧪 Passo 6: Testar no 4G

Após tudo configurado e funcionando:

1. **Aguarde propagação DNS** (se ainda não propagou): 1-2 horas
2. No celular (4G), desative WiFi
3. Acesse: `https://luxbet.site`
4. Deve carregar normalmente
5. Teste funcionalidades (login, depósito, etc.)

---

## 📋 Checklist Completo

### DNS (Hostinger):
- [x] Registros A configurados
- [x] Nameservers da Hostinger
- [ ] DNS propagado (verificar em dnschecker.org)

### Coolify - Frontend:
- [ ] Aplicação criada/configurada
- [ ] Porta 80 configurada
- [ ] Publish Directory: `dist`
- [ ] Is Static Site: SIM
- [ ] Domínios adicionados: `luxbet.site` e `www.luxbet.site`
- [ ] Variável `VITE_API_URL=https://api.luxbet.site` configurada
- [ ] REDEPLOY feito após configurar variável
- [ ] SSL gerado automaticamente
- [ ] Status: Running

### Coolify - Backend:
- [ ] Aplicação criada/configurada
- [ ] Porta 8000 configurada
- [ ] Domínio adicionado: `api.luxbet.site`
- [ ] Variáveis de ambiente configuradas
- [ ] SSL gerado automaticamente
- [ ] Status: Running

### Testes:
- [ ] Backend acessível: `https://api.luxbet.site/api/health`
- [ ] Frontend acessível: `https://luxbet.site`
- [ ] Console mostra `VITE_API_URL` corretamente
- [ ] Testado no 4G e funcionando

---

## 🚨 Problemas Comuns

### Problema 1: Frontend não conecta ao backend

**Causa**: `VITE_API_URL` não configurada ou não incluída no build

**Solução**:
1. Verifique se `VITE_API_URL=https://api.luxbet.site` está configurada
2. **Faça REDEPLOY** do frontend
3. Verifique console do navegador

### Problema 2: SSL não gera

**Causa**: DNS não propagou ainda

**Solução**:
1. Aguarde propagação DNS (1-2h)
2. Force regeneração SSL no Coolify
3. Verifique se domínios estão adicionados corretamente

### Problema 3: Site não carrega no 4G

**Causa**: DNS não propagou ou variável não configurada

**Solução**:
1. Verifique propagação DNS em dnschecker.org
2. Verifique se `VITE_API_URL` está configurada
3. Verifique se fez redeploy após configurar variável

---

## 📝 Resumo das Ações

1. ✅ **DNS**: Já configurado na Hostinger
2. ⏳ **Aguardar**: Propagação DNS (1-2h)
3. 🔧 **Coolify Frontend**: Configurar porta 80, domínios, variável `VITE_API_URL`
4. 🔧 **Coolify Backend**: Configurar porta 8000, domínio `api.luxbet.site`
5. 🚀 **Deploy**: Fazer redeploy do frontend (importante!)
6. 🧪 **Testar**: Após propagação, testar no 4G

---

## 🎯 Ação Imediata

**Agora mesmo, configure no Coolify**:

1. **Frontend**:
   - Porta: `80`
   - Domínios: `luxbet.site` e `www.luxbet.site`
   - Variável: `VITE_API_URL=https://api.luxbet.site`
   - **REDEPLOY**

2. **Backend**:
   - Porta: `8000`
   - Domínio: `api.luxbet.site`
   - **Deploy**

3. **Aguardar**: Propagação DNS e SSL

4. **Testar**: No 4G após propagação
