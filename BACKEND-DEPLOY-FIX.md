# 🔧 Problema: Backend não encontra requirements.txt

## ❌ Erro Atual

```
ERROR: failed to calculate checksum of ref: "/requirements.txt": not found
```

O build está tentando usar commit antigo `8a0b53c` que pode não ter os arquivos corretos.

## ✅ Soluções

### 1. Verificar Base Directory no Coolify

**Aplicação Backend deve ter:**

```
Base Directory: /backend          ← DEVE SER /backend!
Dockerfile Location: /Dockerfile  ← Relativo ao Base Directory
```

### 2. Forçar Pull do Commit Mais Recente

No Coolify:
1. Vá em **Settings** → **Git Source**
2. Clique em **Force Pull** ou **Sync**
3. Ou mude o Branch para outro e depois volte para `cloudflare-deploy`

### 3. Verificar se requirements.txt existe

```bash
# Verificar localmente
ls -la backend/requirements.txt

# Verificar no repositório
git show cloudflare-deploy:backend/requirements.txt
```

### 4. Limpar Cache e Fazer Redeploy

1. **Settings** → **Danger Zone** → **Clean Build**
2. Faça **Redeploy**

## 🔍 Verificação

O commit `8a0b53c` é antigo. O mais recente é `e85ab19` ou posterior.

Confirme no Coolify qual commit está sendo usado:
- Vá em **Deployments** → veja o commit SHA
- Deve ser `e85ab19` ou mais recente

## 📝 Checklist

- [ ] Base Directory: `/backend` (não `/` ou `/frontend`)
- [ ] Dockerfile Location: `/Dockerfile` (relativo ao Base Directory)
- [ ] Commit correto sendo usado (verificar em Deployments)
- [ ] Fez Clean Build antes de redeploy
- [ ] `requirements.txt` existe em `/backend/requirements.txt` no repositório
