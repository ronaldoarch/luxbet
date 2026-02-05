# 🔍 Verificação das Labels Traefik - luxbet.site

## ✅ Análise das Labels Atuais

### O que está correto:

1. ✅ **Traefik habilitado**: `traefik.enable=true`
2. ✅ **Compressão GZIP**: `traefik.http.middlewares.gzip.compress=true`
3. ✅ **Redirecionamento HTTP→HTTPS**: Configurado corretamente
4. ✅ **TLS/SSL**: Configurado com Let's Encrypt
5. ✅ **Porta**: 80 (correto para frontend)
6. ✅ **Regra de Host**: `Host(\`luxbet.site\`)`

---

## ⚠️ Problemas Identificados

### Problema 1: Falta `www.luxbet.site`

As labels atuais só incluem `luxbet.site`, mas não `www.luxbet.site`.

**Atual**:
```yaml
traefik.http.routers.http-0-xxx.rule=Host(`luxbet.site`) && PathPrefix(`/`)
traefik.http.routers.https-0-xxx.rule=Host(`luxbet.site`) && PathPrefix(`/`)
```

**Deveria ser**:
```yaml
traefik.http.routers.http-0-xxx.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`) && PathPrefix(`/`)
traefik.http.routers.https-0-xxx.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`) && PathPrefix(`/`)
```

---

## ✅ Solução: Adicionar www.luxbet.site

### Opção 1: Adicionar Domínio no Coolify (Recomendado)

1. No Coolify, vá na aplicação Frontend
2. Vá em **Domains** ou **Configuration** → **Custom Domain**
3. Adicione: `www.luxbet.site`
4. O Coolify deve gerar labels automaticamente para ambos

### Opção 2: Editar Labels Manualmente

Se precisar editar manualmente, adicione nas **Custom Labels**:

```yaml
traefik.enable=true
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https

# HTTP Router (redireciona para HTTPS)
traefik.http.routers.luxbet-http.entrypoints=web
traefik.http.routers.luxbet-http.middlewares=redirect-to-https
traefik.http.routers.luxbet-http.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`)
traefik.http.routers.luxbet-http.service=luxbet-service

# HTTPS Router
traefik.http.routers.luxbet-https.entrypoints=websecure
traefik.http.routers.luxbet-https.middlewares=gzip
traefik.http.routers.luxbet-https.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`)
traefik.http.routers.luxbet-https.service=luxbet-service
traefik.http.routers.luxbet-https.tls=true
traefik.http.routers.luxbet-https.tls.certresolver=letsencrypt

# Service
traefik.http.services.luxbet-service.loadbalancer.server.port=80
```

**Nota**: O Coolify geralmente gera isso automaticamente quando você adiciona ambos os domínios.

---

## 🔍 Verificações Adicionais

### 1. Verificar se Domínios Estão Adicionados

No Coolify:
- Frontend → Domains
- Deve ter: `luxbet.site` ✅
- Deve ter: `www.luxbet.site` ⚠️ (verificar se está)

### 2. Verificar SSL

- Frontend → Domains → SSL
- Deve estar **"Active"** para ambos domínios
- Se não estiver, aguarde ou force regeneração

### 3. Verificar Status da Aplicação

- Frontend → Status deve ser **"Running"**
- Verifique logs se houver erros

---

## 🚨 Se Ainda Não Funcionar no 4G

### Verificar DNS

1. Acesse: https://dnschecker.org
2. Digite: `luxbet.site`
3. Verifique se retorna: `147.93.147.33`
4. Se não retornar, DNS ainda não propagou

### Verificar Variável de Ambiente

1. Frontend → Environment Variables
2. Verifique se `VITE_API_URL=https://api.luxbet.site` está configurada
3. Se não estiver, adicione e faça **REDEPLOY**

### Verificar Console do Navegador

No celular (4G), acesse o site e console (F12):
```javascript
console.log(import.meta.env.VITE_API_URL);
```

**Esperado**: `https://api.luxbet.site`
**Se mostrar `undefined`**: Variável não foi incluída no build → Fazer redeploy

---

## 📋 Labels Traefik Completas (Recomendadas)

Se quiser configurar manualmente, use estas labels completas:

```yaml
traefik.enable=true

# Middlewares
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https

# HTTP Router (redireciona para HTTPS)
traefik.http.routers.luxbet-http.entrypoints=web
traefik.http.routers.luxbet-http.middlewares=redirect-to-https
traefik.http.routers.luxbet-http.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`)
traefik.http.routers.luxbet-http.service=luxbet-service

# HTTPS Router
traefik.http.routers.luxbet-https.entrypoints=websecure
traefik.http.routers.luxbet-https.middlewares=gzip
traefik.http.routers.luxbet-https.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`)
traefik.http.routers.luxbet-https.service=luxbet-service
traefik.http.routers.luxbet-https.tls=true
traefik.http.routers.luxbet-https.tls.certresolver=letsencrypt

# Service
traefik.http.services.luxbet-service.loadbalancer.server.port=80
```

**Diferenças principais**:
- ✅ Inclui `www.luxbet.site` nas regras
- ✅ Nomes mais limpos (sem IDs aleatórios)
- ✅ Mesma funcionalidade

---

## ✅ Checklist de Verificação

- [ ] Labels Traefik incluem `www.luxbet.site` (ou domínio adicionado no Coolify)
- [ ] Porta 80 configurada corretamente
- [ ] SSL ativo para ambos domínios
- [ ] Aplicação rodando (status "Running")
- [ ] Variável `VITE_API_URL` configurada
- [ ] REDEPLOY feito após configurar variável
- [ ] DNS propagado (verificar em dnschecker.org)
- [ ] Testado no 4G após propagação

---

## 🎯 Ação Recomendada

**Ação imediata**:

1. **Adicionar `www.luxbet.site` no Coolify**:
   - Frontend → Domains → Adicionar `www.luxbet.site`
   - O Coolify deve gerar labels automaticamente

2. **Verificar SSL**:
   - Aguarde SSL ser gerado para ambos domínios
   - Ou force regeneração se necessário

3. **Verificar Variável de Ambiente**:
   - Frontend → Environment Variables
   - Verifique `VITE_API_URL=https://api.luxbet.site`
   - Se não estiver, adicione e faça **REDEPLOY**

4. **Aguardar Propagação DNS**:
   - Verifique em dnschecker.org
   - Aguarde 1-2 horas se necessário

5. **Testar no 4G**:
   - Após propagação DNS
   - Teste `https://luxbet.site` e `https://www.luxbet.site`

---

## 📝 Resumo

**Labels Traefik estão quase corretas**, mas falta:
- ⚠️ Adicionar `www.luxbet.site` nas regras (ou adicionar domínio no Coolify)

**Outras verificações necessárias**:
- Variável `VITE_API_URL` configurada
- REDEPLOY feito
- DNS propagado
- SSL ativo

**Ação**: Adicione `www.luxbet.site` como domínio no Coolify e o sistema deve gerar as labels corretas automaticamente!
