import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, RefreshCw, Trophy, X } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function BetsHistory() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [bets, setBets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }
    fetchBets();
  }, [token, navigate, statusFilter]);

  const fetchBets = async () => {
    setLoading(true);
    setError('');
    try {
      const url = statusFilter === 'all' 
        ? `${API_URL}/api/auth/bets`
        : `${API_URL}/api/auth/bets?status_filter=${statusFilter}`;
      
      const res = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) throw new Error('Falha ao carregar apostas');
      const data = await res.json();
      setBets(data || []);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar histórico de apostas');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'won':
        return 'text-green-400 bg-green-400/20 border-green-400';
      case 'lost':
        return 'text-red-400 bg-red-400/20 border-red-400';
      case 'pending':
        return 'text-yellow-400 bg-yellow-400/20 border-yellow-400';
      default:
        return 'text-gray-400 bg-gray-400/20 border-gray-400';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      'won': 'Ganhou',
      'lost': 'Perdeu',
      'pending': 'Pendente'
    };
    return labels[status.toLowerCase()] || status;
  };

  const getStatusIcon = (status: string) => {
    if (status.toLowerCase() === 'won') {
      return <Trophy size={16} />;
    } else if (status.toLowerCase() === 'lost') {
      return <X size={16} />;
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-[#0a0e0f] text-white">
      <div className="bg-[#0a4d3e] border-b border-[#0d5d4b] sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/conta')}
              className="p-2 hover:bg-[#0d5d4b] rounded transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-xl md:text-2xl font-bold">Minhas Apostas</h1>
            <button
              onClick={fetchBets}
              className="ml-auto p-2 hover:bg-[#0d5d4b] rounded transition-colors"
              disabled={loading}
            >
              <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>
        <div className="container mx-auto px-4 flex gap-2 overflow-x-auto no-scrollbar border-b border-[#0d5d4b]/50 pb-2">
          {['all', 'won', 'lost', 'pending'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap rounded transition-colors ${
                statusFilter === status
                  ? 'bg-[#d4af37] text-black'
                  : 'bg-gray-800 text-gray-300 hover:text-white'
              }`}
            >
              {status === 'all' ? 'Todas' : status === 'won' ? 'Ganhas' : status === 'lost' ? 'Perdidas' : 'Pendentes'}
            </button>
          ))}
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {error && (
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <RefreshCw size={32} className="animate-spin text-[#d4af37]" />
          </div>
        ) : bets.length === 0 ? (
          <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 text-center">
            <p className="text-gray-400 text-lg">Nenhuma aposta encontrada</p>
            <p className="text-gray-500 text-sm mt-2">Suas apostas aparecerão aqui</p>
          </div>
        ) : (
          <div className="space-y-3">
            {bets.map((bet) => (
              <div
                key={bet.id}
                className="bg-gray-900 rounded-xl p-4 border border-gray-800 hover:border-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between flex-wrap gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <span className="font-semibold text-lg">
                        {bet.game_name || bet.game_id || 'Jogo desconhecido'}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded border flex items-center gap-1 ${getStatusColor(bet.status)}`}>
                        {getStatusIcon(bet.status)}
                        {getStatusLabel(bet.status)}
                      </span>
                      {bet.provider && (
                        <span className="text-xs text-gray-400">
                          {bet.provider}
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-2">
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Valor Apostado</div>
                        <div className="text-lg font-semibold text-red-400">
                          -R$ {bet.amount.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Ganho</div>
                        <div className={`text-lg font-semibold ${bet.win_amount > 0 ? 'text-green-400' : 'text-gray-400'}`}>
                          {bet.win_amount > 0 ? '+' : ''}R$ {bet.win_amount.toFixed(2)}
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      {formatDate(bet.created_at)}
                    </div>
                    {bet.transaction_id && (
                      <div className="text-xs text-gray-500 mt-1">
                        ID: {bet.transaction_id}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
