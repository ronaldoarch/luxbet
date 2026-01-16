# 🚀 Guia de Deploy do Frontend no Coolify

## 📋 Configuração no Coolify

### Opção 1: Build Estático com Nginx (Recomendado)

**Configuração:**
```
Repository: https://github.com/ronaldoarch/fortunevegas
Branch: cloudflare-deploy
Base Directory: /frontend
Port: 80
Build Pack: Dockerfile          ← Usa o Dockerfile
Is Static Site?: SIM ✓          ← Importante!
```

**O que acontece:**
- Build do Vite gera arquivos estáticos em `/dist`
- Nginx serve os arquivos estáticos
- Mais eficiente e rápido

---

### Opção 2: Build Estático com Nixpacks

**Configuração:**
```
Repository: https://github.com/ronaldoarch/fortunevegas
Branch: cloudflare-deploy
Base Directory: /frontend
Port: 5173
Build Pack: Nixpacks
Is Static Site?: SIM ✓
```

**Build Command:**
```bash
npm ci && npm run build
```

**Publish Directory:**
```
dist
```

---

### Opção 3: Servidor Vite Preview (Desenvolvimento)

**Configuração:**
```
Repository: https://github.com/ronaldoarch/fortunevegas
Branch: cloudflare-deploy
Base Directory: /frontend
Port: 5173
Build Pack: Nixpacks
Is Static Site?: NÃO
```

**Build Command:**
```bash
npm ci
```

**Start Command:**
```bash
npm run preview -- --host 0.0.0.0 --port ${PORT:-5173}
```

---

## 🔧 Variáveis de Ambiente

**Obrigatória:**
```env
VITE_API_URL=https://sua-url-do-backend.com
```

**Exemplo:**
```env
VITE_API_URL=https://backend-api.coolify.app
```

⚠️ **IMPORTANTE**: Os arquivos do frontend ainda precisam ser atualizados para usar `import.meta.env.VITE_API_URL` em vez de `http://localhost:8000` hardcoded.

---

## ✅ Checklist

### Antes do Deploy:
- [ ] Arquivos do frontend atualizados para usar `VITE_API_URL`
- [ ] `nixpacks.toml` ou `Dockerfile` criado no `/frontend`
- [ ] `package.json` tem scripts `build` e `preview`
- [ ] Variável `VITE_API_URL` configurada no Coolify

### Durante Deploy:
- [ ] Base Directory: `/frontend`
- [ ] Build Pack: `Dockerfile` ou `Nixpacks`
- [ ] Is Static Site: `SIM` (se usar build estático)
- [ ] Port: `80` (estático) ou `5173` (preview)

### Após Deploy:
- [ ] Frontend carrega corretamente
- [ ] Imagens/assets aparecem
- [ ] API conecta (verificar console do navegador)
- [ ] Admin funciona (login, dashboard)

---

## 🐛 Troubleshooting

### Erro: "Nixpacks failed to detect the application type"

**Solução:**
- Verifique se `nixpacks.toml` existe em `/frontend/`
- Ou use `Dockerfile` em vez de Nixpacks
- Ou marque como "Static Site" e defina Publish Directory: `dist`

### Erro: "Cannot find module"

**Solução:**
- Verifique se `npm ci` está sendo executado antes do build
- Confirme que `package.json` está correto

### Frontend não conecta ao backend

**Solução:**
- Verifique se `VITE_API_URL` está configurada
- Verifique console do navegador (F12) para erros CORS
- Confirme URL do backend está acessível

---

## 📝 Recomendação Final

**Para produção, use:**
- **Dockerfile** com Nginx (Opção 1) - Mais eficiente
- **Static Site**: SIM
- **Port**: 80
- **Variável**: `VITE_API_URL` configurada
