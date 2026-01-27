# 🔧 Corrigir: Agente IGameWin Sumindo Após Deploy

## ⚠️ PROBLEMA CRÍTICO ENCONTRADO

Na imagem que você enviou, a variável de ambiente está como:
```
DATABASE_UR
```

Mas o código procura por:
```
DATABASE_URL
```

**Isso faz com que o sistema use SQLite por padrão, perdendo todos os dados!**

---

## ✅ SOLUÇÃO IMEDIATA

### Passo 1: Corrigir Nome da Variável

1. No Coolify, vá em **Backend** → **Environment Variables**
2. Procure por `DATABASE_UR` (sem o "L")
3. **Edite** e renomeie para `DATABASE_URL` (com "L" no final)
4. Ou **Delete** `DATABASE_UR` e crie uma nova `DATABASE_URL`

### Passo 2: Configurar Valor Correto

A variável `DATABASE_URL` deve ter o valor:
```
postgresql://postgres:senha@postgres-luxbet.coolify.internal:5432/luxbet
```

**Substitua pelos valores reais do seu PostgreSQL:**
- `postgres` = usuário do PostgreSQL
- `senha` = senha do PostgreSQL  
- `postgres-luxbet.coolify.internal` = nome do serviço PostgreSQL no Coolify
- `5432` = porta (geralmente 5432)
- `luxbet` = nome do banco de dados

### Passo 3: Verificar Outras Configurações

Certifique-se de que:
- ✅ `Available at Buildtime` está marcado
- ✅ `Available at Runtime` está marcado

### Passo 4: Redeploy

Após corrigir, faça um **Redeploy** do Backend.

---

## 🔍 Verificação Pós-Correção

### 1. Verificar se Está Usando PostgreSQL

Após o deploy, verifique os logs do Backend. Deve aparecer algo como:
```
INFO:     Database connection: postgresql://postgres:***@postgres-luxbet.coolify.internal:5432/luxbet
```

**Se aparecer `sqlite://`, a variável ainda está errada!**

### 2. Testar Persistência do Agente IGameWin

1. Faça login no admin (`/admin`)
2. Vá em **IGameWin**
3. Configure o agente:
   - Agent Code
   - Agent Key
   - API URL
   - Marque como Ativo
4. Clique em **Salvar**
5. **Anote os dados** que você configurou
6. Faça um **Redeploy** do Backend
7. Verifique novamente em **IGameWin**
8. **Os dados devem estar lá!**

---

## 🐛 Se Ainda Não Funcionar

### Verificar Conexão com PostgreSQL

1. No Coolify, vá no serviço **PostgreSQL**
2. Clique em **Terminal**
3. Execute:
   ```sql
   \c luxbet
   SELECT * FROM igamewin_agents;
   ```

**Se retornar vazio:**
- Os dados não estão sendo salvos no PostgreSQL
- Verifique se `DATABASE_URL` está correto
- Verifique se o PostgreSQL tem volume persistente

**Se retornar dados:**
- Os dados estão no banco
- O problema pode ser no frontend não carregando
- Verifique os logs do Backend para erros

---

## 📋 Checklist Final

- [ ] Variável `DATABASE_URL` existe (com "L" no final)
- [ ] Valor começa com `postgresql://` (não `sqlite://`)
- [ ] Usa nome interno do serviço (`.coolify.internal`)
- [ ] PostgreSQL tem volume persistente em `/var/lib/postgresql/data`
- [ ] Backend conecta ao PostgreSQL (verificar logs)
- [ ] Agente IGameWin persiste após redeploy (testar)

---

## 💡 Dica Importante

**Sempre verifique o nome exato das variáveis de ambiente!**
- `DATABASE_URL` ✅ (correto)
- `DATABASE_UR` ❌ (errado - falta o "L")
- `DATABASE_URI` ✅ (também funciona, mas `DATABASE_URL` é o padrão)

O código em `backend/database.py` procura especificamente por `DATABASE_URL`:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fortunevegas.db")
```

Se não encontrar, usa SQLite por padrão, e todos os dados são perdidos!
