# 🔧 Configurar DNS na Contabo - luxbet.site

## ✅ Status Atual

- **Nameservers**: Alterados para Contabo ✅
- **Próximo passo**: Configurar registros DNS na Contabo

---

## 📋 Passo a Passo: Configurar DNS na Contabo

### Passo 1: Acessar Gerenciamento DNS

1. Acesse: https://new.contabo.com/network/dns-management/dns
2. Na lista, encontre `luxbet.site`
3. Clique em `luxbet.site` para abrir a zona DNS

---

### Passo 2: Adicionar Registros A

Na zona DNS do `luxbet.site`, adicione os seguintes registros:

#### Registro 1: Domínio Principal (@)
```
Tipo: A
Nome: @ (ou deixe vazio, ou use o domínio raiz)
Valor: 147.93.147.33
TTL: 3600
```

#### Registro 2: WWW
```
Tipo: A
Nome: www
Valor: 147.93.147.33
TTL: 3600
```

#### Registro 3: API
```
Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 3600
```

**⚠️ IMPORTANTE**: 
- Use registro **A** (não CNAME) para `www`
- Todos os registros A devem apontar para o **mesmo IP**: `147.93.147.33`

---

### Passo 3: Remover Registros Antigos (se houver)

Se houver registros antigos ou incorretos:
- Remova CNAMEs desnecessários
- Remova registros A com IPs incorretos
- Mantenha apenas os 3 registros A acima

---

## 📋 Configuração Final Esperada

Após configurar, você deve ter:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | 3600 |
| A | www | 147.93.147.33 | 3600 |
| A | api | 147.93.147.33 | 3600 |

**Todos apontando para o mesmo IP do servidor Coolify.**

---

## ⏱️ Aguardar Propagação DNS

Após configurar os registros:

1. **Salve as alterações** na Contabo
2. **Aguarde propagação**: 1-2 horas (pode levar até 48h)
3. **Verifique propagação**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Digite: `www.luxbet.site`
   - Digite: `api.luxbet.site`
   - Todos devem retornar: `147.93.147.33`

---

## 🔍 Verificar se Funcionou

### Teste 1: DNS Checker Online
```
https://dnschecker.org
- Digite: luxbet.site
- Verifique se IP 147.93.147.33 aparece em todos os servidores
```

### Teste 2: Terminal
```bash
nslookup luxbet.site
nslookup www.luxbet.site
nslookup api.luxbet.site

# Todos devem retornar: 147.93.147.33
```

### Teste 3: No 4G (Após Propagação)
1. Aguarde 1-2 horas após configurar
2. No celular (4G), desative WiFi
3. Acesse: `https://luxbet.site`
4. Deve carregar normalmente

---

## ⚠️ Importante: Remover DNS da Hostinger

Agora que os nameservers estão na Contabo:

1. **Os registros DNS na Hostinger serão IGNORADOS**
2. Você pode removê-los (opcional, mas recomendado para limpeza)
3. Ou simplesmente deixar lá (não causará problema, mas pode confundir)

**Recomendação**: Remova os registros DNS antigos da Hostinger para evitar confusão.

---

## 🔧 Próximos Passos Após DNS Configurado

### 1. Adicionar Domínios no Coolify

#### Frontend:
- Domínio: `luxbet.site`
- Domínio adicional: `www.luxbet.site` (opcional)

#### Backend:
- Domínio: `api.luxbet.site`

### 2. Verificar Variáveis de Ambiente

#### Frontend (Coolify):
```env
VITE_API_URL=https://api.luxbet.site
```

#### Backend (Coolify):
```env
CORS_ORIGINS=https://luxbet.site,https://www.luxbet.site
```

### 3. Fazer Redeploy

- **Frontend**: Redeploy após configurar `VITE_API_URL`
- **Backend**: Redeploy se necessário

### 4. Aguardar SSL

O Coolify deve gerar certificados SSL automaticamente via Let's Encrypt após o DNS propagar.

---

## 🚨 Problemas Comuns

### Problema 1: DNS não propaga

**Causa**: Nameservers ainda não atualizados globalmente

**Solução**: 
- Aguarde mais tempo (pode levar até 48h)
- Verifique se nameservers estão corretos na Hostinger
- Use DNS público (8.8.8.8) para testar

### Problema 2: Site não carrega após DNS propagar

**Causa**: Domínios não adicionados no Coolify

**Solução**:
- Adicione domínios no Coolify
- Aguarde SSL ser gerado
- Verifique se aplicações estão rodando

### Problema 3: Erro SSL

**Causa**: Certificado não gerado ainda

**Solução**:
- Aguarde alguns minutos após DNS propagar
- Force regeneração SSL no Coolify se necessário

---

## ✅ Checklist Completo

- [x] Nameservers alterados para Contabo
- [ ] Registros A configurados na Contabo (@, www, api)
- [ ] Todos apontando para `147.93.147.33`
- [ ] Aguardou propagação DNS (1-2h)
- [ ] Verificou propagação em dnschecker.org
- [ ] Domínios adicionados no Coolify
- [ ] Variáveis de ambiente configuradas
- [ ] Redeploy do frontend feito
- [ ] SSL gerado automaticamente
- [ ] Testado no 4G e funcionando

---

## 📞 Resumo

1. ✅ **Nameservers**: Alterados para Contabo
2. ⏳ **Próximo**: Configurar registros A na Contabo
3. ⏱️ **Aguardar**: Propagação DNS (1-2h)
4. 🧪 **Testar**: Após propagação, testar no 4G

**Ação imediata**: Configure os 3 registros A na Contabo agora!
