# Acesso via 4G – usar IP direto

## Situação

- **http** e **https** em `luxbet.site` dão **ERR_NAME_NOT_RESOLVED** no 4G.
- No WiFi funciona.
- DNS está correto (todos apontam para `147.93.147.33`).

Conclusão: o **DNS do provedor 4G** não está resolvendo o domínio. Não é problema de código nem de SSL.

---

## Solução 1: Acessar pelo IP (recomendado para 4G)

No celular/computador em **4G**, digite no navegador:

```
http://147.93.147.33
```

- Pode aparecer aviso de “conexão não privada” ou “certificado inválido” (normal ao usar IP).
- Use “Avançado” → “Continuar mesmo assim” (ou equivalente) para abrir o site.
**Se depois disso aparecer "Unavailable server"**: o proxy (Coolify/Traefik) não está configurado para aceitar acesso pelo IP. É preciso **adicionar o IP como domínio** no Coolify para o frontend. Veja o guia: **[CORRIGIR-ACESSO-POR-IP-COOLIFY.md](CORRIGIR-ACESSO-POR-IP-COOLIFY.md)**.

Quando o Coolify estiver configurado para o IP, o site e a API funcionam pelo IP; o aviso de "conexão não segura" é só porque o certificado é do domínio, não do IP.

Guarde esse endereço ou coloque nos favoritos para usar quando estiver no 4G.

---

## Solução 2: Trocar o DNS do aparelho (4G)

Se quiser continuar usando o **nome** `luxbet.site` no 4G, configure um DNS que resolva corretamente.

### Android (4G)

1. **Configurações** → **Rede e Internet** → **Internet**.
2. Toque no ícone de engrenagem ao lado da rede **4G/Dados móveis**.
3. **Avançado** → **DNS privado** (ou “Nome dos servidores DNS”).
4. Escolha **Particular** e digite: `dns.google` ou `one.one.one.one`.  
   Ou use **Manual** e coloque: `8.8.8.8` e `8.8.4.4` (Google) ou `1.1.1.1` e `1.0.0.1` (Cloudflare).

### iPhone (4G)

O iOS não permite alterar DNS só para dados móveis de forma nativa. Opções:

- Usar **Wi‑Fi** quando precisar do domínio, ou  
- Usar o **IP direto** no 4G: `http://147.93.147.33`.

---

## Solução 3: Encurtador / QR Code para o IP

Para facilitar para os usuários no 4G:

1. Crie um link curto que aponte para: `http://147.93.147.33`
2. Ou um **QR Code** que abra: `http://147.93.147.33`
3. Divulgue: “Se o site não abrir no 4G, use este link ou escaneie o QR Code”.

Assim todo mundo pode acessar pelo IP sem decorar o número.

---

## Solução 4: Colocar o site atrás da Cloudflare (DNS)

Colocar o domínio **luxbet.site** na **Cloudflare** (DNS + proxy) pode melhorar a resolução em redes que hoje não resolvem:

1. Crie conta em [cloudflare.com](https://www.cloudflare.com).
2. Adicione o domínio **luxbet.site** e troque os nameservers no registrador (Hostinger, etc.) para os da Cloudflare.
3. Na Cloudflare, crie registro **A** para `@` e `www` (e `api` se usar) apontando para `147.93.147.33`.
4. Deixe o proxy (nuvem laranja) ativado.

Muitas redes 4G usam DNS que resolvem bem os domínios da Cloudflare, o que pode fazer o nome `luxbet.site` passar a funcionar no 4G.

---

## Resumo

| Onde     | Como acessar                    |
|----------|----------------------------------|
| WiFi     | `https://luxbet.site` (normal)  |
| 4G       | `http://147.93.147.33` (IP) ou DNS 8.8.8.8/1.1.1.1 |

Sem HTTPS no 4G dá o mesmo erro porque o problema é **DNS**, não certificado. A solução prática é **usar o IP** ou **mudar o DNS** no 4G.
