# ✅ Verificação Rápida: PostgreSQL Persistindo Dados

## 🔍 Checklist de Verificação

### 1. PostgreSQL tem Volume Persistente?

**No Coolify:**
1. Vá em **Projects** → **PostgreSQL**
2. Clique no seu serviço PostgreSQL
3. Vá na aba **Volumes**
4. **Deve ter um volume** montado em `/var/lib/postgresql/data`

**Se NÃO tiver:**
- Adicione um volume:
  - **Mount Path**: `/var/lib/postgresql/data`
  - **Type**: `Named Volume`
  - **Name**: `luxbet-postgres-data` (ou outro nome)

**⚠️ SEM VOLUME = DADOS PERDIDOS A CADA RECRIAÇÃO DO CONTAINER**

---

### 2. Variável DATABASE_URL Está Configurada?

**No Coolify:**
1. Vá na aplicação **Backend**
2. Clique em **Environment Variables**
3. Procure por `DATABASE_URL`
4. Deve estar no formato:
   ```
   postgresql://postgres:senha@postgres-luxbet.coolify.internal:5432/luxbet
   ```

**Verificações:**
- ✅ Começa com `postgresql://` (não `sqlite://`)
- ✅ Usa o nome interno do serviço (`.coolify.internal`)
- ✅ Tem usuário, senha, host, porta e database

---

### 3. Teste Rápido de Persistência

**Passo 1:** Conecte ao PostgreSQL
- No Coolify, vá no serviço PostgreSQL → **Terminal**
- Execute:
  ```sql
  \c luxbet
  SELECT COUNT(*) FROM users;
  SELECT COUNT(*) FROM media_assets;
  ```

**Passo 2:** Anote os números

**Passo 3:** Faça um redeploy do Backend

**Passo 4:** Verifique novamente
```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM media_assets;
```

**Se os números mudaram para 0:** Os dados não estão persistindo.

---

## 🛠️ Solução Rápida

### Se o PostgreSQL NÃO tem Volume Persistente:

1. **PARE o serviço PostgreSQL** (não delete!)
2. Vá em **Volumes** → **Add Volume**
3. Configure:
   - **Mount Path**: `/var/lib/postgresql/data`
   - **Type**: `Named Volume`
   - **Name**: `luxbet-postgres-data`
4. **INICIE** o serviço novamente
5. Os dados agora devem persistir

### Se a DATABASE_URL está errada:

1. No Coolify, vá no serviço PostgreSQL
2. Copie a **Connection String** completa
3. Vá no Backend → **Environment Variables**
4. Adicione/Edite `DATABASE_URL` com a connection string
5. Faça **Redeploy** do Backend

---

## 📋 Formato Correto da DATABASE_URL

```
postgresql://[usuario]:[senha]@[host]:[porta]/[database]
```

**Exemplo:**
```
postgresql://postgres:minhasenha123@postgres-luxbet.coolify.internal:5432/luxbet
```

**⚠️ IMPORTANTE:**
- Use o nome interno do serviço (`.coolify.internal`)
- Não use `localhost` ou IPs
- A porta padrão é `5432`

---

## 🐛 Problema Persiste?

Se mesmo com volume persistente os dados somem:

1. **Verifique se o PostgreSQL não está sendo deletado**
   - No histórico do Coolify, veja se há "Delete" do PostgreSQL
   - Se sim, pare de deletar e recriar

2. **Verifique se há múltiplos serviços PostgreSQL**
   - Pode estar conectando em um banco diferente
   - Use apenas um serviço PostgreSQL

3. **Verifique os logs do Backend**
   - Procure por erros de conexão
   - Veja se está realmente conectando no PostgreSQL correto

---

## ✅ Confirmação Final

Após configurar tudo:

1. ✅ PostgreSQL tem volume em `/var/lib/postgresql/data`
2. ✅ `DATABASE_URL` configurada corretamente
3. ✅ Backend conecta ao PostgreSQL (ver logs)
4. ✅ Dados persistem após redeploy (teste criando algo e redeployando)

**Se tudo estiver OK, os dados devem persistir!** 🎉
