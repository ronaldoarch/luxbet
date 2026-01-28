# Melhorias Identificadas

## 🐛 Bugs Críticos

### 1. Discrepância entre Saldo Total e Saldo Disponível para Saque
**Problema:** Usuário tem R$ 12,00 no total mas só pode sacar R$ 1,04
**Causa Provável:** Saldo pode estar bloqueado no IGameWin (Transfer Mode)
**Solução:** 
- Calcular saldo disponível considerando saldo no IGameWin
- Criar endpoint que retorna saldo disponível para saque = nosso banco + IGameWin (se sincronizado)
- Ou sincronizar saldo do IGameWin antes de permitir saque

### 2. Saldo Aumenta Sozinho no Jogo (Alguns Centavos)
**Problema:** Saldo aumenta automaticamente durante o jogo
**Causa Provável:** 
- Sincronização automática muito frequente causando race conditions
- Problema na sincronização entre nosso banco e IGameWin
**Solução:**
- Verificar lógica de sincronização automática
- Adicionar validações para evitar atualizações duplicadas
- Implementar lock/transação para evitar race conditions

### 3. Depósito Não Contabiliza Corretamente - Só Conta o Último
**Problema:** Quando faz múltiplos depósitos, apenas o último é contabilizado
**Causa Provável:** 
- Webhook pode estar atualizando o mesmo depósito múltiplas vezes
- Verificação de status pode estar incorreta
- Race condition no processamento de webhooks
**Solução:**
- Verificar se depósito já foi aprovado antes de adicionar saldo novamente
- Adicionar validação para evitar processamento duplicado de webhooks
- Verificar lógica em `webhook_pix_cashin` e `webhook_nxgate_pix_cashin`

## 🎨 Melhorias de UX

### 4. Mostrar Saldo na Tela Principal (Home)
**Problema:** Usuário precisa entrar no perfil para ver o saldo
**Solução:** 
- Adicionar componente de saldo no Header ou HeroBanner
- Mostrar saldo disponível de forma visível na home
- Atualizar automaticamente quando usuário está logado

### 5. Reduzir Tamanho das Imagens dos Jogos
**Problema:** Imagens muito grandes dificultam visualização
**Solução:**
- Reduzir tamanho das imagens no componente GameCards
- Ajustar CSS para imagens menores mas ainda visíveis
- Melhorar layout para mostrar mais jogos por vez

### 6. Facilitar Processo de Cadastro
**Problema:** Formulário de cadastro pode ser simplificado
**Solução:**
- Reduzir campos obrigatórios se possível
- Melhorar validação em tempo real
- Adicionar autocomplete para CPF/telefone
- Simplificar layout do formulário

## 📋 Prioridade de Implementação

1. **ALTA:** Bug de depósito não contabilizar corretamente (#3)
2. **ALTA:** Discrepância de saldo para saque (#1)
3. **MÉDIA:** Saldo aumenta sozinho (#2)
4. **MÉDIA:** Mostrar saldo na home (#4)
5. **BAIXA:** Reduzir imagens dos jogos (#5)
6. **BAIXA:** Facilitar cadastro (#6)
