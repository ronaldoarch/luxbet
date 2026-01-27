# 🔒 Solução: Dados Não Persistem no PostgreSQL

## ⚠️ Problema

Mesmo usando PostgreSQL no Coolify, os dados (agente IGameWin, banners, logos, promoções) são perdidos após cada deploy.

## 🔍 Possíveis Causas

### 1. PostgreSQL sendo Recriado

Se o serviço PostgreSQL está sendo deletado e recriado, os dados serão perdidos.

**Solução:**
- No Coolify, verifique se o PostgreSQL tem **Volume Persistente** configurado
- O PostgreSQL precisa de um volume para persistir os dados

### 2. Variável DATABASE_URL Incorreta

Se a `DATABASE_URL` não está apontando para o PostgreSQL correto, pode estar usando SQLite.

**Verificação:**
1. No Coolify, vá em **Backend** → **Environment Variables**
2. Verifique se `DATABASE_URL` existe e está no formato:
   ```
   postgresql://usuario:senha@host:5432/database
   ```
3. Deve começar com `postgresql://` (não `sqlite://`)

### 3. Banco de Dados Diferente a Cada Deploy

Se o nome do banco ou host está mudando, pode estar criando um banco novo.

**Solução:**
- Use o nome do serviço PostgreSQL interno do Coolify (ex: `postgres-luxbet.coolify.internal`)
- Não use `localhost` ou IPs que podem mudar

---

## ✅ Solução Passo a Passo

### Passo 1: Verificar PostgreSQL no Coolify

1. No Coolify, vá em **Projects** → **PostgreSQL**
2. Encontre seu serviço PostgreSQL
3. **IMPORTANTE**: Verifique se tem **Volume Persistente** configurado
   - Se não tiver, adicione um volume para `/var/lib/postgresql/data`
   - Isso garante que os dados persistem mesmo se o container for recriado

### Passo 2: Verificar Variável DATABASE_URL

1. Vá em **Backend** → **Environment Variables**
2. Verifique a variável `DATABASE_URL`:
   ```
   DATABASE_URL=postgresql://postgres:senha@postgres-luxbet.coolify.internal:5432/luxbet
   ```
3. **Substitua pelos valores reais do seu PostgreSQL**

### Passo 3: Verificar Conexão

Após o deploy, verifique os logs do backend. Deve aparecer:
```
INFO:     Database connection successful
INFO:     Tables created/verified
```

### Passo 4: Testar Persistência

1. Faça login no admin (`/admin`)
2. Configure o IGameWin
3. Faça upload de logo/banner
4. Crie uma promoção
5. **Anote os dados criados**
6. Faça um **Redeploy** do backend
7. Verifique se os dados ainda estão lá

---

## 🛠️ Configuração Correta do PostgreSQL no Coolify

### Criar PostgreSQL com Persistência

1. **Projects** → **PostgreSQL** → **Create**
2. Configure:
   - **Name**: `luxbet-postgres` (ou outro nome)
   - **Database**: `luxbet`
   - **User**: `postgres`
   - **Password**: (senha forte)
   - **Version**: PostgreSQL 15 ou 16
3. **IMPORTANTE**: Na seção **Volumes**, adicione:
   - **Mount Path**: `/var/lib/postgresql/data`
   - **Type**: `Named Volume`
   - **Name**: `luxbet-postgres-data`
4. Clique em **Create**

### Obter Connection String

Após criar, o Coolify mostrará a connection string. Use no formato:
```
postgresql://postgres:senha@postgres-luxbet.coolify.internal:5432/luxbet
```

**⚠️ Use o nome interno do serviço** (`postgres-luxbet.coolify.internal`), não IPs ou localhost.

---

## 🔧 Verificar se Dados Estão Sendo Salvos

### Conectar ao PostgreSQL

1. No Coolify, vá no serviço PostgreSQL
2. Clique em **Terminal** ou **Connect**
3. Execute:
   ```sql
   \c luxbet
   \dt
   ```
4. Deve listar todas as tabelas: `users`, `media_assets`, `promotions`, `igamewin_agents`, etc.

### Verificar Dados

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM media_assets;
SELECT COUNT(*) FROM promotions;
SELECT COUNT(*) FROM igamewin_agents;
```

Se retornar 0 em todas, os dados não estão sendo salvos.

---

## 🐛 Troubleshooting

### Erro: "relation does not exist"

As tabelas não foram criadas. Verifique:
- Se `init_db()` está sendo executado
- Se há erros nos logs do backend
- Se o usuário PostgreSQL tem permissões

### Dados Sumem Após Redeploy

**Causa mais comum**: O PostgreSQL está sendo recriado sem volume persistente.

**Solução**:
1. Pare o serviço PostgreSQL
2. Adicione volume persistente em `/var/lib/postgresql/data`
3. Inicie novamente
4. Os dados devem persistir agora

### Backend Não Conecta ao PostgreSQL

Verifique:
- Se `DATABASE_URL` está correto
- Se o nome do serviço está correto (use `.coolify.internal`)
- Se o PostgreSQL está rodando
- Se há firewall bloqueando a conexão

---

## 📝 Checklist Final

- [ ] PostgreSQL criado com **Volume Persistente** em `/var/lib/postgresql/data`
- [ ] Variável `DATABASE_URL` configurada corretamente no Backend
- [ ] `DATABASE_URL` usa o nome interno do serviço (`.coolify.internal`)
- [ ] Backend conecta ao PostgreSQL (verificar logs)
- [ ] Tabelas foram criadas (verificar com `\dt` no PostgreSQL)
- [ ] Dados persistem após redeploy (testar criando dados e fazendo redeploy)

---

## 💡 Dica Importante

**NUNCA** delete o serviço PostgreSQL sem fazer backup primeiro. Se precisar recriar:
1. Exporte os dados: `pg_dump -U postgres luxbet > backup.sql`
2. Recrie o serviço com volume persistente
3. Importe os dados: `psql -U postgres luxbet < backup.sql`
