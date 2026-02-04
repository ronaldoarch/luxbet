# 🔧 Configurar DNS para luxbet.site

## 🚨 Problema Atual

**Erro**: `DNS_PROBE_FINISHED_BAD_CONFIG`
**Causa**: DNS não configurado ou não propagado para `luxbet.site`

---

## ✅ Solução: Configurar DNS na Hostinger

### Passo 1: Acessar Painel DNS

1. Acesse [hpanel.hostinger.com](https://hpanel.hostinger.com)
2. Faça login
3. Vá em **Domínios** → Clique em **luxbet.site**
4. Clique em **DNS / Nameservers** ou **Gerenciar DNS**
5. Clique em **Editar**

---

### Passo 2: Adicionar Registros A

**⚠️ IMPORTANTE**: Você precisa descobrir o IP do servidor Coolify primeiro.

#### Como descobrir o IP:

**Opção 1 - No Coolify:**
1. Acesse o Coolify
2. Vá em **Settings** → **Servers**
3. Veja o IP do servidor ativo

**Opção 2 - Se já tem outro domínio funcionando:**
```bash
# No terminal, execute:
nslookup api.luxbet.site
# ou
dig api.luxbet.site
```

**Opção 3 - Verificar IP do servidor:**
- Se você tem acesso SSH ao servidor: `hostname -I`
- Ou veja nos logs do Coolify

---

### Passo 3: Configurar Registros DNS

Na Hostinger, adicione os seguintes registros:

#### Registro 1: Domínio Principal (luxbet.site)
```
Tipo: A
Nome: @ (ou deixe vazio)
Valor: [IP_DO_SERVIDOR_COOLIFY]  ← Substitua pelo IP real
TTL: 3600
```

#### Registro 2: WWW (Opcional)
```
Tipo: A
Nome: www
Valor: [IP_DO_SERVIDOR_COOLIFY]  ← Mesmo IP
TTL: 3600
```

#### Registro 3: API (OBRIGATÓRIO)
```
Tipo: A
Nome: api
Valor: [IP_DO_SERVIDOR_COOLIFY]  ← Mesmo IP
TTL: 3600
```

**Exemplo visual na Hostinger:**

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | 3600 |
| A | www | 147.93.147.33 | 3600 |
| A | api | 147.93.147.33 | 3600 |

**⚠️ NOTA**: Substitua `147.93.147.33` pelo IP real do seu servidor Coolify!

---

### Passo 4: Salvar e Aguardar

1. **Salve** as alterações DNS
2. **Aguarde propagação**: 5 minutos a 48 horas (normalmente 1-2 horas)
3. **Verifique propagação**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Verifique se o IP aparece em todos os servidores DNS

---

## 🔍 Verificar se Funcionou

### Teste 1: Verificar DNS Online

1. Acesse: https://dnschecker.org
2. Digite: `luxbet.site`
3. Selecione tipo: `A`
4. Verifique se o IP aparece em todos os servidores

### Teste 2: Verificar no Terminal

```bash
# No terminal (Mac/Linux):
dig luxbet.site
# ou
nslookup luxbet.site

# Deve retornar o IP do servidor
```

### Teste 3: Testar no 4G

1. **Aguarde pelo menos 1 hora** após configurar DNS
2. No celular (4G), desative WiFi
3. Acesse: `https://luxbet.site`
4. Deve carregar normalmente

---

## ⚠️ Problemas Comuns

### Problema 1: DNS não propagou ainda

**Sintoma**: Funciona em alguns lugares mas não em outros

**Solução**: 
- Aguarde mais tempo (pode levar até 48h)
- Use DNS público no celular (8.8.8.8) para testar

### Problema 2: IP errado

**Sintoma**: DNS resolve mas site não carrega

**Solução**:
- Verifique se o IP está correto
- Confirme no Coolify qual é o IP do servidor

### Problema 3: Nameservers incorretos

**Sintoma**: DNS não atualiza mesmo após horas

**Solução**:
- Verifique se os nameservers estão corretos
- Hostinger: `ns1.dns-parking.com` e `ns2.dns-parking.com`
- Se mudou nameservers, pode levar mais tempo

---

## 🚀 Solução Temporária: Usar DNS Público

Enquanto o DNS não propaga, você pode usar DNS público no celular:

### Android:
1. Configurações → WiFi → (seu WiFi) → Configurações Avançadas
2. DNS 1: `8.8.8.8` (Google)
3. DNS 2: `1.1.1.1` (Cloudflare)
4. Salve e teste

### iOS:
1. Configurações → WiFi → (i) ao lado do WiFi
2. Configure DNS → Manual
3. Adicione: `8.8.8.8` e `1.1.1.1`
4. Salve e teste

---

## 📋 Checklist Completo

- [ ] IP do servidor Coolify identificado
- [ ] Registro A para `@` (luxbet.site) configurado
- [ ] Registro A para `www` configurado (opcional)
- [ ] Registro A para `api` configurado
- [ ] DNS salvo na Hostinger
- [ ] Aguardou pelo menos 1 hora
- [ ] Verificou propagação em dnschecker.org
- [ ] Testou no 4G após propagação

---

## 🔗 Links Úteis

- **DNS Checker**: https://dnschecker.org
- **What's My DNS**: https://www.whatsmydns.net
- **Hostinger DNS**: https://hpanel.hostinger.com

---

## 📞 Próximos Passos Após DNS Configurado

1. **Adicionar domínios no Coolify**:
   - Frontend: `luxbet.site` e `www.luxbet.site`
   - Backend: `api.luxbet.site`

2. **Verificar SSL**:
   - Coolify deve gerar SSL automaticamente
   - Aguarde alguns minutos após DNS propagar

3. **Testar**:
   - Frontend: `https://luxbet.site`
   - Backend: `https://api.luxbet.site/api/health`

---

## ⏱️ Tempo Estimado

- **Configuração DNS**: 5 minutos
- **Propagação DNS**: 1-2 horas (pode levar até 48h)
- **SSL automático**: 5-10 minutos após DNS propagar
- **Total**: ~2 horas para funcionar completamente
