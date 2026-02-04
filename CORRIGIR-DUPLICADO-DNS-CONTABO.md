# 🔧 Corrigir Erro DNS - Registro Duplicado na Contabo

## 🚨 Problema Identificado

**Erro**: "Registro de Entrada não é único pelo nome"

**Causa**: Existem **dois registros A** para `luxbet.site` apontando para `147.93.147.33`

**Solução**: Remover um dos registros duplicados

---

## ✅ Solução: Remover Registro Duplicado

### Passo 1: Remover um dos Registros A Duplicados

Na lista de registros DNS da Contabo:

1. Encontre os **dois registros A** para `luxbet.site`:
   ```
   luxbet.site  A  86400  147.93.147.33  (duplicado 1)
   luxbet.site  A  86400  147.93.147.33  (duplicado 2)
   ```

2. Clique no ícone de **lixeira** (🗑️) ao lado de **um** dos registros duplicados

3. Confirme a remoção

4. **Mantenha apenas UM** registro A para `luxbet.site`

---

## 📋 Configuração Correta Esperada

Após remover o duplicado, você deve ter:

| Nome | Tipo | TTL | Valor |
|------|------|-----|-------|
| `luxbet.site` | A | 86400 | 147.93.147.33 |
| `www.luxbet.site` | A | 86400 | 147.93.147.33 |
| `api.luxbet.site` | A | 86400 | 147.93.147.33 |
| `mail.luxbet.site` | A | 86400 | 147.93.147.33 |
| `luxbet.site` | MX | 86400 | mail.luxbet.site |
| `luxbet.site` | NS | 86400 | ns1.contabo.net |
| `luxbet.site` | NS | 86400 | ns2.contabo.net |
| `luxbet.site` | NS | 86400 | ns3.contabo.net |
| `luxbet.site` | SOA | 86400 | (configuração padrão) |

**⚠️ IMPORTANTE**: Verifique se existe registro A para `api.luxbet.site`. Se não existir, adicione!

---

## ➕ Adicionar Registro para API (se não existir)

Se não houver registro A para `api.luxbet.site`:

1. Clique em **"Adicionar um novo registro de recursos"**
2. Preencha:
   - **Nome**: `api`
   - **Tipo**: `A`
   - **TTL**: `86400` (ou `3600`)
   - **Valor**: `147.93.147.33`
3. Salve

---

## ✅ Após Corrigir

1. **O erro deve desaparecer** após remover o duplicado
2. **Salve as alterações**
3. **Aguarde propagação**: 1-2 horas
4. **Verifique**: https://dnschecker.org
   - Digite: `luxbet.site`
   - Deve retornar: `147.93.147.33` (apenas uma vez)

---

## 🔍 Verificar Configuração Final

Após corrigir, verifique se tem:

- ✅ **1 registro A** para `luxbet.site` → `147.93.147.33`
- ✅ **1 registro A** para `www.luxbet.site` → `147.93.147.33`
- ✅ **1 registro A** para `api.luxbet.site` → `147.93.147.33`
- ✅ **Registros NS** corretos (ns1.contabo.net, ns2.contabo.net, ns3.contabo.net)
- ✅ **Sem duplicados**

---

## 📝 Resumo

1. ❌ **Problema**: Dois registros A para `luxbet.site` (duplicado)
2. ✅ **Solução**: Remover um dos registros duplicados
3. ➕ **Verificar**: Se existe registro A para `api.luxbet.site`
4. ⏱️ **Aguardar**: Propagação DNS após corrigir

**Ação imediata**: Remova um dos registros A duplicados para `luxbet.site`!
