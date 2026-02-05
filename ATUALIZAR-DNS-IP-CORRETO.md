# 🔧 Atualizar DNS para IP Correto

## 🚨 IP Correto Identificado

**IP do Servidor**: `177.174.215.222` (não `147.93.147.33`)

**Problema**: DNS estava apontando para IP incorreto!

---

## ✅ Solução: Atualizar Registros DNS

### Na Hostinger:

1. Acesse: https://hpanel.hostinger.com
2. Vá em **Domínios** → **luxbet.site**
3. Clique em **DNS / Nameservers** → **Editar**

### Atualizar Registros A:

#### Registro 1: Domínio Principal (@)
```
Tipo: A
Nome: @
Valor: 177.174.215.222  ← ALTERAR de 147.93.147.33
TTL: 300 ou 3600
```

#### Registro 2: WWW
```
Tipo: A
Nome: www
Valor: 177.174.215.222  ← ALTERAR de 147.93.147.33
TTL: 300 ou 3600
```

#### Registro 3: API
```
Tipo: A
Nome: api
Valor: 177.174.215.222  ← ALTERAR de 147.93.147.33
TTL: 300 ou 3600
```

**⚠️ IMPORTANTE**: Altere TODOS os registros A para o novo IP!

---

## 📋 Configuração Final Esperada

Após atualizar, você deve ter:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 177.174.215.222 | 300-3600 |
| A | www | 177.174.215.222 | 300-3600 |
| A | api | 177.174.215.222 | 300-3600 |

**Todos apontando para o IP correto: `177.174.215.222`**

---

## ⏱️ Após Atualizar DNS

1. **Salve as alterações** na Hostinger
2. **Aguarde propagação**: 1-2 horas (pode levar até 48h)
3. **Verifique propagação**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Deve retornar: `177.174.215.222` (não mais `147.93.147.33`)
4. **Teste no 4G**: Após propagação, teste novamente

---

## 🔍 Verificar se Funcionou

### Teste 1: DNS Checker
```
https://dnschecker.org
Digite: luxbet.site
Deve retornar: 177.174.215.222
```

### Teste 2: Terminal
```bash
nslookup luxbet.site
nslookup www.luxbet.site
nslookup api.luxbet.site

# Todos devem retornar: 177.174.215.222
```

### Teste 3: Testar Conexão Direta
```bash
curl http://177.174.215.222
# Deve retornar algo (mesmo que erro, significa que servidor está acessível)
```

---

## 🚨 Verificar Coolify

Após atualizar DNS, verifique no Coolify:

1. **Servidor**: Verifique se o IP do servidor no Coolify é `177.174.215.222`
2. **Domínios**: Certifique-se de que estão adicionados:
   - Frontend: `luxbet.site` e `www.luxbet.site`
   - Backend: `api.luxbet.site`
3. **SSL**: Aguarde SSL ser gerado/atualizado após DNS propagar

---

## 📝 Resumo

1. ❌ **Problema**: DNS apontando para IP incorreto (`147.93.147.33`)
2. ✅ **Solução**: Atualizar todos os registros A para `177.174.215.222`
3. ⏱️ **Aguardar**: Propagação DNS (1-2h)
4. 🧪 **Testar**: Após propagação, testar no 4G

**Ação imediata**: Atualize todos os registros A na Hostinger para o IP `177.174.215.222`!
