/**
 * Cliente de API com fallback automático para DNS
 * Tenta múltiplas URLs quando há erro de DNS
 */

const SERVER_IP = '147.93.147.33';

/**
 * Obtém a URL da API com fallback inteligente
 */
export function getAPIUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  
  if (envUrl) {
    return envUrl;
  }
  
  // Fallback: usar mesmo domínio do frontend
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // Se estiver em luxbet.site, tentar api.luxbet.site
    if (hostname.includes('luxbet.site')) {
      return `${protocol}//api.luxbet.site`;
    }
    
    // Caso contrário, usar mesmo domínio
    return `${protocol}//${hostname}`;
  }
  
  return 'http://localhost:8000';
}

/**
 * Lista de URLs para tentar em caso de erro DNS
 */
export function getFallbackUrls(): string[] {
  const primaryUrl = getAPIUrl();
  const fallbacks: string[] = [];
  
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // 1. Mesmo domínio do frontend
    if (!primaryUrl.includes(hostname)) {
      fallbacks.push(`${protocol}//${hostname}`);
    }
    
    // 2. IP direto (HTTP - pode dar erro de certificado mas funciona)
    fallbacks.push(`http://${SERVER_IP}`);
  }
  
  return fallbacks;
}

/**
 * Faz requisição com fallback automático
 */
export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const primaryUrl = getAPIUrl();
  const urlsToTry = [primaryUrl, ...getFallbackUrls()];
  
  let lastError: Error | null = null;
  
  for (let i = 0; i < urlsToTry.length; i++) {
    const baseUrl = urlsToTry[i];
    const fullUrl = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
    
    try {
      console.log(`[API Client] Tentativa ${i + 1}/${urlsToTry.length}: ${fullUrl}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);
      
      const response = await fetch(fullUrl, {
        ...options,
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          ...options.headers,
        },
        cache: 'no-store',
        mode: 'cors',
      });
      
      clearTimeout(timeoutId);
      
      // Se funcionou, retornar
      if (response.ok || response.status < 500) {
        if (i > 0) {
          console.log(`✅ Fallback ${i} funcionou! Usando: ${baseUrl}`);
        }
        return response;
      }
      
      // Se não for erro de DNS, não tentar fallback
      if (response.status !== 0) {
        return response;
      }
    } catch (error: any) {
      lastError = error;
      
      const isDNSError = error.message?.includes('ERR_NAME_NOT_RESOLVED') || 
                        error.message?.includes('Failed to fetch') ||
                        error.name === 'TypeError' ||
                        error.name === 'AbortError';
      
      if (!isDNSError) {
        // Não é erro DNS, não tentar fallback
        throw error;
      }
      
      console.warn(`⚠️ Tentativa ${i + 1} falhou (DNS): ${error.message}`);
      
      // Se não for a última tentativa, continuar
      if (i < urlsToTry.length - 1) {
        // Aguardar um pouco antes de tentar próximo
        await new Promise(resolve => setTimeout(resolve, 500));
        continue;
      }
    }
  }
  
  throw lastError || new Error('Todas as tentativas falharam');
}
