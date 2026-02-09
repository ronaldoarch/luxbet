# 🔧 Solução para Erro DNS em 4G (ERR_NAME_NOT_RESOLVED)

## Problema Identificado

O erro `ERR_NAME_NOT_RESOLVED` ocorre quando o DNS não consegue resolver o domínio da API. Isso acontece especificamente em redes 4G, mas funciona no WiFi.

## Causas Possíveis

1. **Variável `VITE_API_URL` não configurada corretamente**
   - O frontend está tentando usar um domínio que não existe ou não está acessível
   - Pode estar usando `localhost` em produção

2. **Problema de DNS do provedor 4G**
   - Alguns provedores 4G têm DNS mais restritivos
   - Pode haver bloqueio ou cache DNS incorreto

3. **Domínio não configurado globalmente**
   - O domínio pode não estar acessível de todas as redes
   - Pode haver problema de propagação DNS

## Solução Imediata

### 1. Verificar Variável de Ambiente no Coolify

No Coolify, vá em **Frontend → Environment Variables** e verifique:

```
VITE_API_URL=https://api.luxbet.site
```

**IMPORTANTE:**
- ✅ Use `https://` (não `http://`)
- ✅ Use o domínio completo (`api.luxbet.site`, não `localhost`)
- ✅ Não use `localhost` ou `127.0.0.1` em produção

### 2. Verificar DNS do Domínio

Teste se o domínio está resolvendo corretamente:

```bash
# No terminal ou usando ferramentas online
nslookup api.luxbet.site
dig api.luxbet.site
```

Se não resolver, o problema é de DNS/configuração do domínio.

### 3. Verificar Configuração do Domínio

Certifique-se de que:
- O domínio `api.luxbet.site` está configurado no DNS
- O registro A ou CNAME aponta para o IP correto do servidor
- O SSL está configurado corretamente

### 4. Testar em Diferentes Redes

- ✅ WiFi: Funciona
- ❌ 4G: Não funciona (ERR_NAME_NOT_RESOLVED)

Isso indica problema de DNS específico do provedor 4G ou configuração incorreta.

## Solução Implementada no Código

O código agora:

1. **Detecta automaticamente o domínio** se `VITE_API_URL` não estiver configurada
2. **Tenta usar `https://api.luxbet.site`** automaticamente se estiver em `luxbet.site`
3. **Loga erros de DNS** especificamente para facilitar debug
4. **Usa fallback** para evitar que a aplicação quebre completamente

## Como Verificar se Está Funcionando

### No Console do Navegador (4G)

Abra o console e procure por:

```
❌ Erro de DNS detectado! O domínio não está resolvendo.
Verifique se VITE_API_URL está configurada corretamente no Coolify.
URL tentada: [URL]
```

### Verificar Variável de Ambiente no Frontend

No console do navegador, execute:

```javascript
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
```

Se retornar `undefined` ou `localhost`, o problema é a variável de ambiente.

## Passos para Resolver

### Passo 1: Verificar Variável no Coolify

1. Acesse o Coolify
2. Vá em **Frontend → Environment Variables**
3. Verifique se `VITE_API_URL` está configurada como:
   ```
   VITE_API_URL=https://api.luxbet.site
   ```

### Passo 2: Fazer Redeploy

Após alterar a variável de ambiente:
1. Salve as alterações
2. Faça redeploy do frontend
3. Aguarde o build completar

### Passo 3: Limpar Cache

No dispositivo com problema (4G):
1. Limpe o cache do navegador
2. Ou use modo anônimo
3. Teste novamente

### Passo 4: Verificar DNS

Se ainda não funcionar, verifique:
- Se o domínio `api.luxbet.site` está acessível publicamente
- Se o DNS está propagado corretamente
- Se há algum bloqueio do provedor 4G

## Teste Rápido

Para testar se o problema é DNS ou código:

1. No dispositivo com 4G, abra o navegador
2. Acesse diretamente: `https://api.luxbet.site/api/health`
3. Se não carregar, o problema é DNS/configuração do servidor
4. Se carregar, o problema é na configuração do frontend

## Solução Alternativa (Temporária)

Se o problema persistir, você pode:

1. **Usar IP direto** (não recomendado para produção):
   ```
   VITE_API_URL=https://[IP_DO_SERVIDOR]
   ```

2. **Usar outro domínio** que funcione no 4G

3. **Configurar DNS alternativo** no dispositivo (8.8.8.8 do Google)

## Monitoramento

O código agora loga especificamente erros de DNS. Monitore os logs para identificar:
- Quantos usuários estão tendo problema de DNS
- Qual domínio está sendo tentado
- Se há padrão (todos 4G, todos WiFi, etc)

## Contato com Suporte

Se o problema persistir após seguir todos os passos:

1. Coletar logs do console do navegador
2. Verificar qual URL está sendo tentada
3. Testar acesso direto ao domínio
4. Verificar configuração DNS do domínio
