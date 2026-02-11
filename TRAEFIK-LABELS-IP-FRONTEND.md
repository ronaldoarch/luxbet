# Labels Traefik – adicionar acesso por IP (frontend)

## O que adicionar

No Coolify, na aplicação **Frontend**, em **Custom Labels** (ou onde você edita as labels do Traefik), **adicione** estas linhas às que você já tem (não remova as existentes):

```properties
# Rota para acesso por IP (HTTP apenas – sem redirect para HTTPS)
traefik.http.routers.http-ip-luxbet.entryPoints=http
traefik.http.routers.http-ip-luxbet.middlewares=gzip
traefik.http.routers.http-ip-luxbet.rule=Host(`147.93.147.33`)
traefik.http.routers.http-ip-luxbet.service=http-0-mgk08sowg0ockk8s0s808880
```

- **http-ip-luxbet**: nome do novo router (pode ser outro nome único se quiser).
- **entryPoints=http**: só HTTP; não usar HTTPS no IP (não há certificado para IP).
- **middlewares=gzip**: mesma compressão do site.
- **rule=Host(`147.93.147.33`)**: atende quando o Host for o IP.
- **service=http-0-mgk08sowg0ockk8s0s808880**: reaproveita o mesmo serviço do frontend (porta 80).

Não use `redirect-to-https` neste router, senão o usuário seria mandado para `https://147.93.147.33` e daria erro de certificado.

---

## Como fica o conjunto (referência)

Suas labels atuais **+** as novas:

```properties
traefik.enable=true
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https

# luxbet.site
traefik.http.routers.http-0-mgk08sowg0ockk8s0s808880.entryPoints=http
traefik.http.routers.http-0-mgk08sowg0ockk8s0s808880.middlewares=redirect-to-https
traefik.http.routers.http-0-mgk08sowg0ockk8s0s808880.rule=Host(`luxbet.site`) && PathPrefix(`/`)
traefik.http.routers.http-0-mgk08sowg0ockk8s0s808880.service=http-0-mgk08sowg0ockk8s0s808880

# www.luxbet.site
traefik.http.routers.http-1-mgk08sowg0ockk8s0s808880.entryPoints=http
traefik.http.routers.http-1-mgk08sowg0ockk8s0s808880.middlewares=redirect-to-https
traefik.http.routers.http-1-mgk08sowg0ockk8s0s808880.rule=Host(`www.luxbet.site`) && PathPrefix(`/`)
traefik.http.routers.http-1-mgk08sowg0ockk8s0s808880.service=http-1-mgk08sowg0ockk8s0s808880

# HTTPS luxbet.site
traefik.http.routers.https-0-mgk08sowg0ockk8s0s808880.entryPoints=https
traefik.http.routers.https-0-mgk08sowg0ockk8s0s808880.middlewares=gzip
traefik.http.routers.https-0-mgk08sowg0ockk8s0s808880.rule=Host(`luxbet.site`) && PathPrefix(`/`)
traefik.http.routers.https-0-mgk08sowg0ockk8s0s808880.service=https-0-mgk08sowg0ockk8s0s808880
traefik.http.routers.https-0-mgk08sowg0ockk8s0s808880.tls.certresolver=letsencrypt
traefik.http.routers.https-0-mgk08sowg0ockk8s0s808880.tls=true

# HTTPS www.luxbet.site
traefik.http.routers.https-1-mgk08sowg0ockk8s0s808880.entryPoints=https
traefik.http.routers.https-1-mgk08sowg0ockk8s0s808880.middlewares=gzip
traefik.http.routers.https-1-mgk08sowg0ockk8s0s808880.rule=Host(`www.luxbet.site`) && PathPrefix(`/`)
traefik.http.routers.https-1-mgk08sowg0ockk8s0s808880.service=https-1-mgk08sowg0ockk8s0s808880
traefik.http.routers.https-1-mgk08sowg0ockk8s0s808880.tls.certresolver=letsencrypt
traefik.http.routers.https-1-mgk08sowg0ockk8s0s808880.tls=true

# --- NOVAS: acesso por IP (apenas HTTP) ---
traefik.http.routers.http-ip-luxbet.entryPoints=http
traefik.http.routers.http-ip-luxbet.middlewares=gzip
traefik.http.routers.http-ip-luxbet.rule=Host(`147.93.147.33`)
traefik.http.routers.http-ip-luxbet.service=http-0-mgk08sowg0ockk8s0s808880

# Services (já existentes)
traefik.http.services.http-0-mgk08sowg0ockk8s0s808880.loadbalancer.server.port=80
traefik.http.services.http-1-mgk08sowg0ockk8s0s808880.loadbalancer.server.port=80
traefik.http.services.https-0-mgk08sowg0ockk8s0s808880.loadbalancer.server.port=80
traefik.http.services.https-1-mgk08sowg0ockk8s0s808880.loadbalancer.server.port=80
```

---

## Depois de salvar

1. Salve as labels no Coolify.
2. Faça **Redeploy** do frontend para o Traefik recarregar.
3. Teste no 4G: `http://147.93.147.33`  
   - Pode aparecer “sua conexão não é segura” (normal).  
   - Ao continuar, o site deve abrir em vez de “Unavailable server”.
