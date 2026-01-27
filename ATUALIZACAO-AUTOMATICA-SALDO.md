# Atualização Automática de Saldo

## ✅ Implementado

O sistema agora atualiza o saldo automaticamente no frontend após transações nos jogos!

## 🔄 Como Funciona

### 1. Atualização Periódica
- **Frequência:** A cada 15 segundos quando o usuário está logado
- **Onde:** Em todas as páginas do site
- **Como:** Busca os dados atualizados do usuário via API `/api/auth/me`

### 2. Atualização ao Voltar para a Aba
- **Quando:** Usuário volta para a aba do navegador
- **Evento:** `window focus`
- **Ação:** Atualiza saldo imediatamente

### 3. Atualização ao Voltar para a Página
- **Quando:** Página fica visível novamente (não está mais oculta)
- **Evento:** `document visibilitychange`
- **Ação:** Atualiza saldo imediatamente

### 4. Atualização Durante o Jogo
- **Frequência:** A cada 10 segundos enquanto está na página do jogo
- **Onde:** Apenas na página `/game/:gameCode`
- **Motivo:** Durante o jogo, as transações acontecem mais frequentemente

## 📊 Fluxo Completo

```
1. Usuário joga e aposta R$ 10
   ↓
2. IGameWin chama nosso /gold_api
   ↓
3. Backend debita R$ 10 do saldo (user.balance = 990)
   ↓
4. Frontend atualiza automaticamente:
   - A cada 15 segundos (em qualquer página)
   - A cada 10 segundos (na página do jogo)
   - Quando volta para a aba
   - Quando página fica visível
   ↓
5. Saldo exibido no header atualiza automaticamente ✅
```

## 🎯 Resultado

**O saldo agora atualiza automaticamente sem precisar recarregar a página!**

- ✅ Atualização periódica (15s em geral, 10s durante jogo)
- ✅ Atualização ao voltar para a aba
- ✅ Atualização ao voltar para a página
- ✅ Saldo sempre sincronizado com o backend

## 🔧 Implementação Técnica

### AuthContext (`frontend/src/contexts/AuthContext.tsx`)
- Adicionado `useEffect` que monitora `token` e `user`
- Configura intervalos e event listeners para atualização automática
- Limpa listeners ao desmontar componente

### Game Page (`frontend/src/pages/Game.tsx`)
- Componente `GameBalanceUpdater` para atualização durante o jogo
- Atualização mais frequente (10s) durante o jogo
- Atualização ao voltar para a aba/página

## ⚙️ Configuração

### Intervalos de Atualização
- **Páginas gerais:** 15 segundos
- **Página do jogo:** 10 segundos

Para alterar os intervalos, edite:
- `AuthContext.tsx`: linha com `15000` (15 segundos)
- `Game.tsx`: linha com `10000` (10 segundos)

## 📝 Notas

- As atualizações são feitas de forma assíncrona e não bloqueiam a interface
- Se o usuário não estiver logado, nenhuma atualização é feita
- Os event listeners são limpos corretamente ao desmontar componentes
- Não há impacto significativo na performance (requisições leves)

---

**Data:** 2026-01-27
**Status:** ✅ Implementado e Funcionando
