# 🔧 Troubleshooting - Erro de SSH no Coolify

## 🐛 Problema

Erro durante o deploy no Coolify:

```
SSH connection failed. Retrying... (Attempt 1/3, waiting 2s)
Error: kex_exchange_identification: read: Connection reset by peer
Error: Command execution failed (exit code 255): mkdir -p /data/coolify/applications/...
```

---

## 🔍 Causas Possíveis

### 1. **Servidor SSH sobrecarregado ou reiniciando**
- O servidor pode estar processando muitas requisições
- O servidor pode estar reiniciando ou atualizando

### 2. **Problemas de rede/firewall**
- Firewall bloqueando conexões SSH
- Problemas de rede temporários
- Timeout de conexão

### 3. **Permissões no servidor**
- Diretório `/data/coolify/applications/` sem permissões adequadas
- Usuário do Coolify sem permissões de escrita

### 4. **Servidor offline ou inacessível**
- Servidor pode estar offline
- Problemas de DNS
- IP do servidor mudou

---

## ✅ Soluções

### Solução 1: Aguardar e Tentar Novamente

**Mais comum**: Problemas temporários de rede ou servidor sobrecarregado.

1. **Aguarde 5-10 minutos**
2. **Tente fazer deploy novamente** no Coolify
3. O Coolify já faz retry automático (3 tentativas)

---

### Solução 2: Verificar Status do Servidor

1. **Acesse o servidor** onde o Coolify está rodando
2. **Verifique se o servidor está online**:
   ```bash
   ping seu-servidor.com
   ```

3. **Verifique se o SSH está funcionando**:
   ```bash
   ssh usuario@seu-servidor.com
   ```

4. **Verifique recursos do servidor**:
   ```bash
   # CPU e memória
   top
   # ou
   htop
   
   # Espaço em disco
   df -h
   ```

---

### Solução 3: Verificar Permissões no Servidor

1. **Acesse o servidor via SSH**
2. **Verifique se o diretório existe e tem permissões**:
   ```bash
   ls -la /data/coolify/applications/
   ```

3. **Crie o diretório manualmente se não existir**:
   ```bash
   sudo mkdir -p /data/coolify/applications/mgk08sowg0ockk8s0s808880
   sudo chown -R coolify:coolify /data/coolify/applications/
   sudo chmod -R 755 /data/coolify/applications/
   ```

   ⚠️ **Substitua `mgk08sowg0ockk8s0s808880` pelo ID real da sua aplicação**

4. **Verifique o usuário do Coolify**:
   ```bash
   whoami
   # Deve ser o usuário que roda o Coolify (geralmente 'coolify' ou seu usuário)
   ```

---

### Solução 4: Verificar Configuração SSH do Coolify

1. **No Coolify**, vá em **Settings** → **Servers**
2. **Verifique a configuração SSH** do servidor:
   - **Host**: IP ou domínio correto
   - **Port**: Porta SSH (geralmente 22)
   - **User**: Usuário correto
   - **Key**: Chave SSH válida

3. **Teste a conexão SSH**:
   - No Coolify, tente fazer **Test Connection** no servidor

---

### Solução 5: Reiniciar Serviços do Coolify

1. **Acesse o servidor**
2. **Reinicie o Coolify** (se estiver rodando como serviço):
   ```bash
   # Se usar Docker Compose
   cd /path/to/coolify
   docker-compose restart
   
   # Ou se usar systemd
   sudo systemctl restart coolify
   ```

3. **Verifique logs do Coolify**:
   ```bash
   docker logs coolify
   # ou
   journalctl -u coolify -f
   ```

---

### Solução 6: Limpar Cache e Tentar Novamente

1. **No Coolify**, vá em **Settings** → **Danger Zone**
2. **Clique em "Clean Build"** (se disponível)
3. **Tente fazer deploy novamente**

---

### Solução 7: Verificar Firewall

1. **No servidor**, verifique se o firewall está bloqueando:
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   
   # CentOS/RHEL
   sudo firewall-cmd --list-all
   ```

2. **Permita conexões SSH** se necessário:
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 22/tcp
   
   # CentOS/RHEL
   sudo firewall-cmd --permanent --add-service=ssh
   sudo firewall-cmd --reload
   ```

---

### Solução 8: Verificar Logs Detalhados

1. **No Coolify**, vá em **Logs** da aplicação
2. **Procure por erros anteriores** que possam indicar o problema
3. **Verifique logs do servidor**:
   ```bash
   # Logs do SSH
   sudo tail -f /var/log/auth.log
   # ou
   sudo journalctl -u ssh -f
   ```

---

## 🔄 Workaround Temporário

Se o problema persistir, você pode tentar:

### Opção 1: Deploy Manual

1. **Clone o repositório** no servidor:
   ```bash
   git clone https://github.com/ronaldoarch/luxbet.git
   cd luxbet
   git checkout main
   ```

2. **Faça build manual**:
   ```bash
   cd backend
   docker build -t luxbet-backend .
   ```

3. **Execute manualmente** (temporário):
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL=... \
     -e SECRET_KEY=... \
     --name luxbet-backend \
     luxbet-backend
   ```

### Opção 2: Usar Outro Servidor

Se possível, configure outro servidor temporariamente no Coolify para fazer o deploy.

---

## 📋 Checklist de Diagnóstico

- [ ] Servidor está online e acessível?
- [ ] SSH funciona manualmente (`ssh usuario@servidor`)?
- [ ] Recursos do servidor estão OK (CPU, memória, disco)?
- [ ] Diretório `/data/coolify/applications/` existe e tem permissões?
- [ ] Firewall não está bloqueando SSH?
- [ ] Configuração SSH no Coolify está correta?
- [ ] Coolify está rodando no servidor?
- [ ] Aguardou alguns minutos e tentou novamente?

---

## 🆘 Se Nada Funcionar

1. **Entre em contato com o suporte do Coolify**: https://coolify.io/docs
2. **Verifique o status do Coolify**: https://status.coolify.io
3. **Considere usar outro método de deploy** temporariamente:
   - Deploy manual via Docker
   - Outra plataforma (Railway, Render, Fly.io)

---

## 📝 Notas Importantes

- **Erros SSH são geralmente temporários** - tente novamente após alguns minutos
- **O Coolify faz retry automático** (3 tentativas) - aguarde
- **Problemas de rede podem causar esse erro** - verifique sua conexão
- **Servidor sobrecarregado pode causar timeouts** - verifique recursos

---

## 🔗 Referências

- [Coolify Documentation](https://coolify.io/docs)
- [Coolify Troubleshooting](https://coolify.io/docs/troubleshooting)
- [SSH Connection Issues](https://coolify.io/docs/troubleshooting/ssh)
