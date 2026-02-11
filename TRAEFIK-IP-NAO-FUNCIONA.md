# "Unavailable server" ao acessar por IP – o que tentar

## 1. Trocar o entrypoint de `http` para `web`

No Coolify, o Traefik costuma usar os nomes **`web`** (porta 80) e **`websecure`** (porta 443), e não `http`/`https`. Se as suas outras rotas usam `http` e mesmo assim o site por domínio funciona, pode ser que o Coolify traduza. Para o **IP**, tente forçar o entrypoint **`web`**.

**Substitua** as 4 linhas do IP por estas (mudança: `entryPoints=web` e regra com `PathPrefix` e `priority`):

```properties
traefik.http.routers.http-ip-luxbet.entryPoints=web
traefik.http.routers.http-ip-luxbet.middlewares=gzip
traefik.http.routers.http-ip-luxbet.priority=100
traefik.http.routers.http-ip-luxbet.rule=Host(`147.93.147.33`) && PathPrefix(`/`)
traefik.http.routers.http-ip-luxbet.service=http-0-mgk08sowg0ockk8s0s808880
```

- **entryPoints=web** – tenta o nome de entrypoint mais comum no Traefik/Coolify.
- **priority=100** – faz essa rota ter prioridade sobre possíveis catch-alls.
- **PathPrefix(`/`)** – igual às outras rotas do frontend.

Salve, redeploy do frontend e teste de novo: `http://147.93.147.33`.

---

## 2. Se ainda der "Unavailable server" – conferir nomes dos entrypoints

No servidor (SSH na VPS), liste os entrypoints que o Traefik está usando:

```bash
# Se o Traefik estiver em Docker
docker ps | grep traefik
docker inspect <container_id_traefik> | grep -A 20 "Entrypoints"
```

Ou no painel do Coolify: **Settings** ou **Traefik** e veja como estão nomeados os entrypoints (ex.: `web`, `websecure`, ou `http`, `https`).

Use **exatamente** o mesmo nome que as rotas HTTP do luxbet.site usam. Se no Coolify aparecer que o entrypoint HTTP é `web`, use `web` nas linhas do IP. Se for `http`, use `http`.

---

## 3. Testar as duas variantes (web e http)

Se não tiver como ver o nome do entrypoint, teste as duas opções.

**Opção A – entrypoint `web` (5 linhas para o IP):**

```properties
traefik.http.routers.http-ip-luxbet.entryPoints=web
traefik.http.routers.http-ip-luxbet.middlewares=gzip
traefik.http.routers.http-ip-luxbet.priority=100
traefik.http.routers.http-ip-luxbet.rule=Host(`147.93.147.33`) && PathPrefix(`/`)
traefik.http.routers.http-ip-luxbet.service=http-0-mgk08sowg0ockk8s0s808880
```

**Opção B – entrypoint `http` (igual às outras rotas do frontend):**

```properties
traefik.http.routers.http-ip-luxbet.entryPoints=http
traefik.http.routers.http-ip-luxbet.middlewares=gzip
traefik.http.routers.http-ip-luxbet.priority=100
traefik.http.routers.http-ip-luxbet.rule=Host(`147.93.147.33`) && PathPrefix(`/`)
traefik.http.routers.http-ip-luxbet.service=http-0-mgk08sowg0ockk8s0s808880
```

Use só uma das opções (A ou B), salve, redeploy e teste.

---

## 4. Ver se o Traefik está recebendo as labels

No Coolify, na aplicação Frontend, confira se as labels do IP aparecem nas **labels do container** (geralmente em **Advanced** ou **Inspect** do container). Se não aparecerem, as "Custom Labels" podem estar em outro lugar (ex.: no serviço/stack, não no container do frontend).

---

## 5. Porta 80 no firewall

Na VPS, confirme que a porta 80 está aberta:

```bash
sudo ufw status
# ou
sudo iptables -L -n | grep 80
```

Se estiver bloqueada, libere:

```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

---

## Resumo rápido

1. Trocar para **entryPoints=web** e adicionar **priority=100** e **PathPrefix(`/`)** nas 5 linhas do IP.
2. Salvar e fazer **Redeploy** do frontend.
3. Testar de novo `http://147.93.147.33`.
4. Se continuar, conferir no Coolify/servidor o nome real do entrypoint HTTP e usar esse nome na label.
