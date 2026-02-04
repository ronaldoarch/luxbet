# 🔧 Correção DNS - luxbet.site

## 🔍 Problemas Identificados na Configuração Atual

Analisando a configuração DNS atual, identifiquei os seguintes problemas:

### ❌ Problema 1: IP Incorreto
- **Atual**: `18.88.9.72`
- **Esperado**: `147.93.147.33` (ou verificar qual é o IP correto do servidor Coolify)

### ❌ Problema 2: CNAME www com erro de digitação
- **Atual**: `www` → CNAME → `luckbet.site` (com "u")
- **Correto**: Deve apontar para o domínio principal ou usar registro A

### ✅ O que está correto:
- Registro A para `@` existe ✅
- Registro A para `api` existe ✅
- Registros CAA para SSL estão configurados ✅

---

## ✅ Correções Necessárias

### Correção 1: Atualizar IP dos Registros A

**Edite os seguintes registros:**

#### Registro 1: Domínio Principal (@)
```
Tipo: A
Name: @
Conteúdo: 147.93.147.33  ← ALTERAR de 18.88.9.72
TTL: 300 (ou 3600)
```

#### Registro 2: API
```
Tipo: A
Name: api
Conteúdo: 147.93.147.33  ← ALTERAR de 18.88.9.72
TTL: 300 (ou 3600)
```

**⚠️ IMPORTANTE**: Antes de alterar, confirme qual é o IP correto do servidor Coolify!

---

### Correção 2: Corrigir CNAME www

**Opção A - Usar Registro A (Recomendado):**
```
Remover: CNAME www → luckbet.site
Adicionar: Tipo A, Name: www, Conteúdo: 147.93.147.33
```

**Opção B - Corrigir CNAME:**
```
Editar: CNAME www → luxbet.site (corrigir digitação)
```

**Recomendação**: Use Opção A (Registro A) para melhor performance.

---

## 🔍 Como Verificar o IP Correto

### Método 1: No Coolify
1. Acesse o Coolify
2. Vá em **Settings** → **Servers**
3. Veja o IP do servidor ativo

### Método 2: Verificar outro domínio funcionando
Se você tem outro domínio funcionando no mesmo servidor:
```bash
nslookup outro-dominio.com
# O IP retornado será o IP do servidor
```

### Método 3: Verificar logs do Coolify
Os logs do Coolify podem mostrar o IP do servidor.

---

## 📋 Passo a Passo para Corrigir

### 1. Confirmar IP do Servidor
- Verifique no Coolify qual é o IP correto
- Anote o IP (pode ser `147.93.147.33` ou outro)

### 2. Editar Registro A para @
1. Na tabela DNS, encontre o registro A com Name `@`
2. Clique em **"Editar"** (botão azul)
3. Altere o **Conteúdo** de `18.88.9.72` para o IP correto
4. Salve

### 3. Editar Registro A para api
1. Na tabela DNS, encontre o registro A com Name `api`
2. Clique em **"Editar"**
3. Altere o **Conteúdo** de `18.88.9.72` para o IP correto
4. Salve

### 4. Corrigir Registro www
1. Encontre o registro CNAME com Name `www`
2. Clique em **"Remover"** (botão vermelho)
3. Clique em **"Adicionar registro"**
4. Preencha:
   - Tipo: `A`
   - Name: `www`
   - Conteúdo: `[IP_CORRETO]` (mesmo IP usado nos outros registros)
   - TTL: `300` ou `3600`
5. Clique em **"Adicionar registro"**

---

## ✅ Configuração Final Esperada

Após as correções, você deve ter:

| Tipo | Name | Conteúdo | TTL |
|------|------|----------|-----|
| A | @ | **[IP_CORRETO]** | 300-3600 |
| A | www | **[IP_CORRETO]** | 300-3600 |
| A | api | **[IP_CORRETO]** | 300-3600 |
| CAA | @ | (vários, manter) | 14400 |

**Todos os registros A devem apontar para o MESMO IP do servidor Coolify.**

---

## ⏱️ Após Fazer as Correções

1. **Salve todas as alterações**
2. **Aguarde propagação**: 5 minutos a 2 horas
3. **Verifique propagação**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Verifique se o IP correto aparece
4. **Teste no 4G**: Após propagação, teste no celular

---

## 🚨 Importante

**Antes de alterar o IP**, confirme qual é o IP correto do servidor Coolify:
- Pode ser `147.93.147.33` (mencionado em outros documentos)
- Pode ser `18.88.9.72` (atual na configuração)
- Pode ser outro IP

**Se não tiver certeza**, verifique no Coolify primeiro!

---

## 🔗 Verificar Após Correção

### Teste 1: DNS Checker
https://dnschecker.org
- Digite: `luxbet.site`
- Verifique se todos os servidores retornam o IP correto

### Teste 2: Terminal
```bash
nslookup luxbet.site
nslookup api.luxbet.site
nslookup www.luxbet.site
```

Todos devem retornar o mesmo IP.

### Teste 3: No 4G
Após 1-2 horas, teste no celular (4G):
- `https://luxbet.site` deve carregar
- `https://api.luxbet.site/api/health` deve funcionar
