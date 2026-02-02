import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, Loader2, AlertCircle, Check } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Withdrawal() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [amount, setAmount] = useState('');
  const [minWithdrawal, setMinWithdrawal] = useState(10);
  const [pixKey, setPixKey] = useState('');
  const [pixKeyType, setPixKeyType] = useState('phoneNumber');
  const [documentValidation, setDocumentValidation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [withdrawal, setWithdrawal] = useState<any>(null);
  const [availableBalance, setAvailableBalance] = useState<number | null>(null);
  const [loadingBalance, setLoadingBalance] = useState(true);
  const [syncingBalance, setSyncingBalance] = useState(false);

  useEffect(() => {
    const fetchMinimums = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/minimums`);
        if (res.ok) {
          const data = await res.json();
          setMinWithdrawal(Number(data.min_withdrawal) || 10);
        }
      } catch {
        // mantém 10 como padrão
      }
    };
    fetchMinimums();
  }, []);

  useEffect(() => {
    // Usar apenas user?.id para evitar loops quando o saldo muda
    if (!token || !user?.id) {
      setLoadingBalance(false);
      return;
    }

    let cancelled = false;

    const fetchAvailableBalance = async () => {
      if (syncingBalance) {
        return; // Evitar múltiplas sincronizações simultâneas
      }

      try {
        setLoadingBalance(true);
        const balanceRes = await fetch(`${API_URL}/api/auth/available-balance`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (cancelled) return;

        if (balanceRes.ok) {
          const balanceData = await balanceRes.json();
          
          // Se precisa sincronizar saldo do IGameWin, fazer isso primeiro
          if (balanceData.needs_sync && !syncingBalance) {
            setSyncingBalance(true);
            console.log('[Withdrawal] Sincronizando saldo do IGameWin...');
            try {
              const syncRes = await fetch(`${API_URL}/api/public/games/sync-balance`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (cancelled) return;

              if (syncRes.ok) {
                console.log('[Withdrawal] Saldo sincronizado com sucesso');
                // Aguardar um pouco antes de buscar novamente para garantir que o backend processou
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Buscar saldo novamente após sincronização
                const updatedBalanceRes = await fetch(`${API_URL}/api/auth/available-balance`, {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  }
                });
                if (cancelled) return;
                
                if (updatedBalanceRes.ok) {
                  const updatedBalanceData = await updatedBalanceRes.json();
                  setAvailableBalance(updatedBalanceData.available_balance || user.balance);
                } else {
                  setAvailableBalance(balanceData.available_balance || user.balance);
                }
              } else {
                setAvailableBalance(balanceData.available_balance || user.balance);
              }
            } finally {
              setSyncingBalance(false);
            }
          } else {
            setAvailableBalance(balanceData.available_balance || user.balance);
          }
        } else {
          setAvailableBalance(user?.balance || 0);
        }
      } catch (err) {
        if (cancelled) return;
        console.error('[Withdrawal] Erro ao buscar saldo disponível:', err);
        setAvailableBalance(user?.balance || 0);
      } finally {
        if (!cancelled) {
          setLoadingBalance(false);
        }
      }
    };

    fetchAvailableBalance();

    return () => {
      cancelled = true;
    };
  }, [token, user?.id]); // Usar apenas user?.id para evitar loops

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

    if (value < minWithdrawal) {
      setError(`Valor mínimo de saque é R$ ${minWithdrawal.toFixed(2).replace('.', ',')}`);
      return;
    }

    if (!pixKey.trim()) {
      setError('Digite a chave PIX de destino.');
      return;
    }

    setLoading(true);

    try {
      // 1. Verificar saldo disponível (usar o valor já carregado se disponível)
      let currentBalance = availableBalance !== null ? availableBalance : user.balance;
      
      // Se não temos saldo atualizado ou precisa sincronizar, buscar do servidor
      if (availableBalance === null || syncingBalance) {
        const balanceRes = await fetch(`${API_URL}/api/auth/available-balance`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (balanceRes.ok) {
          const balanceData = await balanceRes.json();
          
          // Se precisa sincronizar saldo do IGameWin, fazer isso primeiro (apenas uma vez)
          if (balanceData.needs_sync && !syncingBalance) {
            setSyncingBalance(true);
            console.log('[Withdrawal] Sincronizando saldo do IGameWin antes do saque...');
            try {
              const syncRes = await fetch(`${API_URL}/api/public/games/sync-balance`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (syncRes.ok) {
                console.log('[Withdrawal] Saldo sincronizado com sucesso');
                // Aguardar um pouco antes de buscar novamente
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Buscar saldo atualizado após sincronização
                const updatedBalanceRes = await fetch(`${API_URL}/api/auth/available-balance`, {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  }
                });
                if (updatedBalanceRes.ok) {
                  const updatedBalanceData = await updatedBalanceRes.json();
                  currentBalance = updatedBalanceData.available_balance || user.balance;
                  setAvailableBalance(currentBalance);
                } else {
                  currentBalance = balanceData.available_balance || user.balance;
                  setAvailableBalance(currentBalance);
                }
              } else {
                currentBalance = balanceData.available_balance || user.balance;
                setAvailableBalance(currentBalance);
              }
            } finally {
              setSyncingBalance(false);
            }
          } else {
            currentBalance = balanceData.available_balance || user.balance;
            setAvailableBalance(currentBalance);
          }
        }
      }

      // Verificar saldo disponível
      if (currentBalance < value) {
        setError(`Saldo insuficiente. Disponível: R$ ${currentBalance.toFixed(2)}`);
        setLoading(false);
        return;
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
        // Tratamento específico para erro 502 (Bad Gateway)
        if (response.status === 502) {
          setError('Servidor temporariamente indisponível. Por favor, tente novamente em alguns instantes.');
          setLoading(false);
          return;
        }

        // Tentar obter mensagem de erro do servidor
        let errorMessage = 'Erro ao processar saque. Tente novamente.';
        try {
          const data = await response.json();
          errorMessage = data.detail || data.message || errorMessage;
        } catch {
          // Se não conseguir parsear JSON, usar mensagem padrão baseada no status
          if (response.status === 400) {
            errorMessage = 'Dados inválidos. Verifique os valores informados.';
          } else if (response.status === 401) {
            errorMessage = 'Sessão expirada. Por favor, faça login novamente.';
          } else if (response.status === 500) {
            errorMessage = 'Erro interno do servidor. Tente novamente mais tarde.';
          }
        }
        throw new Error(errorMessage);
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
                <p className="text-yellow-400">⚠️ Valor mínimo: R$ {minWithdrawal.toFixed(2).replace('.', ',')}</p>
                <p className="text-white">
                  💰 Saldo disponível: {
                    loadingBalance 
                      ? 'Carregando...' 
                      : `R$ ${(availableBalance !== null ? availableBalance : user?.balance || 0).toFixed(2).replace('.', ',')}`
                  }
                </p>
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
