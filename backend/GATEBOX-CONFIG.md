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

O webhook espera no body (exemplo): `externalId` ou `transactionId`, e `status` (ex.: PAID, COMPLETED, CONCLUIDO para aprovação; ERROR, CANCELLED para falha).

## 3. Endpoints utilizados (referência)

- **Auth:** `POST /v1/customers/auth/sign-in`
- **Depósito PIX:** `POST /v1/customers/pix/create-immediate-qrcode`
- **Saque PIX:** `POST /v1/customers/pix/withdraw`
- **Status:** `GET /v1/customers/pix/status?externalId=...`
- **Saldo:** `POST /v1/customers/account/balance`

A collection Postman `GATEBOX API.postman_collection.json` na raiz do projeto pode ser importada para testar a API diretamente.
