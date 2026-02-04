/**
 * Configuração centralizada da API
 * Detecta automaticamente se está em produção e valida configuração
 */

// Detectar se está em produção (não localhost)
const isProduction = typeof window !== 'undefined' && 
  !window.location.hostname.includes('localhost') && 
  !window.location.hostname.includes('127.0.0.1');

// Obter URL da API
const getApiUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // Se tem variável de ambiente, usa ela
  if (envUrl) {
    return envUrl;
  }
  
  // Se está em produção e não tem variável, retorna vazio (vai dar erro)
  if (isProduction) {
    console.error(
      '❌ VITE_API_URL não configurada! ' +
      'Configure a variável de ambiente VITE_API_URL no Coolify.'
    );
    return '';
  }
  
  // Em desenvolvimento, usa localhost
  return 'http://localhost:8000';
};

export const API_URL = getApiUrl();

// Validar configuração em produção
if (isProduction && !API_URL) {
  console.error(
    '%c⚠️ CONFIGURAÇÃO NECESSÁRIA ⚠️',
    'color: red; font-size: 16px; font-weight: bold;'
  );
  console.error(
    'A variável VITE_API_URL não está configurada.\n' +
    'Configure no Coolify → Frontend → Environment Variables:\n' +
    'VITE_API_URL=https://sua-url-do-backend.com'
  );
}
