# 🔧 Variáveis de Ambiente - Frontend

## 📋 Variáveis Necessárias

O frontend precisa de **1 variável principal**:

### ✅ Obrigatória

```env
VITE_API_URL=https://backend.coolify.app
```

ou

```env
VITE_API_URL=https://api.seudominio.com
```

**Descrição**: URL base da API do backend (sem barra no final)

---

## 📝 Onde é Usada

A variável `VITE_API_URL` é usada para:

1. **Autenticação** (`AdminLogin.tsx`)
   - Login de admin: `POST ${VITE_API_URL}/api/auth/login`

2. **Admin Dashboard** (`Admin.tsx`)
   - Estatísticas: `GET ${VITE_API_URL}/api/admin/stats`
   - Usuários: `GET ${VITE_API_URL}/api/admin/users`
   - Depósitos: `GET ${VITE_API_URL}/api/admin/deposits`
   - Saques: `GET ${VITE_API_URL}/api/admin/withdrawals`
   - FTDs: `GET ${VITE_API_URL}/api/admin/ftds`
   - Gateways: `GET ${VITE_API_URL}/api/admin/gateways`
   - IGameWin: `GET ${VITE_API_URL}/api/admin/igamewin/...`
   - Mídia (logos/banners): `GET/POST/DELETE ${VITE_API_URL}/api/admin/media/...`

3. **Header** (`Header.tsx`)
   - Logo: `GET ${VITE_API_URL}/api/public/media/logo`

4. **Hero Banner** (`HeroBanner.tsx`)
   - Banners: `GET ${VITE_API_URL}/api/public/media/banners`

5. **Novidades** (`NovidadesSection.tsx`)
   - Jogos: `GET ${VITE_API_URL}/api/public/games`

---

## 🔧 Como Configurar no Coolify

### No Frontend (Aplicação 2):

1. Vá em **Environment Variables**
2. Adicione:
   ```env
   VITE_API_URL=https://sua-url-do-backend.com
   ```
3. Faça **Redeploy** para aplicar as mudanças

### Exemplo Completo:

Se seu backend está em `https://fortunevegas-api.coolify.app`:

```env
VITE_API_URL=https://fortunevegas-api.coolify.app
```

---

## ⚠️ Importante

- No Vite, variáveis de ambiente devem começar com `VITE_` para serem expostas no código cliente
- A URL não deve ter barra (`/`) no final
- Use `https://` em produção (não `http://`)
- Em desenvolvimento, pode usar `http://localhost:8000` como fallback

---

## 🔄 Próximos Passos

**⚠️ ATENÇÃO**: Os arquivos do frontend ainda têm URLs hardcoded (`http://localhost:8000`).

**Para funcionar com variáveis de ambiente, precisamos atualizar:**

- `frontend/src/pages/AdminLogin.tsx`
- `frontend/src/pages/Admin.tsx`
- `frontend/src/components/Header.tsx`
- `frontend/src/components/HeroBanner.tsx`
- `frontend/src/components/NovidadesSection.tsx`

**Mudança necessária em cada arquivo:**

```typescript
// ANTES:
const API_URL = 'http://localhost:8000';

// DEPOIS:
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

Quer que eu atualize todos esses arquivos agora?
