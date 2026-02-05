# 🔧 Configurar DNS na Hostinger - luxbet.site (Final)

## ✅ Status Atual

- **Nameservers**: Voltaram para Hostinger ✅
- **Próximo passo**: Configurar registros DNS corretamente na Hostinger

---

## 📋 Passo a Passo: Configurar DNS na Hostinger

### Passo 1: Acessar Painel DNS

1. Acesse: https://hpanel.hostinger.com
2. Vá em **Domínios** → Clique em **luxbet.site**
3. Clique em **DNS / Nameservers** ou **Gerenciar DNS**
4. Clique em **Editar**

---

### Passo 2: Remover Registros Antigos/Incorretos

Antes de adicionar novos registros, verifique e remova:

- ❌ Qualquer CNAME para `www` → `luxbet.site` (ou `luckbet.site`)
- ❌ Registros A duplicados
- ❌ Registros com IPs incorretos

**Mantenha apenas**:
- ✅ Registros MX (se necessário para email)
- ✅ Registros TXT (se necessário para verificação)
- ✅ Outros registros essenciais

---

### Passo 3: Adicionar Registros A Corretos

Adicione os seguintes registros DNS:

#### Registro 1: Domínio Principal (@)
```
Tipo: A
Nome: @ (ou deixe vazio)
Valor: 147.93.147.33
TTL: 3600 (ou 300)
```

#### Registro 2: WWW (IMPORTANTE: Use A, não CNAME!)
```
Tipo: A (NÃO CNAME!)
Nome: www
Valor: 147.93.147.33
TTL: 3600 (ou 300)
```

**⚠️ CRÍTICO**: Use registro **A** para `www`, NÃO CNAME!

#### Registro 3: API
```
Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 3600 (ou 300)
```

---

### Passo 4: Verificar Configuração Final

Após adicionar, você deve ter:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | 300-3600 |
| A | www | 147.93.147.33 | 300-3600 |
| A | api | 147.93.147.33 | 300-3600 |

**Todos apontando para o mesmo IP: `147.93.147.33`**

---

## ⚠️ Erros Comuns a Evitar

### ❌ Erro 1: Usar CNAME para www
```
❌ ERRADO:
Tipo: CNAME
Nome: www
Valor: luxbet.site
```

```
✅ CORRETO:
Tipo: A
Nome: www
Valor: 147.93.147.33
```

### ❌ Erro 2: IP Incorreto
- Verifique se o IP `147.93.147.33` está correto
- Confirme no Coolify qual é o IP do servidor

### ❌ Erro 3: Registros Duplicados
- Não adicione o mesmo registro duas vezes
- Se já existe, edite ao invés de criar novo

---

## 🔍 Verificar Nameservers

Na Hostinger, verifique se os nameservers estão corretos:

**Nameservers da Hostinger** (deve estar assim):
```
ns1.dns-parking.com
ns2.dns-parking.com
```

Se estiver diferente, altere para os da Hostinger.

---

## ⏱️ Após Configurar

1. **Salve todas as alterações**
2. **Aguarde propagação**: 1-2 horas (pode levar até 48h)
3. **Verifique propagação**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Digite: `www.luxbet.site`
   - Digite: `api.luxbet.site`
   - Todos devem retornar: `147.93.147.33`

---

## 🧪 Testar Após Propagação

### Teste 1: DNS Checker
```
https://dnschecker.org
- Digite: luxbet.site
- Deve retornar: 147.93.147.33
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

**⚠️ IMPORTANTE**: Se não estiver configurado, configure e faça **REDEPLOY**!

#### Backend (Coolify):
CORS já está configurado para permitir tudo, mas pode adicionar:
```env
CORS_ORIGINS=https://luxbet.site,https://www.luxbet.site
```

### 3. Fazer Redeploy

- **Frontend**: Redeploy após configurar `VITE_API_URL`
- **Backend**: Redeploy se necessário

### 4. Aguardar SSL

O Coolify deve gerar certificados SSL automaticamente via Let's Encrypt após DNS propagar.

---

## 🚨 Remover Configuração da Contabo

Como você voltou para Hostinger, é recomendado:

1. **Na Contabo**: Remova a zona DNS `luxbet.site` (ou simplesmente ignore)
2. **Na Hostinger**: Configure tudo aqui

**Nota**: Se os nameservers não apontam para Contabo, a configuração lá não causa problema, mas é bom limpar para evitar confusão.

---

## ✅ Checklist Completo

### DNS na Hostinger:
- [ ] Nameservers da Hostinger configurados
- [ ] Registro A para `@` → `147.93.147.33`
- [ ] Registro A para `www` → `147.93.147.33` (NÃO CNAME!)
- [ ] Registro A para `api` → `147.93.147.33`
- [ ] Sem duplicados
- [ ] Sem CNAMEs incorretos
- [ ] Aguardou propagação (1-2h)

### Coolify:
- [ ] Domínios adicionados (frontend e backend)
- [ ] Variável `VITE_API_URL` configurada
- [ ] REDEPLOY do frontend feito
- [ ] SSL gerado automaticamente

### Testes:
- [ ] DNS propagado (verificado em dnschecker.org)
- [ ] Backend acessível via `https://api.luxbet.site/api/health`
- [ ] Frontend acessível via `https://luxbet.site`
- [ ] Testado no 4G e funcionando

---

## 📝 Resumo

1. ✅ **Nameservers**: Voltaram para Hostinger
2. ⏳ **Próximo**: Configurar registros A na Hostinger
3. ⚠️ **IMPORTANTE**: Use registro A para `www`, NÃO CNAME!
4. ⏱️ **Aguardar**: Propagação DNS (1-2h)
5. 🔧 **Depois**: Adicionar domínios no Coolify e fazer redeploy
6. 🧪 **Testar**: Após propagação, testar no 4G

**Ação imediata**: Configure os 3 registros A na Hostinger agora, usando registro A (não CNAME) para `www`!
