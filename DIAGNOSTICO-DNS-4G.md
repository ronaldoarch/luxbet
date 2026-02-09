# 🔍 Diagnóstico DNS - Problema no 4G

## Situação Confirmada

- ❌ `luxbet.site` não resolve no DNS do provedor 4G
- ❌ `api.luxbet.site` não resolve no DNS do provedor 4G  
- ✅ Funciona no WiFi (DNS diferente)

**Isso confirma que é um problema de DNS, não de código.**

## Testes Imediatos

### 1. Testar DNS de Diferentes Servidores

No dispositivo com 4G, você pode testar usando ferramentas online:

1. **Acesse:** https://dnschecker.org
2. **Digite:** `luxbet.site`
3. **Verifique:** Se o IP aparece em todos os servidores DNS

Se alguns servidores não conseguem resolver, o problema é de propagação DNS.

### 2. Verificar Configuração DNS Atual

**Na Hostinger (ou seu provedor DNS):**

Verifique se existe:
```
Tipo: A
Nome: @ (ou vazio)
Valor: [IP do servidor Coolify]
TTL: 300-3600
```

**Para api.luxbet.site:**
```
Tipo: A
Nome: api
Valor: [IP do servidor Coolify]
TTL: 300-3600
```

### 3. Descobrir o IP do Servidor

No Coolify:
1. Vá em **Settings** → **Servers**
2. Anote o IP do servidor (provavelmente `147.93.147.33` ou similar)

### 4. Testar com IP Direto

Como teste temporário, você pode tentar acessar diretamente pelo IP:

```
https://[IP_DO_SERVIDOR]
```

**⚠️ ATENÇÃO:** Isso pode dar erro de certificado SSL, mas confirma se o servidor está acessível.

## Soluções

### Solução 1: Verificar e Corrigir DNS (RECOMENDADO)

1. **Acesse o painel DNS** (Hostinger, Cloudflare, etc.)
2. **Verifique os registros A:**
   - Deve ter registro A para `@` (domínio principal)
   - Deve ter registro A para `api` (subdomínio)
   - Ambos devem apontar para o mesmo IP

3. **Verifique o TTL:**
   - TTL muito alto (86400+) pode causar problemas
   - Recomendado: 300-600 segundos

4. **Limpe cache DNS:**
   - No painel DNS, procure por opção de "Clear Cache" ou "Flush DNS"
   - Aguarde alguns minutos

### Solução 2: Usar Mesmo Domínio (Sem Subdomínio)

Se o problema persistir, considere usar o mesmo domínio para API:

**No Coolify:**
- Backend: Configure para responder em `luxbet.site/api/*`
- Frontend: Configure para usar `luxbet.site`

**Variáveis de Ambiente:**
```
VITE_API_URL=https://luxbet.site/api
```

Isso evita problemas com subdomínios.

### Solução 3: Usar DNS Público no Dispositivo

**Android:**
1. Configurações → Conexões → Wi-Fi
2. Toque e segure na rede → Modificar rede
3. Opções avançadas → Configurações de IP → Estático
4. DNS 1: `8.8.8.8` (Google)
5. DNS 2: `1.1.1.1` (Cloudflare)

**iOS:**
1. Configurações → Wi-Fi
2. Toque no "i" ao lado da rede
3. Configure DNS → Manual
4. Adicione: `8.8.8.8` e `1.1.1.1`

**Para 4G:** Mais difícil, mas pode usar VPN ou app de DNS.

### Solução 4: Verificar Bloqueio do Provedor

Alguns provedores 4G bloqueiam certos domínios. Teste:

1. Tente acessar de outro dispositivo 4G (outro provedor)
2. Se funcionar em outro provedor, é bloqueio específico
3. Considere usar CDN (Cloudflare) para contornar bloqueios

## Verificações no Coolify

### 1. Verificar Domínios Configurados

No Coolify, verifique:

**Backend:**
- Domains → Deve ter `api.luxbet.site` ou `luxbet.site`

**Frontend:**
- Domains → Deve ter `luxbet.site` e `www.luxbet.site`

### 2. Verificar SSL

- Certificados devem estar válidos
- Verifique se não há erros de SSL nos logs

### 3. Verificar Logs

Nos logs do Coolify, procure por:
- Erros de DNS
- Erros de certificado SSL
- Erros de conexão

## Próximos Passos

1. ✅ Verificar configuração DNS no provedor (Hostinger, etc.)
2. ✅ Verificar se o IP está correto nos registros A
3. ✅ Testar com DNS público (8.8.8.8)
4. ✅ Verificar propagação DNS em https://dnschecker.org
5. ✅ Considerar usar mesmo domínio para API (sem subdomínio)

## Contato com Suporte

Se o problema persistir:

1. **Contate o provedor DNS** (Hostinger, etc.)
   - Pergunte se há problemas conhecidos
   - Verifique se o domínio está bloqueado

2. **Contate o provedor 4G**
   - Pergunte se há bloqueio do domínio
   - Verifique se há restrições DNS

3. **Considere usar Cloudflare**
   - Cloudflare tem melhor propagação DNS
   - Pode contornar bloqueios de provedores

## Teste Rápido

Para confirmar que é DNS:

1. No dispositivo com 4G, configure DNS manual: `8.8.8.8`
2. Tente acessar `luxbet.site` novamente
3. Se funcionar com DNS público, confirma que é problema do DNS do provedor 4G
