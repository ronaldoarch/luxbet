# Configurar Persistent Storage para Uploads (Banners e Logos)

## 🐛 Problema

Os banners e logos quebram após cada deploy porque os arquivos são salvos em `/app/uploads` dentro do container, mas esse diretório **não está em um volume persistente**. Quando o container é recriado durante o deploy, os arquivos são perdidos.

## ✅ Solução

Adicionar um **segundo Persistent Storage** especificamente para o diretório de uploads.

---

## 📋 Passo a Passo no Coolify

### 1. Acessar Configuração de Persistent Storage

1. No Coolify, vá para seu deployment `luxbet`
2. Clique em **"Configuration"** no menu lateral
3. Clique em **"Persistent Storage"** no menu lateral esquerdo

### 2. Adicionar Novo Volume para Uploads

1. Na seção **"Volumes"**, clique em **"Add Volume"** ou **"Create Volume"**
2. Configure o novo volume:
   - **Source Path**: `/` (deixe como está - será criado automaticamente)
   - **Destination Path**: `/app/uploads` ⚠️ **IMPORTANTE: Este é o caminho dentro do container**
   - **Name**: `luxbet-uploads` (ou qualquer nome descritivo)

3. Clique em **"Save"** ou **"Create"**

### 3. Verificar Configuração

Após adicionar, você deve ter **2 volumes** configurados:

1. **Volume do Banco de Dados:**
   - Destination Path: `/var/lib/postgresql/data`
   - Name: `i88kc8oc4cc0owsggk88wk40` (ou similar)

2. **Volume de Uploads (NOVO):**
   - Destination Path: `/app/uploads`
   - Name: `luxbet-uploads` (ou o nome que você escolheu)

### 4. Fazer Redeploy

Após adicionar o volume:

1. Vá para a página principal do deployment
2. Clique em **"Redeploy"** ou **"Restart"**
3. Aguarde o deploy completar

---

## 🔍 Verificação

### Verificar se o Volume Está Montado

Após o redeploy, você pode verificar se o volume está funcionando:

1. **Fazer upload de um novo banner/logo** no painel admin
2. **Fazer um novo deploy**
3. **Verificar se o arquivo ainda existe** após o deploy

Se o arquivo ainda existir após o deploy, o persistent storage está funcionando! ✅

### Verificar nos Logs

Se você tiver acesso ao terminal do container, pode verificar:

```bash
# Verificar se o diretório existe e tem arquivos
ls -la /app/uploads/logos
ls -la /app/uploads/banners

# Verificar se é um mount point (deve mostrar o tipo como "volume")
df -h /app/uploads
```

---

## 📝 Configuração Atual do Código

O código já está configurado para usar `/app/uploads`:

```python
# backend/routes/media.py
UPLOAD_BASE_PATH = os.getenv("UPLOAD_BASE_PATH", "/app/uploads")
UPLOAD_BASE_DIR = Path(UPLOAD_BASE_PATH)
UPLOAD_DIRS = {
    MediaType.LOGO: UPLOAD_BASE_DIR / "logos",      # /app/uploads/logos
    MediaType.BANNER: UPLOAD_BASE_DIR / "banners",  # /app/uploads/banners
}
```

**Não é necessário alterar o código** - apenas adicionar o volume persistente no Coolify.

---

## ⚠️ Importante

### Após Adicionar o Volume

1. **Os arquivos antigos serão perdidos** (porque o volume novo começa vazio)
2. **Você precisará fazer upload novamente** dos banners e logos
3. **A partir de agora**, os arquivos serão preservados entre deploys

### Migração de Arquivos Existentes (Opcional)

Se você quiser preservar os arquivos existentes antes de adicionar o volume:

1. **Antes de adicionar o volume:**
   - Acesse o terminal do container atual
   - Faça backup dos arquivos: `tar -czf uploads-backup.tar.gz /app/uploads`

2. **Após adicionar o volume e fazer redeploy:**
   - Acesse o novo container
   - Restaure os arquivos: `tar -xzf uploads-backup.tar.gz -C /`

---

## 🎯 Resultado Esperado

Após configurar o persistent storage:

- ✅ **Banners e logos não serão mais perdidos** após deploys
- ✅ **Arquivos serão preservados** entre diferentes versões do código
- ✅ **Uploads funcionarão normalmente** sem necessidade de reenviar após cada deploy

---

## 📸 Captura de Tela Esperada

Após configurar, você deve ver algo assim na tela de Persistent Storage:

```
Volumes (2)
├── Volume 1: /var/lib/postgresql/data → Banco de dados
└── Volume 2: /app/uploads → Uploads (banners e logos) ← NOVO
```

---

## 🔧 Troubleshooting

### Problema: Volume não aparece após criar

- **Solução**: Verifique se salvou corretamente e faça um redeploy

### Problema: Arquivos ainda são perdidos após deploy

- **Solução**: Verifique se o Destination Path está exatamente como `/app/uploads` (sem barra no final)
- **Solução**: Verifique se o volume está realmente montado usando `df -h /app/uploads` no container

### Problema: Erro de permissão ao fazer upload

- **Solução**: O código já cria os diretórios com permissões corretas (755), mas se necessário:
  ```bash
  chmod -R 755 /app/uploads
  ```

---

## ✅ Checklist

- [ ] Acessou "Persistent Storage" no Coolify
- [ ] Criou novo volume com Destination Path: `/app/uploads`
- [ ] Salvou a configuração
- [ ] Fez redeploy do aplicativo
- [ ] Testou fazendo upload de um banner/logo
- [ ] Fez outro deploy e verificou que o arquivo ainda existe
