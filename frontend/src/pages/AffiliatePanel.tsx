import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, DollarSign, Users, TrendingUp, Copy, Check, Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type AffiliateTab = 'comecar' | 'link' | 'meus-dados' | 'desempenho' | 'comissao';
type PeriodKey = 'this_week' | 'last_week' | 'this_month' | 'last_month';

const PERIOD_LABELS: Record<PeriodKey, string> = {
  this_week: 'Esta Semana',
  last_week: 'Última Semana',
  this_month: 'Este Mês',
  last_month: 'Mês passado',
};

interface MeusDadosResponse {
  period: string;
  novos_subordinados: number;
  depositos: number;
  primeiros_depositos: number;
  usuarios_registrados_com_1_deposito: number;
  valor_deposito: number;
  valor_primeiro_deposito: number;
  registro_e_1_deposito: number;
  valor_saque: number;
  numero_saques: number;
  receber_recompensas: number;
  apostas_validas: number;
  vd_diretas: number;
}

function fmtNum(n: number): string {
  return (n ?? 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function fmtBrl(n: number): string {
  return (n ?? 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function AffiliatePanel() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [affiliate, setAffiliate] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<AffiliateTab>('link');
  const [period, setPeriod] = useState<PeriodKey>('this_month');
  const [meusDados, setMeusDados] = useState<MeusDadosResponse | null>(null);
  const [meusDadosLoading, setMeusDadosLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }
    fetchAffiliateData();
  }, [token, navigate]);

  useEffect(() => {
    if (activeTab === 'meus-dados' && affiliate && token) {
      fetchMeusDados();
    }
  }, [activeTab, period, affiliate?.id, token]);

  const fetchAffiliateData = async () => {
    try {
      const res = await fetch(`${API_URL}/api/public/affiliate/dashboard`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        if (res.status === 404) {
          setError('Você não é um afiliado. Entre em contato com o suporte.');
        } else {
          throw new Error('Erro ao carregar dados do afiliado');
        }
        setLoading(false);
        return;
      }
      const data = await res.json();
      setAffiliate(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const fetchMeusDados = async () => {
    setMeusDadosLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/api/public/affiliate/meus-dados?period=${period}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (res.ok) {
        const data = await res.json();
        setMeusDados(data);
      } else {
        setMeusDados(null);
      }
    } catch {
      setMeusDados(null);
    } finally {
      setMeusDadosLoading(false);
    }
  };

  const copyAffiliateLink = () => {
    if (affiliate?.affiliate_code) {
      const link = `${window.location.origin}?ref=${affiliate.affiliate_code}`;
      navigator.clipboard.writeText(link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const tabs: { id: AffiliateTab; label: string }[] = [
    { id: 'comecar', label: 'Começar' },
    { id: 'link', label: 'Link de Convite' },
    { id: 'meus-dados', label: 'Meus Dados' },
    { id: 'desempenho', label: 'Desempenho' },
    { id: 'comissao', label: 'Comissão' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e0f] text-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin h-12 w-12 mx-auto mb-4 text-[#d4af37]" />
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  if (error && !affiliate) {
    return (
      <div className="min-h-screen bg-[#0a0e0f] text-white">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-6">
            <p className="text-red-400">{error}</p>
            <button
              onClick={() => navigate('/conta')}
              className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
            >
              Voltar
            </button>
          </div>
        </div>
      </div>
    );
  }

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
            <h1 className="text-xl md:text-2xl font-bold">Promoção</h1>
          </div>
        </div>
        {/* Tabs */}
        <div className="container mx-auto px-4 flex gap-1 overflow-x-auto no-scrollbar border-b border-[#0d5d4b]/50">
          {tabs.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-[#d4af37] text-[#d4af37]'
                  : 'border-transparent text-gray-300 hover:text-white'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Começar */}
        {activeTab === 'comecar' && (
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <h2 className="text-xl font-bold mb-4">Como começar</h2>
            <ul className="space-y-3 text-gray-300">
              <li>1. Copie seu <strong className="text-[#d4af37]">Link de Convite</strong> na aba ao lado.</li>
              <li>2. Compartilhe o link com seus amigos (WhatsApp, redes sociais, etc.).</li>
              <li>3. Quando alguém se cadastrar pelo seu link e fizer o primeiro depósito, você ganha CPA e revshare.</li>
              <li>4. Acompanhe tudo em <strong className="text-[#d4af37]">Meus Dados</strong> e <strong className="text-[#d4af37]">Comissão</strong>.</li>
            </ul>
          </div>
        )}

        {/* Link de Convite */}
        {activeTab === 'link' && (
          <>
            <div className="bg-gradient-to-br from-[#0a4d3e] to-[#0d5d4b] rounded-2xl p-6 mb-6 border border-[#d4af37]/20">
              <h2 className="text-xl font-bold mb-4">Seu Link de Afiliado</h2>
              <div className="bg-gray-900 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-400 mb-2">Código:</p>
                <p className="text-2xl font-bold text-[#d4af37] mb-4">{affiliate?.affiliate_code}</p>
                <p className="text-sm text-gray-400 mb-2">Link completo:</p>
                <p className="text-sm break-all font-mono">
                  {typeof window !== 'undefined' ? `${window.location.origin}?ref=${affiliate?.affiliate_code}` : ''}
                </p>
              </div>
              <button
                onClick={copyAffiliateLink}
                className="w-full bg-[#d4af37] hover:bg-[#ffd700] text-black font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {copied ? <><Check size={20} /> Link Copiado!</> : <><Copy size={20} /> Copiar Link</>}
              </button>
            </div>
          </>
        )}

        {/* Meus Dados - grid com filtro de período */}
        {activeTab === 'meus-dados' && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {(Object.keys(PERIOD_LABELS) as PeriodKey[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    period === p
                      ? 'bg-[#d4af37] text-black'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {PERIOD_LABELS[p]}
                </button>
              ))}
            </div>
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <h2 className="text-lg font-bold mb-4">Dados do Subordinado</h2>
              {meusDadosLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="animate-spin h-10 w-10 text-[#d4af37]" />
                </div>
              ) : meusDados ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  <MetricCard label="Novos subordinados" value={fmtNum(meusDados.novos_subordinados)} />
                  <MetricCard label="Depósitos" value={fmtNum(meusDados.depositos)} />
                  <MetricCard label="Primeiros Depósitos" value={fmtNum(meusDados.primeiros_depositos)} />
                  <MetricCard label="Usuários registrados com 1º depósito" value={fmtNum(meusDados.usuarios_registrados_com_1_deposito)} />
                  <MetricCard label="Depósito" value={`R$ ${fmtBrl(meusDados.valor_deposito)}`} />
                  <MetricCard label="Valor do primeiro depósito" value={`R$ ${fmtBrl(meusDados.valor_primeiro_deposito)}`} />
                  <MetricCard label="Registro e 1º depósito" value={`R$ ${fmtBrl(meusDados.registro_e_1_deposito)}`} />
                  <MetricCard label="Valor do Saque" value={`R$ ${fmtBrl(meusDados.valor_saque)}`} />
                  <MetricCard label="Número de saques" value={fmtNum(meusDados.numero_saques)} />
                  <MetricCard label="Receber recompensas" value={`R$ ${fmtBrl(meusDados.receber_recompensas)}`} highlight />
                  <MetricCard label="Apostas Válidas" value={`R$ ${fmtBrl(meusDados.apostas_validas)}`} highlight />
                  <MetricCard label="V/D diretas" value={`R$ ${fmtBrl(meusDados.vd_diretas)}`} negative={meusDados.vd_diretas < 0} />
                </div>
              ) : (
                <p className="text-gray-400 py-4">Nenhum dado disponível para o período.</p>
              )}
            </div>
          </div>
        )}

        {/* Desempenho - resumo geral */}
        {activeTab === 'desempenho' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <Users className="text-[#d4af37]" size={24} />
                <h3 className="text-sm text-gray-400">Indicações</h3>
              </div>
              <p className="text-2xl font-bold">{affiliate?.total_referrals ?? 0}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign className="text-green-400" size={24} />
                <h3 className="text-sm text-gray-400">Depósitos dos indicados</h3>
              </div>
              <p className="text-2xl font-bold">R$ {fmtBrl(affiliate?.total_deposits ?? 0)}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="text-blue-400" size={24} />
                <h3 className="text-sm text-gray-400">CPA Ganho</h3>
              </div>
              <p className="text-2xl font-bold">R$ {fmtBrl(affiliate?.total_cpa_earned ?? 0)}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign className="text-[#d4af37]" size={24} />
                <h3 className="text-sm text-gray-400">Revshare Ganho</h3>
              </div>
              <p className="text-2xl font-bold">R$ {fmtBrl(affiliate?.total_revshare_earned ?? 0)}</p>
            </div>
          </div>
        )}

        {/* Comissão */}
        {activeTab === 'comissao' && (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                <h3 className="text-sm text-gray-400 mb-2">Total Ganho</h3>
                <p className="text-2xl font-bold text-[#d4af37]">R$ {fmtBrl(affiliate?.total_earnings ?? 0)}</p>
              </div>
              <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                <h3 className="text-sm text-gray-400 mb-2">CPA Ganho</h3>
                <p className="text-2xl font-bold">R$ {fmtBrl(affiliate?.total_cpa_earned ?? 0)}</p>
              </div>
              <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                <h3 className="text-sm text-gray-400 mb-2">Revshare Ganho</h3>
                <p className="text-2xl font-bold">R$ {fmtBrl(affiliate?.total_revshare_earned ?? 0)}</p>
              </div>
              <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                <h3 className="text-sm text-gray-400 mb-2">Status</h3>
                <p className={`text-lg font-semibold ${affiliate?.is_active ? 'text-green-400' : 'text-red-400'}`}>
                  {affiliate?.is_active ? 'Ativo' : 'Inativo'}
                </p>
              </div>
            </div>
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <h2 className="text-xl font-bold mb-4">Configurações da Comissão</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400 mb-1">CPA (Cost Per Acquisition)</p>
                  <p className="text-2xl font-bold text-[#d4af37]">R$ {fmtBrl(affiliate?.cpa_amount ?? 0)}</p>
                  <p className="text-xs text-gray-500 mt-1">Por cada novo jogador com 1º depósito</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Revshare</p>
                  <p className="text-2xl font-bold text-[#d4af37]">{(affiliate?.revshare_percentage ?? 0).toFixed(2)}%</p>
                  <p className="text-xs text-gray-500 mt-1">Sobre os depósitos dos indicados</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  highlight,
  negative,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  negative?: boolean;
}) {
  return (
    <div className={`rounded-xl p-4 border ${highlight ? 'border-[#d4af37]/50 bg-[#d4af37]/5' : 'border-gray-800 bg-gray-800/50'}`}>
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className={`text-lg font-bold ${negative ? 'text-red-400' : highlight ? 'text-[#d4af37]' : ''}`}>
        {value}
      </p>
    </div>
  );
}
