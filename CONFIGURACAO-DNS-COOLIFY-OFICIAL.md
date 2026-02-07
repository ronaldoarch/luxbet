# 📚 Configuração DNS no Coolify - Guia Oficial Aplicado

## 🎯 Como o Coolify Funciona com DNS

### Conceito Principal

**Coolify precisa de registros A** apontando para o IP do servidor (`147.93.147.33` no seu caso).

**Você pode usar o mesmo IP** para múltiplos domínios e subdomínios.

---

## ✅ Configuração para luxbet.site

### Domínio Único

Para usar `luxbet.site` com IP `147.93.147.33`:

**Na Hostinger, configure**:
```
Tipo: A
Nome: @ (ou deixe vazio)
Valor: 147.93.147.33
TTL: 300
```

**No Coolify**:
- Adicione domínio: `https://luxbet.site`
- Coolify automaticamente configura HTTPS e SSL

---

### Subdomínios (www, api)

**Na Hostinger, configure**:

#### Para www:
```
Tipo: A
Nome: www
Valor: 147.93.147.33
TTL: 300
```

#### Para api:
```
Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 300
```

**No Coolify**:
- Frontend: Adicione `https://luxbet.site` e `https://www.luxbet.site`
- Backend: Adicione `https://api.luxbet.site`
- Coolify automaticamente configura HTTPS e SSL para todos

---

## 🔒 HTTPS & Certificados SSL

### Como Funciona Automaticamente

Quando você adiciona um domínio com `https://` no Coolify:

1. ✅ **Configuração Automática do Proxy**: Coolify configura Traefik automaticamente
2. ✅ **Emissão de Certificado**: Coolify solicita certificado SSL do Let's Encrypt automaticamente
3. ✅ **Renovação Automática**: Certificados são renovados automaticamente antes de expirar

**⚠️ IMPORTANTE**: Você não precisa fazer nada especial! Apenas use `https://` ao adicionar domínio.

---

### Validação DNS

**Desde versão beta.191**, Coolify valida registros DNS usando DNS da Cloudflare (`1.1.1.1`).

**Se quiser usar outro DNS**:
- Coolify → Settings → Advanced → Custom DNS Servers
- Adicione servidores DNS separados por vírgula

---

## 🎯 Configuração Recomendada para luxbet.site

### Na Hostinger (DNS):

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | 300 |
| A | www | 147.93.147.33 | 300 |
| A | api | 147.93.147.33 | 300 |

**⚠️ CRÍTICO**: Use registro **A** (não CNAME) para todos!

---

### No Coolify - Frontend:

**Domains**:
```
https://luxbet.site
https://www.luxbet.site
```

**Environment Variables**:
```
VITE_API_URL=https://api.luxbet.site
```

**⚠️ IMPORTANTE**: Após adicionar `VITE_API_URL`, faça **REDEPLOY**!

---

### No Coolify - Backend:

**Domains**:
```
https://api.luxbet.site
```

**CORS** (se necessário):
```
CORS_ORIGINS=https://luxbet.site,https://www.luxbet.site
```

---

## 🔍 Validação DNS no Coolify

### Como Funciona

Coolify valida DNS automaticamente quando você adiciona um domínio:

1. **Verifica se DNS está propagado** usando DNS da Cloudflare (`1.1.1.1`)
2. **Aguarda propagação** se necessário
3. **Gera SSL** automaticamente após DNS propagar

**Se DNS não propagou ainda**:
- Coolify pode mostrar aviso
- SSL pode não ser gerado até DNS propagar
- Aguarde propagação DNS completa

---

## 🚨 Troubleshooting

### Problema 1: SSL Não É Gerado

**Causas possíveis**:
- DNS ainda não propagou completamente
- Domínio não está apontando para IP correto
- Problema com Let's Encrypt

**Solução**:
1. Verifique se DNS está propagado:
   ```bash
   nslookup luxbet.site
   # Deve retornar: 147.93.147.33
   ```

2. Aguarde propagação DNS completa

3. Force regeneração SSL no Coolify:
   - Coolify → Domains → SSL → Regenerate

---

### Problema 2: Certificado Self-Signed

**Causa**: Let's Encrypt não conseguiu gerar certificado

**Sintoma**: Navegador mostra aviso de segurança

**Solução**:
1. Verifique se DNS está propagado corretamente
2. Verifique se domínio está apontando para IP correto
3. Force regeneração SSL no Coolify
4. Aguarde alguns minutos

---

### Problema 3: DNS Não Valida no Coolify

**Causa**: DNS ainda não propagou para servidor DNS usado pelo Coolify

**Solução**:
1. Aguarde mais tempo para propagação DNS
2. Verifique propagação em: https://dnschecker.org
3. Se necessário, mude DNS server no Coolify:
   - Settings → Advanced → Custom DNS Servers
   - Adicione: `8.8.8.8,1.1.1.1` (Google e Cloudflare)

---

## ✅ Checklist Completo

### DNS na Hostinger:
- [ ] Registro A para `@` → `147.93.147.33` com TTL `300`
- [ ] Registro A para `www` → `147.93.147.33` com TTL `300` (NÃO CNAME!)
- [ ] Registro A para `api` → `147.93.147.33` com TTL `300`
- [ ] Não há CNAME para `www`
- [ ] Não há registros duplicados

### Coolify - Frontend:
- [ ] Domínio `https://luxbet.site` adicionado
- [ ] Domínio `https://www.luxbet.site` adicionado (opcional)
- [ ] Variável `VITE_API_URL=https://api.luxbet.site` configurada
- [ ] **REDEPLOY feito** após configurar variável
- [ ] SSL gerado automaticamente (verificar status)

### Coolify - Backend:
- [ ] Domínio `https://api.luxbet.site` adicionado
- [ ] SSL gerado automaticamente (verificar status)
- [ ] Aplicação rodando

### Validação:
- [ ] DNS propagado (verificar em dnschecker.org)
- [ ] SSL válido (verificar cadeado no navegador)
- [ ] Site acessível via `https://luxbet.site`
- [ ] Backend acessível via `https://api.luxbet.site/api/health`

---

## 💡 Dicas Importantes

### 1. Use Sempre `https://` no Coolify

**✅ CORRETO**:
```
https://luxbet.site
https://api.luxbet.site
```

**❌ ERRADO**:
```
luxbet.site
http://luxbet.site
```

**Por quê**: Coolify só configura SSL automaticamente se você usar `https://`!

---

### 2. Use Registro A (Não CNAME)

**✅ CORRETO**:
```
Tipo: A
Nome: www
Valor: 147.93.147.33
```

**❌ ERRADO**:
```
Tipo: CNAME
Nome: www
Valor: luxbet.site
```

**Por quê**: Coolify funciona melhor com registros A diretos.

---

### 3. Aguarde Propagação DNS

**Antes de adicionar domínio no Coolify**:
- Verifique se DNS propagou em: https://dnschecker.org
- Aguarde até maioria dos servidores retornar `147.93.147.33`
- Depois adicione domínio no Coolify

**Por quê**: SSL só é gerado após DNS propagar completamente.

---

### 4. Faça REDEPLOY Após Configurar Variáveis

**Após adicionar `VITE_API_URL`**:
- Faça **REDEPLOY** do frontend
- Aguarde build completar
- Teste novamente

**Por quê**: Variáveis de ambiente são incluídas no build, não em runtime.

---

## 🎯 Resumo para luxbet.site

### Passo 1: Configurar DNS na Hostinger
```
A @ → 147.93.147.33 (TTL 300)
A www → 147.93.147.33 (TTL 300)
A api → 147.93.147.33 (TTL 300)
```

### Passo 2: Aguardar Propagação DNS
- Verificar em: https://dnschecker.org
- Aguardar até maioria dos servidores retornar `147.93.147.33`

### Passo 3: Adicionar Domínios no Coolify
- Frontend: `https://luxbet.site`, `https://www.luxbet.site`
- Backend: `https://api.luxbet.site`

### Passo 4: Configurar Variáveis
- Frontend: `VITE_API_URL=https://api.luxbet.site`
- **Fazer REDEPLOY** após configurar

### Passo 5: Aguardar SSL
- Coolify gera SSL automaticamente
- Aguarde alguns minutos
- Verifique status no Coolify

---

**Status**: ✅ Seguindo documentação oficial do Coolify

**Ação**: Verificar se domínios estão adicionados com `https://` no Coolify
