# ✅ Verificação de Configuração IGameWin - Transfer Mode

## 📋 Informações do Painel

Com base na imagem do painel IGameWin, aqui estão as configurações atuais:

### ✅ Configurações Corretas:

1. **API Type:** `TRANSFER MODE` ✅
   - Confirmado! O modo está correto.

2. **Agent Code:** `welisson4916` ✅
   - Este código deve estar configurado no banco de dados.

3. **Token (Agent Key):** `45047e3afb9011f0b8f1bc2411881493` ✅
   - Este token precisa estar configurado no banco de dados como `agent_key`.

4. **Agent Status:** `Active` ✅
   - O agente está ativo.

5. **Language Games:** `BRL - Portuguese` ✅
   - Idioma configurado corretamente.

6. **Currency:** `BRL - Brazil Real (R$)` ✅
   - Moeda configurada corretamente.

---

## ⚠️ Configurações que Precisam de Atenção:

### 1. IPv4 Whitelist for API

**Valor atual:** `147.93.147.33`

**Status:** ✅ **Este IP está correto!**  
Este é o IP do servidor Coolify conforme documentação do projeto.

**Ação necessária:**
- ✅ Este IP está correto e deve funcionar
- ✅ Se ainda assim houver problemas de autenticação, verifique se o backend está realmente rodando neste IP
- ✅ Para confirmar o IP do servidor, você pode verificar no painel do Coolify em **Settings** → **Servers**

**Como atualizar:**
1. No painel IGameWin, vá em **Profile**
2. Localize o campo **"IPv4 Whitelist for API"**
3. Atualize com o IP correto do seu servidor
4. Clique em **"Change"** para salvar

---

### 2. IPv6 Whitelist for API

**Valor atual:** `welisson4916` ⚠️ **INCORRETO**

**Problema:** O campo contém o Agent Code ao invés de um endereço IPv6.

**Ação necessária:**
- Se você **não usa IPv6**, deixe o campo **vazio**
- Se você **usa IPv6**, adicione o endereço IPv6 correto do seu servidor
- **Remova** o valor `welisson4916` deste campo

**Como corrigir:**
1. No painel IGameWin, vá em **Profile**
2. Localize o campo **"IPv6 Whitelist for API"**
3. **Deixe vazio** (se não usar IPv6) ou adicione o IPv6 correto
4. Clique em **"Change"** para salvar

---

### 3. Domínios Permitidos (CORS) - NÃO VISÍVEL NESTA PÁGINA

**Problema:** Não vemos campos para "Domínios permitidos" ou "Allowed domains" na página Profile.

**Onde procurar:**
1. **"Configuration Website"** (no menu lateral)
   - Esta seção pode ter configurações relacionadas a domínios permitidos
2. **Outras seções do painel**
   - Procure por campos como:
     - "Allowed Domains"
     - "Site Domains"
     - "Whitelist Domains"
     - "CORS Settings"

**Domínios que precisam ser permitidos:**
```
luxbet.site
www.luxbet.site
api.luxbet.site
```

---

## 🔧 Verificar Configuração no Banco de Dados

### Verificar se o Agent Key está configurado:

Execute no backend:

```python
# Via API Admin
GET /api/admin/igamewin-agents

# Deve retornar:
{
  "id": 1,
  "agent_code": "welisson4916",
  "agent_key": "45047e3afb9011f0b8f1bc2411881493",  # ← Deve ser este token
  "api_url": "https://api.igamewin.com",
  "is_active": true
}
```

### Se não estiver configurado:

1. **Via Admin Panel:**
   - Acesse `/admin`
   - Vá em **Gateways** → **IGameWin**
   - Configure:
     - Agent Code: `welisson4916`
     - Agent Key: `45047e3afb9011f0b8f1bc2411881493`
     - API URL: `https://api.igamewin.com`
     - Is Active: `true`

2. **Via API:**
   ```bash
   POST /api/admin/igamewin-agents
   {
     "agent_code": "welisson4916",
     "agent_key": "45047e3afb9011f0b8f1bc2411881493",
     "api_url": "https://api.igamewin.com",
     "is_active": true
   }
   ```

---

## 📋 Checklist Completo

### No Painel IGameWin:

- [x] **API Type:** `TRANSFER MODE` ✅
- [x] **Agent Code:** `welisson4916` ✅
- [x] **Token:** `45047e3afb9011f0b8f1bc2411881493` ✅
- [x] **Agent Status:** `Active` ✅
- [ ] **IPv4 Whitelist:** Verificar se `147.93.147.33` é o IP correto do servidor
- [ ] **IPv6 Whitelist:** Remover `welisson4916` e deixar vazio (ou adicionar IPv6 correto)
- [ ] **Domínios Permitidos:** Procurar em "Configuration Website" e adicionar `luxbet.site`, `www.luxbet.site`, `api.luxbet.site`

### No Banco de Dados (Backend):

- [ ] **Agent Code:** `welisson4916` configurado
- [ ] **Agent Key:** `45047e3afb9011f0b8f1bc2411881493` configurado
- [ ] **API URL:** `https://api.igamewin.com` configurado
- [ ] **Is Active:** `true`

---

## 🔍 Próximos Passos

### 1. Verificar IP do Servidor

```bash
# Execute no servidor onde o backend está rodando
curl ifconfig.me
```

**Se o IP retornado for diferente de `147.93.147.33`:**
- Atualize o campo "IPv4 Whitelist for API" no painel IGameWin

### 2. Corrigir IPv6 Whitelist

- Remova `welisson4916` do campo IPv6
- Deixe vazio (se não usar IPv6)

### 3. Procurar Configuração de Domínios Permitidos

- Acesse **"Configuration Website"** no menu lateral
- Procure por campos relacionados a domínios permitidos
- Adicione: `luxbet.site`, `www.luxbet.site`, `api.luxbet.site`

### 4. Verificar Configuração no Backend

- Acesse `/admin` → **Gateways** → **IGameWin**
- Verifique se todas as credenciais estão corretas
- Se não estiverem, configure usando os valores do painel IGameWin

---

## 🧪 Testar Após Configurações

### Teste 1: Verificar Agente no Backend

```bash
curl -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  https://api.luxbet.site/api/admin/igamewin-agents
```

### Teste 2: Verificar Saldo do Agente

```bash
curl -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  https://api.luxbet.site/api/admin/igamewin/agent-balance
```

**Deve retornar:** `{"balance": 7000.00}` (ou o saldo atual)

### Teste 3: Iniciar um Jogo

1. Faça login no site
2. Tente iniciar um jogo (ex: Aviator)
3. Verifique se não há erros de CORS no console (F12)

---

## 💡 Notas Importantes

1. **Transfer Mode:** Como está configurado, o saldo é gerenciado pelo IGameWin. Nosso backend faz `user_deposit` e `user_withdraw` para transferir saldo.

2. **IPv4 Whitelist:** Se o IP estiver incorreto, todas as chamadas da API serão bloqueadas pelo IGameWin.

3. **IPv6 Whitelist:** O valor incorreto (`welisson4916`) pode causar problemas se você usar IPv6. Deixe vazio se não usar.

4. **CORS:** Os erros de CORS precisam ser resolvidos adicionando domínios permitidos no painel IGameWin (provavelmente em "Configuration Website").

---

## 📞 Se Precisar de Ajuda

Se não encontrar os campos para domínios permitidos:

1. **Contate o suporte do IGameWin**
2. **Informe:**
   - Agent Code: `welisson4916`
   - Problema: Erros de CORS ao carregar recursos do jogo
   - Domínios que precisam ser permitidos: `luxbet.site`, `www.luxbet.site`, `api.luxbet.site`
   - Erro específico: `Access to XMLHttpRequest blocked by CORS policy`
