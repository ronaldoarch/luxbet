# 🔧 Resolver Conflito DNS - Registro www

## 🚨 Problema Identificado

**Erro**: "O registro de recurso DNS não é válido ou está em conflito com outro registro de recurso"

**Causa**: Já existe um registro **CNAME** para `www` apontando para `luxbet.site`. Você não pode ter um registro **A** e um **CNAME** para o mesmo nome ao mesmo tempo.

---

## ✅ Solução: Remover CNAME e Adicionar A

### Passo 1: Remover o CNAME Existente

1. Na tabela de registros DNS, encontre o registro:
   ```
   Tipo: CNAME
   Nome: www
   Conteúdo: luxbet.site
   ```

2. Clique no botão **"Remover"** (vermelho) ao lado desse registro

3. Confirme a remoção

---

### Passo 2: Adicionar Registro A para www

Agora que o CNAME foi removido, você pode adicionar o registro A:

1. No formulário "Adicionar registro", preencha:
   - **Tipo**: `A` (já está selecionado)
   - **Nome**: `www`
   - **Aponta para**: `147.93.147.33`
   - **TTL**: `300` (ou `3600`)

2. Clique em **"Adicionar registro"**

3. Agora deve funcionar sem erro! ✅

---

## 📋 Configuração Final Esperada

Após fazer as alterações, você deve ter:

| Tipo | Nome | Conteúdo | TTL |
|------|------|----------|-----|
| A | @ | `147.93.147.33` | 300 |
| A | www | `147.93.147.33` | 300 |
| A | api | `147.93.147.33` | 300 |

**Todos os registros A apontando para o mesmo IP.**

---

## ⚠️ Por Que Não Pode Ter CNAME e A Juntos?

- **CNAME**: Aponta um nome para outro nome (ex: `www` → `luxbet.site`)
- **A**: Aponta um nome diretamente para um IP (ex: `www` → `147.93.147.33`)

DNS não permite ambos para o mesmo nome porque causaria ambiguidade:
- O DNS não saberia se deve resolver `www` para o IP do CNAME ou usar o IP do registro A diretamente

**Regra**: Escolha UM tipo de registro por nome:
- **CNAME**: Se quiser que `www` aponte para outro domínio
- **A**: Se quiser que `www` aponte diretamente para um IP

**Para seu caso, use registro A** (mais direto e performático).

---

## ✅ Após Corrigir

1. **Salve as alterações**
2. **Aguarde propagação**: 5 minutos a 2 horas
3. **Verifique**: https://dnschecker.org
   - Digite: `www.luxbet.site`
   - Verifique se o IP `147.93.147.33` aparece
4. **Teste no 4G**: Após propagação, teste no celular

---

## 🔍 Verificar se Funcionou

### Teste 1: DNS Checker
```
https://dnschecker.org
Digite: www.luxbet.site
Deve retornar: 147.93.147.33
```

### Teste 2: Terminal
```bash
nslookup www.luxbet.site
# Deve retornar: 147.93.147.33
```

### Teste 3: Navegador
Após propagação DNS:
- Acesse: `https://www.luxbet.site`
- Deve carregar normalmente

---

## 📝 Resumo

1. ❌ **Problema**: CNAME `www` conflita com registro A `www`
2. ✅ **Solução**: Remover CNAME, adicionar registro A
3. ⏱️ **Tempo**: 5 minutos para configurar + 1-2h para propagar
4. 🧪 **Teste**: Após propagação, teste no 4G
