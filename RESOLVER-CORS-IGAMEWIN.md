# 🔧 Como Resolver Erros de CORS do IGameWin

## 🔍 Problema Identificado

O jogo está conseguindo iniciar (obter URL de lançamento), mas quando tenta carregar recursos do IGameWin, recebe erros de CORS:

```
Access to XMLHttpRequest at 'https://igamewin.com/gs2c/common/v2/games-html5/games/vs/vs10bbbonanza/desktop/customizations.info?key=bdd0b' 
from origin 'https://api.igamewin.com' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Mensagem no jogo:** "Retry limit of client config exceeded!"

**Detalhes técnicos importantes:**
- **Origem:** `https://api.igamewin.com` (onde o jogo é carregado pelo IGameWin)
- **Destino:** `https://igamewin.com` (recursos que o jogo tenta carregar)
- **Problema:** O servidor `igamewin.com` não está enviando o header `Access-Control-Allow-Origin` permitindo `api.igamewin.com`
- **Observação:** Este é um problema **interno do IGameWin** - eles precisam permitir que seus próprios domínios (`api.igamewin.com`) acessem recursos de `igamewin.com`

---

## 🎯 Causa Raiz

Este é um problema de configuração no lado do **IGameWin**. Eles precisam:

1. **Configurar domínios permitidos** para que recursos possam ser carregados
2. **Adicionar headers CORS** nas respostas dos recursos do jogo
3. **Permitir que `luxbet.site`** acesse recursos de `igamewin.com`

---

## ✅ Solução: Configurar no Painel IGameWin

### Passo 1: Acessar Configurações do Agente

1. **Acesse** o painel administrativo do IGameWin
2. **Vá em** "Agente de atualização" ou "Agent Settings"
3. **Localize** campos relacionados a domínios

### Passo 2: Configurar Domínios Permitidos

Procure por campos como:
- **"Domínios permitidos"** (Allowed Domains)
- **"Site domains"** (Domínios do site)
- **"Whitelist domains"** (Domínios na lista branca)
- **"Allowed origins"** (Origens permitidas)

**Adicione os seguintes domínios:**
```
luxbet.site
www.luxbet.site
api.luxbet.site
```

### Passo 3: Verificar Campo "Ponto final do site"

Certifique-se de que está configurado como:
```
https://api.luxbet.site
```

### Passo 4: Salvar e Aguardar

1. **Salve** todas as alterações
2. **Aguarde** 5-10 minutos para a configuração ser aplicada
3. **Teste** iniciar o jogo novamente

---

## 🔧 O Que Fizemos no Nosso Código

### Melhorias no Iframe:

Adicionamos atributos adicionais ao iframe para melhor compatibilidade:

```tsx
<iframe
  src={gameUrl}
  allow="fullscreen; autoplay; payment; geolocation; microphone; camera"
  sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-presentation"
  referrerPolicy="no-referrer-when-downgrade"
/>
```

Isso ajuda, mas **não resolve** o problema de CORS - isso precisa ser configurado no lado do IGameWin.

---

## 📞 Se Não Houver Campos para Domínios Permitidos

Se você não encontrar campos para configurar domínios permitidos no painel:

### Contate o Suporte do IGameWin

**Informações para fornecer:**

1. **Agent Code:** `welisson4916`
2. **Problema:** Erros de CORS ao carregar recursos do jogo
3. **Domínios que precisam ser permitidos:**
   - `luxbet.site`
   - `www.luxbet.site`
   - `api.luxbet.site`
4. **Erro específico:**
   ```
   Access to XMLHttpRequest at 'https://igamewin.com/gs2c/common/v2/games-html5/games/vs/vs10bbbonanza/desktop/customizations.info?key=bdd0b' 
   from origin 'https://api.igamewin.com' has been blocked by CORS policy: 
   No 'Access-Control-Allow-Origin' header is present on the requested resource.
   ```
5. **Problema adicional identificado:** O próprio IGameWin tem problema interno de CORS:
   - `api.igamewin.com` não consegue acessar recursos de `igamewin.com`
   - Isso afeta TODOS os jogos, não apenas os do seu site
   - Precisa que o IGameWin configure CORS internamente entre seus próprios domínios
6. **Jogos afetados:** Todos os jogos (Big Bass Bonanza, Aviator, etc.)

**Peça para eles:**
- Adicionar os domínios acima à lista de domínios permitidos
- Configurar headers CORS (`Access-Control-Allow-Origin`) nas respostas dos recursos do jogo
- Verificar se há alguma configuração adicional necessária

---

## 🧪 Como Verificar se Foi Resolvido

### Teste 1: Verificar Console do Navegador

1. Abra o jogo
2. Pressione **F12** para abrir DevTools
3. Vá na aba **Console**
4. **Verifique se ainda há erros de CORS**

**Se não houver mais erros de CORS** → Problema resolvido! ✅

### Teste 2: Verificar se o Jogo Carrega

- O jogo deve carregar completamente
- Não deve aparecer "Retry limit of client config exceeded!"
- Os recursos do jogo devem carregar normalmente

---

## 📋 Checklist Completo

- [ ] Campo "Ponto final do site" configurado como `https://api.luxbet.site`
- [ ] Campo "Domínios permitidos" configurado com `luxbet.site`, `www.luxbet.site`, `api.luxbet.site`
- [ ] Aguardou 5-10 minutos após salvar configurações
- [ ] Testou iniciar o jogo novamente
- [ ] Verificou console do navegador - não há mais erros de CORS
- [ ] Jogo carrega completamente sem erros

---

## 🔄 Status Atual

✅ **Resolvido:**
- Endpoint `/gold_api` implementado
- Erro `ERROR_GET_BALANCE_END_POINT` resolvido
- Jogo consegue obter URL de lançamento
- Iframe melhorado com atributos adicionais

⚠️ **Pendente (Configuração IGameWin):**
- Erros de CORS ao carregar recursos
- Precisa configurar domínios permitidos no painel IGameWin
- Precisa que IGameWin adicione headers CORS nas respostas

---

## 💡 Nota Importante

**Não podemos resolver isso apenas com código nosso.** Os erros de CORS acontecem porque:

1. O jogo (carregado em `luxbet.site`) tenta acessar recursos de `igamewin.com`
2. O servidor `igamewin.com` não está enviando o header `Access-Control-Allow-Origin`
3. O navegador bloqueia a requisição por segurança

**A solução está no lado do IGameWin** - eles precisam:
- Adicionar `luxbet.site` aos domínios permitidos
- Configurar headers CORS nas respostas dos recursos

---

## 🎯 Próximos Passos

1. **Configure** domínios permitidos no painel IGameWin
2. **Aguarde** alguns minutos
3. **Teste** o jogo novamente
4. **Se não funcionar**, contate o suporte do IGameWin com as informações acima
