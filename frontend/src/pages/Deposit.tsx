import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, Copy, Check, Loader2, QrCode, AlertCircle } from 'lucide-react';
import QRCodeSVG from 'react-qr-code';
import { trackMetaEvent } from '../components/MetaPixel';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Deposit() {
  const navigate = useNavigate();
  const { user, token, refreshUser } = useAuth();
  const [amount, setAmount] = useState('');
  const [minDeposit, setMinDeposit] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [deposit, setDeposit] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [qrCodeError, setQrCodeError] = useState(false);
  const [paymentConfirmed, setPaymentConfirmed] = useState(false);

  useEffect(() => {
    const fetchMinimums = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/minimums`);
        if (res.ok) {
          const data = await res.json();
          setMinDeposit(Number(data.min_deposit) || 2);
        }
      } catch {
        // mantém 2 como padrão
      }
    };
    fetchMinimums();
  }, []);

  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setDeposit(null);

    if (!token || !user) {
      setError('Você precisa estar logado para depositar');
      return;
    }

    const value = parseFloat(amount.replace(',', '.'));
    if (isNaN(value) || value <= 0) {
      setError('Valor inválido. Digite um valor maior que zero.');
      return;
    }

    if (value < minDeposit) {
      setError(`Valor mínimo de depósito é R$ ${minDeposit.toFixed(2).replace('.', ',')}`);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/public/payments/deposit/pix`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: value,
          payer_name: user.username || user.email,
          payer_tax_id: user.cpf || '', // CPF será gerado automaticamente no backend se não fornecido
          payer_email: user.email,
          payer_phone: user.phone || undefined
        })
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: 'Erro ao gerar PIX' }));
        // Tratar erros de validação (422) que podem ter formato diferente
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            // FastAPI retorna array de erros de validação
            const errors = data.detail.map((err: any) => err.msg || err.message || JSON.stringify(err)).join(', ');
            throw new Error(errors);
          } else if (typeof data.detail === 'string') {
            throw new Error(data.detail);
          } else {
            throw new Error(JSON.stringify(data.detail));
          }
        }
        throw new Error('Erro ao gerar código PIX');
      }

      const data = await response.json();
      setDeposit(data);
      setQrCodeError(false); // Reset QR code error when new deposit is created
      
      // Disparar evento InitiateCheckout do Meta Pixel
      trackMetaEvent('InitiateCheckout', {
        content_name: 'Depósito PIX',
        value: value,
        currency: 'BRL'
      });
    } catch (err: any) {
      setError(err.message || 'Erro ao processar depósito. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const copyPixCode = () => {
    if (deposit?.metadata_json) {
      try {
        const metadata = JSON.parse(deposit.metadata_json);
        const pixCode = metadata.pix_code;
        if (pixCode) {
          navigator.clipboard.writeText(pixCode);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }
      } catch (e) {
        console.error('Erro ao copiar código PIX:', e);
      }
    }
  };

  const getPixCode = () => {
    if (deposit?.metadata_json) {
      try {
        const metadata = JSON.parse(deposit.metadata_json);
        return metadata.pix_code || '';
      } catch (e) {
        return '';
      }
    }
    return '';
  };

  const getPixQrCode = () => {
    if (deposit?.metadata_json) {
      try {
        const metadata = JSON.parse(deposit.metadata_json);
        return metadata.pix_qr_code_base64 || '';
      } catch (e) {
        return '';
      }
    }
    return '';
  };

  // Verificar confirmação de pagamento via notificações quando há depósito pendente
  useEffect(() => {
    if (!deposit || !token || paymentConfirmed) return;

    // Verificar se o depósito está pendente
    const isPending = deposit.status === 'pending';
    if (!isPending) {
      // Se já foi aprovado, atualizar saldo e marcar como confirmado
      if (deposit.status === 'approved') {
        setPaymentConfirmed(true);
        refreshUser().catch(err => {
          console.warn('[Deposit] Erro ao atualizar saldo:', err);
        });
      }
      return;
    }

    // Verificar notificações de depósito aprovado a cada 3 segundos quando pendente
    const checkPaymentConfirmation = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/notifications`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (res.ok) {
          const notifications = await res.json();
          
          // Procurar notificação de depósito aprovado recente
          const depositNotification = notifications.find((n: any) => 
            n.type === 'success' && 
            (n.title.includes('Depósito') || n.message.includes('depósito')) &&
            n.message.includes(deposit.amount.toFixed(2))
          );
          
          if (depositNotification) {
            console.log('[Deposit] ✅ Pagamento confirmado via notificação! Atualizando saldo...');
            setPaymentConfirmed(true);
            
            // Atualizar saldo do usuário
            await refreshUser();
            
            // Extrair valor do depósito
            const depositAmount = deposit?.amount || 0;
            
            // Disparar evento Purchase do Meta Pixel
            trackMetaEvent('Purchase', {
              value: depositAmount,
              currency: 'BRL'
            });
            
            // Verificar se é primeiro depósito (FTD) para disparar Lead
            // Verificar histórico de depósitos para determinar se é FTD
            try {
              const transactionsRes = await fetch(`${API_URL}/api/auth/transactions`, {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              if (transactionsRes.ok) {
                const transactionsData = await transactionsRes.json();
                const deposits = (transactionsData.transactions || []).filter((t: any) => 
                  t.type === 'deposit' && t.status === 'approved'
                );
                // Se este é o primeiro depósito aprovado, disparar Lead
                if (deposits.length === 1) {
                  trackMetaEvent('Lead', {
                    content_name: 'First Time Deposit',
                    value: depositAmount,
                    currency: 'BRL'
                  });
                }
              }
            } catch (err) {
              console.warn('[Deposit] Erro ao verificar FTD:', err);
            }
            
            // Limpar erro se houver
            setError('');
          }
        }
      } catch (err) {
        console.warn('[Deposit] Erro ao verificar notificações:', err);
      }
    };

    // Verificar imediatamente e depois a cada 3 segundos
    checkPaymentConfirmation();
    const interval = setInterval(checkPaymentConfirmation, 3000);

    return () => clearInterval(interval);
  }, [deposit, token, paymentConfirmed, refreshUser]);

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
            <h1 className="text-xl md:text-2xl font-bold">Depositar</h1>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {!deposit ? (
          <form onSubmit={handleDeposit} className="space-y-6">
            {/* Informações */}
            <div className="bg-gradient-to-br from-[#0a4d3e] to-[#0d5d4b] rounded-2xl p-6 border border-[#d4af37]/20">
              <h2 className="text-xl font-bold mb-4">Depósito via PIX</h2>
              <p className="text-gray-300 text-sm mb-4">
                Digite o valor que deseja depositar. O código PIX será gerado automaticamente.
              </p>
              <p className="text-yellow-400 text-sm">
                ⚠️ Valor mínimo: R$ {minDeposit.toFixed(2).replace('.', ',')}
              </p>
            </div>

            {/* Formulário */}
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Valor do Depósito (R$)
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

                {error && (
                  <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !amount}
                  className="w-full bg-[#ff6b35] hover:bg-[#ff7b35] disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin" size={20} />
                      Gerando código PIX...
                    </>
                  ) : (
                    'Gerar Código PIX'
                  )}
                </button>
              </div>
            </div>
          </form>
        ) : (
          <div className="space-y-6">
            {/* Mensagem de Pagamento Confirmado */}
            {paymentConfirmed && (
              <div className="bg-gradient-to-br from-green-900/50 to-green-800/50 rounded-2xl p-6 border-2 border-green-500 animate-pulse">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-green-500/30 p-2 rounded-lg">
                    <Check className="text-green-400" size={24} />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-green-400">✅ Pagamento Confirmado!</h2>
                    <p className="text-gray-200 text-sm mt-1">
                      Seu depósito de R$ {deposit.amount.toFixed(2).replace('.', ',')} foi aprovado e creditado na sua conta.
                    </p>
                    {user && (
                      <p className="text-[#d4af37] font-semibold mt-2">
                        Saldo atual: R$ {user.balance.toFixed(2).replace('.', ',')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Sucesso - QR Code Gerado */}
            {!paymentConfirmed && (
              <div className="bg-gradient-to-br from-green-900/30 to-green-800/30 rounded-2xl p-6 border border-green-500/30">
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-green-500/20 p-2 rounded-lg">
                    <Check className="text-green-400" size={24} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">Código PIX Gerado!</h2>
                    <p className="text-gray-300 text-sm">Escaneie o QR Code ou copie o código PIX</p>
                    <p className="text-yellow-400 text-xs mt-1">
                      ⏳ Aguardando confirmação do pagamento...
                    </p>
                  </div>
                </div>
                <div className="bg-gray-900 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Valor a pagar:</p>
                  <p className="text-2xl font-bold text-[#d4af37]">
                    R$ {deposit.amount.toFixed(2).replace('.', ',')}
                  </p>
                </div>
              </div>
            )}

            {/* QR Code */}
            {getPixCode() && (
              <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 text-center">
                <h3 className="text-lg font-bold mb-4 flex items-center justify-center gap-2">
                  <QrCode size={20} className="text-[#d4af37]" />
                  QR Code PIX
                </h3>
                <div className="bg-white p-4 rounded-lg inline-block">
                  {getPixQrCode() && getPixQrCode().trim() && !qrCodeError ? (
                    <img
                      src={`data:image/png;base64,${getPixQrCode()}`}
                      alt="QR Code PIX"
                      className="w-64 h-64 mx-auto"
                      onError={() => {
                        // Se a imagem base64 falhar, marcar erro para usar QR gerado
                        setQrCodeError(true);
                      }}
                    />
                  ) : (
                    <div className="w-64 h-64 mx-auto flex items-center justify-center">
                      <QRCodeSVG
                        value={getPixCode()}
                        size={256}
                        level="H"
                        bgColor="#ffffff"
                        fgColor="#000000"
                      />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Código PIX */}
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <h3 className="text-lg font-bold mb-4">Código PIX (Copiar e Colar)</h3>
              <div className="bg-gray-800 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-300 break-all font-mono">
                  {getPixCode()}
                </p>
              </div>
              <button
                onClick={copyPixCode}
                className="w-full bg-[#d4af37] hover:bg-[#ffd700] text-black font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {copied ? (
                  <>
                    <Check size={20} />
                    Código Copiado!
                  </>
                ) : (
                  <>
                    <Copy size={20} />
                    Copiar Código PIX
                  </>
                )}
              </button>
            </div>

            {/* Instruções */}
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-3">Como pagar:</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-300">
                <li>Abra o app do seu banco</li>
                <li>Escolha a opção PIX</li>
                <li>Escaneie o QR Code ou cole o código PIX</li>
                <li>Confirme o pagamento</li>
                <li>Seu saldo será creditado automaticamente após confirmação</li>
              </ol>
            </div>

            {/* Botões */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setDeposit(null);
                  setAmount('');
                  setError('');
                }}
                className="flex-1 bg-gray-800 hover:bg-gray-700 text-white font-semibold py-3 rounded-lg transition-colors"
              >
                Novo Depósito
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
