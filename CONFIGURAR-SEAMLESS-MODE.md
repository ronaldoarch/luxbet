# 🔵 Como Configurar para Seamless Mode

## ✅ Vantagens do Seamless Mode

- ✅ **Saldo único** - fica apenas no nosso banco de dados
- ✅ **Sem sincronização manual** - não precisa transferir saldo antes/depois do jogo
- ✅ **Sem oscilação de saldo** - saldo não zera durante o jogo
- ✅ **Mais controle** - temos controle total sobre o saldo
- ✅ **Saque mais simples** - saldo sempre disponível para saque
- ✅ **Menos chamadas API** - IGameWin chama nosso site apenas quando necessário

---

## 🔧 Configuração no Painel IGameWin

### Passo 1: Configurar Tipo de API

1. **Acesse** o painel administrativo do IGameWin
2. **Vá em** "Agente de atualização" ou "Agent Update"
3. **Localize** o campo **"Tipo de API"** ou **"API Type"**
4. **Selecione:** "Seamless" ou "Modo Seamless" ou "Seamless Mode"
   - ⚠️ **NÃO selecione** "Contínuo", "Transfer" ou "Continuous"

### Passo 2: Configurar Ponto Final do Site

1. **Localize** o campo **"Ponto final do site"** ou **"Site Endpoint"**
2. **Configure como:** URL do seu backend (ex: `https://api.luxbet.site` ou `https://api.luxbets.com.br`)
   - ⚠️ **IMPORTANTE:** Deve ser a URL do **backend** (não do frontend)
   - ⚠️ **NÃO inclua** `/gold_api` no final - apenas a URL base do backend
   - O IGameWin automaticamente adiciona `/gold_api` ao final
3. **Salve** as configurações

**Troca de domínio?** Se mudou de domínio e o saldo não desconta, veja [DOMINIO-NOVO-CONFIG.md](./DOMINIO-NOVO-CONFIG.md).

### Passo 3: Aguardar Aplicação

1. **Aguarde** 2-5 minutos para a configuração ser aplicada
2. **Teste** iniciando um jogo

---

## 🔍 Como Verificar se Está em Seamless Mode

### Nos Logs do Backend:

Quando você tentar iniciar um jogo, deve ver:

```
[Launch Game] 🔍 Detectando modo de operação do IGameWin
[Launch Game] Verificando saldo do usuário no IGameWin para detectar modo...
[Launch Game] ✅ DETECTADO: Modo Seamless (Seamless Mode)
[Launch Game] O IGameWin está configurado para chamar nosso /gold_api
[Launch Game] Não faremos transferências - o saldo fica no nosso banco
[Launch Game] ⚡ Modo Seamless detectado - pulando transferências
[Launch Game] ✅ JOGO LANÇADO EM MODO SEAMLESS
```

**Se você vê "Modo Seamless detectado"** → Está em Seamless Mode ✅

**Se você vê "Modo Transfer"** → Ainda está em Transfer Mode ⚠️

### Durante o Jogo:

Quando você jogar, deve ver nos logs:

```
[Gold API] ⚡⚡⚡ CHAMADA RECEBIDA NO /gold_api ⚡⚡⚡
[Gold API] Método: user_balance
[Gold API] Método: transaction
```

**Se você vê chamadas ao `/gold_api`** → Seamless Mode está funcionando ✅

---

## 📋 Como Funciona no Seamless Mode

### Fluxo Automático:

1. **Usuário clica** para iniciar jogo
2. **Backend detecta** Seamless Mode (recebe `ERROR_GET_BALANCE_END_POINT`)
3. **Backend cria usuário** no IGameWin (se não existir)
4. **Backend chama** `game_launch` no IGameWin
5. **IGameWin retorna** URL do jogo
6. **Jogo carrega** e chama nosso `/gold_api` para buscar saldo
7. **Durante o jogo**, IGameWin chama `/gold_api` para processar transações
8. **Saldo permanece** no nosso banco durante todo o processo

### Vantagens:

- ✅ **Não precisa sincronizar** - saldo sempre no nosso banco
- ✅ **Saque funciona direto** - saldo sempre disponível
- ✅ **Sem oscilação** - saldo não zera durante o jogo
- ✅ **Menos complexidade** - não precisa gerenciar dois saldos

---

## 🔄 Comparação: Seamless vs Transfer Mode

| Aspecto | Seamless Mode | Transfer Mode |
|---------|---------------|---------------|
| **Onde fica o saldo?** | No nosso banco | No IGameWin |
| **Sincronização** | Automática (via `/gold_api`) | Manual (antes/depois do jogo) |
| **Transferências** | Não precisa | Precisa fazer manualmente |
| **Saldo durante jogo** | Permanece no banco | Transferido para IGameWin |
| **Saque** | Funciona direto | Precisa sincronizar primeiro |
| **Complexidade** | Menor (apenas endpoint) | Maior (gerenciar dois saldos) |

---

## ✅ Checklist de Configuração

- [ ] Acessou painel IGameWin
- [ ] Configurou "Tipo de API" como "Seamless"
- [ ] Configurou "Ponto final do site" como `https://api.luxbet.site` (URL do backend)
- [ ] Salvou configurações
- [ ] Aguardou 2-5 minutos
- [ ] Testou iniciar um jogo
- [ ] Verificou logs - deve mostrar "Modo Seamless detectado"
- [ ] Verificou logs durante jogo - deve mostrar chamadas ao `/gold_api`

---

## 🎯 Resultado Esperado

Após configurar Seamless Mode:

1. **Saldo não zera** durante o jogo ✅
2. **Não precisa sincronizar** manualmente ✅
3. **Saque funciona** diretamente ✅
4. **Menos problemas** de saldo ✅

---

## 📝 Notas Importantes

- O código **detecta automaticamente** o modo - não precisa configurar nada no código
- O endpoint `/gold_api` **já está implementado** e funcionando
- Se receber `ERROR_GET_BALANCE_END_POINT`, significa que está tentando usar Seamless Mode mas o endpoint não está acessível
- Verifique se o campo "Ponto final do site" está configurado corretamente
- Aguarde alguns minutos após salvar as configurações no painel IGameWin

---

## 🆘 Troubleshooting

### Problema: Ainda está em Transfer Mode

**Solução:**
1. Verifique se o campo "Tipo de API" está como "Seamless"
2. Aguarde mais tempo (até 10 minutos)
3. Limpe cache do navegador
4. Tente iniciar um jogo novamente

### Problema: Erro `ERROR_GET_BALANCE_END_POINT` ou saldo não desconta

**Solução:**
1. Verifique se o campo "Ponto final do site" está configurado com a URL do seu backend (ex: `https://api.luxbets.com.br`)
2. **Se trocou de domínio:** atualize "Ponto final do site" para a nova URL. Veja [DOMINIO-NOVO-CONFIG.md](./DOMINIO-NOVO-CONFIG.md)
3. Verifique se o endpoint `/gold_api` está acessível publicamente
4. Teste acessando: `https://SEU-BACKEND/gold_api` (deve retornar JSON)

### Problema: Não vejo chamadas ao `/gold_api` nos logs

**Solução:**
1. Verifique se está realmente em Seamless Mode (veja logs ao iniciar jogo)
2. Verifique se o campo "Ponto final do site" está correto
3. Aguarde alguns minutos após configurar
