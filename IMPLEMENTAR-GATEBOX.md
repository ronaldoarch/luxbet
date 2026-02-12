# 🚀 Como Implementar o Gatebox - Guia Completo

Este guia passo a passo mostra como configurar e implementar o gateway Gatebox na aplicação (backend FastAPI).

---

## 📋 Pré-requisitos

1. **Credenciais da Gatebox**
   - Username (geralmente CNPJ): `93892492000158`
   - Password: `@Homolog1` (ou a senha fornecida)
   - Acesso ao painel administrativo da Gatebox

2. **Acesso ao Admin da Aplicação**
   - Conta de administrador configurada
   - Acesso à rota `/api/admin/gateways` (via frontend admin ou API)

3. **Informações do Servidor**
   - IP de saída do servidor (para whitelist)
   - URL pública da API (para webhook) — ex.: `https://api.luxbet.site`

---

## 🔧 Passo 1: Configurar no Painel Admin

### Opção A: Via API Admin (Recomendado)

1. **Acesse o painel admin** (frontend) ou use a API:
   ```
   GET  https://seu-dominio.com/api/admin/gateways
   POST https://seu-dominio.com/api/admin/gateways
   ```
   (Com autenticação Bearer de admin.)

2. **Crie ou edite o gateway:**
   - **Nome**: `Gatebox` (ou qualquer nome que contenha "gatebox")
   - **Tipo**: `pix` (gateway PIX)
   - **Ativo**: `true`
   - **Credenciais** (JSON):
   ```json
   {
     "username": "93892492000158",
     "password": "@Homolog1",
     "api_url": "https://api.gatebox.com.br"
   }
   ```

3. **Salve a configuração**

### Opção B: Via Variáveis de Ambiente (Alternativa)

Se preferir usar variáveis de ambiente ao invés do painel admin, o backend pode ser estendido para ler `GATEBOX_USERNAME`, `GATEBOX_PASSWORD`, `GATEBOX_BASE_URL`. **Atualmente a configuração via Admin (tabela `gateways`) tem prioridade.**

**Nota:** A configuração via Admin (banco de dados) é a usada pelo código atual.

---

## 🌐 Passo 2: Configurar Webhook no Painel Gatebox

O webhook é **obrigatório** para depósitos e saques serem processados automaticamente. A Gatebox usa **uma única URL** para todos os eventos.

1. **Acesse o painel administrativo da Gatebox**

2. **Configure a URL do webhook (uma para todos os eventos):**
   ```
   https://sua-api.com/api/webhooks/gatebox
   ```
   Exemplo com domínio:
   ```
   https://api.luxbet.site/api/webhooks/gatebox
   ```

3. **Salve a configuração no painel Gatebox**

O sistema identifica se o evento é depósito (cash-in) ou saque (cash-out) pelo payload (`type`/`event`/`transactionType`) ou pelo `externalId` (busca em depósitos e saques).

**⚠️ Importante:**
- O webhook deve ser acessível publicamente (sem autenticação)
- Use HTTPS (não HTTP)
- A variável `WEBHOOK_BASE_URL` no servidor deve apontar para a URL pública da API (ex.: `https://api.luxbet.site`)

---

## 🔒 Passo 3: Configurar Whitelist de IP (Obrigatório para Saques)

A Gatebox valida o **IP do servidor** que faz as requisições. Você precisa adicionar esse IP na whitelist.

### Como descobrir o IP do servidor

**Método 1: Via API Admin**
```bash
GET /api/admin/gatebox/ip
# Requer autenticação admin (Bearer token)
# Resposta: { "ip": "x.x.x.x", "message": "..." }
```

**Método 2: Diagnóstico completo**
```bash
GET /api/admin/gatebox/diagnostico
# Requer autenticação admin
# Retorna: outbound_ip, gatebox_config, auth_ok, webhook_urls
```

**Método 3: Via terminal no servidor**
```bash
curl https://api.ipify.org
```

### Adicionar IP na Whitelist

1. **Acesse o painel administrativo da Gatebox**
2. **Vá em "Configurações" → "Whitelist de IP"**
3. **Adicione o IP retornado por `/api/admin/gatebox/ip` ou pelo diagnóstico**
4. **Salve**

**⚠️ Problemas comuns:**
- Se o servidor tiver múltiplos IPs (IPv4 e IPv6), adicione **todos**
- Se ainda der erro 403 após adicionar, use o diagnóstico e confira qual IP a Gatebox está vendo
- Contate o suporte da Gatebox se necessário: *"Qual IP de origem vocês registram quando a requisição ao endpoint POST /v1/customers/pix/withdraw retorna 403?"*

---

## ✅ Passo 4: Testar a Configuração

### Teste 1: Verificar configuração

- `GET /api/admin/gateways` — listar gateways; verifique se o Gatebox está ativo.

### Teste 2: Testar autenticação e IP

- `GET /api/admin/gatebox/diagnostico` — retorna:
  - `outbound_ip`: IP para whitelist
  - `gatebox_config`: gateway configurado (sem senha)
  - `auth_ok`: se o sign-in na Gatebox funcionou
  - `webhook_urls`: URLs que devem ser configuradas no painel Gatebox

### Teste 3: Criar depósito de teste

1. Como **usuário** (frontend), acesse a página de depósito.
2. Selecione **PIX** (o sistema usa o gateway PIX ativo; se for Gatebox, usará automaticamente).
3. Informe um valor (ex.: R$ 10,00) e confirme.
4. Verifique se o **QR Code PIX** é gerado.

**Endpoint usado pelo frontend:**
```http
POST /api/public/payments/deposit/pix
Content-Type: application/json
Authorization: Bearer <token_do_usuario>

{
  "amount": 10.00,
  "payer_name": "Nome",
  "payer_tax_id": "12345678901",
  "payer_email": "email@exemplo.com",
  "payer_phone": "+5511999999999"
}
```

### Teste 4: Verificar webhook

1. **Pague o PIX** gerado (ou simule o pagamento).
2. **Verifique os logs** do servidor para ver se o webhook foi recebido em `POST /api/webhooks/gatebox`.
3. **Confirme** que o saldo foi creditado automaticamente.

---

## 🔍 Verificação de Problemas

### Problema: "IP não autorizado" ao fazer saque

**Solução:**
1. Chame `GET /api/admin/gatebox/diagnostico` e use o `outbound_ip`.
2. Adicione **todos** os IPs (IPv4 e IPv6, se houver) na whitelist da Gatebox.
3. Contate o suporte da Gatebox para confirmar qual IP eles veem nas requisições.

### Problema: Webhook não está chegando

**Solução:**
1. Verifique se a URL no painel Gatebox está exatamente como a retornada em `GET /api/admin/gatebox/diagnostico` (campo `webhook_url`).
2. Verifique se a URL é acessível publicamente:
   ```bash
   curl -X POST https://sua-api.com/api/webhooks/gatebox -H "Content-Type: application/json" -d '{}'
   ```
   (Deve retornar 200 ou corpo com status, não timeout.)
3. Configure um cron como fallback (se existir endpoint de verificação de depósitos pendentes).

### Problema: Erro 401 - Não autenticado

**Solução:**
1. Verifique username e password nas credenciais do gateway (Admin).
2. Verifique se o gateway está **ativo**.
3. O sistema renova o token automaticamente em caso de erro; confira os logs para mensagens `[Gatebox]`.

### Problema: Erro 502 ao gerar PIX

**Solução:**
1. Confirme que a resposta do sign-in da Gatebox inclui `access_token` no corpo (formato: `{ "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }`).
2. Verifique se a URL base está correta (`https://api.gatebox.com.br`).
3. Verifique se o serviço Gatebox está online e se não há firewall bloqueando a saída do servidor.

---

## 📚 Estrutura no Projeto (FastAPI)

A implementação do Gatebox está organizada assim:

```
backend/
  ├── gatebox_api.py              # Cliente da API Gatebox (auth, PIX, saldo, saque)
  ├── main.py                     # App FastAPI, rotas, CORS
  └── routes/
      ├── payments.py             # Depósito PIX, saque PIX, webhooks Gatebox
      └── admin.py                # CRUD gateways, GET /api/admin/gatebox/ip e /diagnostico

Rotas principais:
  POST /api/public/payments/deposit/pix    # Criar depósito PIX (usa Gatebox se for o gateway ativo)
  POST /api/public/payments/withdrawal/pix # Saque PIX (usa Gatebox se ativo)
  POST /api/webhooks/gatebox               # Webhook único para todos os eventos (depósito e saque)
  GET  /api/admin/gateways                 # Listar/CRUD gateways
  GET  /api/admin/gatebox/ip                # IP para whitelist
  GET  /api/admin/gatebox/diagnostico       # IP + config + teste de auth + URLs webhook
```

---

## 🔄 Fluxo de Funcionamento

### Depósito (Cash-In)

1. Usuário solicita depósito → `POST /api/public/payments/deposit/pix`
2. Sistema cria transação pendente no banco
3. Sistema autentica na Gatebox → `POST /v1/customers/auth/sign-in`
4. Sistema gera QR Code PIX → `POST /v1/customers/pix/create-immediate-qrcode`
5. Usuário paga o PIX
6. Gatebox envia webhook → `POST /api/webhooks/gatebox`
7. Sistema processa depósito e credita saldo
8. Bônus é aplicado conforme promoções ativas

### Saque (Cash-Out)

1. Usuário solicita saque → `POST /api/public/payments/withdrawal/pix`
2. Sistema valida saldo e cria registro de saque
3. Sistema autentica na Gatebox → `POST /v1/customers/auth/sign-in`
4. Sistema realiza saque → `POST /v1/customers/pix/withdraw`
5. Gatebox processa o PIX
6. Gatebox envia webhook → `POST /api/webhooks/gatebox`
7. Sistema atualiza status do saque (aprovado/rejeitado)

---

## 📝 Exemplo de Uso via API

### Criar depósito

```bash
curl -X POST "https://sua-api.com/api/public/payments/deposit/pix" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token_usuario>" \
  -d '{
    "amount": 100.00,
    "payer_name": "Nome",
    "payer_tax_id": "12345678901",
    "payer_email": "email@exemplo.com",
    "payer_phone": "+5511999999999"
  }'
```

Resposta esperada (exemplo): `qr_code`, `qr_code_text`, `transaction_id`, `gatebox_transaction_id` (se aplicável).

### Realizar saque

```bash
curl -X POST "https://sua-api.com/api/public/payments/withdrawal/pix" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token_usuario>" \
  -d '{
    "amount": 50.00,
    "pix_key": "+5514999999999",
    "pix_key_type": "phone"
  }'
```

(Consulte o schema exato em `payments.py` para `pix_key` / `pix_key_type`.)

---

## 🔐 Segurança

1. **Credenciais** do gateway são armazenadas no banco (campo `credentials`, JSON).
2. **Tokens** Gatebox são cacheados em memória e renovados automaticamente (~1h).
3. **Webhooks** não usam autenticação por token (a Gatebox envia apenas o payload JSON); a validação é por payload e por externalId/transactionId.
4. **IP** é validado pela Gatebox para saques (whitelist no painel deles).

---

## ✅ Checklist Final

- [ ] Credenciais configuradas em Admin → Gateways (gateway PIX com nome contendo "Gatebox")
- [ ] Gateway marcado como **ativo**
- [ ] Webhook configurado no painel Gatebox (uma URL para todos os eventos): `{WEBHOOK_BASE_URL}/api/webhooks/gatebox`
- [ ] IP do servidor adicionado na whitelist da Gatebox (use `GET /api/admin/gatebox/ip`)
- [ ] Teste de depósito funcionando (QR Code gerado)
- [ ] Teste de saque funcionando (se aplicável)
- [ ] Webhooks recebendo notificações (verificar logs)

---

**Pronto!** O Gatebox está implementado e configurado. 🎉
