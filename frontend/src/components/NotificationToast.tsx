import { useEffect, useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CheckCircle, X, Bell } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  link?: string;
  created_at: string;
}

export default function NotificationToast() {
  const { token, user, refreshUser } = useAuth();
  const [showNotification, setShowNotification] = useState(false);
  const [currentNotification, setCurrentNotification] = useState<Notification | null>(null);
  const checkedIdsRef = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (!token || !user) return;

    const markAsRead = async (id: number) => {
      try {
        await fetch(`${API_URL}/api/public/notifications/${id}/read`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (err) {
        console.error('Erro ao marcar notificação como lida:', err);
      }
    };

    const fetchNotifications = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/notifications`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          // Filtrar apenas notificações não lidas e de sucesso que ainda não foram exibidas
          const unreadSuccess = data.filter((n: Notification) => 
            !n.is_read && n.type === 'success' && !checkedIdsRef.current.has(n.id)
          );
          
          if (unreadSuccess.length > 0) {
            const latest = unreadSuccess[0];
            setCurrentNotification(latest);
            setShowNotification(true);
            checkedIdsRef.current.add(latest.id);
            
            // Se for notificação de depósito aprovado, atualizar saldo imediatamente
            if (latest.title.includes('Depósito') || latest.message.includes('depósito')) {
              console.log('[Notification] Depósito aprovado detectado - atualizando saldo...');
              refreshUser().catch(err => {
                console.warn('[Notification] Erro ao atualizar saldo:', err);
              });
            }
            
            // Marcar como lida após 5 segundos
            setTimeout(() => {
              markAsRead(latest.id);
              setShowNotification(false);
            }, 5000);
          }
        }
      } catch (err) {
        console.error('Erro ao buscar notificações:', err);
      }
    };

    // Buscar imediatamente
    fetchNotifications();

    // Buscar a cada 10 segundos
    const interval = setInterval(fetchNotifications, 10000);

    return () => clearInterval(interval);
  }, [token, user]);

  const handleClose = async () => {
    if (currentNotification) {
      try {
        await fetch(`${API_URL}/api/public/notifications/${currentNotification.id}/read`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (err) {
        console.error('Erro ao marcar notificação como lida:', err);
      }
    }
    setShowNotification(false);
  };

  if (!showNotification || !currentNotification) return null;

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
      <div className={`bg-gradient-to-r ${
        currentNotification.type === 'success' ? 'from-green-900 to-green-800' :
        currentNotification.type === 'error' ? 'from-red-900 to-red-800' :
        currentNotification.type === 'warning' ? 'from-yellow-900 to-yellow-800' :
        'from-blue-900 to-blue-800'
      } border ${
        currentNotification.type === 'success' ? 'border-green-500' :
        currentNotification.type === 'error' ? 'border-red-500' :
        currentNotification.type === 'warning' ? 'border-yellow-500' :
        'border-blue-500'
      } rounded-lg p-4 shadow-xl max-w-md min-w-[320px]`}>
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${
            currentNotification.type === 'success' ? 'bg-green-500/20' :
            currentNotification.type === 'error' ? 'bg-red-500/20' :
            currentNotification.type === 'warning' ? 'bg-yellow-500/20' :
            'bg-blue-500/20'
          }`}>
            {currentNotification.type === 'success' ? (
              <CheckCircle className="text-green-400" size={20} />
            ) : (
              <Bell className="text-white" size={20} />
            )}
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-white mb-1">{currentNotification.title}</h3>
            <p className="text-gray-200 text-sm">{currentNotification.message}</p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
