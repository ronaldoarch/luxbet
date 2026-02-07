# ⚡ Reduzir TTL para Acelerar Propagação DNS (URGENTE)

## 🚨 Problema Identificado

**Situação**: Site não funciona no 4G em **múltiplos estados do Brasil**  
**Causa**: TTL alto nos registros DNS = propagação lenta  
**Solução**: Reduzir TTL de `3600` para `300` segundos

---

## ✅ Solução: Reduzir TTL (FAZER AGORA)

### Passo 1: Acessar Hostinger

1. Acesse: https://hpanel.hostinger.com
2. Faça login
3. Vá em **Domínios** → Clique em **luxbet.site**
4. Clique em **DNS / Nameservers** ou **Gerenciar DNS**
5. Clique em **Editar**

---

### Passo 2: Editar Registros A e Reduzir TTL

**Para cada registro A**, edite o campo **TTL**:

#### Registro 1: Domínio Principal (@)

**Antes**:
```
Tipo: A
Nome: @
Valor: 147.93.147.33
TTL: 3600  ← ALTERAR PARA 300
```

**Depois**:
```
Tipo: A
Nome: @
Valor: 147.93.147.33
TTL: 300  ← ALTERADO!
```

#### Registro 2: WWW

**Antes**:
```
Tipo: A
Nome: www
Valor: 147.93.147.33
TTL: 3600  ← ALTERAR PARA 300
```

**Depois**:
```
Tipo: A
Nome: www
Valor: 147.93.147.33
TTL: 300  ← ALTERADO!
```

#### Registro 3: API

**Antes**:
```
Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 3600  ← ALTERAR PARA 300
```

**Depois**:
```
Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 300  ← ALTERADO!
```

---

### Passo 3: Salvar Alterações

1. **Salve** todas as alterações
2. **Confirme** que os 3 registros A agora têm TTL = `300`

---

## 📊 Diferença: TTL 3600 vs TTL 300

### Com TTL 3600 (1 hora):
- DNS espera até **1 hora** antes de atualizar cache
- Propagação demora **24-48 horas** para completar
- Usuários 4G podem ficar sem acesso por até 48h

### Com TTL 300 (5 minutos):
- DNS atualiza cache a cada **5 minutos**
- Propagação completa em **2-6 horas**
- Usuários 4G começam a funcionar muito mais rápido

**Resultado**: Propagação **4-8x mais rápida**! ⚡

---

## ⏱️ Timeline Após Reduzir TTL

| Tempo | O Que Acontece |
|-------|----------------|
| **Agora** | TTL reduzido para 300 |
| **+5 minutos** | Primeiros servidores DNS começam a atualizar |
| **+30 minutos** | Mais servidores DNS atualizando |
| **+1-2 horas** | Maioria dos servidores DNS atualizados |
| **+2-4 horas** | DNS de provedores móveis começando a atualizar |
| **+4-6 horas** | Maioria dos DNS de provedores móveis atualizados |
| **+12 horas** | Praticamente todos os DNS atualizados |

**Comparado com TTL 3600**: Propagação completa em 2-6h ao invés de 24-48h!

---

## 🔍 Como Verificar Se Funcionou

### Teste 1: Verificar TTL na Hostinger

1. Acesse Hostinger → DNS
2. Veja os registros A
3. Confirme que TTL está em `300` (não `3600`)

### Teste 2: Verificar Propagação em DNS Brasileiros

**Em https://dnschecker.org**:

1. Digite: `www.luxbet.site`
2. Teste DNS específicos de provedores brasileiros:
   - `200.160.2.3` (Vivo)
   - `200.222.2.90` (Claro)
   - `200.221.11.100` (TIM)
   - `201.6.96.245` (Oi)

3. Veja quantos retornam `147.93.147.33`
4. Após 2-4 horas, maioria deve retornar

### Teste 3: Testar no 4G

**Após 2-4 horas**:
1. No celular (4G), acesse: `https://luxbet.site`
2. Se funcionar: Propagação completou! ✅
3. Se não funcionar: Aguarde mais 2-4 horas

---

## ⚠️ IMPORTANTE: Verificações Adicionais

### Verificar Se Não Há CNAME para www

**Na Hostinger**:
- ❌ **NÃO deve haver** CNAME para `www`
- ✅ **Deve haver** registro A para `www`

**Se houver CNAME**:
1. **Remova** o CNAME
2. **Adicione** registro A para `www` → `147.93.147.33` com TTL `300`

### Verificar Se Todos Apontam para IP Correto

**Confirme que está assim**:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | 147.93.147.33 | **300** |
| A | www | 147.93.147.33 | **300** |
| A | api | 147.93.147.33 | **300** |

**Todos devem apontar para `147.93.147.33` com TTL `300`**

---

## 🎯 Por Que Isso Resolve o Problema?

### O Problema:

1. **TTL alto (3600)** = DNS espera 1 hora antes de atualizar
2. **Provedores móveis** têm múltiplos servidores DNS
3. **Cada servidor** espera até 1 hora antes de atualizar
4. **Propagação completa** demora 24-48 horas
5. **Usuários 4G** ficam sem acesso durante esse tempo

### A Solução:

1. **TTL baixo (300)** = DNS atualiza a cada 5 minutos
2. **Servidores DNS** atualizam muito mais rápido
3. **Propagação completa** em 2-6 horas
4. **Usuários 4G** começam a funcionar muito mais rápido

---

## 📝 Checklist Completo

### Na Hostinger:

- [ ] Acessei DNS / Nameservers
- [ ] Editei registro A para `@`
- [ ] Mudei TTL de `3600` para `300` no registro `@`
- [ ] Editei registro A para `www`
- [ ] Mudei TTL de `3600` para `300` no registro `www`
- [ ] Editei registro A para `api`
- [ ] Mudei TTL de `3600` para `300` no registro `api`
- [ ] Confirmei que não há CNAME para `www`
- [ ] Confirmei que todos apontam para `147.93.147.33`
- [ ] Salvei todas as alterações

### Após Reduzir TTL:

- [ ] Aguardei 1-2 horas
- [ ] Testei DNS de provedores brasileiros em dnschecker.org
- [ ] Vejo que mais servidores retornam `147.93.147.33`
- [ ] Testei no 4G após 2-4 horas
- [ ] Site funciona no 4G! ✅

---

## 🚀 Ação Imediata

**FAÇA AGORA** (5 minutos):

1. ✅ Acesse Hostinger
2. ✅ Edite os 3 registros A
3. ✅ Mude TTL de `3600` para `300`
4. ✅ Salve alterações
5. ⏳ Aguarde 2-4 horas
6. 🧪 Teste no 4G

**Isso vai acelerar a propagação DNS significativamente!** ⚡

---

## 💡 Dica Extra

**Após propagação completar**, você pode aumentar TTL novamente para `3600` se quiser (para reduzir carga nos servidores DNS), mas **agora é importante manter em `300`** para acelerar propagação.

**Status**: ⚡ Reduzir TTL = Propagação 4-8x mais rápida!
