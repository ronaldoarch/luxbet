# 🔧 Resolver Conflito: Contabo + Hostinger DNS

## 🚨 Problema Identificado

Você tem o domínio `luxbet.site` configurado em **dois lugares**:
1. **Contabo**: DNS Zone Management
2. **Hostinger**: Registros DNS

**Isso causa conflito!** Você precisa escolher **UM** provedor DNS apenas.

---

## ✅ Solução: Escolher Um Provedor DNS

### Opção 1: Usar Contabo (Recomendado se servidor está na Contabo)

Se seu servidor Coolify está na Contabo:

#### Passo 1: Configurar DNS na Contabo

1. Acesse: https://new.contabo.com/network/dns-management/dns
2. Clique em `luxbet.site` na lista
3. Adicione os registros:

```
Tipo: A
Nome: @ (ou deixe vazio)
Valor: 147.93.147.33
TTL: 3600

Tipo: A
Nome: www
Valor: 147.93.147.33
TTL: 3600

Tipo: A
Nome: api
Valor: 147.93.147.33
TTL: 3600
```

#### Passo 2: Alterar Nameservers na Hostinger

1. Na Hostinger, vá em **DNS / Nameservers**
2. Clique em **"Alterar Nameservers"**
3. Altere para os nameservers da Contabo (eles devem fornecer)
4. **Exemplo** (verifique na Contabo):
   ```
   ns1.contabo.com
   ns2.contabo.com
   ```
   Ou os nameservers específicos que a Contabo fornecer

#### Passo 3: Remover Registros DNS da Hostinger

Após mudar nameservers, os registros DNS na Hostinger serão ignorados. Mas é bom limpar:

1. Remova todos os registros A, CNAME, etc. da Hostinger
2. Deixe apenas os registros essenciais (MX, TXT se necessário)

---

### Opção 2: Usar Hostinger (Recomendado se mais simples)

Se preferir manter tudo na Hostinger:

#### Passo 1: Remover da Contabo

1. Na Contabo, remova a zona DNS `luxbet.site`
2. Ou simplesmente ignore (não vai causar problema se nameservers não apontarem para Contabo)

#### Passo 2: Configurar DNS na Hostinger

1. Na Hostinger, mantenha nameservers da Hostinger:
   ```
   ns1.dns-parking.com
   ns2.dns-parking.com
   ```

2. Configure registros DNS:
   ```
   Tipo: A
   Nome: @
   Valor: 147.93.147.33
   TTL: 3600

   Tipo: A
   Nome: www
   Valor: 147.93.147.33
   TTL: 3600

   Tipo: A
   Nome: api
   Valor: 147.93.147.33
   TTL: 3600
   ```

**⚠️ IMPORTANTE**: Se você criou CNAME `www` → `luxbet.site`, **remova** e use registro A em vez disso!

---

## 🔍 Como Saber Qual Usar?

### Use Contabo se:
- ✅ Servidor está na Contabo
- ✅ Quer gerenciar tudo em um lugar
- ✅ Contabo fornece nameservers próprios

### Use Hostinger se:
- ✅ Já está acostumado com Hostinger
- ✅ Nameservers já estão configurados na Hostinger
- ✅ Quer simplicidade

---

## ⚠️ Problema com CNAME www → luxbet.site

Você mencionou que criou CNAME `www` → `luxbet.site` na Hostinger.

**Isso pode causar loop!** Se `www` aponta para `luxbet.site` e ambos estão no mesmo servidor, pode haver problemas.

**Solução**: Use registro **A** para `www` apontando diretamente para o IP:

```
Tipo: A (NÃO CNAME)
Nome: www
Valor: 147.93.147.33
TTL: 3600
```

---

## 📋 Checklist de Configuração

### Se escolher Contabo:
- [ ] Adicionar registros A na Contabo
- [ ] Obter nameservers da Contabo
- [ ] Alterar nameservers na Hostinger
- [ ] Aguardar propagação (1-48h)
- [ ] Remover registros DNS da Hostinger (opcional)

### Se escolher Hostinger:
- [ ] Remover zona DNS da Contabo (ou ignorar)
- [ ] Manter nameservers da Hostinger
- [ ] Configurar registros A na Hostinger
- [ ] **Remover CNAME www** e usar registro A
- [ ] Aguardar propagação (1-2h)

---

## 🎯 Recomendação

**Para seu caso, recomendo usar Hostinger** porque:
1. Já está configurado lá
2. Nameservers já devem estar corretos
3. Mais simples de gerenciar

**Ações necessárias**:
1. **Remover CNAME `www` → `luxbet.site`** na Hostinger
2. **Adicionar registro A `www` → `147.93.147.33`** na Hostinger
3. **Ignorar ou remover** zona DNS da Contabo (se nameservers não apontam para Contabo, não causa problema)

---

## ⏱️ Após Configurar

1. **Salve alterações**
2. **Aguarde propagação**: 1-2 horas
3. **Verifique**: https://dnschecker.org
   - Digite: `www.luxbet.site`
   - Deve retornar: `147.93.147.33`
4. **Teste no 4G**: Após propagação

---

## 🚨 Importante

**Você NÃO pode ter DNS configurado em dois lugares ao mesmo tempo!**

- Se nameservers apontam para **Hostinger** → Configure DNS na **Hostinger**
- Se nameservers apontam para **Contabo** → Configure DNS na **Contabo**

**Verifique os nameservers atuais**:
- Na Hostinger, veja quais nameservers estão configurados
- Se são da Hostinger (`ns1.dns-parking.com`), configure DNS na Hostinger
- Se são da Contabo, configure DNS na Contabo
