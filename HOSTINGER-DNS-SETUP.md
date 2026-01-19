# 🔧 Configurar DNS na Hostinger para fortunevegas.site

## 📍 Passos Específicos para Hostinger

### 1. Acessar Gerenciamento DNS

1. No painel da Hostinger, vá em **Domínios** → **DNS / Nameservers**
2. Clique em **Editar** na seção DNS/Nameservers

### 2. Configurar Registros DNS

#### Opção A: Manter Nameservers da Hostinger (Recomendado)

Se você mantiver os nameservers da Hostinger (`ns1.dns-parking.com`, `ns2.dns-parking.com`), você precisa adicionar apenas um registro DNS:

**Para o domínio principal (fortunevegas.site):**
```
Tipo: A
Nome: @ (ou deixe vazio para domínio raiz)
Valor: 147.93.147.33
TTL: 3600
```

**Opcional - WWW:**
```
Tipo: A (ou CNAME)
Nome: www
Valor: 147.93.147.33 (ou fortunevegas.site se usar CNAME)
TTL: 3600
```

**⚠️ IMPORTANTE:** Backend e Frontend usarão o mesmo domínio `fortunevegas.site`. O backend estará disponível em `fortunevegas.site/api`.

#### Opção B: Usar Nameservers do Coolify

Se o Coolify fornecer nameservers próprios, você pode alterar:

1. Na Hostinger, clique em **Editar** em DNS/Nameservers
2. Altere para os nameservers do Coolify (exemplo):
   - `ns1.coolify.app`
   - `ns2.coolify.app`

**⚠️ IMPORTANTE:** Se mudar os nameservers, o gerenciamento DNS passará a ser feito totalmente pelo Coolify.

---

## 🔍 Como Descobrir o IP do Servidor Coolify

### Método 1: No Painel do Coolify

1. Acesse seu painel Coolify
2. Vá em **Settings** → **Servers**
3. O IP do servidor ativo será mostrado lá

### Método 2: Após Adicionar Domínio no Coolify

1. No Coolify, adicione o domínio na aplicação
2. O Coolify pode mostrar o IP necessário ou configurar automaticamente

### Método 3: Verificar Subdomínio do Coolify

Se seu site no Coolify já está acessível via subdomínio (ex: `backend-xxx.coolify.app`), você pode:

1. Fazer um lookup DNS do subdomínio:
   ```bash
   nslookup backend-xxx.coolify.app
   # ou
   dig backend-xxx.coolify.app
   ```
2. O IP retornado será o IP do servidor Coolify

---

## 📝 Exemplo Completo de Configuração

### Cenário: fortunevegas.site apontando para Coolify

#### 1. Registros DNS na Hostinger:

```
Tipo: A
Nome: @
Valor: 147.93.147.33  (IP do Coolify)
TTL: 3600

Tipo: A (ou CNAME)
Nome: www
Valor: 147.93.147.33  (ou fortunevegas.site se usar CNAME)
TTL: 3600
```

**Nota:** Apenas um registro A para o domínio principal é necessário. Backend e Frontend compartilham o mesmo domínio.

#### 2. Configurar no Coolify:

**Backend:**
- Domínio: `fortunevegas.site`
- SSL será gerado automaticamente
- API estará disponível em `https://fortunevegas.site/api`

**Frontend:**
- Domínio: `fortunevegas.site` (mesmo domínio do backend)
- Domínio adicional: `www.fortunevegas.site` (opcional)
- SSL será gerado automaticamente

**⚠️ IMPORTANTE:** Como ambos usam o mesmo domínio, você pode configurar apenas o frontend com o domínio e usar um proxy reverso, OU configurar ambos separadamente mas com o mesmo domínio (o Coolify irá gerenciar o roteamento).

#### 3. Variáveis de Ambiente:

**Backend - CORS_ORIGINS:**
```env
CORS_ORIGINS=https://fortunevegas.site,https://www.fortunevegas.site
```

**Frontend - VITE_API_URL:**
```env
VITE_API_URL=https://fortunevegas.site/api
```

Ou use URL relativa (recomendado quando backend e frontend estão no mesmo domínio):
```env
VITE_API_URL=/api
```

#### 4. Fazer Redeploy:

Após alterar variáveis de ambiente, faça redeploy das aplicações.

---

## ⏱️ Tempo de Propagação

Após configurar os DNS:

- **Propagação DNS:** 5 minutos a 48 horas (normalmente 1-2 horas)
- **Verificar propagação:** https://dnschecker.org
- **SSL/HTTPS:** Configurado automaticamente pelo Coolify após propagação

---

## ✅ Verificar Configuração

### 1. Verificar DNS Propagado:

```bash
# No terminal
dig fortunevegas.site
dig api.fortunevegas.site

# Deve retornar o IP do Coolify
```

### 2. Verificar Backend Funcionando:

```bash
curl https://api.fortunevegas.site/api/health
# Deve retornar: {"status": "healthy"}
```

### 3. Verificar Frontend Funcionando:

- Acesse `https://fortunevegas.site` no navegador
- Deve carregar sem erros
- Verifique console (F12) para erros de CORS

---

## 🆘 Troubleshooting Específico Hostinger

### ❌ Erro: "Não consigo encontrar opção de editar DNS"

**Solução:**
1. Certifique-se de estar em **Domínios** → **DNS / Nameservers**
2. Se os nameservers estão como `dns-parking.com`, você precisa:
   - Ou mudar para nameservers do Coolify
   - Ou usar o painel da Hostinger para gerenciar DNS (se disponível)

### ❌ Erro: "DNS não resolve após configuração"

**Soluções:**
1. Aguarde até 48 horas (pode ser propagação lenta)
2. Verifique se os registros foram salvos corretamente na Hostinger
3. Limpe cache DNS:
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Mac/Linux
   sudo dscacheutil -flushcache
   ```

### ❌ Erro: "SSL não gera no Coolify"

**Soluções:**
1. Aguarde propagação DNS completa (verifique em dnschecker.org)
2. Verifique se o domínio aponta para o IP correto
3. No Coolify, tente regenerar o certificado manualmente

---

## 📞 Precisa de Mais Ajuda?

Se tiver dificuldades:

1. Tire prints das telas de configuração DNS na Hostinger
2. Verifique se você tem acesso ao IP do servidor Coolify
3. Teste se o subdomínio do Coolify já está funcionando

---

**Domínio:** fortunevegas.site  
**Nameservers atuais:** ns1.dns-parking.com, ns2.dns-parking.com