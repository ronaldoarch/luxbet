# ⚠️ Erros de CORS ao Carregar Recursos do IGameWin

## ✅ Progresso: ERROR_GET_BALANCE_END_POINT Resolvido!

O erro `ERROR_GET_BALANCE_END_POINT` foi resolvido! Agora o jogo está conseguindo iniciar, mas há um novo problema: **erros de CORS ao carregar recursos do IGameWin**.

---

## 🔍 Problema Atual

O jogo está iniciando, mas quando tenta carregar recursos (como `demo.json`, assets, etc.) do IGameWin, recebe erros de CORS:

```
Access to XMLHttpRequest at 'https://igamewin.com/aviator/demo.json?v=4.2.29-hotfix-5' 
from origin 'https://api.igamewin.com' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Mensagem no jogo:** "Retry limit of client config exceeded!"

---

## 🔍 Causa

Este é um problema do lado do **IGameWin**, não do nosso código. O IGameWin não está configurando os headers CORS corretamente para permitir que os recursos sejam carregados quando o jogo é exibido em nosso domínio (`luxbet.site`).

---

## ✅ Soluções Possíveis

### Solução 1: Configurar Domínio Permitido no Painel IGameWin

1. **Acesse** o painel administrativo do IGameWin
2. **Vá em** "Agente de atualização" ou configurações do agente
3. **Procure por** campos relacionados a:
   - "Domínios permitidos"
   - "Allowed domains"
   - "Site domains"
   - "Whitelist domains"
4. **Adicione** o domínio: `luxbet.site`
5. **Salve** e aguarde alguns minutos

### Solução 2: Verificar Campo "Ponto final do site"

Certifique-se de que o campo **"Ponto final do site"** está configurado como:
- ✅ `https://api.luxbet.site` (para o endpoint `/gold_api`)
- ✅ E também verifique se há um campo separado para "Domínios permitidos" ou "Site domains"

### Solução 3: Contatar Suporte IGameWin

Se não houver campos para configurar domínios permitidos:

1. **Contate o suporte do IGameWin**
2. **Informe:**
   - Agent Code: `welisson4916`
   - Domínio que precisa ser permitido: `luxbet.site`
   - Erro específico: CORS ao carregar recursos de `igamewin.com`
   - Jogo afetado: Aviator Core (e possivelmente outros)

---

## 🧪 Como Verificar se Está Funcionando

### Teste 1: Verificar se o jogo inicia
- O jogo deve conseguir obter a URL de lançamento
- O iframe deve carregar

### Teste 2: Verificar se recursos carregam
- Abra o console do navegador (F12)
- Verifique se há erros de CORS
- Se não houver erros de CORS, o problema foi resolvido

---

## 📋 Checklist

- [ ] Campo "Ponto final do site" configurado como `https://api.luxbet.site`
- [ ] Campo "Domínios permitidos" ou similar configurado com `luxbet.site`
- [ ] Aguardou alguns minutos após salvar configurações
- [ ] Testou iniciar o jogo novamente
- [ ] Verificou console do navegador para erros de CORS

---

## 🔄 Status Atual

✅ **Resolvido:**
- Endpoint `/gold_api` implementado e funcionando
- Erro `ERROR_GET_BALANCE_END_POINT` resolvido
- Jogo consegue iniciar e obter URL de lançamento

⚠️ **Pendente:**
- Erros de CORS ao carregar recursos do IGameWin
- Precisa configurar domínios permitidos no painel IGameWin

---

## 💡 Nota Importante

Os erros de CORS são **diferentes** do erro `ERROR_GET_BALANCE_END_POINT`:

- **ERROR_GET_BALANCE_END_POINT**: Problema ao buscar saldo antes de lançar o jogo
- **CORS Errors**: Problema ao carregar recursos do jogo após o lançamento

O primeiro problema foi resolvido! Agora precisamos resolver o segundo, que é uma configuração no lado do IGameWin.
