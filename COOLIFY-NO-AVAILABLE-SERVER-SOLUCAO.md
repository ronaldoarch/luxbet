# "No Available Server" no Coolify (WiFi e 4G) – solução

Documentação oficial: **[No Available Server (503) Error](https://coolify.io/docs/troubleshoot/applications/no-available-server)**

O erro **"no available server"** no Coolify significa que o **Traefik** (proxy) não encontra nenhum **(healthy)** container para encaminhar o tráfego.

---

## 1. Não adicionar o IP no campo Domains

**Importante:** Não coloque `http://147.93.147.33` no campo **Domains**.

Desde o beta.191 o Coolify **valida DNS** para cada domínio (com 1.1.1.1, etc.). Um **endereço IP não é um FQDN** (nome de domínio), então a validação falha e aparece:

- **"Validating DNS failed."**
- `http://147.93.147.33 -> host.docker.internal`

Ou seja: o Coolify espera um nome de domínio (ex.: `luxbet.site`), não um IP. Para acesso por IP, use **apenas** as **Custom Labels** do Traefik (ou a **Dynamic Configuration**), sem colocar o IP em Domains.

**Se você já adicionou o IP em Domains:**

1. Remova **`http://147.93.147.33`** do campo **Domains** (deixe só `https://luxbet.site` e `https://www.luxbet.site`).
2. Mantenha as **Custom Labels** do Traefik para o IP (router `http-ip-luxbet` com `Host(\`147.93.147.33\`)`).
3. Salve e faça **Redeploy** para aplicar a configuração e sumir o aviso de “The latest configuration has not been applied”.

---

## 2. Diagnóstico (container saudável?)

O 503 também aparece quando o Traefik **não considera o container saudável**.

### 2.1 Status do container

No servidor (SSH na VPS):

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

- Se o container do frontend aparecer com **(unhealthy)** → o problema é **health check**.
- Solução temporária: na aplicação Frontend no Coolify, desative o **Health Check**, salve e reinicie. Teste de novo `http://147.93.147.33`.
- Depois ajuste o health check (path, porta, comando) conforme: [Health Checks](https://coolify.io/docs/knowledge-base/health-checks).

### 2.2 Labels do Traefik no container

Confirme se as labels do IP estão mesmo no container do frontend:

```bash
# Troque <NOME_DO_CONTAINER_FRONTEND> pelo nome real (ex.: algo como luxbet-frontend-...)
docker ps --format "{{.Names}}" | grep -i front
docker inspect <NOME_DO_CONTAINER_FRONTEND> --format '{{json .Config.Labels}}' | jq
```

Procure por `traefik.http.routers.http-ip-luxbet` (ou o nome que você usou). Se **não aparecer**, as Custom Labels do IP não estão sendo aplicadas nesse container.

### 2.3 Logs do proxy (Traefik)

```bash
docker logs coolify-proxy --tail 100
```

Veja se há erros ao acessar `http://147.93.147.33` (ex.: backend não encontrado, serviço inexistente).

### 2.4 Versão do Traefik (Docker API)

Se no log do proxy aparecer algo como **"client version 1.24 is too old"**, o problema é a versão do Traefik.

- No Coolify: **Servers** → **[Seu servidor]** → **Proxy** → **Configuration**.
- Altere a versão do Traefik para **v3.6.1** (ou v2.11.31 se estiver em v2).
- **Restart Proxy**.

Detalhes: [Update Traefik to Fix Docker API Version Issue](https://coolify.io/docs/troubleshoot/applications/no-available-server#update-traefik-to-fix-docker-api-version-issue).

---

## 3. Rota por IP via Dynamic Configuration (Traefik)

Se as labels no container não forem aplicadas ou não funcionarem, dá para criar a rota do IP **direto no Traefik**, sem depender das labels do container.

1. No Coolify: **Servers** → **[Seu servidor]** → **Proxy** → **Dynamic Configurations**.
2. Crie uma nova configuração (ou edite uma existente) em **YAML**.
3. Descubra o **nome do container** do frontend:
   ```bash
   docker ps --format "{{.Names}}" | grep -i front
   ```
   Exemplo de nome: `coolify-luxbet-frontend-xxxxx` (use o que aparecer aí).

4. Use um conteúdo no formato abaixo (substitua `NOME_DO_CONTAINER_FRONTEND` pelo nome real):

```yaml
http:
  routers:
    luxbet-by-ip:
      rule: "Host(`147.93.147.33`)"
      entryPoints:
        - http
      service: luxbet-frontend-by-ip
  services:
    luxbet-frontend-by-ip:
      loadBalancer:
        servers:
          - url: "http://NOME_DO_CONTAINER_FRONTEND:80"
        passHostHeader: true
```

5. Salve a configuração dinâmica. O Traefik aplica sem precisar reiniciar.
6. Teste: `http://147.93.147.33`.

Se o Traefik do Coolify usar o entrypoint **`web`** em vez de **`http`**, troque na configuração:

```yaml
entryPoints:
  - web
```

---

## 4. Porta e binding

- Na aplicação Frontend no Coolify, em **Ports Exposes**, deve estar **80** (ou a porta em que o Nginx/APP escuta).
- O serviço dentro do container deve escutar em **0.0.0.0** (não só em localhost).

---

## Resumo rápido

| O que fazer | Onde |
|-------------|------|
| Adicionar `http://147.93.147.33` como domínio | Frontend → Domains |
| Ver se o container está (unhealthy) | `docker ps` |
| Desativar health check para testar | Frontend → Health Check → desativar |
| Ver se as labels do IP estão no container | `docker inspect <container> \| jq .Config.Labels` |
| Ver erros do proxy | `docker logs coolify-proxy --tail 100` |
| Atualizar Traefik (Docker API) | Proxy → Configuration → v3.6.1 → Restart Proxy |
| Criar rota por IP no Traefik | Proxy → Dynamic Configurations (YAML acima) |

Documentação oficial: [coolify.io/docs/troubleshoot/applications/no-available-server](https://coolify.io/docs/troubleshoot/applications/no-available-server).

---

## "Validating DNS failed" ao usar IP em Domains

Se você adicionou `http://147.93.147.33` em **Domains** e apareceu:

- **"Validating DNS failed."**  
- **"Make sure you have added the DNS records correctly."**  
- **`http://147.93.147.33 -> host.docker.internal`**

**Motivo:** O Coolify valida cada “domínio” via DNS (FQDN). Um IP não é um nome de domínio, então a validação falha.

**O que fazer:**

1. **Remova** `http://147.93.147.33` do campo **Domains** (deixe só os domínios reais: `https://luxbet.site`, `https://www.luxbet.site`).
2. Use a rota por IP **só** via **Custom Labels** do Traefik (router para `Host(\`147.93.147.33\`)`) ou via **Dynamic Configuration** (ver passo 3 acima).
3. Clique em **Redeploy** para aplicar a configuração e remover o aviso **"The latest configuration has not been applied"**.
