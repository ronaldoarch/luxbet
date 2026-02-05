# 🔍 Diferença Entre Configurações do Coolify

## 📊 Comparação das Duas Configurações

### Configuração 1: "midasdelares-prod-gqip-compression"
```
Ports Exposed: 8000
Ports Mapping: 8000
Publish Directory: 8000
Traefik Port: 8000
DNS Provider: Hostinger
```

### Configuração 2: "ml"
```
Ports Exposed: 80
Ports Mapping: (vazio)
Traefik Port: 80
Build Pack: Docker Compose
```

---

## 🔍 Diferenças Principais

### 1. **Porta Exposta**

#### Configuração 1 (Porta 8000):
- **Ports Exposed**: `8000`
- **Traefik redireciona para**: Porta 8000 do container
- **Uso**: Aplicação que roda internamente na porta 8000

#### Configuração 2 (Porta 80):
- **Ports Exposed**: `80`
- **Traefik redireciona para**: Porta 80 do container
- **Uso**: Aplicação que roda internamente na porta 80 (padrão HTTP)

---

### 2. **Ports Mapping**

#### Configuração 1:
- **Ports Mapping**: `8000`
- Define mapeamento explícito de porta

#### Configuração 2:
- **Ports Mapping**: (vazio)
- Usa porta padrão ou detecta automaticamente

---

### 3. **Publish Directory**

#### Configuração 1:
- **Publish Directory**: `8000`
- ⚠️ **Isso parece estar errado!** Publish Directory deve ser um diretório (ex: `dist`, `build`), não uma porta

#### Configuração 2:
- **Publish Directory**: Não visível na imagem (provavelmente correto ou não aplicável)

---

### 4. **Build Pack**

#### Configuração 1:
- Não especificado na imagem (provavelmente Nixpacks ou Dockerfile)

#### Configuração 2:
- **Build Pack**: `Docker Compose`
- Usa docker-compose para orquestração

---

### 5. **Traefik Configuration**

#### Configuração 1:
```yaml
traefik.http.services.gqip.loadbalancer.server.port=8000
```
- Traefik redireciona tráfego para porta **8000** do container

#### Configuração 2:
```yaml
traefik.http.services.loadbalancer-server-port80.loadbalancer.server.port=80
```
- Traefik redireciona tráfego para porta **80** do container

---

## 🎯 Qual Usar para luxbet.site?

### Para Frontend (Vite/React):

**Recomendação**: Porta 80 ou deixar vazio (Coolify detecta automaticamente)

```
Ports Exposed: 80 (ou deixar vazio)
Ports Mapping: (vazio)
Publish Directory: dist
Build Pack: Nixpacks ou Dockerfile
```

**Por quê?**
- Frontend estático geralmente roda na porta 80
- Coolify pode detectar automaticamente
- Mais simples e padrão

---

### Para Backend (FastAPI):

**Recomendação**: Porta 8000 (se sua aplicação roda nessa porta)

```
Ports Exposed: 8000
Ports Mapping: 8000
Build Pack: Nixpacks ou Dockerfile
```

**Por quê?**
- FastAPI geralmente roda na porta 8000 por padrão
- Traefik redireciona corretamente
- Mantém consistência

---

## ⚠️ Problema na Configuração 1

Na primeira imagem, vejo:
- **Publish Directory**: `8000` ❌

**Isso está ERRADO!** Publish Directory deve ser:
- `dist` (para Vite)
- `build` (para Create React App)
- `out` (para Next.js)
- **NÃO uma porta!**

**Correção**:
```
Publish Directory: dist (ou o diretório de build correto)
```

---

## 📋 Configuração Recomendada para luxbet.site

### Frontend:

```
Name: luxbet-frontend
Build Pack: Nixpacks (ou Dockerfile)
Base Directory: /frontend
Ports Exposed: 80 (ou deixar vazio)
Ports Mapping: (vazio)
Publish Directory: dist
Is Static Site: SIM ✓
```

### Backend:

```
Name: luxbet-backend
Build Pack: Nixpacks (ou Dockerfile)
Base Directory: /backend
Ports Exposed: 8000
Ports Mapping: 8000
Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔧 Traefik Labels (Custom Labels)

### Para Frontend (Porta 80):

```yaml
traefik.http.routers.luxbet-frontend.rule=Host(`luxbet.site`) || Host(`www.luxbet.site`)
traefik.http.routers.luxbet-frontend.entrypoints=websecure
traefik.http.routers.luxbet-frontend.tls=true
traefik.http.services.luxbet-frontend.loadbalancer.server.port=80
```

### Para Backend (Porta 8000):

```yaml
traefik.http.routers.luxbet-backend.rule=Host(`api.luxbet.site`)
traefik.http.routers.luxbet-backend.entrypoints=websecure
traefik.http.routers.luxbet-backend.tls=true
traefik.http.services.luxbet-backend.loadbalancer.server.port=8000
```

---

## 📝 Resumo das Diferenças

| Aspecto | Config 1 (8000) | Config 2 (80) |
|---------|----------------|---------------|
| **Porta** | 8000 | 80 |
| **Uso** | Backend/API | Frontend/Web |
| **Publish Directory** | ❌ Errado (8000) | ✅ Correto |
| **Build Pack** | Não especificado | Docker Compose |
| **Traefik Port** | 8000 | 80 |

---

## ✅ Recomendação Final

**Para luxbet.site:**

1. **Frontend**: Use porta 80 (ou deixe vazio)
   - Coolify detecta automaticamente
   - Padrão para sites estáticos

2. **Backend**: Use porta 8000
   - FastAPI roda nessa porta
   - Traefik redireciona corretamente

3. **Publish Directory**: Use `dist` (não uma porta!)
   - Diretório onde o build gera os arquivos

4. **DNS**: Use registro A (mais simples) ou CNAME (se preferir)

---

## 🚨 Correção Necessária

Se você está usando a Configuração 1 como referência:

**Corrija o Publish Directory**:
- ❌ `8000` (porta)
- ✅ `dist` (diretório de build)

Isso pode estar causando problemas no deploy!
