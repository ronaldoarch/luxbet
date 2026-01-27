# 🔧 Configuração do IGameWin - Painel Administrativo

## ⚠️ Importante

As configurações abaixo devem ser feitas no **painel administrativo do IGameWin** (não no nosso sistema). Essas configurações são essenciais para que as URLs dos jogos funcionem corretamente.

---

## 📋 Configurações Necessárias

### 1. **Lista de Permissões IPv4 para API**

**Campo:** `Lista de permissões IPv4 para API - Vários IPs separados por ';'`

**O que configurar:**
- Adicione o **IP do seu servidor backend** que faz as chamadas à API do IGameWin
- Se você tem múltiplos IPs, separe-os com ponto e vírgula (`;`)

**Como descobrir o IP do servidor:**
- Se estiver usando Coolify: vá em **Settings** → **Servers** e veja o IP do servidor
- Se estiver usando outro provedor: consulte a documentação ou painel do provedor
- Exemplo de IP: `147.93.147.33`

**Formato correto:**
```
147.93.147.33
```

**Múltiplos IPs (separados por `;`):**
```
147.93.147.33;192.168.1.1;10.0.0.1
```

---

### 2. **Lista de Permissões IPv6 para API**

**Campo:** `Lista de permissões IPv6 para API - Vários IPs separados por ';'`

**⚠️ ERRO COMUM:** Não coloque texto como "Midaslabs" neste campo. Ele aceita apenas endereços IPv6 válidos.

**O que fazer:**
- Se você **não usa IPv6**, deixe este campo **VAZIO**
- Se você usa IPv6, adicione apenas endereços IPv6 válidos no formato correto

**Formato IPv6 correto:**
```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

**Se não usar IPv6:**
```
(deixe vazio)
```

---

### 3. **Jogos de Linguagem**

**Campo:** `Jogos de linguagem`

**Recomendação:**
- Selecione: **BRL - Português** (ou a linguagem desejada)
- Isso afeta a linguagem dos jogos retornados pela API

---

### 4. **Moeda**

**Campo:** `Moeda`

**Recomendação:**
- Selecione: **BRL - Real brasileiro (R$)** (ou a moeda desejada)
- Isso afeta a moeda usada nas transações dos jogos

---

### 5. **Tipo de API**

**Campo:** `Tipo de API`

**Recomendação:**
- Selecione: **Modo de transferência** (já está selecionado na imagem)
- Este modo permite que o sistema gerencie transferências de saldo automaticamente

---

### 6. **Senha (se necessário)**

**Campos:** `Senha atual`, `Nova Senha`, `Confirme sua senha`

**Quando configurar:**
- Apenas se você quiser alterar a senha do painel administrativo
- Se não quiser alterar, deixe os campos vazios

**⚠️ Se aparecer erro:** "O novo campo de senha é obrigatório"
- Deixe os campos vazios se não quiser alterar a senha
- Ou preencha todos os três campos se quiser alterar

---

## 🔍 Por que essas configurações são importantes?

### **Permissões de IP (IPv4/IPv6):**
- Se o IP do seu servidor **não estiver na lista**, a API do IGameWin pode **bloquear todas as requisições**
- Isso causaria erros ao tentar:
  - Listar jogos
  - Iniciar jogos
  - Criar usuários
  - Consultar saldos
  - Fazer transferências

### **Linguagem e Moeda:**
- Afetam as URLs retornadas pelos jogos
- Garantem que os jogos sejam exibidos no idioma e moeda corretos

---

## ✅ Checklist de Configuração

- [ ] **IPv4:** Adicionei o IP do servidor backend na lista de permissões IPv4
- [ ] **IPv6:** Deixei vazio (se não usar) ou adicionei IPs IPv6 válidos
- [ ] **Linguagem:** Configurei para "BRL - Português" (ou idioma desejado)
- [ ] **Moeda:** Configurei para "BRL - Real brasileiro" (ou moeda desejada)
- [ ] **Tipo de API:** Está como "Modo de transferência"
- [ ] **Senha:** Deixei vazia (se não quiser alterar) ou preenchi todos os campos

---

## 🚨 Erros Comuns e Soluções

### Erro: "O formato do endereço IPv6 é inválido"
**Causa:** Texto como "Midaslabs" foi colocado no campo IPv6
**Solução:** Deixe o campo IPv6 vazio ou adicione apenas endereços IPv6 válidos

### Erro: "O novo campo de senha é obrigatório"
**Causa:** Tentou alterar senha mas não preencheu todos os campos
**Solução:** Deixe todos os campos de senha vazios (se não quiser alterar) ou preencha todos os três campos

### URLs dos jogos não funcionam
**Possíveis causas:**
1. IP do servidor não está na lista de permissões IPv4
2. Linguagem/moeda configuradas incorretamente
3. Credenciais (agent_code/agent_key) incorretas no nosso sistema

**Solução:**
1. Verifique se o IP do servidor está na lista de permissões IPv4
2. Verifique as configurações de linguagem e moeda
3. Verifique as credenciais no nosso painel admin (aba IGameWin)

---

## 📞 Suporte

Se após configurar tudo corretamente ainda houver problemas:
1. Verifique os logs do backend para ver erros específicos
2. Entre em contato com o suporte do IGameWin
3. Verifique se as credenciais estão corretas no nosso sistema
