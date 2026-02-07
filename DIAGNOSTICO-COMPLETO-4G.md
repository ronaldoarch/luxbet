# 🔍 Diagnóstico Completo - 4G Não Funciona (TTL 300)

## ✅ O Que Já Está Correto

- ✅ TTL está em `300` (correto)
- ✅ DNS configurado na Hostinger

---

## 🔍 Verificações Necessárias (Ordem de Prioridade)

### 1. Verificar Configuração DNS na Hostinger (5 minutos)

**Acesse**: https://hpanel.hostinger.com → Domínios → luxbet.site → DNS

**Confirme que está assim**:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | 300 |
| A | www | 147.93.147.33 | 300 |
| A | api | 147.93.147.33 | 300 |

**⚠️ VERIFICAÇÕES CRÍTICAS**:

- ❌ **NÃO deve haver** CNAME para `www` → Se houver, **REMOVA** e use registro A
- ✅ **Todos devem apontar** para `147.93.147.33` (mesmo IP)
- ✅ **TTL deve estar** em `300` (confirmado ✅)
- ❌ **Não deve haver** registros duplicados

**Se encontrar problemas**: Corrija e aguarde 1-2 horas.

---

### 2. Verificar Propagação em DNS de Provedores Brasileiros (10 minutos)

**Acesse**: https://dnschecker.org

**Teste DNS específicos**:

1. Digite: `www.luxbet.site`
2. Selecione tipo: `A`
3. Teste DNS específicos:
   - `200.160.2.3` (Vivo)
   - `200.222.2.90` (Claro)
   - `200.221.11.100` (TIM)
   - `201.6.96.245` (Oi)

**Resultados possíveis**:

- ✅ **Todos retornam `147.93.147.33`**: DNS está OK, problema pode ser no Coolify
- ⚠️ **Alguns retornam, outros não**: Propagação ainda em andamento (aguardar mais 2-4h)
- ❌ **Nenhum retorna**: Problema de configuração DNS (verificar Hostinger)

---

### 3. Verificar Configuração no Coolify (10 minutos)

#### Frontend:

**Verificar**:
- ✅ Domínio `luxbet.site` adicionado?
- ✅ Domínio `www.luxbet.site` adicionado? (opcional mas recomendado)
- ✅ Variável `VITE_API_URL=https://api.luxbet.site` configurada?
- ✅ **REDEPLOY feito** após configurar variável? ⚠️ CRÍTICO
- ✅ SSL válido para ambos domínios?
- ✅ Aplicação rodando?

**Se `VITE_API_URL` não estiver configurada ou redeploy não foi feito**:
1. Coolify → Frontend → Environment Variables
2. Adicione: `VITE_API_URL=https://api.luxbet.site`
3. **Faça REDEPLOY** (crucial!)
4. Aguarde build completar
5. Teste novamente

#### Backend:

**Verificar**:
- ✅ Domínio `api.luxbet.site` adicionado?
- ✅ SSL válido?
- ✅ Aplicação rodando?
- ✅ CORS configurado?

---

### 4. Testar Backend Diretamente (2 minutos)

**No celular (4G)**, acesse:
```
https://api.luxbet.site/api/health
```

**Resultados**:
- ✅ **Se funcionar**: DNS está OK, problema pode ser no frontend
- ❌ **Se não funcionar**: DNS ainda não propagou ou há problema de configuração

---

### 5. Testar Frontend e Verificar Console (5 minutos)

**No celular (4G)**:

1. Acesse: `https://luxbet.site`
2. Abra console do navegador (F12 ou menu desenvolvedor)
3. Veja erros no console
4. Digite no console:
   ```javascript
   console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
   ```

**Resultados**:
- ✅ **Se mostrar `https://api.luxbet.site`**: Variável está OK
- ❌ **Se mostrar `undefined` ou `localhost`**: Fazer redeploy do frontend
- ❌ **Se houver erros CORS**: Verificar configuração CORS no backend
- ❌ **Se houver erros de rede**: Verificar se backend está acessível

---

## 🎯 Soluções Baseadas no Diagnóstico

### Se DNS de Provedores Não Retornam `147.93.147.33`:

**Causa**: Propagação ainda em andamento ou configuração DNS incorreta

**Solução**:
1. Verificar configuração DNS na Hostinger (passo 1)
2. Aguardar mais 2-4 horas
3. Testar novamente em dnschecker.org

---

### Se DNS Retorna mas Backend Não Funciona:

**Causa**: Problema no Coolify (domínio não adicionado, SSL, etc.)

**Solução**:
1. Verificar se `api.luxbet.site` está adicionado no Coolify
2. Verificar se SSL está ativo
3. Verificar se aplicação está rodando
4. Verificar logs do Coolify

---

### Se Backend Funciona mas Frontend Não:

**Causa**: `VITE_API_URL` não configurada ou redeploy não feito

**Solução**:
1. Coolify → Frontend → Environment Variables
2. Adicione: `VITE_API_URL=https://api.luxbet.site`
3. **Faça REDEPLOY**
4. Aguarde build completar
5. Teste novamente

---

### Se Frontend Carrega mas `VITE_API_URL` está `undefined`:

**Causa**: Variável não foi incluída no build

**Solução**:
1. Coolify → Frontend → Environment Variables
2. Confirme que `VITE_API_URL=https://api.luxbet.site` está configurada
3. **Faça REDEPLOY** (crucial!)
4. Aguarde build completar
5. Teste novamente

---

## 📊 Checklist Completo de Diagnóstico

### DNS (Hostinger):
- [ ] TTL está em `300` ✅ (confirmado)
- [ ] Registro A para `@` → `147.93.147.33` com TTL `300`
- [ ] Registro A para `www` → `147.93.147.33` com TTL `300` (NÃO CNAME!)
- [ ] Registro A para `api` → `147.93.147.33` com TTL `300`
- [ ] Não há registros duplicados
- [ ] Não há CNAME para `www`
- [ ] Nameservers corretos (ns1.dns-parking.com, ns2.dns-parking.com)

### Propagação DNS:
- [ ] DNS da Vivo retorna `147.93.147.33`?
- [ ] DNS da Claro retorna `147.93.147.33`?
- [ ] DNS da TIM retorna `147.93.147.33`?
- [ ] DNS da Oi retorna `147.93.147.33`?

### Coolify - Frontend:
- [ ] Domínio `luxbet.site` adicionado
- [ ] Domínio `www.luxbet.site` adicionado (opcional)
- [ ] Variável `VITE_API_URL=https://api.luxbet.site` configurada
- [ ] **REDEPLOY feito** após configurar variável
- [ ] SSL válido para ambos domínios
- [ ] Aplicação rodando

### Coolify - Backend:
- [ ] Domínio `api.luxbet.site` adicionado
- [ ] SSL válido
- [ ] Aplicação rodando
- [ ] CORS configurado

### Testes:
- [ ] Backend acessível via `https://api.luxbet.site/api/health` no 4G
- [ ] Frontend acessível via `https://luxbet.site` no 4G
- [ ] Console mostra `VITE_API_URL=https://api.luxbet.site` (não `undefined`)

---

## 🚀 Ação Recomendada Agora

### 1. Verificar DNS na Hostinger (5 min)

**Confirme**:
- Não há CNAME para `www`
- Todos apontam para `147.93.147.33`
- TTL está em `300`

### 2. Testar DNS de Provedores (10 min)

**Em dnschecker.org**:
- Teste DNS da Vivo, Claro, TIM, Oi
- Veja quantos retornam `147.93.147.33`

### 3. Verificar Coolify (10 min)

**Frontend**:
- Confirme que `VITE_API_URL` está configurada
- **Faça REDEPLOY** se necessário

**Backend**:
- Confirme que `api.luxbet.site` está adicionado
- Confirme que SSL está ativo

### 4. Testar no 4G (5 min)

**Backend**:
- `https://api.luxbet.site/api/health`

**Frontend**:
- `https://luxbet.site`
- Console: `import.meta.env.VITE_API_URL`

---

## 💡 Causas Mais Comuns

1. **CNAME para www** ao invés de registro A
2. **`VITE_API_URL` não configurada** ou redeploy não feito
3. **Propagação ainda em andamento** (mesmo com TTL 300, pode levar 2-6h)
4. **Domínios não adicionados** no Coolify
5. **SSL não gerado** ou inválido

---

## ✅ Próximos Passos

1. ✅ **Verificar DNS** na Hostinger (confirmar que não há CNAME)
2. ✅ **Testar DNS** de provedores em dnschecker.org
3. ✅ **Verificar Coolify** (variável `VITE_API_URL` e redeploy)
4. ⏳ **Aguardar mais 2-4 horas** se propagação ainda em andamento
5. 🧪 **Testar novamente** no 4G

---

**Status**: ⏳ TTL correto, mas precisa verificar outras configurações

**Ação Imediata**: Verificar DNS na Hostinger e Coolify, depois testar DNS de provedores
