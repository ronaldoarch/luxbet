# 🔧 Solução - Erro DNS no 4G

## 🚨 Problema Identificado

**Erro**: `DNS_PROBE_FINISHED_BAD_CONFIG`
**Mensagem**: "Não foi possível encontrar o endereço IP do servidor de luxbet.site"

**Causa**: O DNS do domínio `luxbet.site` não está configurado corretamente ou não está propagado para todas as redes.

---

## ✅ Soluções

### Solução 1: Verificar Configuração DNS (Recomendado)

O domínio `luxbet.site` precisa ter registros DNS configurados corretamente.

#### No seu provedor de domínio (ex: Hostinger, GoDaddy, etc.):

1. **Acesse o painel de DNS do domínio**
2. **Verifique se existem registros A ou CNAME**:

   **Registro A** (para domínio principal):
   ```
   Tipo: A
   Nome: @ ou luxbet.site
   Valor: IP_DO_SERVIDOR
   TTL: 3600
   ```

   **Registro A** (para subdomínio api):
   ```
   Tipo: A
   Nome: api
   Valor: IP_DO_SERVIDOR
   TTL: 3600
   ```

   **OU Registro CNAME**:
   ```
   Tipo: CNAME
   Nome: api
   Valor: dominio-do-coolify.com
   TTL: 3600
   ```

3. **Verifique os Nameservers**:
   - Devem apontar para o provedor correto
   - Exemplo Hostinger: `ns1.dns-parking.com` e `ns2.dns-parking.com`

---

### Solução 2: Verificar Propagação DNS

Use ferramentas online para verificar se o DNS está propagado:

1. **DNS Checker**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Selecione tipo: `A`
   - Verifique se todos os servidores DNS retornam o mesmo IP

2. **What's My DNS**: https://www.whatsmydns.net
   - Digite: `luxbet.site`
   - Verifique propagação global

**Se alguns servidores retornam IP e outros não:**
- DNS ainda está propagando (pode levar até 48h)
- Aguarde ou verifique configuração

---

### Solução 3: Usar IP Direto Temporariamente

Enquanto o DNS não resolve, você pode usar o IP direto do servidor:

1. **Descubra o IP do servidor**:
   - No Coolify, veja o IP do servidor
   - Ou use ferramentas como `ping` ou `nslookup` em outro dispositivo

2. **Configure temporariamente no Coolify**:
   ```
   VITE_API_URL=https://IP_DO_SERVIDOR
   ```
   **⚠️ ATENÇÃO**: Isso só funciona se o servidor aceitar conexões por IP e tiver certificado SSL válido para o IP.

3. **Faça redeploy do frontend**

---

### Solução 4: Verificar DNS no Celular

No celular (4G), teste:

1. **Usar DNS público**:
   - Vá em Configurações → WiFi → (seu WiFi) → Configurações Avançadas
   - Altere DNS para: `8.8.8.8` (Google) ou `1.1.1.1` (Cloudflare)
   - Teste novamente

2. **Testar com aplicativo de DNS**:
   - Use app como "DNS Changer" para testar diferentes DNS

---

### Solução 5: Verificar no Coolify

1. **Verifique se o domínio está configurado**:
   - Coolify → Projeto → Domains
   - Verifique se `luxbet.site` e `api.luxbet.site` estão configurados

2. **Verifique certificado SSL**:
   - Certificado deve estar válido para ambos os domínios
   - Renove se necessário

---

## 🔍 Diagnóstico Rápido

### Teste 1: DNS funciona em WiFi mas não no 4G?

**Possível causa**: DNS do provedor móvel está bloqueando ou não propagado

**Solução**: 
- Use DNS público no celular (8.8.8.8)
- Ou aguarde propagação DNS

### Teste 2: DNS não funciona em lugar nenhum?

**Possível causa**: DNS não configurado ou configurado incorretamente

**Solução**:
- Verifique configuração DNS no provedor
- Verifique se registros A/CNAME estão corretos

### Teste 3: Backend funciona mas frontend não?

**Possível causa**: Frontend também precisa de DNS configurado

**Solução**:
- Configure DNS para `luxbet.site` (não apenas `api.luxbet.site`)

---

## 📋 Checklist DNS

- [ ] Registro A configurado para `luxbet.site` → IP do servidor
- [ ] Registro A configurado para `api.luxbet.site` → IP do servidor
- [ ] Nameservers corretos no provedor de domínio
- [ ] DNS propagado (verificar em dnschecker.org)
- [ ] Certificado SSL válido para ambos domínios
- [ ] Domínios configurados no Coolify
- [ ] TTL não muito alto (recomendado: 3600 segundos)

---

## 🚀 Configuração DNS Recomendada

### Para Hostinger (exemplo):

```
Tipo    Nome    Valor                    TTL
A       @       IP_DO_SERVIDOR           3600
A       api     IP_DO_SERVIDOR           3600
CNAME   www     luxbet.site              3600
```

### Para Cloudflare (se usar):

1. Adicione domínio no Cloudflare
2. Configure registros A:
   - `luxbet.site` → IP do servidor
   - `api.luxbet.site` → IP do servidor
3. Ative Proxy (laranja) se quiser proteção DDoS

---

## ⚠️ Importante

1. **Propagação DNS pode levar até 48 horas**
2. **Diferentes provedores DNS propagam em velocidades diferentes**
3. **DNS móvel pode ser mais lento que DNS residencial**
4. **Use DNS público (8.8.8.8) para testar se é problema do provedor**

---

## 📞 Próximos Passos

1. **Verifique configuração DNS no provedor de domínio**
2. **Confirme que registros A estão apontando para o IP correto**
3. **Aguarde propagação DNS (ou use DNS público para testar)**
4. **Teste novamente no 4G após algumas horas**

---

## 🔗 Links Úteis

- **DNS Checker**: https://dnschecker.org
- **What's My DNS**: https://www.whatsmydns.net
- **Google DNS**: 8.8.8.8 e 8.8.4.4
- **Cloudflare DNS**: 1.1.1.1 e 1.0.0.1
