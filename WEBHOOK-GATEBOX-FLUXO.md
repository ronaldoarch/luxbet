# Fluxo de processamento do webhook Gatebox

Este documento descreve como o backend (Python/FastAPI) processa o webhook da Gatebox para depósitos (crédito de saldo) e saques.

**Endpoint:** `POST /api/webhooks/gatebox`  
**Código:** `backend/routes/payments.py` — funções `webhook_gatebox`, `_process_gatebox_cashin`, `_process_gatebox_cashout`, `_process_gatebox_withdrawal_fail`, `_process_gatebox_reversal`.

---

## Recebimento do webhook

### 1. Payload

O body é lido como JSON. A Gatebox pode enviar os campos no **topo** do JSON ou dentro de **`data`**:

```python
data = await request.json()
inner = data.get("data")
if isinstance(inner, dict):
    external_id = data.get("externalId") or inner.get("externalId") or ...
    transaction_id = data.get("transactionId") or inner.get("transactionId") or ...
    gatebox_uuid = data.get("uuid") or inner.get("uuid")
    gatebox_identifier = data.get("identifier") or inner.get("identifier")
else:
    external_id = data.get("externalId") or data.get("external_id")
    # ...
```

### 2. Identificadores usados para buscar depósito/saque

- **external_id** — ex.: `DEP_14_1770913041` (depósito) ou identificador do saque  
- **transaction_id** — ID da transação no gateway  
- **gatebox_uuid** — `uuid` retornado pela Gatebox (ex.: ao criar QR)  
- **gatebox_identifier** — `identifier` do payload  

Se nenhum desses existir, responde `200` com mensagem e não processa.

### 3. Tipo de evento

A função `_gatebox_event_type(data)` devolve um dos:

- `PIX_REVERSAL` — reversão de depósito  
- `PIX_REVERSAL_OUT` — reversão/falha de saque  
- `PIX_REFUND` — estorno (pode ser depósito ou saque)  
- `PIX_PAY_IN` — entrada (depósito)  
- `PIX_PAY_OUT` — saída (saque)  

---

## Ordem de processamento

1. **PIX_REVERSAL** (reversão de depósito) → `_process_gatebox_reversal`  
2. **PIX_REVERSAL_OUT** ou **PIX_REFUND** (falha de saque ou estorno de depósito) → `_process_gatebox_withdrawal_fail` ou `_process_gatebox_reversal`  
3. Depósito pago (cash-in) ou saque confirmado/falha (cash-out) → `_process_gatebox_cashin` ou `_process_gatebox_cashout`  

Reversões são tratadas antes para evitar crédito indevido.

---

## Processamento de depósitos (crédito de saldo)

### Identificação

- Evento de cash-in: tipo **PIX_PAY_IN** ou payload tratado como depósito quando não é reversão e a busca encontra um **Deposit**.

### Busca do depósito

- **Por external_id / transaction_id:**  
  `Deposit` com `external_id` ou `transaction_id` iguais aos extraídos do payload.  
- **Por gatebox_uuid / gatebox_identifier:**  
  Busca em `metadata_json` (e dentro de `gateway_response` / `gatebox_response`) por `gatebox_transaction_id`, `uuid`, `identifier`.  

Função: `_find_deposit_by_external_or_metadata(db, external_id, transaction_id, gatebox_uuid, gatebox_identifier)`.

### Fallbacks quando não acha depósito/saque

1. **Fallback 1 — API de status por uuid/transaction_id**  
   Se não encontrou depósito nem saque e tem `gatebox_uuid` ou `transaction_id`:  
   chama `GateboxAPI.get_pix_status(transaction_id=...)`.  
   Se a resposta trouxer `externalId` / `transactionId` / `uuid`, faz nova busca de depósito e saque com esses valores e processa se achar.

2. **Fallback 2 — Depósitos e saques PENDING por external_id**  
   Se o status do webhook for de sucesso (PAID, COMPLETED, CONCLUIDO, APROVADO, PAID_OUT, SUCCESS) e ainda não tiver depósito nem saque:  
   - **Depósitos:** busca até 10 depósitos **PENDING** com `external_id` preenchido (mais recentes primeiro). Para cada um chama `get_pix_status(external_id=dep.external_id)`. Se a API devolver status de sucesso, considera esse depósito como o pago e processa cash-in.  
   - **Saques:** em seguida, se ainda não tiver saque, busca até 10 saques **PENDING** com `external_id` preenchido. Para cada um chama `get_pix_status(external_id=w.external_id)`. Se a API devolver status de sucesso, considera esse saque e processa cash-out (marca APPROVED).

### Duplicidade

- Se o depósito já está com `status == APPROVED`, o cash-in só atualiza metadata e faz commit; o crédito já foi feito antes (evita duplo crédito).

### Crédito de saldo (`_process_gatebox_cashin`)

O status é lido de `data.status`, `data.statusTransaction` ou `data.data.status`.  
Só credita se o status for um de:  
`PAID`, `COMPLETED`, `CONCLUIDO`, `APROVADO`, `PAID_OUT`, `SUCCESS`.

- Atualiza `deposit.status` para `APPROVED`.  
- Incrementa `user.balance` com `deposit.amount`.  
- Chama `apply_promotion_bonus(db, user, deposit)` (bônus conforme promoções).  
- Chama `update_affiliate_on_deposit_approved(db, user, deposit)` (promotor/afiliado).  
- Cria notificação “Depósito Aprovado!”.  
- Grava `webhook_data` e `webhook_received_at` em `deposit.metadata_json` e faz `db.commit()`.

---

## Processamento de saques

### Identificação

- Evento de cash-out: tipo **PIX_PAY_OUT** (ou lógica de `_gatebox_event_is_cashout`).

### Busca do saque

- Mesma ideia do depósito: por `external_id`, `transaction_id` e por `gatebox_uuid` / `gatebox_identifier` em `metadata_json`.  
- Função: `_find_withdrawal_by_external_or_metadata(...)`.  
- **Na criação do saque (Gatebox):** o sistema envia `external_id` no formato `WTH_{user_id}_{timestamp}` e grava na resposta o `uuid`/`identifier` da Gatebox em `metadata_json` como `gatebox_transaction_id` e em `gateway_response`, para o webhook localizar o saque mesmo quando a Gatebox envia só `uuid`.

### Saque confirmado (`_process_gatebox_cashout`)

- Status do webhook em `COMPLETED`, `SUCCESS`, `PAID_OUT`, `APROVADO`:  
  atualiza `withdrawal.status` para `APPROVED` (o saldo já foi debitado na solicitação do saque).  
- Atualiza metadata e faz commit.

### Saque falhou (reversão de saque)

- Status do webhook em:  
  `ERROR`, `CANCELLED`, `REJECTED`, `FAILED`, `REVERSED`, `REVERSAL`, `ESTORNO`, `CANCELADO`, `FALHA`, `REFUNDED`.  
- Ou evento **PIX_REVERSAL_OUT** / **PIX_REFUND** (quando a busca retorna um Withdrawal).  
- Chama `_process_gatebox_withdrawal_fail`:  
  - Se o saque ainda não está `REJECTED`, devolve o valor: `user.balance += withdrawal.amount`.  
  - Marca `withdrawal.status = REJECTED`.  
  - Cria notificação “Saque não realizado” / valor devolvido.  
  - Grava metadata e faz commit.

---

## Reversão de depósito (estorno)

- Evento **PIX_REVERSAL** ou **PIX_REFUND** quando a busca retorna um **Deposit**.  
- `_process_gatebox_reversal`:  
  - Só debita se `deposit.status == APPROVED`.  
  - Debita `min(deposit.amount, user.balance)` de `user.balance` (nunca deixa saldo negativo).  
  - Marca `deposit.status = REJECTED`.  
  - Cria notificação “Depósito revertido”.  
  - Grava metadata e faz commit.

---

## Respostas e erros

- Sem identificadores: `200` + `{"status": "received", "message": "externalId/transactionId/uuid/identifier não encontrado"}`.  
- Reversão/estorno sem encontrar registro: `200` + mensagem “Depósito não encontrado para reversão” ou “Transação não encontrada para reversão/estorno”.  
- Nenhum depósito/saque encontrado (incluindo fallbacks): `200` + `{"status": "received", "message": "Transação não encontrada (depósito ou saque)"}`.  
- Exceção não tratada: log da exceção e retorno `{"status": "error", "message": str(e)}`.  

Sempre se responde 200 quando o payload foi recebido, para evitar retentativas desnecessárias pela Gatebox.

---

## Segurança e boas práticas

- **Idempotência:** Verificação de `deposit.status == APPROVED` / `withdrawal.status != REJECTED` antes de creditar/debitar.  
- **Transações:** Uso de `db.commit()` após alterações consistentes.  
- **Auditoria:** Payload e data do webhook gravados em `metadata_json` do Deposit/Withdrawal.  
- **Logs:** `[Webhook Gatebox]` com payload resumido, fallbacks e crédito/devolução.

---

## Exemplo de payloads (referência)

**Depósito pago (ex.):**

```json
{
  "type": "PIX_PAY_IN",
  "status": "COMPLETED",
  "externalId": "DEP_14_1770913041",
  "transactionId": "0067ac98-eed3-458d-96eb-3a40c4df8d3a",
  "uuid": "0067ac98-eed3-458d-96eb-3a40c4df8d3a"
}
```

**Saque confirmado (ex.):**

```json
{
  "type": "PIX_PAY_OUT",
  "status": "COMPLETED",
  "externalId": "WTH_14_...",
  "uuid": "..."
}
```

**Saque falhou / reversão:**

```json
{
  "type": "PIX_REVERSAL_OUT",
  "status": "FAILED",
  "externalId": "...",
  "reason": "Chave PIX inválida"
}
```

---

## Como o sistema prepara depósito e saque para o webhook

- **Depósito (PIX):** ao gerar o QR, o backend envia à Gatebox um `external_id` no formato `DEP_{user_id}_{timestamp}` e guarda na tabela `deposits` esse valor em `external_id` e a resposta completa (incl. `uuid`/`identifier`) em `metadata_json` (`gateway_response` / `gatebox_transaction_id`). O saldo **só é creditado** quando o webhook confirma o pagamento.  
- **Saque (PIX):** ao solicitar o saque, o backend envia `external_id` no formato `WTH_{user_id}_{timestamp}` e **debita o saldo na hora**. Na resposta da Gatebox guarda `external_id` e `gatebox_transaction_id` (uuid/identifier) em `withdrawals.metadata_json`. O webhook usa isso para: (1) marcar saque como APPROVED quando o PIX é pago; (2) devolver o valor ao usuário se o saque falhar (PIX_REVERSAL_OUT / status de falha).

Assim, o webhook credita corretamente em depósitos e mantém consistência em saques (sucesso = APPROVED; falha = devolução de saldo).

---

## Monitoramento

- Logs do servidor: `[Webhook Gatebox] Payload: ...`, `Fallback: ...`, `Creditando saldo: ...`, `Fallback 2: depósito encontrado por external_id=...`, `Fallback 2: saque encontrado por external_id=...`.  
- Verificar na aplicação se o saldo do usuário foi creditado/debitado após o webhook e se as notificações foram criadas.
