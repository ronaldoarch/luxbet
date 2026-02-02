import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, DollarSign, Users, TrendingUp, Loader2, UserPlus } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type ManagerTab = 'comecar' | 'sub-afiliados' | 'desempenho' | 'comissao';

function fmtBrl(n: number): string {
  return (n ?? 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function ManagerPanel() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [manager, setManager] = useState<any>(null);
  const [subs, setSubs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<ManagerTab>('sub-afiliados');
  const [subForm, setSubForm] = useState({
    username: '',
    email: '',
    password: '',
    affiliate_code: '',
    cpa_amount: '',
    revshare_percentage: '0'
  });
  const [creating, setCreating] = useState(false);
  const [createSuccess, setCreateSuccess] = useState('');

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }
    fetchManagerData();
  }, [token, navigate]);

  useEffect(() => {
    if (manager && token && activeTab === 'sub-afiliados') {
      fetchSubs();
    }
  }, [manager, activeTab, token]);

  const fetchManagerData = async () => {
    try {
      const res = await fetch(`${API_URL}/api/public/manager/dashboard`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        if (res.status === 404) {
          setError('Você não é um gerente. Entre em contato com o suporte.');
        } else {
          throw new Error('Erro ao carregar dados do gerente');
        }
        setLoading(false);
        return;
      }
      const data = await res.json();
      setManager(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/public/manager/sub-affiliates`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setSubs(data);
      }
    } catch {
      setSubs([]);
    }
  };

  const handleCreateSub = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setCreateSuccess('');
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/public/manager/sub-affiliates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          username: subForm.username,
          email: subForm.email,
          password: subForm.password,
          affiliate_code: subForm.affiliate_code,
          cpa_amount: parseFloat(subForm.cpa_amount) || 0,
          revshare_percentage: parseFloat(subForm.revshare_percentage) || 0
        })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Erro ao criar sub-afiliado');
      }
      setCreateSuccess('Sub-afiliado criado com sucesso!');
      setSubForm({ username: '', email: '', password: '', affiliate_code: '', cpa_amount: '', revshare_percentage: '0' });
      fetchSubs();
      fetchManagerData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const tabs: { id: ManagerTab; label: string }[] = [
    { id: 'comecar', label: 'Começar' },
    { id: 'sub-afiliados', label: 'Sub-Afiliados' },
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

  if (error && !manager) {
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
            <h1 className="text-xl md:text-2xl font-bold">Painel do Gerente</h1>
          </div>
        </div>
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
        {activeTab === 'comecar' && (
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <h2 className="text-xl font-bold mb-4">Como funciona o painel do Gerente</h2>
            <ul className="space-y-3 text-gray-300">
              <li>1. O admin atribuiu um <strong className="text-[#d4af37]">CPA Pool</strong> (ex: R$ 30) para você.</li>
              <li>2. Crie <strong className="text-[#d4af37]">Sub-Afiliados</strong> na aba ao lado e distribua o CPA entre eles.</li>
              <li>3. Quando um sub-afiliado trouxer alguém pelo link e essa pessoa fizer o 1º depósito: o sub ganha o CPA que você definiu e você ganha a mesma quantia (comissão sobre o que distribuiu).</li>
              <li>4. Exemplo: você tem 30 de CPA, cria um sub com 15 de CPA. Quando o sub converter, ele ganha 15 e você ganha 15.</li>
            </ul>
          </div>
        )}

        {activeTab === 'sub-afiliados' && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <UserPlus size={24} /> Criar Sub-Afiliado
              </h2>
              {error && <div className="bg-red-500/20 text-red-400 p-3 rounded mb-4">{error}</div>}
              {createSuccess && <div className="bg-green-500/20 text-green-400 p-3 rounded mb-4">{createSuccess}</div>}
              <form onSubmit={handleCreateSub} className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Username *</label>
                  <input
                    type="text"
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600 focus:border-[#d4af37] focus:outline-none"
                    value={subForm.username}
                    onChange={e => setSubForm({ ...subForm, username: e.target.value })}
                    required
                    placeholder="usuario123"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Email *</label>
                  <input
                    type="email"
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600 focus:border-[#d4af37] focus:outline-none"
                    value={subForm.email}
                    onChange={e => setSubForm({ ...subForm, email: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Senha *</label>
                  <input
                    type="password"
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600 focus:border-[#d4af37] focus:outline-none"
                    value={subForm.password}
                    onChange={e => setSubForm({ ...subForm, password: e.target.value })}
                    required
                    minLength={6}
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Código do Afiliado *</label>
                  <input
                    type="text"
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600 focus:border-[#d4af37] focus:outline-none"
                    value={subForm.affiliate_code}
                    onChange={e => setSubForm({ ...subForm, affiliate_code: e.target.value })}
                    required
                    placeholder="SUB001"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">CPA (R$) - para este sub *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600 focus:border-[#d4af37] focus:outline-none"
                    value={subForm.cpa_amount}
                    onChange={e => setSubForm({ ...subForm, cpa_amount: e.target.value })}
                    required
                    placeholder="15"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Revshare (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600 focus:border-[#d4af37] focus:outline-none"
                    value={subForm.revshare_percentage}
                    onChange={e => setSubForm({ ...subForm, revshare_percentage: e.target.value })}
                    placeholder="0"
                  />
                </div>
                <div className="md:col-span-2 lg:col-span-3">
                  <button
                    type="submit"
                    disabled={creating}
                    className="px-6 py-3 bg-[#d4af37] hover:bg-[#ffd700] text-black font-semibold rounded-lg disabled:opacity-50"
                  >
                    {creating ? 'Criando...' : 'Criar Sub-Afiliado'}
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <h2 className="text-xl font-bold mb-4">Meus Sub-Afiliados</h2>
              <p className="text-gray-400 text-sm mb-4">
                CPA Pool: R$ {fmtBrl(manager?.cpa_pool ?? 0)} | Distribuído: R$ {fmtBrl(manager?.cpa_distributed ?? 0)}
              </p>
              {subs.length === 0 ? (
                <p className="text-gray-400 py-4">Nenhum sub-afiliado cadastrado ainda.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-400 border-b border-gray-700">
                        <th className="py-3 px-2">Código</th>
                        <th className="py-3 px-2">Usuário</th>
                        <th className="py-3 px-2">CPA</th>
                        <th className="py-3 px-2">Revshare</th>
                        <th className="py-3 px-2">Indicações</th>
                        <th className="py-3 px-2">Depósitos</th>
                        <th className="py-3 px-2">Ganho</th>
                        <th className="py-3 px-2">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {subs.map((s) => (
                        <tr key={s.id} className="border-b border-gray-800">
                          <td className="py-3 px-2 font-mono text-[#d4af37]">{s.affiliate_code}</td>
                          <td className="py-3 px-2">{s.username}</td>
                          <td className="py-3 px-2">R$ {fmtBrl(s.cpa_amount)}</td>
                          <td className="py-3 px-2">{s.revshare_percentage}%</td>
                          <td className="py-3 px-2">{s.total_referrals}</td>
                          <td className="py-3 px-2">R$ {fmtBrl(s.total_deposits)}</td>
                          <td className="py-3 px-2">R$ {fmtBrl(s.total_earnings)}</td>
                          <td className="py-3 px-2">{s.is_active ? 'Ativo' : 'Inativo'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'desempenho' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <Users className="text-[#d4af37]" size={24} />
                <h3 className="text-sm text-gray-400">Sub-Afiliados</h3>
              </div>
              <p className="text-2xl font-bold">{manager?.sub_affiliates_count ?? 0}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign className="text-green-400" size={24} />
                <h3 className="text-sm text-gray-400">CPA Pool</h3>
              </div>
              <p className="text-2xl font-bold">R$ {fmtBrl(manager?.cpa_pool ?? 0)}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="text-blue-400" size={24} />
                <h3 className="text-sm text-gray-400">CPA Ganho</h3>
              </div>
              <p className="text-2xl font-bold">R$ {fmtBrl(manager?.total_cpa_earned ?? 0)}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign className="text-[#d4af37]" size={24} />
                <h3 className="text-sm text-gray-400">Revshare Ganho</h3>
              </div>
              <p className="text-2xl font-bold">R$ {fmtBrl(manager?.total_revshare_earned ?? 0)}</p>
            </div>
          </div>
        )}

        {activeTab === 'comissao' && (
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <h2 className="text-xl font-bold mb-4">Sua Comissão</h2>
            <p className="text-gray-400 mb-4">
              Você ganha o mesmo valor de CPA que atribui aos sub-afiliados quando eles convertem. 
              Também recebe revshare sobre os depósitos dos indicados dos seus subs.
            </p>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Total Ganho</p>
                <p className="text-2xl font-bold text-[#d4af37]">R$ {fmtBrl(manager?.total_earnings ?? 0)}</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">CPA Ganho</p>
                <p className="text-2xl font-bold">R$ {fmtBrl(manager?.total_cpa_earned ?? 0)}</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Revshare Ganho</p>
                <p className="text-2xl font-bold">R$ {fmtBrl(manager?.total_revshare_earned ?? 0)}</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Revshare (%)</p>
                <p className="text-2xl font-bold">{(manager?.revshare_percentage ?? 0).toFixed(2)}%</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
