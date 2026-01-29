import { X, Search, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  filters: { query: string; provider: string };
  onFiltersChange: (partial: { query?: string; provider?: string }) => void;
  providers?: string[];
}

// Backend FastAPI - usa variável de ambiente ou fallback para localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Game {
  name: string;
  code: string;
}

export default function Sidebar({ isOpen, onClose, filters, onFiltersChange, providers = [] }: SidebarProps) {
  const navigate = useNavigate();
  const [popularGames, setPopularGames] = useState<Game[]>([]);
  const [loadingGames, setLoadingGames] = useState(true);
  
  // Nomes dos jogos que queremos exibir no menu
  const gameNamesToShow = [
    'Fortune Tiger',
    'Mine',
    'Gate of Olympus',
    'Aviator',
  ];

  useEffect(() => {
    const fetchGames = async () => {
      setLoadingGames(true);
      try {
        const res = await fetch(`${API_URL}/api/public/games`);
        if (!res.ok) throw new Error('Falha ao carregar jogos');
        const data = await res.json();
        const allGames: Game[] = (data.games || []).map((g: any) => ({
          name: g.name || g.title || '',
          code: g.code || '',
        }));

        // Filtrar e mapear os jogos que queremos exibir
        const matchedGames: Game[] = [];
        for (const gameName of gameNamesToShow) {
          // Buscar jogo que corresponde ao título (busca parcial, case-insensitive)
          const normalizedGameName = gameName.toLowerCase().trim();
          const matchedGame = allGames.find((g) => {
            const normalizedGameTitle = g.name.toLowerCase().trim();
            return normalizedGameTitle.includes(normalizedGameName) || 
                   normalizedGameName.includes(normalizedGameTitle);
          });

          if (matchedGame && matchedGame.code) {
            matchedGames.push({
              name: matchedGame.name,
              code: matchedGame.code,
            });
          }
        }

        setPopularGames(matchedGames);
      } catch (err) {
        console.error('Erro ao buscar jogos para o menu', err);
        // Em caso de erro, usar lista estática como fallback
        setPopularGames([
          { name: 'Fortune Tiger', code: 'fortune-tiger' },
          { name: 'Mine', code: 'mine' },
          { name: 'Gate of Olympus', code: 'gate-of-olympus' },
          { name: 'Aviator', code: 'aviator' },
        ]);
      } finally {
        setLoadingGames(false);
      }
    };

    fetchGames();
  }, []);

  const handleSupportClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onClose(); // Fechar sidebar primeiro
    // Scroll para o topo e tentar abrir o chat widget
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      const chatButton = document.querySelector('[aria-label="Abrir chat"]') as HTMLElement;
      if (chatButton) {
        chatButton.click();
      } else {
        // Se não encontrar o botão, apenas navegar para home onde o chat está disponível
        navigate('/');
      }
    }, 100);
  };

  const handlePromocoesClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onClose(); // Fechar sidebar primeiro
    navigate('/promocoes');
  };

  return (
    <>
      {/* Overlay para mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen w-[220px] bg-[#0a4d3e] text-white z-[60] overflow-y-auto shadow-2xl transition-transform border-r border-[#0d5d4b] sidebar-custom md:fixed md:top-[60px] md:h-[calc(100vh-60px)] md:z-40 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="min-h-full pb-6">
          {/* Close button apenas no mobile */}
          <button
            onClick={onClose}
            className="md:hidden absolute top-3 right-3 p-2 hover:bg-[#0d5d4b] rounded transition-colors z-10"
            aria-label="Fechar menu"
          >
            <X size={20} />
          </button>

          {/* Promoções */}
          <div className="border-b border-[#0d5d4b]">
            <div className="px-4 py-3 space-y-3">
              {/* Cashback */}
              <button
                onClick={(e) => {
                  e.preventDefault();
                  onClose();
                  navigate('/depositar');
                }}
                className="w-full bg-blue-600 rounded-lg p-4 text-left hover:bg-blue-700 transition-all duration-200 border-2 border-blue-600 hover:border-blue-500 hover:shadow-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-blue-100 font-semibold uppercase mb-1.5 leading-tight">Cashback 25%</div>
                    <div className="text-base font-bold text-white leading-tight">Depositar</div>
                  </div>
                </div>
              </button>

              {/* Promoções - com efeito neon */}
              <button
                onClick={handlePromocoesClick}
                className="neon-button w-full relative bg-gray-800 border-2 border-yellow-500 rounded-lg p-4 text-left hover:border-yellow-400 transition-all duration-200 overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-500/0 via-yellow-500/50 to-yellow-500/0 animate-shimmer"></div>
                <div className="relative flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-gray-400 font-semibold uppercase mb-1.5 leading-tight">Acesse as</div>
                    <div className="text-base font-bold text-white leading-tight">Promoções</div>
                  </div>
                  <div className="text-3xl ml-2 flex-shrink-0">🎁</div>
                </div>
              </button>

              {/* Chat - com efeito neon */}
              <button
                onClick={handleSupportClick}
                className="neon-button w-full relative bg-gray-800 border-2 border-yellow-500 rounded-lg p-4 text-left hover:border-yellow-400 transition-all duration-200 overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-500/0 via-yellow-500/50 to-yellow-500/0 animate-shimmer"></div>
                <div className="relative flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-gray-400 font-semibold uppercase mb-1.5 leading-tight">Chat ao vivo</div>
                    <div className="text-base font-bold text-white leading-tight">Suporte 24h</div>
                  </div>
                  <div className="text-3xl ml-2 flex-shrink-0">💬</div>
                </div>
              </button>
            </div>
          </div>

          {/* Barra de Pesquisa */}
          <div className="border-b border-[#0d5d4b] px-4 py-3">
            <div className="relative mb-2">
              <input
                type="text"
                placeholder="Pesquise um jogo..."
                value={filters.query}
                onChange={(e) => onFiltersChange({ query: e.target.value })}
                className="w-full bg-[#0d5d4b] border border-[#0a4d3e] rounded-lg px-3 py-2 pr-9 text-white text-xs placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#d4af37] focus:border-transparent transition-all duration-200"
              />
              <Search className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400" size={14} />
            </div>
            <div className="relative">
              <select
                value={filters.provider}
                onChange={(e) => onFiltersChange({ provider: e.target.value })}
                className="w-full bg-[#0d5d4b] border border-[#0a4d3e] rounded-lg px-3 py-2 text-white text-xs appearance-none focus:outline-none focus:ring-2 focus:ring-[#d4af37] focus:border-transparent transition-all duration-200 pr-8"
              >
                <option value="">Todos os provedores</option>
                {providers.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={14} />
            </div>
          </div>

          {/* Jogos Populares */}
          <nav className="border-b border-[#0d5d4b]">
            <div className="flex items-center justify-between px-4 py-3 bg-[#0a4d3e]">
              <h3 className="text-sm font-bold text-[#d4af37] uppercase tracking-wide">Jogos Populares</h3>
            </div>
            <div className="px-4 pb-3">
              {loadingGames ? (
                <div className="text-center py-4">
                  <div className="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-[#d4af37]"></div>
                </div>
              ) : (
                <ul className="space-y-1">
                  {popularGames.map((game) => (
                    <li key={game.code}>
                      <a
                        href={`/jogo/${game.code}`}
                        onClick={(e) => {
                          e.preventDefault();
                          onClose();
                          navigate(`/jogo/${game.code}`);
                        }}
                        className="block px-1 py-2 rounded-md text-xs hover:bg-[#0d5d4b] transition-all duration-200 text-gray-100 hover:text-white"
                      >
                        {game.name}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </nav>

          {/* Links de Suporte e Promoções */}
          <nav className="px-4 pt-4 pb-6">
            <ul className="space-y-1">
              <li>
                <button
                  onClick={handleSupportClick}
                  className="block w-full text-left px-1 py-2 rounded-md text-xs hover:bg-[#0d5d4b] transition-all duration-200 text-gray-100 hover:text-white"
                >
                  Suporte Ao Vivo
                </button>
              </li>
              <li>
                <button
                  onClick={handlePromocoesClick}
                  className="block w-full text-left px-1 py-2 rounded-md text-xs hover:bg-[#0d5d4b] transition-all duration-200 text-gray-100 hover:text-white"
                >
                  Promoções
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </aside>
    </>
  );
}
