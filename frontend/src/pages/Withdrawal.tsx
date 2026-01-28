import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, Loader2, AlertCircle, Check } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Withdrawal() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [amount, setAmount] = useState('');
  const [pixKey, setPixKey] = useState('');
  const [pixKeyType, setPixKeyType] = useState('phoneNumber');
  const [documentValidation, setDocumentValidation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [withdrawal, setWithdrawal] = useState<any>(null);

  const handleWithdrawal = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setWithdrawal(null);

    if (!token || !user) {
      setError('Você precisa estar logado para sacar');
      return;
    }

    const value = parseFloat(amount.replace(',', '.'));
    if (isNaN(value) || value <= 0) {
      setError('Valor inválido. Digite um valor maior que zero.');
      return;
    }

    if (value < 10) {
      setError('Valor mínimo de saque é R$ 10,00');
      return;
    }

    if (!pixKey.trim()) {
      setError('Digite a chave PIX de destino.');
      return;
    }

    setLoading(true);

    try {
      // 1. Verificar saldo disponível (pode incluir saldo no IGameWin)
      const balanceRes = await fetch(`${API_URL}/api/auth/available-balance`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (balanceRes.ok) {
        const balanceData = await balanceRes.json();
        
        // Se precisa sincronizar saldo do IGameWin, fazer isso primeiro
        if (balanceData.needs_sync) {
          console.log('[Withdrawal] Sincronizando saldo do IGameWin antes do saque...');
          const syncRes = await fetch(`${API_URL}/api/public/games/sync-balance`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (syncRes.ok) {
            console.log('[Withdrawal] Saldo sincronizado com sucesso');
            // Atualizar dados do usuário após sincronização
            // O AuthContext atualizará automaticamente
          }
        }

        // Verificar saldo disponível após sincronização
        const availableBalance = balanceData.available_balance || user.balance;
        if (availableBalance < value) {
          const totalBalance = balanceData.total_balance || user.balance;
          if (totalBalance >= value && balanceData.needs_sync) {
            setError(`Saldo insuficiente no momento. Você tem R$ ${totalBalance.toFixed(2)} no total, mas precisa sincronizar primeiro. Tente novamente em alguns segundos.`);
          } else {
            setError(`Saldo insuficiente. Disponível: R$ ${availableBalance.toFixed(2)}`);
          }
          setLoading(false);
          return;
        }
      }

      // 2. Processar saque
      const response = await fetch(`${API_URL}/api/public/payments/withdrawal/pix`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: value,
          pix_key: pixKey.trim(),
          pix_key_type: pixKeyType,
          document_validation: documentValidation || undefined
        })
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: 'Erro ao processar saque' }));
        throw new Error(data.detail || 'Erro ao processar saque');
      }

      const data = await response.json();
      setWithdrawal(data);
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Erro ao processar saque. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e0f] text-white">
      {/* Header */}
      <div className="bg-[#0a4d3e] border-b border-[#0d5d4b] sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/conta')}
              className="p-2 hover:bg-[#0d5d4b] rounded transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-xl md:text-2xl font-bold">Sacar</h1>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {!success ? (
          <form onSubmit={handleWithdrawal} className="space-y-6">
            {/* Informações */}
            <div className="bg-gradient-to-br from-[#0a4d3e] to-[#0d5d4b] rounded-2xl p-6 border border-[#d4af37]/20">
              <h2 className="text-xl font-bold mb-4">Saque via PIX</h2>
              <p className="text-gray-300 text-sm mb-4">
                Digite o valor e a chave PIX de destino. O saque será processado automaticamente.
              </p>
              <div className="space-y-2 text-sm">
                <p className="text-yellow-400">⚠️ Valor mínimo: R$ 10,00</p>
                <p className="text-white">💰 Saldo disponível: R$ {user?.balance.toFixed(2).replace('.', ',') || '0,00'}</p>
              </div>
            </div>

            {/* Formulário */}
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Valor do Saque (R$)
                </label>
                <input
                  type="text"
                  inputMode="decimal"
                  value={amount}
                  onChange={(e) => {
                    const value = e.target.value.replace(/[^0-9,]/g, '');
                    setAmount(value);
                  }}
                  placeholder="0,00"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-xl font-semibold focus:border-[#d4af37] focus:outline-none"
                  required
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Tipo de Chave PIX
                </label>
                <select
                  value={pixKeyType}
                  onChange={(e) => setPixKeyType(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-[#d4af37] focus:outline-none"
                  disabled={loading}
                >
                  <option value="phoneNumber">Telefone (DDD + Número)</option>
                  <option value="email">E-mail</option>
                  <option value="document">CPF/CNPJ</option>
                  <option value="randomKey">Chave Aleatória</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Chave PIX de Destino
                </label>
                <input
                  type="text"
                  value={pixKey}
                  onChange={(e) => setPixKey(e.target.value)}
                  placeholder={
                    pixKeyType === 'phoneNumber' ? '62999999999' :
                    pixKeyType === 'email' ? 'seu@email.com' :
                    pixKeyType === 'document' ? '000.000.000-00' :
                    'Chave aleatória'
                  }
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-[#d4af37] focus:outline-none"
                  required
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Validar CPF/CNPJ (Opcional)
                </label>
                <input
                  type="text"
                  value={documentValidation}
                  onChange={(e) => setDocumentValidation(e.target.value)}
                  placeholder="000.000.000-00"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:border-[#d4af37] focus:outline-none"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Valida se o CPF/CNPJ pertence à chave PIX informada
                </p>
              </div>

              {error && (
                <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 flex items-start gap-3">
                  <AlertCircle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !amount || !pixKey}
                className="w-full bg-[#d4af37] hover:bg-[#ffd700] disabled:bg-gray-700 disabled:cursor-not-allowed text-black font-semibold py-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Processando saque...
                  </>
                ) : (
                  'Confirmar Saque'
                )}
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-6">
            {/* Sucesso */}
            <div className="bg-gradient-to-br from-green-900/30 to-green-800/30 rounded-2xl p-6 border border-green-500/30">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-green-500/20 p-2 rounded-lg">
                  <Check className="text-green-400" size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Saque Solicitado!</h2>
                  <p className="text-gray-300 text-sm">Seu saque está sendo processado</p>
                </div>
              </div>
              <div className="bg-gray-900 rounded-lg p-4 space-y-2">
                <div>
                  <p className="text-sm text-gray-400">Valor do saque:</p>
                  <p className="text-2xl font-bold text-[#d4af37]">
                    R$ {withdrawal?.amount.toFixed(2).replace('.', ',')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Status:</p>
                  <p className="text-lg font-semibold text-yellow-400">
                    {withdrawal?.status === 'PENDING' ? 'Pendente' : withdrawal?.status}
                  </p>
                </div>
              </div>
            </div>

            {/* Informações */}
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-3">Informações:</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• O saque será processado em até 24 horas</li>
                <li>• Você receberá uma notificação quando o saque for concluído</li>
                <li>• O valor foi bloqueado da sua conta</li>
                <li>• Em caso de cancelamento, o valor será revertido automaticamente</li>
              </ul>
            </div>

            {/* Botões */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setSuccess(false);
                  setAmount('');
                  setPixKey('');
                  setError('');
                  setWithdrawal(null);
                }}
                className="flex-1 bg-gray-800 hover:bg-gray-700 text-white font-semibold py-3 rounded-lg transition-colors"
              >
                Novo Saque
              </button>
              <button
                onClick={() => navigate('/conta')}
                className="flex-1 bg-[#0a4d3e] hover:bg-[#0d5d4b] text-white font-semibold py-3 rounded-lg transition-colors"
              >
                Voltar para Conta
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
