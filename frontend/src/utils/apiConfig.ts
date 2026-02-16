/**
 * Configuração centralizada da API
 * Detecta automaticamente se está em produção e valida configuração
 * Inclui fallback para IP direto quando DNS não funciona
 */

// IP do servidor para fallback quando DNS não funciona
const SERVER_IP = '147.93.147.33';

// Detectar se está em produção (não localhost)
const isProduction = typeof window !== 'undefined' && 
  !window.location.hostname.includes('localhost') && 
  !window.location.hostname.includes('127.0.0.1');

// Obter URL da API com fallback inteligente
const getApiUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // Log para debug
  console.log('[API Config] VITE_API_URL from env:', envUrl);
  console.log('[API Config] Hostname atual:', typeof window !== 'undefined' ? window.location.hostname : 'N/A');
  
  // Se tem variável de ambiente, usa ela
  if (envUrl) {
    console.log('[API Config] Usando URL da variável de ambiente:', envUrl);
    return envUrl;
  }
  
  // Se está em produção e não tem variável, tentar detectar automaticamente
  if (isProduction && typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // luxbet.site -> api.luxbet.site
    if (hostname.includes('luxbet.site')) {
      const apiUrl = `${protocol}//api.luxbet.site`;
      console.log('[API Config] Fallback: usando', apiUrl, 'baseado no hostname:', hostname);
      return apiUrl;
    }
    
    // Novo domínio: luxbet.com.br, luxbet.app, etc. -> api.luxbet.com.br, api.luxbet.app
    // Se o hostname NÃO começa com "api.", tentar api.{hostname} (padrão comum após troca de domínio)
    if (!hostname.startsWith('api.')) {
      const apiSubdomainUrl = `${protocol}//api.${hostname}`;
      console.log('[API Config] Fallback para novo domínio: usando', apiSubdomainUrl);
      return apiSubdomainUrl;
    }
    
    // Se já está em api.xxx, usar mesmo domínio
    const sameDomainUrl = `${protocol}//${hostname}`;
    console.log('[API Config] Fallback: usando mesmo domínio:', sameDomainUrl);
    return sameDomainUrl;
  }
  
  // Em desenvolvimento, usa localhost
  console.warn('[API Config] Usando localhost como último fallback');
  return 'http://localhost:8000';
};

export const API_URL = getApiUrl();

// Exportar IP do servidor para uso em fallbacks
export const SERVER_IP_FALLBACK = SERVER_IP;

// Log final da URL que será usada
console.log('[API Config] URL final da API:', API_URL);
console.log('[API Config] IP do servidor para fallback:', SERVER_IP);

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
