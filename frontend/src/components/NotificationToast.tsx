import { useEffect, useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CheckCircle, X, Bell } from 'lucide-react';
import { trackMetaEvent } from './MetaPixel';

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

    const markAsRead = (id: number) =>
      fetch(`${API_URL}/api/public/notifications/${id}/read`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      }).catch(() => {}); // 404 para notificação global é esperado

    const fetchNotifications = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/notifications`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          // Todas as notificações não lidas que ainda não foram exibidas (qualquer tipo: info, success, warning, error, promotion)
          const unread = data.filter((n: Notification) => 
            !n.is_read && !checkedIdsRef.current.has(n.id)
          );
          
          if (unread.length > 0) {
            const latest = unread[0];
            setCurrentNotification(latest);
            setShowNotification(true);
            checkedIdsRef.current.add(latest.id);
            
            // Se for notificação de depósito aprovado, atualizar saldo e disparar eventos do pixel
            if (latest.title?.includes('Depósito') || latest.message?.includes('depósito')) {
              refreshUser().catch(() => {});
              
              // Buscar o depósito mais recente aprovado para obter o valor exato
              if (token) {
                fetch(`${API_URL}/api/auth/transactions`, {
                  headers: { 'Authorization': `Bearer ${token}` }
                })
                  .then(res => res.ok ? res.json() : null)
                  .then(data => {
                    if (data && data.transactions) {
                      // Buscar depósitos aprovados ordenados por data (mais recente primeiro)
                      const approvedDeposits = (data.transactions || [])
                        .filter((t: any) => t.type === 'deposit' && t.status === 'approved')
                        .sort((a: any, b: any) => {
                          const dateA = new Date(a.created_at || 0).getTime();
                          const dateB = new Date(b.created_at || 0).getTime();
                          return dateB - dateA; // Mais recente primeiro
                        });
                      
                      if (approvedDeposits.length > 0) {
                        const latestDeposit = approvedDeposits[0];
                        const depositAmount = latestDeposit.amount || 0;
                        const isFTD = approvedDeposits.length === 1;
                        
                        // Disparar evento Purchase do Meta Pixel com valor do depósito
                        trackMetaEvent('Purchase', {
                          value: depositAmount,
                          currency: 'BRL',
                          content_name: isFTD ? 'First Time Deposit (FTD)' : 'Deposit',
                          content_category: isFTD ? 'FTD' : 'Deposit'
                        });
                        
                        console.log(`[Meta Pixel] Purchase disparado: R$ ${depositAmount.toFixed(2)} ${isFTD ? '(FTD)' : ''}`);
                      } else {
                        // Fallback: tentar extrair da mensagem se não encontrar na API
                        const amountMatch = latest.message.match(/R\$\s*([\d,]+\.?\d*)/);
                        const amount = amountMatch ? parseFloat(amountMatch[1].replace(',', '.')) : 0;
                        if (amount > 0) {
                          trackMetaEvent('Purchase', {
                            value: amount,
                            currency: 'BRL'
                          });
                          console.log(`[Meta Pixel] Purchase disparado (fallback): R$ ${amount.toFixed(2)}`);
                        }
                      }
                    }
                  })
                  .catch(err => {
                    console.warn('[Meta Pixel] Erro ao buscar depósito:', err);
                    // Fallback: tentar extrair da mensagem
                    const amountMatch = latest.message.match(/R\$\s*([\d,]+\.?\d*)/);
                    const amount = amountMatch ? parseFloat(amountMatch[1].replace(',', '.')) : 0;
                    if (amount > 0) {
                      trackMetaEvent('Purchase', {
                        value: amount,
                        currency: 'BRL'
                      });
                      console.log(`[Meta Pixel] Purchase disparado (fallback): R$ ${amount.toFixed(2)}`);
                    }
                  });
              }
            }
            
            // Fechar popup após 6 segundos (ou usuário pode fechar antes)
            setTimeout(() => {
              markAsRead(latest.id).catch(() => {});
              setShowNotification(false);
            }, 6000);
          }
        }
      } catch (err) {
        console.error('Erro ao buscar notificações:', err);
      }
    };

    // Buscar imediatamente
    fetchNotifications();

    // Buscar a cada 5 segundos para novas notificações aparecerem rápido
    const interval = setInterval(fetchNotifications, 5000);

    return () => clearInterval(interval);
  }, [token, user]);

  const handleClose = () => {
    if (currentNotification) {
      fetch(`${API_URL}/api/public/notifications/${currentNotification.id}/read`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      }).catch(() => {});
    }
    setShowNotification(false);
  };

  if (!showNotification || !currentNotification) return null;

  const typeStyles = {
    success: { bg: 'from-green-900 to-green-800', border: 'border-green-500', icon: 'bg-green-500/20' },
    error: { bg: 'from-red-900 to-red-800', border: 'border-red-500', icon: 'bg-red-500/20' },
    warning: { bg: 'from-yellow-900 to-yellow-800', border: 'border-yellow-500', icon: 'bg-yellow-500/20' },
    promotion: { bg: 'from-purple-900 to-purple-800', border: 'border-purple-500', icon: 'bg-purple-500/20' },
    info: { bg: 'from-blue-900 to-blue-800', border: 'border-blue-500', icon: 'bg-blue-500/20' },
  };
  const style = typeStyles[currentNotification.type as keyof typeof typeStyles] || typeStyles.info;

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
      <div className={`bg-gradient-to-r ${style.bg} border ${style.border} rounded-lg p-4 shadow-xl max-w-md min-w-[320px]`}>
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${style.icon}`}>
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
