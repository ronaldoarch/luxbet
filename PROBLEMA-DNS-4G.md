# 🚨 Problema Crítico: DNS não resolve no 4G

## Situação Atual

- ❌ `luxbet.site` não resolve no DNS do provedor 4G
- ❌ `api.luxbet.site` não resolve no DNS do provedor 4G
- ✅ Funciona no WiFi (DNS diferente)

## Causa Raiz

O problema não é código, mas sim **configuração DNS do domínio**. O provedor 4G não consegue resolver o domínio `luxbet.site`.

## Soluções Imediatas

### Solução 1: Verificar Configuração DNS (RECOMENDADO)

1. **Verificar registros DNS do domínio**
   - Acesse o painel do seu provedor de DNS (Cloudflare, Hostinger, etc.)
   - Verifique se os registros A/AAAA estão configurados corretamente
   - Verifique se o TTL não está muito alto (recomendado: 300-600 segundos)

2. **Testar DNS de diferentes locais**
   ```bash
   # Testar de diferentes servidores DNS
   nslookup luxbet.site 8.8.8.8      # Google DNS
   nslookup luxbet.site 1.1.1.1      # Cloudflare DNS
   nslookup luxbet.site 208.67.222.222  # OpenDNS
   ```

3. **Verificar propagação DNS**
   - Use ferramentas online como: https://www.whatsmydns.net/
   - Verifique se o domínio resolve globalmente

### Solução 2: Usar DNS Público (Temporário)

No dispositivo com problema 4G:

**Android:**
1. Configurações → Conexões → Wi-Fi
2. Toque e segure na rede WiFi
3. Modificar rede → Opções avançadas
4. Configurações de IP → Estático
5. DNS 1: `8.8.8.8` (Google)
6. DNS 2: `1.1.1.1` (Cloudflare)

**iOS:**
1. Configurações → Wi-Fi
2. Toque no "i" ao lado da rede
3. Configure DNS → Manual
4. Adicione: `8.8.8.8` e `1.1.1.1`

**Para 4G (mais complexo):**
- Precisa usar VPN ou app de DNS
- Ou configurar DNS no nível do roteador

### Solução 3: Usar IP Direto (EMERGÊNCIA)

Se o DNS não resolver, você pode usar o IP direto:

1. **Descobrir o IP do servidor:**
   ```bash
   # No terminal ou usando ferramentas online
   nslookup luxbet.site
   # ou
   dig luxbet.site +short
   ```

2. **Configurar variável de ambiente temporariamente:**
   ```
   VITE_API_URL=https://[IP_DO_SERVIDOR]
   ```

   **⚠️ ATENÇÃO:** Isso não funcionará com SSL se o certificado for baseado em domínio.

### Solução 4: Configurar DNS Alternativo no Backend

Se o problema for apenas com `api.luxbet.site`, você pode:

1. **Usar o mesmo domínio do frontend:**
   - Configurar o backend para responder em `luxbet.site/api` em vez de `api.luxbet.site`
   - Isso evita problemas de DNS com subdomínios

2. **Configurar proxy reverso:**
   - Nginx/Caddy pode fazer proxy de `luxbet.site/api/*` para o backend
   - Tudo fica no mesmo domínio

## Verificações Necessárias

### 1. Verificar DNS do Domínio

```bash
# Verificar se o domínio resolve
dig luxbet.site
dig api.luxbet.site

# Verificar de diferentes servidores DNS
dig @8.8.8.8 luxbet.site
dig @1.1.1.1 luxbet.site
```

### 2. Verificar Configuração no Provedor DNS

- **Registro A:** Deve apontar para o IP do servidor
- **Registro AAAA:** Se usar IPv6
- **TTL:** Recomendado 300-600 segundos (não muito alto)
- **Propagação:** Pode levar até 48 horas

### 3. Verificar Certificado SSL

- Certificado deve ser válido para `luxbet.site` e `*.luxbet.site`
- Ou certificado separado para `api.luxbet.site`

## Solução Definitiva

A solução definitiva depende de onde está hospedado o DNS:

### Se estiver usando Cloudflare:
1. Verifique se o proxy está ativado (nuvem laranja)
2. Verifique se os registros estão corretos
3. Limpe o cache do Cloudflare

### Se estiver usando Hostinger/outros:
1. Verifique os registros A/AAAA
2. Verifique se o IP está correto
3. Aguarde propagação (pode levar horas)

### Se estiver usando Coolify:
1. Verifique se o domínio está configurado corretamente
2. Verifique se o DNS está apontando para o Coolify
3. Verifique logs do Coolify para erros

## Teste Rápido

Para confirmar que é problema de DNS:

1. **No dispositivo com 4G, tente:**
   - Abrir `https://luxbet.site` diretamente
   - Se não abrir, é problema de DNS do domínio principal

2. **Testar com IP direto:**
   - Descubra o IP do servidor
   - Tente acessar `https://[IP]` (pode dar erro de certificado, mas confirma se é DNS)

3. **Testar com DNS público:**
   - Configure DNS 8.8.8.8 no dispositivo
   - Tente acessar novamente

## Próximos Passos

1. ✅ Verificar configuração DNS do domínio `luxbet.site`
2. ✅ Verificar se o IP está correto nos registros DNS
3. ✅ Testar de diferentes servidores DNS
4. ✅ Considerar usar mesmo domínio para API (sem subdomínio)
5. ✅ Verificar se há bloqueio do provedor 4G

## Contato com Suporte

Se o problema persistir:

1. Entre em contato com o provedor DNS
2. Verifique se há bloqueio do provedor 4G
3. Considere usar CDN (Cloudflare) para melhor propagação DNS
