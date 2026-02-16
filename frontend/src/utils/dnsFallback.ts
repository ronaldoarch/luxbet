/**
 * Utilitário para lidar com problemas de DNS em diferentes redes (WiFi vs 4G)
 * Tenta múltiplas URLs e métodos de conexão quando há erro de DNS
 */

interface DNSFallbackOptions {
  primaryUrl: string;
  fallbackUrls?: string[];
  timeout?: number;
}

/**
 * Tenta fazer uma requisição com fallback automático em caso de erro DNS
 */
export async function fetchWithDNSFallback(
  url: string,
  options: RequestInit = {},
  dnsOptions: DNSFallbackOptions
): Promise<Response> {
  const { primaryUrl, fallbackUrls = [], timeout = 10000 } = dnsOptions;
  
  // Lista de URLs para tentar (primary + fallbacks)
  const urlsToTry = [primaryUrl, ...fallbackUrls];
  
  let lastError: Error | null = null;
  
  for (const baseUrl of urlsToTry) {
    try {
      const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
      
      // Criar AbortController para timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      try {
        const response = await fetch(fullUrl, {
          ...options,
          signal: controller.signal,
          mode: 'cors',
        });
        
        clearTimeout(timeoutId);
        
        // Se a resposta foi bem-sucedida, retornar
        if (response.ok || response.status < 500) {
          return response;
        }
        
        // Se não for erro de DNS, não tentar fallback
        if (response.status !== 0) {
          return response;
        }
      } catch (error: any) {
        clearTimeout(timeoutId);
        
        // Se não for erro de DNS/timeout, não tentar fallback
        if (error.name !== 'AbortError' && 
            !error.message?.includes('Failed to fetch') &&
            !error.message?.includes('ERR_NAME_NOT_RESOLVED') &&
            !error.message?.includes('NetworkError')) {
          throw error;
        }
        
        lastError = error;
        console.warn(`[DNS Fallback] Falha ao conectar com ${baseUrl}: ${error.message}`);
      }
    } catch (error: any) {
      lastError = error;
      console.warn(`[DNS Fallback] Erro ao tentar ${baseUrl}: ${error.message}`);
    }
  }
  
  // Se todas as tentativas falharam, lançar o último erro
  throw lastError || new Error('Todas as tentativas de conexão falharam');
}

/**
 * Detecta se o erro é relacionado a DNS
 */
export function isDNSError(error: any): boolean {
  if (!error) return false;
  
  const errorMessage = error.message?.toLowerCase() || '';
  const errorName = error.name?.toLowerCase() || '';
  
  return (
    errorName.includes('name_not_resolved') ||
    errorMessage.includes('name_not_resolved') ||
    errorMessage.includes('err_name_not_resolved') ||
    errorMessage.includes('dns') ||
    errorMessage.includes('failed to fetch') ||
    errorMessage.includes('networkerror')
  );
}

/**
 * Obtém a URL da API com fallback inteligente
 */
export function getAPIUrlWithFallback(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  
  if (envUrl) {
    return envUrl;
  }
  
  // Em produção, tentar detectar automaticamente
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol || 'https:';
    
    // luxbet.site -> api.luxbet.site
    if (hostname.includes('luxbet.site')) {
      return `${protocol}//api.luxbet.site`;
    }
    
    // Novo domínio: usar api.{hostname} (padrão após troca de domínio)
    if (!hostname.startsWith('api.')) {
      return `${protocol}//api.${hostname}`;
    }
  }
  
  // Fallback para desenvolvimento
  return 'http://localhost:8000';
}
