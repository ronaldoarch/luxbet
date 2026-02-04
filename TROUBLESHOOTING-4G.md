# 🔧 Troubleshooting - Plataforma não abre no 4G

## 🚨 Problema

A plataforma não está abrindo ou funcionando quando acessada via rede 4G (dados móveis).

---

## 🔍 Causas Comuns

### 1. **Variável de Ambiente Não Configurada** ⚠️ MAIS COMUM

**Problema**: O frontend está tentando usar `http://localhost:8000` porque `VITE_API_URL` não está configurada.

**Sintomas**:
- Site carrega mas nada funciona
- Erros no console: `Failed to fetch` ou `NetworkError`
- Requisições para `localhost:8000` falhando

**Solução**:
1. Acesse o Coolify
2. Vá na aplicação do **Frontend**
3. Clique em **Environment Variables**
4. Adicione:
   ```env
   VITE_API_URL=https://sua-url-do-backend.com
   ```
   **Exemplo**:
   ```env
   VITE_API_URL=https://api.luxbet.site
   ```
5. **Faça REDEPLOY** (importante!)

---

### 2. **URL do Backend Incorreta**

**Problema**: A URL do backend está errada ou não está acessível.

**Verificação**:
1. Teste a URL do backend no navegador:
   ```
   https://api.luxbet.site/api/health
   ```
   Deve retornar: `{"status": "healthy"}`

2. Teste no 4G:
   - Abra o navegador no celular (4G)
   - Acesse: `https://api.luxbet.site/api/health`
   - Se não funcionar, o problema é DNS ou rede

**Solução**:
- Verifique se o DNS está configurado corretamente
- Verifique se o certificado SSL está válido
- Teste com IP direto se possível

---

### 3. **Problema de CORS**

**Problema**: O backend está bloqueando requisições do frontend.

**Verificação**:
- Abra o console do navegador (F12)
- Veja se há erros de CORS
- Erro típico: `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Solução**:
O backend já está configurado para permitir todas as origens (`allow_origins=["*"]`), mas verifique:
1. Acesse `backend/main.py`
2. Confirme que está assim:
   ```python
   allow_origins=["*"],  # Temporarily allow all for debugging
   ```

---

### 4. **Problema de DNS**

**Problema**: O DNS não está resolvendo corretamente no 4G.

**Verificação**:
1. No celular (4G), abra o navegador
2. Tente acessar: `https://api.luxbet.site`
3. Se não carregar, pode ser problema de DNS

**Solução**:
- Verifique configuração DNS no provedor
- Use DNS público (8.8.8.8 ou 1.1.1.1)
- Aguarde propagação DNS (pode levar até 48h)

---

### 5. **Certificado SSL Inválido**

**Problema**: Certificado SSL expirado ou inválido.

**Verificação**:
- No navegador, veja se há aviso de certificado
- Clique no cadeado ao lado da URL
- Verifique se o certificado é válido

**Solução**:
- Renove o certificado SSL no Coolify
- Configure Let's Encrypt automaticamente

---

### 6. **Cache do Navegador**

**Problema**: Navegador está usando versão antiga em cache.

**Solução**:
1. Limpe o cache do navegador
2. Ou use modo anônimo/privado
3. Ou force refresh: `Ctrl+Shift+R` (Windows) / `Cmd+Shift+R` (Mac)

---

## 🔧 Solução Rápida

### Passo 1: Verificar Variável de Ambiente

No Coolify → Frontend → Environment Variables:

```env
VITE_API_URL=https://api.luxbet.site
```

**⚠️ IMPORTANTE**: 
- Use `https://` (não `http://`)
- Não coloque barra (`/`) no final
- Faça **REDEPLOY** após alterar

### Passo 2: Verificar Build

Após o redeploy, verifique se o build incluiu a variável:

1. Acesse o frontend
2. Abra o console (F12)
3. Digite:
   ```javascript
   console.log(import.meta.env.VITE_API_URL)
   ```
4. Deve mostrar a URL do backend (não `undefined`)

### Passo 3: Testar no 4G

1. Desative WiFi no celular
2. Use apenas dados móveis (4G)
3. Acesse o site
4. Abra o console (F12 no Chrome mobile ou use ferramentas de desenvolvedor)
5. Verifique erros

---

## 🐛 Debug no Console

### Verificar URL da API

No console do navegador, execute:

```javascript
// Verificar variável de ambiente
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);

// Testar conexão com backend
fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/health`)
  .then(r => r.json())
  .then(d => console.log('Backend OK:', d))
  .catch(e => console.error('Backend ERRO:', e));
```

### Erros Comuns

**Erro**: `Failed to fetch`
- **Causa**: Backend não acessível ou URL errada
- **Solução**: Verifique `VITE_API_URL`

**Erro**: `NetworkError`
- **Causa**: Problema de rede ou CORS
- **Solução**: Verifique CORS no backend

**Erro**: `localhost:8000`
- **Causa**: `VITE_API_URL` não configurada
- **Solução**: Configure variável e faça redeploy

---

## ✅ Checklist Completo

- [ ] `VITE_API_URL` configurada no Coolify (Frontend)
- [ ] URL usa `https://` (não `http://`)
- [ ] URL não tem barra no final
- [ ] Redeploy feito após alterar variável
- [ ] Backend acessível via `https://api.luxbet.site/api/health`
- [ ] Backend acessível no 4G (teste no celular)
- [ ] Certificado SSL válido
- [ ] DNS configurado corretamente
- [ ] CORS configurado no backend (`allow_origins=["*"]`)
- [ ] Cache do navegador limpo

---

## 📞 Próximos Passos

Se ainda não funcionar:

1. **Verifique logs do Coolify**:
   - Frontend → Logs
   - Backend → Logs
   - Procure por erros

2. **Teste endpoints diretamente**:
   ```bash
   # No celular (4G), abra no navegador:
   https://api.luxbet.site/api/health
   https://api.luxbet.site/api/public/games
   ```

3. **Verifique firewall**:
   - Backend pode estar bloqueando IPs móveis
   - Verifique configurações de firewall no Coolify

4. **Teste com IP direto** (se disponível):
   - Use IP do servidor em vez de domínio
   - Isso ajuda a identificar se é problema de DNS

---

## 🔄 Melhorias Futuras

Para evitar esse problema no futuro:

1. **Remover fallback para localhost** em produção
2. **Adicionar validação** de `VITE_API_URL` no build
3. **Mostrar erro amigável** se API não estiver configurada
4. **Adicionar health check** no frontend
