# 🚀 Configuração Rápida de DNS

## 📍 IP do Servidor

**IP do Servidor Coolify:** `147.93.147.33`

---

## 🔧 Passo a Passo: Configurar DNS

### 1. Acessar Painel DNS

**Se for Hostinger:**
1. Acesse [hpanel.hostinger.com](https://hpanel.hostinger.com)
2. Vá em **Domínios** → Selecione seu domínio
3. Clique em **DNS / Nameservers** ou **Gerenciar DNS**

**Se for outro provedor (Registro.br, GoDaddy, etc.):**
1. Acesse o painel do provedor
2. Vá em **DNS** ou **Zona DNS**
3. Procure por **Adicionar Registro** ou **Gerenciar DNS**

---

### 2. Adicionar Registro A

Adicione os seguintes registros DNS:

#### Registro 1: Domínio Principal
```
Tipo: A
Nome: @ (ou deixe vazio, ou use o domínio raiz)
Valor: 147.93.147.33
TTL: 3600 (ou padrão)
```

#### Registro 2: WWW (Opcional)
```
Tipo: A
Nome: www
Valor: 147.93.147.33
TTL: 3600 (ou padrão)
```

**OU use CNAME para www:**
```
Tipo: CNAME
Nome: www
Valor: seu-dominio.com (ou @)
TTL: 3600
```

#### Registro 3: API (Se usar subdomínio separado)
```
Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 3600
```

---

### 3. Exemplo Visual

**Na Hostinger, os campos ficam assim:**

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | 3600 |
| A | www | 147.93.147.33 | 3600 |
| A | api | 147.93.147.33 | 3600 |

---

### 4. Salvar e Aguardar

1. **Salve** os registros DNS
2. **Aguarde propagação:** 5 minutos a 48 horas (normalmente 1-2 horas)
3. **Verifique propagação:** Use [https://dnschecker.org](https://dnschecker.org)

---

## ✅ Verificar se Funcionou

### No Terminal:
```bash
# Verificar DNS
dig seu-dominio.com
# ou
nslookup seu-dominio.com

# Deve retornar: 147.93.147.33
```

### Online:
- Acesse [https://dnschecker.org](https://dnschecker.org)
- Digite seu domínio
- Verifique se o IP `147.93.147.33` aparece em todos os servidores

---

## 🔐 Próximos Passos

Após o DNS propagar:

1. **Adicionar domínio no Coolify:**
   - Backend: Adicione o domínio na aplicação
   - Frontend: Adicione o domínio na aplicação

2. **SSL será gerado automaticamente** pelo Coolify via Let's Encrypt

3. **Atualizar variáveis de ambiente:**
   - Backend: `CORS_ORIGINS=https://seu-dominio.com`
   - Frontend: `VITE_API_URL=https://seu-dominio.com/api`

4. **Fazer redeploy** das aplicações

---

## ⚠️ Importante

- **Não remova** outros registros DNS existentes (MX, TXT, etc.) a menos que saiba o que está fazendo
- **Aguarde a propagação** antes de testar
- **Desative hosting** na Hostinger se estiver usando Coolify (pode causar conflitos)

---

## 🆘 Problemas Comuns

### DNS não resolve
- Aguarde mais tempo (pode levar até 48h)
- Verifique se salvou os registros corretamente
- Limpe cache DNS: `ipconfig /flushdns` (Windows) ou `sudo dscacheutil -flushcache` (Mac)

### SSL não gera
- Aguarde propagação DNS completa
- Verifique se o domínio está adicionado no Coolify
- Tente regenerar certificado manualmente no Coolify

---

**Última atualização:** 2026-01-20  
**IP do Servidor:** 147.93.147.33
