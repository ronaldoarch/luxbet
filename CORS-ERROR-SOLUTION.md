# 🚨 Erro CORS nos Jogos - Análise e Soluções

## 📋 Problema Identificado

Os jogos estão sendo bloqueados por **política CORS** quando tentam fazer requisições XMLHttpRequest dentro do iframe.

### Erro Observado:
```
Access to XMLHttpRequest at 'https://igamewin.com/gs2c/...' 
from origin 'https://api.igamewin.com' 
has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### O que está acontecendo:

1. **O jogo é carregado em um iframe** na sua página (`luxbet.site`)
2. **A URL retornada** aponta para `https://pgsoft6.api.igamewin.com/...` ou `https://api.igamewin.com/...`
3. **Dentro do iframe**, o jogo tenta fazer requisições para `https://igamewin.com/gs2c/...`
4. **O navegador detecta** que a origem é `https://api.igamewin.com` (mesmo domínio da URL do jogo)
5. **O servidor `igamewin.com`** não retorna os headers CORS necessários (`Access-Control-Allow-Origin`)
6. **O navegador bloqueia** todas as requisições

---

## 🔍 Análise Técnica

### Requisições Bloqueadas:
- `https://igamewin.com/games/pragmatic/desktop/wurfl.js`
- `https://igamewin.com/gs2c/stats.do?...`
- `https://igamewin.com/gs2c/common/v3/games-html5/games/vs/vs20clustcol/desktop/customizations.info`
- `https://igamewin.com/gs2c/common/v3/games-html5/games/vs/vs20clustcol/desktop/packages/pt_desktop.json`
- `https://igamewin.com/gs2c/common/v3/games-html5/games/vs/vs20clustcol/desktop/build.js`

### Por que isso acontece?

O problema é que o **IGameWin não configurou CORS corretamente** em seus servidores. Eles precisam adicionar headers como:
```
Access-Control-Allow-Origin: https://api.igamewin.com
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## ✅ Soluções Possíveis

### Solução 1: Contatar Suporte do IGameWin (RECOMENDADO)

**Esta é a solução mais adequada**, pois o problema está no lado deles.

**O que pedir ao suporte:**
1. Configurar CORS no servidor `igamewin.com` para permitir requisições de `https://api.igamewin.com`
2. Ou configurar CORS para permitir requisições de qualquer origem (menos seguro, mas funciona)
3. Verificar se há configurações específicas necessárias no painel administrativo

**Informações para fornecer:**
- Domínio onde os jogos serão carregados: `luxbet.site`
- Erro específico: CORS bloqueando requisições de `api.igamewin.com` para `igamewin.com`
- Exemplos de URLs bloqueadas: `https://igamewin.com/gs2c/...`

---

### Solução 2: Usar Proxy no Backend (WORKAROUND)

Criar um proxy no backend para fazer as requisições em nome do jogo. **⚠️ Esta solução pode não funcionar completamente** porque o jogo precisa fazer requisições diretas.

**Implementação:**

1. **Criar endpoint de proxy no backend:**

```python
# backend/routes/admin.py
@public_router.get("/games/proxy/{path:path}")
async def game_proxy(
    path: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Proxy para requisições do jogo - WORKAROUND para CORS"""
    # Construir URL completa
    target_url = f"https://igamewin.com/{path}"
    
    # Adicionar query parameters se houver
    if request.query_params:
        target_url += f"?{request.query_params}"
    
    # Fazer requisição
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                target_url,
                headers={
                    "User-Agent": request.headers.get("User-Agent", "Mozilla/5.0"),
                },
                timeout=30.0
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": response.headers.get("Content-Type", "application/json"),
                    "Access-Control-Allow-Origin": "*",
                }
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Erro no proxy: {str(e)}")
```

**Problema:** O jogo ainda tentará fazer requisições diretas para `igamewin.com`, então isso não resolve completamente.

---

### Solução 3: Modificar URL do Jogo (NÃO RECOMENDADO)

Tentar modificar a URL retornada para usar um domínio diferente. **⚠️ Isso pode quebrar a autenticação do jogo.**

---

### Solução 4: Configurar "Ponto final do site" no Painel IGameWin ⚠️ IMPORTANTE

**CRÍTICO:** No formulário de atualização do agente, há um campo **"Ponto final do site (Site Endpoint)"** que está configurado com `https://example.com` (valor de exemplo).

**Este campo precisa ser configurado com a URL correta do seu site!**

**Como configurar:**

1. **No formulário "Agente de atualização":**
   - Localize o campo **"Ponto final do site"**
   - **Altere de:** `https://example.com`
   - **Para:** `https://luxbet.site` (ou a URL do seu site em produção)
   - **⚠️ IMPORTANTE:** Não inclua `/gold_api` no final da URL (conforme instrução no campo)

2. **URLs corretas para configurar:**
   - **Produção:** `https://luxbet.site`
   - **Desenvolvimento:** `http://localhost:3000` (se testando localmente)

3. **Após configurar:**
   - Clique em **"Salvar"**
   - Aguarde alguns minutos para a configuração ser aplicada
   - Teste novamente carregar um jogo

**Por que isso é importante:**

O campo "Ponto final do site" informa ao IGameWin qual é o domínio onde os jogos serão carregados. Com essa informação, o IGameWin pode:
- Configurar CORS corretamente para permitir requisições desse domínio
- Validar requisições vindas desse domínio
- Configurar headers de segurança apropriados

**Outras configurações a verificar no painel:**
- Configurações de "Domínios permitidos"
- Configurações de "CORS"
- Configurações de "Origins permitidos"
- Configurações de "Whitelist de domínios"

---

## 🎯 Solução Recomendada

### Passo 1: Contatar Suporte IGameWin

Enviar email/ticket ao suporte do IGameWin com:

**Assunto:** Erro CORS ao carregar jogos em iframe

**Corpo:**
```
Olá,

Estou enfrentando erros de CORS ao tentar carregar jogos em um iframe.

Erro específico:
Access to XMLHttpRequest at 'https://igamewin.com/gs2c/...' 
from origin 'https://api.igamewin.com' 
has been blocked by CORS policy.

Os jogos são carregados em: https://luxbet.site
A URL de lançamento retornada aponta para: https://api.igamewin.com ou https://pgsoft6.api.igamewin.com

Dentro do iframe, o jogo tenta fazer requisições para:
- https://igamewin.com/games/pragmatic/desktop/wurfl.js
- https://igamewin.com/gs2c/stats.do
- https://igamewin.com/gs2c/common/v3/games-html5/...

Essas requisições estão sendo bloqueadas porque o servidor igamewin.com não retorna os headers CORS necessários.

Por favor, configure CORS no servidor igamewin.com para permitir requisições de:
- https://api.igamewin.com
- https://pgsoft6.api.igamewin.com
- https://luxbet.site

Ou configure para permitir requisições de qualquer origem (menos seguro, mas funciona).

Agradeço a atenção.
```

---

### Passo 2: Verificar Configurações no Painel

Enquanto aguarda resposta, verificar no painel administrativo do IGameWin:
- Seção de "Configurações de API"
- Seção de "Domínios permitidos"
- Seção de "CORS" ou "Cross-Origin"

---

### Passo 3: Workaround Temporário (Se Necessário)

Se precisar de uma solução temporária enquanto aguarda o suporte, pode tentar:

1. **Abrir o jogo em nova aba** em vez de iframe (pior UX, mas pode funcionar)
2. **Usar window.open()** para abrir o jogo em popup

**Exemplo:**
```typescript
// Em vez de iframe, abrir em nova janela
window.open(gameUrl, '_blank', 'width=1920,height=1080');
```

---

## 📝 Notas Importantes

1. **Este não é um problema do nosso código** - o backend está funcionando corretamente
2. **A URL está sendo retornada corretamente** - o problema é CORS no servidor do IGameWin
3. **Não podemos resolver isso apenas com código** - precisa de configuração no lado do IGameWin
4. **A solução definitiva** é o IGameWin configurar CORS corretamente

---

## 🔄 Status Atual

- ✅ Backend retornando URL corretamente
- ✅ Frontend carregando URL no iframe corretamente
- ❌ Servidor IGameWin bloqueando requisições por CORS
- ⏳ Aguardando configuração do lado do IGameWin

---

## 📞 Próximos Passos

1. Contatar suporte do IGameWin sobre configuração de CORS
2. Verificar configurações no painel administrativo
3. Aguardar resposta e implementação
4. Testar novamente após configuração
