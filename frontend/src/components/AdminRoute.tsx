import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

// Backend FastAPI - usa variável de ambiente ou fallback para localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AdminRouteProps {
  children: React.ReactNode;
}

export default function AdminRoute({ children }: AdminRouteProps) {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAdmin = async () => {
      const token = localStorage.getItem('admin_token');
      
      console.log('[AdminRoute] Verificando acesso admin...');
      console.log('[AdminRoute] Token encontrado:', token ? 'SIM' : 'NÃO');
      
      if (!token) {
        console.log('[AdminRoute] Sem token, redirecionando...');
        setIsAdmin(false);
        setLoading(false);
        return;
      }

      try {
        console.log('[AdminRoute] Fazendo requisição para /api/auth/me...');
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        console.log('[AdminRoute] Resposta status:', response.status);

        if (response.ok) {
          const user = await response.json();
          console.log('[AdminRoute] Dados do usuário:', user);
          console.log('[AdminRoute] Role do usuário:', user.role);
          
          // Verificar se o usuário tem role ADMIN (case-insensitive)
          const userRole = String(user.role || '').toLowerCase();
          if (userRole === 'admin') {
            console.log('[AdminRoute] Usuário é admin, permitindo acesso!');
            setIsAdmin(true);
          } else {
            console.log('[AdminRoute] Usuário NÃO é admin, role:', userRole);
            setIsAdmin(false);
            localStorage.removeItem('admin_token');
          }
        } else {
          const errorText = await response.text();
          console.error('[AdminRoute] Falha na verificação de admin:', response.status, errorText);
          setIsAdmin(false);
          localStorage.removeItem('admin_token');
        }
      } catch (error) {
        console.error('[AdminRoute] Erro ao verificar admin:', error);
        setIsAdmin(false);
        localStorage.removeItem('admin_token');
      } finally {
        setLoading(false);
      }
    };

    checkAdmin();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Carregando...</div>
      </div>
    );
  }

  if (!isAdmin) {
    // Se não for admin, mas o carregamento terminou, redireciona
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
