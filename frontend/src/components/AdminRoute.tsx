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
      // Aceitar admin_token OU user_token (quem logou na home tem user_token)
      const token = localStorage.getItem('admin_token') || localStorage.getItem('user_token');
      
      if (!token) {
        setIsAdmin(false);
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const user = await response.json();
          const userRole = String(user.role || '').toLowerCase();
          if (userRole === 'admin') {
            // Garantir que admin_token existe para próximas visitas
            localStorage.setItem('admin_token', token);
            setIsAdmin(true);
          } else {
            setIsAdmin(false);
            localStorage.removeItem('admin_token');
          }
        } else {
          setIsAdmin(false);
          localStorage.removeItem('admin_token');
        }
      } catch (error) {
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
