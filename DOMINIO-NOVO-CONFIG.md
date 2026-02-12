# 🔄 Configurar Novo Domínio (ex: luxbets.com.br)

Quando você troca de domínio (ex: de `luxbet.site` para `luxbets.com.br`), **o saldo não será descontado** durante o jogo até que você atualize as configurações abaixo.

---

## ⚠️ Passo obrigatório: IGameWin "Ponto final do site"

O IGameWin chama nosso endpoint `/gold_api` para buscar saldo e processar apostas. Ele usa a URL configurada no painel.

### O que fazer

1. **Acesse** o painel administrativo do IGameWin
2. **Vá em** "Agente de atualização" ou "Agent Update"
3. **Localize** o campo **"Ponto final do site"** (Site Endpoint)
4. **Atualize** para a URL do seu novo backend:
   - Antes: `https://api.luxbet.site`
   - Depois: `https://api.luxbets.com.br` (ou `https://api.seudominio.com.br` se usar subdomínio)
5. **Salve** e aguarde 2–5 minutos

### Exemplo

| Domínio novo | URL do backend | Valor em "Ponto final do site" |
|--------------|----------------|--------------------------------|
| luxbets.com.br | api.luxbets.com.br | `https://api.luxbets.com.br` |
| luxbets.com.br | Mesmo domínio | `https://luxbets.com.br` |

⚠️ **Não inclua** `/gold_api` no final. O IGameWin adiciona automaticamente.

---

## Variáveis de ambiente no servidor

No Coolify (ou onde o backend estiver rodando), configure:

```
WEBHOOK_BASE_URL=https://api.luxbets.com.br
```

(Ou a URL real do seu backend.)

Isso afeta webhooks de pagamento (Gatebox, SuitPay, etc.) e mensagens de erro.

---

## Testar se está funcionando

1. Inicie um jogo
2. Verifique os logs do backend – deve aparecer algo como:
   ```
   [Gold API] ⚡⚡⚡ CHAMADA RECEBIDA NO /gold_api ⚡⚡⚡
   [Gold API] Método: user_balance
   [Gold API] Método: transaction
   ```
3. Faça uma aposta – o saldo deve ser descontado normalmente

---

## Resumo

- [ ] Atualizar "Ponto final do site" no painel IGameWin
- [ ] Configurar `WEBHOOK_BASE_URL` no servidor
- [ ] Aguardar 2–5 minutos
- [ ] Testar um jogo e conferir se o saldo é descontado
