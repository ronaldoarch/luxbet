# 🔍 Verificar Proxy, Firewall e DNS over HTTPS (DoH)

## 🎯 Problema

Erro: `DNS_PROBE_FINISHED_BAD_CONFIG`  
Sugestões do navegador:
- Checking the proxy, firewall, and DNS configuration
- Changing DNS over HTTPS settings

---

## ✅ Solução 1: Verificar e Desabilitar Proxy

### No Celular (Android):

1. **Acesse Configurações**:
   - Configurações → Rede e Internet → Wi-Fi
   - Ou Configurações → Conexões → Wi-Fi

2. **Verifique Proxy**:
   - Toque no Wi-Fi conectado (ou mantenha pressionado)
   - Toque em "Modificar" ou "Configurações avançadas"
   - Procure por "Proxy" ou "Configurações de proxy"
   - Se estiver configurado, mude para "Nenhum" ou "Desabilitado"

3. **Para Dados Móveis (4G)**:
   - Configurações → Rede e Internet → Rede móvel
   - Configurações avançadas → Proxy
   - Se estiver configurado, desabilite

### No Celular (iOS):

1. **Acesse Configurações**:
   - Configurações → Wi-Fi

2. **Verifique Proxy**:
   - Toque no "i" ao lado do Wi-Fi conectado
   - Role até "Proxy HTTP"
   - Se estiver configurado, mude para "Desativado"

3. **Para Dados Móveis (4G)**:
   - iOS geralmente não permite proxy em dados móveis
   - Mas verifique: Configurações → Celular → Opções de Dados

---

## ✅ Solução 2: Verificar DNS over HTTPS (DoH)

### O Que É DNS over HTTPS?

DNS over HTTPS (DoH) é uma configuração que criptografa consultas DNS. Às vezes pode causar problemas se o servidor DoH não propagou ainda.

### No Chrome (Android/iOS):

1. **Acesse Configurações**:
   - Abra Chrome
   - Menu (3 pontos) → Configurações

2. **Verifique DoH**:
   - Privacidade e segurança → Segurança
   - Procure por "Usar DNS seguro" ou "Secure DNS"
   - Se estiver ativado, tente desativar temporariamente
   - Ou mude para "Com seu provedor atual"

### No Firefox (Android/iOS):

1. **Acesse Configurações**:
   - Abra Firefox
   - Menu → Configurações

2. **Verifique DoH**:
   - Privacidade → DNS sobre HTTPS
   - Se estiver ativado, desative temporariamente
   - Ou mude para "Desativado"

### No Safari (iOS):

1. **Acesse Configurações**:
   - Configurações → Safari

2. **Verifique DoH**:
   - Safari não tem configuração explícita de DoH
   - Mas verifique se há extensões ou configurações de privacidade que possam estar interferindo

---

## ✅ Solução 3: Verificar Firewall/Antivírus

### No Celular:

1. **Verifique Apps de Segurança**:
   - Procure por apps como: Avast, AVG, Norton, McAfee, etc.
   - Abra o app de segurança
   - Verifique se há bloqueios de DNS ou firewall ativo
   - Desative temporariamente para testar

2. **Verifique VPN**:
   - Se você tem VPN ativada, desative temporariamente
   - VPN pode usar DNS próprio que ainda não propagou

3. **Modo de Desenvolvedor**:
   - Se você tem modo desenvolvedor ativado, verifique configurações de rede
   - Algumas configurações podem interferir com DNS

---

## ✅ Solução 4: Limpar Cache DNS e Configurações de Rede

### Android:

1. **Limpar Cache DNS**:
   - Configurações → Aplicativos → Chrome (ou seu navegador)
   - Armazenamento → Limpar cache
   - Limpar dados (cuidado: vai limpar senhas salvas)

2. **Resetar Configurações de Rede**:
   - Configurações → Sistema → Redefinir opções
   - Redefinir opções de Wi-Fi, celular e Bluetooth
   - ⚠️ Isso vai remover todas as redes Wi-Fi salvas

### iOS:

1. **Limpar Cache DNS**:
   - Configurações → Safari
   - Limpar histórico e dados do site

2. **Resetar Configurações de Rede**:
   - Configurações → Geral → Transferir ou Redefinir iPhone
   - Redefinir → Redefinir configurações de rede
   - ⚠️ Isso vai remover todas as redes Wi-Fi salvas

---

## ✅ Solução 5: Usar DNS Público (Recomendado)

Se proxy/firewall/DoH estão causando problemas, use DNS público:

### Android:

1. **Instale app**: "1.1.1.1" (Cloudflare) ou "DNS Changer"
2. **Configure DNS**:
   - DNS 1: `8.8.8.8` (Google)
   - DNS 2: `1.1.1.1` (Cloudflare)
3. **Ative** e teste no 4G

### iOS:

1. **Instale app**: "1.1.1.1" (Cloudflare)
2. **Configure DNS**:
   - DNS 1: `8.8.8.8` (Google)
   - DNS 2: `1.1.1.1` (Cloudflare)
3. **Ative** e teste no 4G

**Por que funciona**: DNS públicos já propagaram e não dependem de configurações locais.

---

## 🔍 Diagnóstico Passo a Passo

### Passo 1: Verificar Proxy

1. ✅ Verifique se há proxy configurado
2. ✅ Se houver, desative temporariamente
3. ✅ Teste no 4G

### Passo 2: Verificar DNS over HTTPS

1. ✅ Abra configurações do navegador
2. ✅ Procure por "DNS seguro" ou "Secure DNS"
3. ✅ Desative temporariamente
4. ✅ Teste no 4G

### Passo 3: Verificar Firewall/Antivírus

1. ✅ Verifique apps de segurança instalados
2. ✅ Desative temporariamente
3. ✅ Teste no 4G

### Passo 4: Limpar Cache DNS

1. ✅ Limpe cache do navegador
2. ✅ Reinicie celular
3. ✅ Teste no 4G

### Passo 5: Usar DNS Público

1. ✅ Instale app DNS
2. ✅ Configure DNS público
3. ✅ Teste no 4G

---

## 🧪 Testes de Verificação

### Teste 1: Verificar DNS Atual

**No celular (4G)**:
1. Instale app "Network Info" ou "DNS Changer"
2. Veja qual DNS está sendo usado
3. Anote os IPs

**No computador (WiFi)**:
```bash
# Teste DNS específico
nslookup www.luxbet.site 8.8.8.8
# Deve retornar: 147.93.147.33

nslookup www.luxbet.site 1.1.1.1
# Deve retornar: 147.93.147.33
```

### Teste 2: Verificar Se Proxy Está Ativo

**No celular**:
1. Abra navegador
2. Acesse: https://whatismyipaddress.com
3. Veja se o IP mostrado é do seu provedor móvel
4. Se for diferente, pode haver proxy/VPN ativo

### Teste 3: Testar Backend Diretamente

**No celular (4G)**:
```
https://api.luxbet.site/api/health
```

**Resultados**:
- ✅ Se funcionar: DNS está OK, problema pode ser proxy/firewall
- ❌ Se não funcionar: DNS ainda não propagou ou há bloqueio

---

## 📊 Configurações Comuns que Podem Causar Problemas

### 1. Proxy Corporativo

Se você está em rede corporativa ou usando VPN:
- Desative temporariamente
- Teste em rede doméstica/4G direto

### 2. DNS over HTTPS Ativado

Se DoH está ativado e usando servidor que não propagou:
- Desative temporariamente
- Ou mude para DNS público (8.8.8.8, 1.1.1.1)

### 3. Firewall/Antivírus

Apps de segurança podem bloquear DNS:
- Desative temporariamente para testar
- Adicione exceção se necessário

### 4. VPN Ativa

VPN pode usar DNS próprio:
- Desative temporariamente
- Teste sem VPN

---

## 🎯 Solução Recomendada (Ordem de Prioridade)

### 1. Desabilitar DNS over HTTPS (RÁPIDO - 2 minutos)

**Chrome**:
- Configurações → Privacidade e segurança → Segurança
- "Usar DNS seguro" → Desativado ou "Com seu provedor atual"

**Firefox**:
- Configurações → Privacidade → DNS sobre HTTPS → Desativado

### 2. Verificar e Desabilitar Proxy (RÁPIDO - 2 minutos)

**Android**:
- Configurações → Wi-Fi → (seu Wi-Fi) → Proxy → Nenhum

**iOS**:
- Configurações → Wi-Fi → (i) → Proxy HTTP → Desativado

### 3. Limpar Cache DNS (RÁPIDO - 5 minutos)

- Limpar cache do navegador
- Reiniciar celular
- Resetar conexão 4G

### 4. Usar DNS Público (DEFINITIVO - 10 minutos)

- Instalar app "1.1.1.1"
- Configurar DNS: 8.8.8.8 e 1.1.1.1
- Ativar e testar

---

## 💡 Por Que Isso Resolve?

1. **DNS over HTTPS**: Pode estar usando servidor DoH que ainda não propagou
2. **Proxy**: Pode estar interceptando e bloqueando requisições DNS
3. **Firewall**: Pode estar bloqueando consultas DNS
4. **DNS Público**: Contorna todas essas configurações e usa DNS que já propagou

---

## 📝 Checklist Completo

- [ ] Verificar e desabilitar proxy
- [ ] Verificar e desabilitar DNS over HTTPS
- [ ] Verificar e desabilitar firewall/antivírus temporariamente
- [ ] Verificar e desabilitar VPN temporariamente
- [ ] Limpar cache DNS do navegador
- [ ] Reiniciar celular
- [ ] Resetar conexão 4G
- [ ] Usar DNS público no celular
- [ ] Testar no 4G

---

## ✅ Resultado Esperado

Após seguir esses passos:
- ✅ Proxy não interfere mais
- ✅ DNS over HTTPS não causa problemas
- ✅ Firewall não bloqueia
- ✅ DNS público funciona imediatamente
- ✅ Site funciona no 4G

---

**Ação Recomendada**: Comece desabilitando DNS over HTTPS e proxy. Se não funcionar, use DNS público no celular - isso deve resolver imediatamente! 🚀
