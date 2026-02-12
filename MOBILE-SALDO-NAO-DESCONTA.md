# 📱 Saldo não desconta no celular (PC funciona)

Se o saldo **desconta no PC** mas **não desconta no celular**, o problema costuma ser de rede ou configuração específica do mobile.

---

## 🔍 Diagnóstico rápido

### 1. Conferir logs do backend

Jogue no **celular** e observe os logs do backend (Coolify ou terminal):

**Se aparecer:**
```
[Gold API] ⚡⚡⚡ CHAMADA RECEBIDA NO /gold_api ⚡⚡⚡
[Gold API] Método: user_balance
[Gold API] Método: transaction
```
→ As requisições chegam ao backend. O problema é outro (ex.: resposta não tratada corretamente pelo jogo).

**Se não aparecer nada:**
→ As requisições **não chegam** ao backend. Causa provável: rede ou DNS no celular.

---

## 🎯 Causas mais prováveis

### 1. Rede do celular (4G) diferente do PC

- **PC**: WiFi (casa/escritório) – DNS resolve, tudo funciona.
- **Celular**: 4G – DNS pode não resolver ou operadora pode bloquear.

**O que fazer:**
- Teste o celular no **mesmo WiFi do PC**. Se funcionar, o problema é na rede 4G.
- Nesse caso, vale usar outro domínio (como já feito com luxbets.com.br) ou verificar bloqueio/DNS da operadora.

---

### 2. Configuração separada para mobile no IGameWin

Alguns provedores têm:

- **"Ponto final do site"** para desktop
- **"Ponto final do site (mobile)"** ou **"Site Endpoint (Mobile)"**

**O que fazer:**
- No painel IGameWin, procure campos como:
  - Site Endpoint (Mobile)
  - Mobile Site URL
  - Ponto final do site (mobile)
- Se existir, configure com a mesma URL do backend: `https://api.luxbets.com.br`
- Se não tiver certeza, consulte o suporte do IGameWin.

---

### 3. URL diferente para mobile

Se o frontend mobile usa outro domínio (ex.: `m.luxbets.com.br`), confira se:

- O backend está acessível em `https://api.luxbets.com.br`
- O IGameWin está configurado com `https://api.luxbets.com.br` (não `https://m.luxbets.com.br` ou outra URL de frontend)

---

## ✅ Checklist

- [ ] Conferir logs do backend jogando no celular
- [ ] Testar celular no mesmo WiFi do PC
- [ ] Verificar se existe configuração de mobile no painel IGameWin
- [ ] Confirmar que "Ponto final do site" está como `https://api.luxbets.com.br`
- [ ] Se der erro em 4G, considerar DNS ou bloqueio da operadora

---

## 📞 Suporte IGameWin

Se as requisições não chegam no mobile e o WiFi funciona, vale perguntar ao suporte do IGameWin:

- “Existe configuração separada para mobile?”
- “O endpoint é chamado a partir do navegador do usuário ou dos seus servidores?”
- “Há restrições ou bloqueios para chamadas vindas de celulares?”
