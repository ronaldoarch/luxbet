import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, Download, RefreshCw } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function TransactionHistory() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }
    fetchTransactions();
  }, [token, navigate]);

  const fetchTransactions = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/auth/transactions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) throw new Error('Falha ao carregar histórico');
      const data = await res.json();
      setTransactions(data.transactions || []);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar histórico de transações');
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
      case 'approved':
        return 'text-green-400';
      case 'pending':
        return 'text-yellow-400';
      case 'rejected':
      case 'cancelled':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      'approved': 'Aprovado',
      'pending': 'Pendente',
      'rejected': 'Rejeitado',
      'cancelled': 'Cancelado'
    };
    return labels[status.toLowerCase()] || status;
  };

  const getTypeLabel = (type: string) => {
    return type === 'deposit' ? 'Depósito' : 'Saque';
  };

  const getTypeColor = (type: string) => {
    return type === 'deposit' ? 'text-green-400' : 'text-red-400';
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
            <h1 className="text-xl md:text-2xl font-bold">Histórico de Transações</h1>
            <button
              onClick={fetchTransactions}
              className="ml-auto p-2 hover:bg-[#0d5d4b] rounded transition-colors"
              disabled={loading}
            >
              <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
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
        ) : transactions.length === 0 ? (
          <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 text-center">
            <p className="text-gray-400 text-lg">Nenhuma transação encontrada</p>
            <p className="text-gray-500 text-sm mt-2">Suas transações aparecerão aqui</p>
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map((transaction) => (
              <div
                key={`${transaction.type}-${transaction.id}`}
                className="bg-gray-900 rounded-xl p-4 border border-gray-800 hover:border-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between flex-wrap gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`font-semibold ${getTypeColor(transaction.type)}`}>
                        {getTypeLabel(transaction.type)}
                      </span>
                      <span className={`text-sm ${getStatusColor(transaction.status)}`}>
                        {getStatusLabel(transaction.status)}
                      </span>
                    </div>
                    <div className="text-2xl font-bold mb-1">
                      {transaction.type === 'deposit' ? '+' : '-'}R$ {transaction.amount.toFixed(2)}
                    </div>
                    <div className="text-sm text-gray-400">
                      {formatDate(transaction.created_at)}
                    </div>
                    {transaction.transaction_id && (
                      <div className="text-xs text-gray-500 mt-1">
                        ID: {transaction.transaction_id}
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
