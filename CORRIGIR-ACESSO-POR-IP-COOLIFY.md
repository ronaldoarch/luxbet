# Corrigir: "Sua conexão não é segura" + "Unavailable server" ao acessar por IP

## O que está acontecendo

1. **"Sua conexão não é segura"**  
   Aparece ao acessar `http://147.93.147.33` porque:
   - É HTTP (sem certificado) ou
   - O certificado é do domínio `luxbet.site`, não do IP.

2. **"Unavailable server"** (depois de continuar)  
   O **Traefik** (proxy do Coolify) só tem rotas para o **nome** do domínio (`luxbet.site`, `www.luxbet.site`).  
   Quando você acessa pelo **IP** (`147.93.147.33`), o navegador envia `Host: 147.93.147.33`.  
   Nenhuma rota do Traefik usa esse Host → Traefik responde "unavailable" ou 503.

Ou seja: o servidor recebe o pedido, mas o proxy **não sabe para qual aplicação enviar** quando o Host é o IP.

---

## Solução: Aceitar o IP no Coolify (Traefik)

É preciso fazer o Traefik **também** atender pedidos em que o Host seja o IP `147.93.147.33`, encaminhando para o mesmo frontend (e, se quiser, para a API).

### Passo 1: Frontend – adicionar o IP como domínio no Coolify

1. Acesse o **Coolify** (ex.: `http://147.93.147.33:8000`).
2. Abra o projeto e a aplicação **Frontend** (luxbet.site).
3. Vá em **Domains** (ou **Configuration** → domínios).
4. **Adicione** o domínio/host: `147.93.147.33`.
5. Para esse “domínio” (IP):
   - **Não** use SSL/HTTPS (Let's Encrypt não emite certificado para IP).
   - Deixe apenas **HTTP** para o IP.
6. Salve e faça **Redeploy** do frontend se o Coolify pedir.

Assim o Traefik passa a ter uma rota para `Host(`147.93.147.33`)` e encaminha para o frontend.  
Quem acessar `http://147.93.147.33` vai:
- Ver "sua conexão não é segura" (normal em HTTP ou ao usar IP).
- Poder continuar e **ver o site** (sem "unavailable server").

### Passo 2: API – mesmo IP na aplicação da API (se for outro serviço)

Se a **API** for outra aplicação no Coolify (ex.: `api.luxbet.site`):

1. Abra a aplicação **Backend/API** no Coolify.
2. Em **Domains**, adicione também: `147.93.147.33` (ou um subdomínio que você não use, só para rotear; na prática, o mais simples é usar path-based routing ou o mesmo IP com path `/api` – depende de como está configurado).

Se no seu setup a API é acessada por **path** no mesmo domínio (ex.: `luxbet.site/api`), a rota do frontend já pode estar repassando `/api` para o backend; nesse caso, ao adicionar o IP no frontend, o Traefik pode já encaminhar `http://147.93.147.33/api` para a API. Se a API for por **host** (`api.luxbet.site`), então no Coolify você precisa adicionar uma rota para o IP também (por exemplo, um domínio "147.93.147.33" na aplicação da API e regra por path `/api` ou outro esquema que você use).

### Passo 3: Frontend – URL da API quando o usuário entra por IP

Se o usuário abre o site por `http://147.93.147.33`, o frontend precisa chamar a API no **mesmo host** (IP), por exemplo:

- `http://147.93.147.33/api/...`  

Isso costuma ser resolvido com **URL relativa** (ex.: ` /api/...` ou variável `VITE_API_URL` vazia ou igual a `''` em build), para que o browser use o mesmo host (e porta) da página. Confirme no projeto do frontend que, ao abrir por IP, as chamadas não vão para `https://api.luxbet.site` e sim para o mesmo IP.

---

## Se o Coolify não permitir "domínio" igual ao IP

Algumas versões do Coolify só aceitam nomes de domínio. Nesse caso dá para fazer na mão com **labels do Traefik** no serviço do frontend:

- Adicionar um **router** que tenha regra:
  - `Host(\`147.93.147.33\`)`
- Apontar esse router para o **mesmo service** do frontend (porta 80).
- Esse router pode ser só **HTTP** (entrada `web`), sem HTTPS.

Exemplo de labels (ajuste o nome do router/service se o Coolify tiver gerado outros):

```yaml
# Rota extra para acesso por IP (HTTP apenas)
traefik.http.routers.luxbet-ip.entrypoints=web
traefik.http.routers.luxbet-ip.rule=Host(`147.93.147.33`)
traefik.http.routers.luxbet-ip.service=luxbet-service
```

Assim, ao acessar `http://147.93.147.33`, o Traefik encaminha para o frontend e deixa de aparecer "unavailable server".

---

## Resumo

| Problema                    | Causa                                      | Ação                                                |
|----------------------------|--------------------------------------------|-----------------------------------------------------|
| "Sua conexão não é segura" | HTTP ou certificado só para luxbet.site    | Normal ao usar IP; usuário pode "Continuar".        |
| "Unavailable server"       | Traefik não tem rota para Host = IP        | Adicionar IP como domínio no Coolify ou por labels. |

Depois de configurar a rota para o IP no Coolify/Traefik, **sem HTTPS** no IP continua dando "sua conexão não é segura", mas o site **carrega** em vez de "unavailable server".
