# Configurar gateway Gatebox (PIX)

## 1. No painel admin da aplicação

1. Acesse **Admin** → **Gateways** (ou configuração de gateways PIX).
2. Crie um novo gateway ou edite um existente.
3. **Nome:** use exatamente `Gatebox` (ou um nome que contenha "gatebox") para o sistema detectar o provedor.
4. **Tipo:** `pix`.
5. **Credenciais** (JSON):

```json
{
  "username": "93892492000158",
  "password": "sua_senha",
  "api_url": "https://api.gatebox.com.br"
}
```

- **username:** CNPJ ou usuário fornecido pela Gatebox.
- **password:** senha de acesso à API.
- **api_url:** opcional; se não informar, usa `https://api.gatebox.com.br`.

6. Marque o gateway como **Ativo** e salve.

## 2. Webhooks (se a Gatebox enviar notificações)

Configure no painel da Gatebox as URLs de callback (se disponível):

- **Cash-in (depósito):** `https://api.luxbet.site/api/webhooks/gatebox/pix-cashin`
- **Cash-out (saque):** `https://api.luxbet.site/api/webhooks/gatebox/pix-cashout`

Substitua `https://api.luxbet.site` pela URL base da sua API (`WEBHOOK_BASE_URL`).

O webhook espera no body: `externalId` ou `transactionId`, e `status` (ex.: PAID, COMPLETED, CONCLUIDO para aprovação; ERROR, CANCELLED para falha).

## 3. Endpoints utilizados (referência)

Conforme collection Postman e documentação Gatebox:

| Endpoint | Método | Uso |
|----------|--------|-----|
| `/v1/customers/auth/sign-in` | POST | Login: `username`, `password` → `access_token` |
| `/v1/customers/pix/create-immediate-qrcode` | POST | Depósito: `externalId`, `amount`, `document`, `name`, `expire`; opcional: `email`, `phone`, `identification`, `description` |
| `/v1/customers/pix/status` | GET | Status: `transactionId`, `externalId` ou `endToEnd` |
| `/v1/customers/pix/withdraw` | POST | Saque: `externalId`, `key`, `name`, `amount`; opcional: `documentNumber`, `description` |
| `/v1/customers/account/balance` | POST | Saldo da conta |
| `/v1/customers/pix/pix-search` | GET | Validar chave PIX: query `dict=<chave sem pontuação>` |

### Resposta do create-immediate-qrcode (depósito)

A API retorna HTTP 201 com corpo no formato `{ "statusCode": 200, "data": { ... } }`. O código PIX (copia e cola) está em **`data.key`**. Outros campos úteis em `data`: `uuid`, `identifier`, `keyType` (ex.: "QRCODE"), `status` (ex.: "CREATED"), `externalId`, `expire`, `amount`.

O backend desembrulha automaticamente o objeto `data` e usa `key` como código PIX e `uuid`/`identifier` como referência da transação.

## 4. Postman

A collection `GATEBOX API.postman_collection.json` na raiz do projeto pode ser importada para testar a API diretamente. Configure a variável `API_URL` (ex.: `https://api.gatebox.com.br`) e faça Sign-in para obter o token usado nas demais requisições.
