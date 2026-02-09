/**
 * Função utilitária para fazer requisições fetch com timeout e melhor tratamento de erros
 * Compatível com diferentes dispositivos e redes
 */

const DEFAULT_TIMEOUT = 30000; // 30 segundos

interface FetchOptions extends RequestInit {
  timeout?: number;
}

/**
 * Faz uma requisição fetch com timeout e tratamento de erros melhorado
 */
export async function fetchWithTimeout(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options;

  // Criar AbortController para timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    // Adicionar headers padrão para compatibilidade
    const headers = new Headers(fetchOptions.headers);
    
    // Headers de compatibilidade para diferentes dispositivos
    if (!headers.has('Accept')) {
      headers.set('Accept', 'application/json, */*');
    }
    if (!headers.has('Cache-Control')) {
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
    }
    if (!headers.has('Pragma')) {
      headers.set('Pragma', 'no-cache');
    }

    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
      // Adicionar credentials para CORS
      credentials: 'include',
      // Modo cors explícito
      mode: 'cors',
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);
    
    // Tratar diferentes tipos de erro
    if (error.name === 'AbortError') {
      throw new Error(`Timeout: A requisição demorou mais de ${timeout}ms. Verifique sua conexão.`);
    }
    
    if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
      throw new Error('Erro de conexão. Verifique sua internet e tente novamente.');
    }
    
    if (error.message?.includes('CORS')) {
      throw new Error('Erro de CORS. Entre em contato com o suporte.');
    }
    
    throw error;
  }
}

/**
 * Faz uma requisição fetch com retry automático em caso de falha
 */
export async function fetchWithRetry(
  url: string,
  options: FetchOptions = {},
  maxRetries: number = 3
): Promise<Response> {
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fetchWithTimeout(url, options);
    } catch (error: any) {
      lastError = error;
      
      // Não tentar novamente se for erro 4xx (erro do cliente)
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }
      
      // Aguardar antes de tentar novamente (exponential backoff)
      if (attempt < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError || new Error('Falha após múltiplas tentativas');
}
