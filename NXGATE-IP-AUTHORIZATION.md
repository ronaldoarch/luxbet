# NXGate - Autorização de IP

## Problema

Ao tentar realizar saques via PIX usando o gateway NXGate, você pode receber o erro:

```
403 Forbidden - IP não autorizado
```

Este erro ocorre porque o IP do servidor onde a aplicação está hospedada não está autorizado na conta NXGate.

## IP Detectado

O IP público do servidor detectado é: **147.93.147.33**

## Solução

Para resolver este problema, você precisa autorizar o IP do servidor na conta NXGate:

### Passos para Autorizar o IP:

1. **Acesse o painel da NXGate**
   - Faça login na sua conta NXGate
   - Navegue até as configurações de segurança ou IPs autorizados

2. **Adicione o IP do servidor**
   - Adicione o IP `147.93.147.33` na lista de IPs autorizados
   - Salve as alterações

3. **Verifique se o IP está correto**
   - O IP pode mudar se o servidor for reiniciado ou se você mudar de provedor
   - Você pode verificar o IP atual do servidor nos logs da aplicação quando tentar fazer um saque

### Como Verificar o IP Atual do Servidor

O IP do servidor é detectado automaticamente e aparece nos logs quando há uma tentativa de saque:

```
[NXGate] IP público do servidor detectado: 147.93.147.33
```

Se o IP mudar, você precisará atualizar a lista de IPs autorizados na NXGate.

## Melhorias Implementadas

O código foi melhorado para:

1. **Detecção mais robusta de erros de IP**: O sistema agora detecta erros de IP não autorizado de forma mais confiável, mesmo se a resposta da API não estiver no formato esperado.

2. **Mensagens de erro mais claras**: As mensagens de erro agora incluem o IP detectado e instruções sobre como autorizá-lo.

3. **Tratamento de erros melhorado**: O sistema trata diferentes formatos de resposta de erro da API NXGate.

## Notas Importantes

- O IP do servidor pode mudar se você:
  - Reiniciar o servidor
  - Mudar de provedor de hospedagem
  - Usar um balanceador de carga que muda o IP de saída

- Se o IP mudar frequentemente, considere:
  - Usar um IP fixo (static IP) do provedor de hospedagem
  - Configurar um range de IPs autorizados (se suportado pela NXGate)
  - Usar um serviço de proxy com IP fixo

## Suporte

Se você não tem acesso ao painel da NXGate ou precisa de ajuda para autorizar o IP, entre em contato com:
- Suporte técnico da NXGate
- Administrador do sistema que configurou a conta NXGate
