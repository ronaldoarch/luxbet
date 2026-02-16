# Troubleshooting: Login após troca de domínio

## Problema
Alguns usuários relatam "senha incorreta" após a troca de domínio, mesmo com a senha correta.

## Causas possíveis e soluções

### 1. URL da API incorreta (mais comum)
**Causa:** O frontend estava apontando para o domínio errado (ex: `luxbet.com.br` em vez de `api.luxbet.com.br`).

**Solução aplicada:** O `apiConfig` agora detecta automaticamente o subdomínio `api.` para novos domínios. Ex: `luxbet.com.br` → `api.luxbet.com.br`.

**Verificação:** Configure `VITE_API_URL` no build do frontend para o novo domínio:
```
VITE_API_URL=https://api.novodominio.com
```

### 2. Espaços ao colar usuário/senha
**Causa:** Usuários copiam/colam com espaços no início ou fim.

**Solução aplicada:** O backend agora faz `strip()` em username e password antes de validar.

### 3. Redefinir senha (usuários afetados)
Se o usuário continua sem conseguir entrar após as correções acima:

1. Acesse o painel admin → Usuários
2. Localize o usuário (por username, email ou telefone)
3. Use o endpoint `POST /api/admin/users/{user_id}/reset-password` com body:
   ```json
   { "new_password": "nova_senha_temporaria" }
   ```
4. Informe a nova senha ao usuário e peça para alterar após o primeiro login

### 4. Banco de dados migrado
Se houve migração de servidor/banco e os hashes de senha foram corrompidos (encoding, truncation), a única solução é redefinir a senha manualmente via admin (item 3).

## Checklist de deploy após troca de domínio

- [ ] `VITE_API_URL` configurado no frontend (Coolify/CI)
- [ ] CORS permitindo o novo domínio (ou `*` em desenvolvimento)
- [ ] Backend acessível em `https://api.novodominio.com`
- [ ] Rebuild do frontend após alterar variáveis de ambiente
