# 🔍 Diagnóstico de Problemas em Dispositivos Específicos

Este documento explica como diagnosticar e resolver problemas quando a aplicação funciona em alguns dispositivos mas não em outros.

## ✅ Melhorias Implementadas

### Backend (`backend/main.py`)

1. **Middleware de Logging**
   - Logs de todas as requisições com IP, User-Agent e tempo de processamento
   - Facilita identificar padrões em dispositivos com problemas

2. **Detecção Melhorada de IP**
   - Considera headers `X-Forwarded-For` e `X-Real-IP` para proxies/CDNs
   - Evita problemas de rate limiting incorreto

3. **Headers de Compatibilidade**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `X-XSS-Protection: 1; mode=block`
   - `Cache-Control: no-cache, no-store, must-revalidate`
   - `Pragma: no-cache`
   - `Expires: 0`

4. **CORS Otimizado**
   - `expose_headers: ["*"]` - expõe todos os headers
   - `max_age: 3600` - cache de preflight por 1 hora

### Frontend (`frontend/src/components/Sidebar.tsx`)

1. **Timeout nas Requisições**
   - Timeout de 15 segundos para evitar requisições infinitas
   - AbortController para cancelar requisições lentas

2. **Retry Automático**
   - Tenta novamente automaticamente em caso de erro de rede
   - Delay exponencial entre tentativas

3. **Headers de Requisição**
   - `Accept: application/json`
   - `Cache-Control: no-cache`
   - `mode: cors` explícito

## 🔍 Como Diagnosticar Problemas

### 1. Verificar Logs do Backend

Acesse os logs do backend e procure por:
- Requisições do dispositivo com problema
- Erros específicos (timeout, CORS, etc)
- User-Agent do dispositivo

```bash
# Exemplo de log esperado:
# Request: GET /api/public/games - IP: 192.168.1.100 - UA: Mozilla/5.0...
# Response: GET /api/public/games - Status: 200 - Time: 0.123s
```

### 2. Testar Endpoint de Health

O endpoint `/api/health` agora retorna informações de debug:

```bash
curl https://api.luxbet.site/api/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "headers": {...}
}
```

### 3. Verificar Console do Navegador

No dispositivo com problema, abra o console do navegador e verifique:
- Erros de CORS
- Erros de timeout
- Erros de rede
- Headers de resposta

### 4. Verificar Headers de Resposta

Use ferramentas como:
- Chrome DevTools → Network tab
- Firefox DevTools → Network tab
- Postman/Insomnia

Verifique se os headers de compatibilidade estão presentes:
- `X-Content-Type-Options`
- `Cache-Control`
- `Access-Control-Allow-Origin`

## 🐛 Problemas Comuns e Soluções

### Problema: Timeout em alguns dispositivos

**Sintomas:**
- Requisições demoram muito ou nunca completam
- Erro "Timeout" no console

**Soluções:**
1. Verificar se o dispositivo tem conexão estável
2. Verificar se há firewall/proxy bloqueando
3. Aumentar timeout se necessário (padrão: 15s)

### Problema: CORS em alguns dispositivos

**Sintomas:**
- Erro "CORS policy" no console
- Requisições bloqueadas pelo navegador

**Soluções:**
1. Verificar se `allow_origins=["*"]` está ativo no backend
2. Verificar headers `Access-Control-Allow-Origin` na resposta
3. Limpar cache do navegador

### Problema: Cache em alguns dispositivos

**Sintomas:**
- Dados desatualizados
- Requisições retornam dados antigos

**Soluções:**
1. Headers `Cache-Control: no-cache` já implementados
2. Limpar cache do navegador
3. Usar modo anônimo para testar

### Problema: Rate Limiting incorreto

**Sintomas:**
- Muitas requisições bloqueadas
- Erro 429 (Too Many Requests)

**Soluções:**
1. Verificar se IP está sendo detectado corretamente
2. Verificar logs para ver IP real vs IP detectado
3. Ajustar função `get_client_ip()` se necessário

## 📊 Monitoramento

### Logs Importantes para Monitorar

1. **Tempo de Resposta**
   - Verificar se há dispositivos com tempo muito alto
   - Header `X-Process-Time` mostra tempo de processamento

2. **Taxa de Erro**
   - Monitorar erros por User-Agent
   - Identificar padrões em dispositivos específicos

3. **Taxa de Timeout**
   - Monitorar quantos timeouts ocorrem
   - Identificar se é problema de rede ou servidor

## 🔧 Configurações Adicionais

### Variáveis de Ambiente

No backend, você pode configurar:

```env
# Timeout padrão para requisições (em segundos)
REQUEST_TIMEOUT=30

# Log level
LOG_LEVEL=INFO

# CORS origins (separados por vírgula)
CORS_ORIGINS=https://luxbet.site,https://www.luxbet.site
```

### Ajustar Timeout no Frontend

No arquivo `frontend/src/components/Sidebar.tsx`, você pode ajustar:

```typescript
const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 segundos
```

Para dispositivos com conexão lenta, aumentar para 30 segundos:

```typescript
const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos
```

## 📝 Checklist de Diagnóstico

Quando um dispositivo não funciona:

- [ ] Verificar logs do backend para requisições desse dispositivo
- [ ] Testar endpoint `/api/health` do dispositivo
- [ ] Verificar console do navegador para erros
- [ ] Verificar headers de resposta nas DevTools
- [ ] Testar em modo anônimo (sem cache)
- [ ] Testar em outra rede (WiFi vs 4G)
- [ ] Verificar User-Agent do dispositivo
- [ ] Verificar se há firewall/proxy bloqueando
- [ ] Comparar com dispositivo que funciona

## 🆘 Suporte

Se o problema persistir após seguir este guia:

1. Coletar logs do backend
2. Coletar screenshots do console do navegador
3. Coletar informações do dispositivo (User-Agent, IP, etc)
4. Verificar se há padrão (todos iOS, todos Android, etc)
