import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';

// Backend FastAPI - usa variável de ambiente ou fallback para localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Game() {
  const { gameCode } = useParams<{ gameCode: string }>();
  const navigate = useNavigate();
  const { user, token, loading: authLoading, refreshUser } = useAuth();
  const [gameUrl, setGameUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Aguardar o AuthContext terminar de carregar
    if (authLoading) {
      return;
    }

    if (!token || !user) {
      setError('Você precisa estar logado para jogar');
      setLoading(false);
      return;
    }

    // Verificar se o usuário tem saldo (apenas na carga inicial)
    // NÃO revalidar quando user.balance mudar durante o jogo: em Transfer Mode o saldo
    // está no IGameWin e o AuthContext pode atualizar user com balance=0, expulsando o jogador
    if (!user.balance || user.balance <= 0) {
      setError('Você precisa ter saldo para jogar. Faça um depósito primeiro.');
      setLoading(false);
      return;
    }

    if (!gameCode) {
      setError('Código do jogo não encontrado');
      setLoading(false);
      return;
    }

    const launchGame = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/games/${gameCode}/launch?lang=pt`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({ detail: 'Erro ao iniciar jogo' }));
          const errorMessage = data.detail || 'Erro ao iniciar jogo';
          
          // Mensagens de erro mais amigáveis
          if (res.status === 503) {
            setError(`${errorMessage}\n\nO servidor pode estar temporariamente indisponível. Tente novamente em alguns instantes.`);
          } else if (res.status === 401) {
            setError(`${errorMessage}\n\nPor favor, faça logout e login novamente.`);
          } else if (res.status === 502) {
            setError(`${errorMessage}\n\nPor favor, tente novamente em alguns instantes ou entre em contato com o suporte.`);
          } else {
            setError(errorMessage);
          }
          return;
        }

        const data = await res.json();
        const url = data.game_url || data.launch_url;
        
        if (!url) {
          setError('URL do jogo não foi retornada pelo servidor. Por favor, tente novamente.');
          return;
        }
        
        // Validar URL antes de definir
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
          setError('URL do jogo inválida. Por favor, entre em contato com o suporte.');
          return;
        }
        
        setGameUrl(url);
      } catch (err: any) {
        // Tratar erros de rede
        if (err.name === 'TypeError' && err.message.includes('fetch')) {
          setError('Erro de conexão. Verifique sua internet e tente novamente.');
        } else {
          setError(err.message || 'Erro ao carregar jogo. Por favor, tente novamente.');
        }
      } finally {
        setLoading(false);
      }
    };

    launchGame();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- user removido: AuthContext atualiza
    // balance para 0 durante o jogo (saldo no IGameWin); re-executar expulsaria o jogador
  }, [gameCode, token, authLoading]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e0f] text-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin h-12 w-12 text-[#d4af37] mx-auto mb-4" />
          <p className="text-lg">Carregando jogo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0e0f] text-white">
        <div className="container mx-auto px-4 py-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-[#d4af37] hover:text-[#ffd700] mb-6 transition-colors"
          >
            <ArrowLeft size={20} />
            Voltar
          </button>
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 flex items-start gap-4">
            <AlertCircle className="text-red-400 flex-shrink-0 mt-1" size={24} />
            <div>
              <h2 className="text-xl font-bold text-red-400 mb-2">Erro ao carregar jogo</h2>
              <p className="text-red-200">{error}</p>
              <button
                onClick={() => navigate('/')}
                className="mt-4 px-4 py-2 bg-[#ff6b35] hover:bg-[#ff7b35] rounded-lg transition-colors"
              >
                Voltar para Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0e0f] text-white game-container">
      {/* Header com botão voltar */}
      <div className="bg-[#0a4d3e] border-b border-[#0d5d4b] sticky top-0 z-40 game-header">
        <div className="container mx-auto px-4 py-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-white hover:text-[#d4af37] transition-colors"
          >
            <ArrowLeft size={20} />
            <span className="font-medium">Voltar</span>
          </button>
        </div>
      </div>

      {/* Iframe do jogo */}
      {gameUrl && (
        <div className="w-full game-iframe-container relative flex-1 min-h-0">
          <iframe
            src={gameUrl}
            className="w-full h-full min-h-0 flex-1 border-0"
            title="Jogo"
            allow="fullscreen; autoplay; payment; geolocation; microphone; camera"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-presentation allow-downloads"
            referrerPolicy="no-referrer-when-downgrade"
            onError={() => {
              setError('Erro ao carregar o jogo. Por favor, tente novamente.');
              setGameUrl(null);
            }}
            onLoad={() => {
              console.log('[Game] Iframe carregado com sucesso');
            }}
          />
          {/* Overlay de erro caso o iframe falhe */}
          <div id="game-error-overlay" className="hidden absolute inset-0 bg-black/80 flex items-center justify-center z-50">
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 max-w-md mx-4">
              <h3 className="text-xl font-bold text-red-400 mb-2">Erro ao carregar jogo</h3>
              <p className="text-red-200 mb-4">O jogo não pôde ser carregado. Por favor, tente novamente.</p>
              <button
                onClick={() => {
                  window.location.reload();
                }}
                className="px-4 py-2 bg-[#ff6b35] hover:bg-[#ff7b35] rounded-lg transition-colors"
              >
                Recarregar Página
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Atualizar saldo quando usuário volta da página do jogo */}
      {gameUrl && (
        <GameBalanceUpdater refreshUser={refreshUser} />
      )}
    </div>
  );
}

// Componente para atualizar saldo quando usuário SAI do jogo
// IMPORTANTE: 
// - Em Transfer Mode: precisa sincronizar ao sair do jogo (saldo está no IGameWin)
// - Em Seamless Mode: NÃO precisa sincronizar (saldo sempre fica no nosso banco, IGameWin chama /gold_api)
// O backend detecta automaticamente o modo e retorna resposta apropriada.
function GameBalanceUpdater({ refreshUser }: { refreshUser: () => Promise<void> }) {
  useEffect(() => {
    const token = localStorage.getItem('user_token');
    
    const syncAndRefresh = async () => {
      if (!token) return;
      try {
        // Tentar sincronizar (backend vai retornar que não é necessário se estiver em Seamless Mode)
        const syncRes = await fetch(`${API_URL}/api/public/games/sync-balance`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        if (syncRes.ok) {
          const syncData = await syncRes.json();
          if (syncData.mode === 'seamless') {
            console.log('[Game] Seamless Mode - sincronização não necessária');
          } else {
            console.log('[Game] Saldo sincronizado ao sair:', syncData);
          }
        }
      } catch (err) {
        console.warn('[Game] Erro ao sincronizar saldo:', err);
      }
      try {
        // Sempre atualizar dados do usuário (saldo já está atualizado no nosso banco)
        await refreshUser();
      } catch (err) {}
    };
    
    // Sincronizar APENAS ao desmontar (usuário sai da página do jogo)
    // Em Seamless Mode, o backend vai retornar que não é necessário
    return () => {
      syncAndRefresh();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- deps vazias: sync só no unmount real.
    // refreshUser em deps causava loop (cleanup rodava a cada re-render do AuthContext)
  }, []);
  
  return null; // Componente invisível
}
