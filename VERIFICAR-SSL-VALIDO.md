# 🔒 Como Verificar se SSL Está Válido

## 🎯 Métodos de Verificação

### Método 1: Verificar no Coolify (Mais Rápido)

#### No Coolify:

1. **Acesse o Coolify**: `http://147.93.147.33:8000` (ou seu IP do Coolify)

2. **Vá na aplicação** (Frontend ou Backend)

3. **Clique na aba "Domains"** ou veja a lista de domínios

4. **Verifique o status do SSL**:
   - ✅ **"Active"** ou **"Valid"** = SSL válido
   - ⚠️ **"Pending"** ou **"Generating"** = SSL ainda sendo gerado (aguarde alguns minutos)
   - ❌ **"Invalid"** ou **"Error"** = SSL com problema
   - ❌ **"Expired"** = SSL expirado

5. **Para cada domínio**:
   - `luxbet.site` → SSL deve estar "Active"
   - `www.luxbet.site` → SSL deve estar "Active" (se adicionado)
   - `api.luxbet.site` → SSL deve estar "Active"

---

### Método 2: Verificar no Navegador (Mais Visual)

#### No Navegador:

1. **Acesse o site**:
   - Frontend: `https://luxbet.site`
   - Backend: `https://api.luxbet.site`

2. **Verifique o cadeado**:
   - ✅ **Cadeado verde/fechado** = SSL válido
   - ⚠️ **Cadeado com aviso** = SSL com problema
   - ❌ **Sem cadeado** ou **"Não seguro"** = SSL inválido ou ausente

3. **Clique no cadeado** para ver detalhes:
   - Válido até: Data de expiração
   - Emitido por: Let's Encrypt (geralmente)
   - Certificado válido: Sim/Não

---

### Método 3: Usar Ferramentas Online (Mais Detalhado)

#### SSL Labs (Recomendado):

1. **Acesse**: https://www.ssllabs.com/ssltest/

2. **Digite o domínio**:
   - `luxbet.site`
   - `www.luxbet.site`
   - `api.luxbet.site`

3. **Aguarde a análise** (pode levar alguns minutos)

4. **Verifique a nota**:
   - ✅ **A ou A+** = SSL excelente
   - ⚠️ **B ou C** = SSL com problemas menores
   - ❌ **F** = SSL com problemas graves

5. **Veja detalhes**:
   - Certificado válido
   - Cadeia de certificados
   - Protocolos suportados
   - Cipher suites

---

#### SSL Checker:

1. **Acesse**: https://www.sslshopper.com/ssl-checker.html

2. **Digite o domínio**:
   - `luxbet.site`
   - `api.luxbet.site`

3. **Veja o resultado**:
   - ✅ **"Valid"** = SSL válido
   - ❌ **"Invalid"** = SSL inválido
   - ⚠️ **"Expired"** = SSL expirado

---

### Método 4: Verificar via Terminal (Mais Técnico)

#### No Terminal (Linux/Mac):

```bash
# Verificar SSL do frontend
openssl s_client -connect luxbet.site:443 -servername luxbet.site

# Verificar SSL do backend
openssl s_client -connect api.luxbet.site:443 -servername api.luxbet.site
```

**O que procurar**:
- ✅ **"Verify return code: 0 (ok)"** = SSL válido
- ❌ **"Verify return code: X"** = SSL com problema

---

#### Usando curl:

```bash
# Verificar SSL do frontend
curl -I https://luxbet.site

# Verificar SSL do backend
curl -I https://api.luxbet.site/api/health
```

**Resultados**:
- ✅ **HTTP/2 200** ou **HTTP/1.1 200** = SSL válido e funcionando
- ❌ **SSL certificate problem** = SSL inválido
- ❌ **Connection refused** = Servidor não está respondendo

---

### Método 5: Verificar no Celular (4G)

#### No Celular:

1. **Acesse o site** no navegador do celular (4G):
   - `https://luxbet.site`
   - `https://api.luxbet.site/api/health`

2. **Verifique o cadeado**:
   - ✅ **Cadeado verde/fechado** = SSL válido
   - ⚠️ **Aviso de segurança** = SSL com problema

3. **Se houver aviso**:
   - Clique em "Avançado" ou "Detalhes"
   - Veja qual é o problema específico

---

## 🔍 Problemas Comuns e Soluções

### Problema 1: SSL "Pending" ou "Generating"

**Causa**: SSL ainda está sendo gerado pelo Let's Encrypt

**Solução**:
1. Aguarde 5-10 minutos
2. Verifique novamente no Coolify
3. Se ainda estiver pendente após 30 minutos, force regeneração:
   - Coolify → Domains → SSL → Regenerate

---

### Problema 2: SSL "Invalid" ou "Error"

**Causas possíveis**:
- DNS não propagou completamente
- Domínio não está apontando para o servidor correto
- Problema com Let's Encrypt

**Solução**:
1. Verifique se DNS está propagado:
   - `nslookup luxbet.site` deve retornar `147.93.147.33`
   - `nslookup api.luxbet.site` deve retornar `147.93.147.33`

2. Aguarde mais tempo para DNS propagar

3. Force regeneração do SSL no Coolify:
   - Coolify → Domains → SSL → Regenerate

---

### Problema 3: SSL "Expired"

**Causa**: Certificado expirou (Let's Encrypt renova automaticamente, mas pode falhar)

**Solução**:
1. Force renovação no Coolify:
   - Coolify → Domains → SSL → Regenerate

2. Aguarde alguns minutos

3. Verifique novamente

---

### Problema 4: Cadeado com Aviso no Navegador

**Causas possíveis**:
- Certificado não confiável
- Certificado expirado
- Cadeia de certificados incompleta
- Mixed content (HTTP e HTTPS misturados)

**Solução**:
1. Clique no cadeado para ver detalhes
2. Veja qual é o problema específico
3. Se for mixed content, corrija no código
4. Se for certificado, force regeneração no Coolify

---

## ✅ Checklist de Verificação SSL

### No Coolify:
- [ ] SSL está "Active" para `luxbet.site`
- [ ] SSL está "Active" para `www.luxbet.site` (se adicionado)
- [ ] SSL está "Active" para `api.luxbet.site`
- [ ] Não há erros ou avisos

### No Navegador:
- [ ] Cadeado verde/fechado em `https://luxbet.site`
- [ ] Cadeado verde/fechado em `https://api.luxbet.site`
- [ ] Sem avisos de segurança
- [ ] Certificado válido até data futura

### Testes Online:
- [ ] SSL Labs mostra nota A ou A+
- [ ] SSL Checker mostra "Valid"
- [ ] Sem erros de certificado

### No Celular (4G):
- [ ] Cadeado verde/fechado no navegador
- [ ] Sem avisos de segurança
- [ ] Site carrega normalmente

---

## 🚀 Como Forçar Regeneração do SSL no Coolify

### Se SSL não está válido:

1. **Acesse Coolify**: `http://147.93.147.33:8000`

2. **Vá na aplicação** (Frontend ou Backend)

3. **Clique na aba "Domains"**

4. **Para cada domínio com problema**:
   - Clique no domínio
   - Procure opção "Regenerate SSL" ou "Renew SSL"
   - Clique para regenerar

5. **Aguarde 5-10 minutos**

6. **Verifique novamente**

---

## 📊 Status Esperado

### SSL Válido:
- ✅ Coolify: "Active"
- ✅ Navegador: Cadeado verde/fechado
- ✅ SSL Labs: Nota A ou A+
- ✅ SSL Checker: "Valid"
- ✅ Certificado válido até data futura

### SSL com Problema:
- ❌ Coolify: "Invalid", "Error" ou "Expired"
- ❌ Navegador: Cadeado com aviso ou "Não seguro"
- ❌ SSL Labs: Nota F ou erro
- ❌ SSL Checker: "Invalid" ou "Expired"

---

## 💡 Dica Importante

**Let's Encrypt renova automaticamente** certificados SSL antes de expirar, mas pode falhar se:
- DNS não está propagado corretamente
- Domínio não está apontando para o servidor
- Servidor não está acessível

**Se SSL não está válido**, geralmente é porque:
1. DNS ainda não propagou completamente
2. Domínio não está adicionado no Coolify
3. Problema temporário com Let's Encrypt

**Solução**: Aguardar propagação DNS completa e forçar regeneração do SSL.

---

## 🎯 Verificação Rápida (2 minutos)

### Passo 1: No Navegador
1. Acesse: `https://luxbet.site`
2. Veja se há cadeado verde/fechado
3. Se houver, SSL está válido ✅

### Passo 2: No Coolify
1. Acesse Coolify → Aplicação → Domains
2. Veja se SSL está "Active"
3. Se estiver, SSL está válido ✅

**Se ambos estiverem OK, SSL está válido!** 🎉

---

**Status**: ✅ SSL válido se cadeado verde no navegador e "Active" no Coolify
