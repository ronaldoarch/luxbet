# Cloudflare – checklist para abrir no 4G

Se o site ainda não abre no 4G depois de colocar na Cloudflare, confira estes itens.

---

## 1. Propagação dos nameservers

Trocar os nameservers na Hostinger para os da Cloudflare pode levar **até 24–48 horas** (às vezes mais) para todas as redes (incluindo 4G) usarem a Cloudflare.

- **O que fazer:** Aguardar e testar de novo no 4G depois de algumas horas ou no dia seguinte.
- **Como conferir:** No celular no 4G, use um app como “DNS Lookup” ou acesse [dnschecker.org](https://dnschecker.org) e pesquise `luxbet.site`. Se ainda aparecer o IP antigo ou “não resolve” em vários servidores, a propagação não terminou.

---

## 2. DNS na Cloudflare

Em **Cloudflare** → **luxbet.site** → **DNS** → **Records**:

| Nome   | Tipo | Conteúdo        | Proxy     |
|--------|------|-----------------|-----------|
| `@`    | A    | 147.93.147.33   | Proxied (nuvem laranja) |
| `www`  | A    | 147.93.147.33   | Proxied   |
| `api`  | A    | 147.93.147.33   | Proxied   |

- **`@`** = domínio raiz (luxbet.site).
- **`www`** = www.luxbet.site (se alguém abrir com www).
- **Proxied** faz o tráfego passar pela Cloudflare (melhor para 4G e SSL).

Se faltar `www`, adicione um registro **A** com Nome `www`, Conteúdo `147.93.147.33`, Proxy **Proxied**.

---

## 3. SSL/TLS (certificado)

Se aparecer “This hostname is not covered by a certificate” ou o navegador no 4G mostrar erro de certificado/HTTPS, o site pode “não abrir” por causa disso.

- **Cloudflare** → **SSL/TLS** → **Overview**  
  - Modo: **Full** ou **Full (strict)** (não deixar em “Flexible” se o servidor tiver HTTPS).
- **SSL/TLS** → **Edge Certificates**  
  - **Universal SSL**: deve estar ativo (On).  
  - Se estiver “Pending” ou com erro, aguardar ou ver CAA (abaixo).

---

## 4. CAA (se o certificado não for emitido)

Registros **CAA** podem impedir a Cloudflare de emitir o certificado. Se o Universal SSL não ativar ou continuar “not covered”:

- Em **DNS** → **Records**, veja os registros **CAA**.
- Se quiser que a Cloudflare emita o certificado, pode ser preciso adicionar uma CAA que permita a CA da Cloudflare ou ajustar/remover CAA conforme a [documentação da Cloudflare](https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/).

---

## 5. Firewall / segurança (Cloudflare)

Se o 4G estiver sendo bloqueado:

- **Security** → **WAF** ou **Firewall**: ver se há regras bloqueando país, IP ou “bot”.
- **Security** → **Settings** → **Security Level**: testar em **Medium** (evitar “I’m Under Attack” no início).
- **Bot Fight Mode**: se estiver On, pode bloquear alguns acessos; pode testar desligar para ver se o 4G abre.

---

## 6. Teste no 4G

- **Apagar cache / abrir em aba anônima** no celular (4G) e acessar `https://luxbet.site`.
- Se der **ERR_NAME_NOT_RESOLVED**: ainda é DNS (propagação ou 4G usando DNS que não atualizou).
- Se abrir mas der **erro de certificado / conexão não segura**: ajustar SSL/TLS e certificado (itens 3 e 4).
- Se a página **não carregar** (timeout, 502, 503): pode ser origem (Coolify/servidor) ou regra/firewall na Cloudflare (item 5).

---

## Resumo rápido

| O que verificar | Onde na Cloudflare |
|-----------------|--------------------|
| Registros A para @, www, api (Proxied) | DNS → Records |
| Modo SSL Full ou Full (strict) | SSL/TLS → Overview |
| Universal SSL ativo | SSL/TLS → Edge Certificates |
| Sem bloqueio no firewall | Security → WAF / Firewall |
| Aguardar propagação (24–48 h) | Nameservers na Hostinger |

Depois de tudo certo, o domínio tende a abrir no 4G; se ainda não abrir, o mais comum é **propagação** (4G ainda usando DNS antigo) ou **erro de certificado** no navegador.
