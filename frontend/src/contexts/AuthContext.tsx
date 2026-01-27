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

    // Atualizar saldo periodicamente (a cada 15 segundos)
    const balanceInterval = setInterval(() => {
      if (token) {
        fetchUser(token);
      }
    }, 15000); // 15 segundos

    // Atualizar saldo quando a página ganha foco (usuário volta para a aba)
    const handleFocus = () => {
      if (token) {
        fetchUser(token);
      }
    };
    window.addEventListener('focus', handleFocus);

    // Atualizar saldo quando a página fica visível novamente
    const handleVisibilityChange = () => {
      if (!document.hidden && token) {
        fetchUser(token);
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
      const res = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setLoading(false);
        return userData;
      } else {
        localStorage.removeItem('user_token');
        localStorage.removeItem('admin_token');
        setToken(null);
        setUser(null);
        setLoading(false);
        return null;
      }
    } catch (err) {
      console.error('Erro ao buscar usuário:', err);
      localStorage.removeItem('user_token');
      localStorage.removeItem('admin_token');
      setToken(null);
      setUser(null);
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
