import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

// Backend FastAPI - usa variável de ambiente ou fallback para localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface User {
  id: number;
  username: string;
  email: string;
  cpf?: string;
  phone?: string;
  role: string;
  balance: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<{ isAdmin?: boolean } | void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  loading: boolean;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  cpf?: string;
  phone?: string;
  affiliate_code?: string;  // ref do link de afiliado (?ref=CODIGO)
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Carregar token do localStorage ao iniciar
  useEffect(() => {
    const storedToken = localStorage.getItem('user_token');
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  // Atualizar saldo automaticamente quando usuário está logado
  useEffect(() => {
    if (!token || !user) return;

    // Variável para evitar múltiplas chamadas simultâneas
    let isFetching = false;

    // Atualizar saldo periodicamente (a cada 15 segundos para evitar sobrecarga)
    const balanceInterval = setInterval(() => {
      if (token && !isFetching) {
        isFetching = true;
        // Usar catch para evitar que erros interrompam o intervalo
        fetchUser(token).finally(() => {
          isFetching = false;
        });
      }
    }, 15000); // 15 segundos - reduzido de 5 para evitar race conditions

    // Atualizar saldo quando a página ganha foco (usuário volta para a aba)
    const handleFocus = () => {
      if (token) {
        fetchUser(token).catch(() => {
          // Silenciar erros durante atualização automática
        });
      }
    };
    window.addEventListener('focus', handleFocus);

    // Atualizar saldo quando a página fica visível novamente
    const handleVisibilityChange = () => {
      if (!document.hidden && token) {
        fetchUser(token).catch(() => {
          // Silenciar erros durante atualização automática
        });
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      clearInterval(balanceInterval);
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [token, user]);

  const fetchUser = async (authToken: string): Promise<User | null> => {
    try {
      const res = await fetch(`${API_URL}/api/auth/me?t=${Date.now()}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        // Adicionar cache: 'no-cache' e timestamp para garantir dados atualizados
        cache: 'no-cache',
      });
      if (res.ok) {
        const userData = await res.json();
        // Log para debug - verificar se saldo está sendo atualizado
        if (user && Math.abs((user.balance || 0) - (userData.balance || 0)) > 0.01) {
          console.log(`[Balance Update] Saldo atualizado: R$ ${user.balance?.toFixed(2)} → R$ ${userData.balance?.toFixed(2)}`);
        }
        setUser(userData);
        setLoading(false);
        return userData;
      } else {
        // Só limpar tokens se for erro 401 (não autorizado)
        // Não limpar em caso de outros erros (500, 502, etc) - pode ser temporário
        if (res.status === 401 || res.status === 403) {
          localStorage.removeItem('user_token');
          localStorage.removeItem('admin_token');
          setToken(null);
          setUser(null);
        }
        setLoading(false);
        return null;
      }
    } catch (err) {
      // NUNCA limpar tokens em caso de erro de rede - pode ser temporário
      // Apenas logar se não for erro de rede
      if (err instanceof TypeError && err.message.includes('Failed to fetch')) {
        // Erro de rede - não limpar tokens, apenas retornar null
        // O token pode estar válido, apenas não conseguimos conectar
        return null;
      }
      // Outros erros também não devem limpar tokens automaticamente
      // Apenas logar para debug
      console.error('Erro ao buscar usuário:', err);
      setLoading(false);
      return null;
    }
  };

  const login = async (username: string, password: string) => {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Erro ao fazer login');
    }

    const authToken = data.access_token;
    localStorage.setItem('user_token', authToken);
    setToken(authToken);
    const userData = await fetchUser(authToken);
    const isAdmin = userData && String(userData.role || '').toLowerCase() === 'admin';
    if (isAdmin) {
      localStorage.setItem('admin_token', authToken);
      return { isAdmin: true };
    }
  };

  const register = async (userData: RegisterData) => {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Erro ao criar conta');
    }

    // Após registro, fazer login automaticamente
    await login(userData.username, userData.password);
  };

  const logout = () => {
    localStorage.removeItem('user_token');
    localStorage.removeItem('admin_token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    if (token) {
      await fetchUser(token);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, refreshUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
