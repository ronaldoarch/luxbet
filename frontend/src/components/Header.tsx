import { useEffect, useState } from 'react';
import { Gift, Menu as MenuIcon, Wallet, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Backend FastAPI - usa variável de ambiente ou fallback para localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface HeaderProps {
  onMenuClick?: () => void;
  onLoginClick?: () => void;
  onRegisterClick?: () => void;
}

export default function Header({ onMenuClick, onLoginClick, onRegisterClick }: HeaderProps) {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const [totalBalance, setTotalBalance] = useState<number | null>(null);

  useEffect(() => {
    const fetchLogo = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/media/logo`);
        if (res.ok) {
          const data = await res.json();
          if (data.url) {
            // Se a URL já começar com /api, usa direto; senão constrói com API_URL
            const url = data.url.startsWith('/api') 
              ? `${API_URL}${data.url}`
              : `${API_URL}/api/public/media${data.url}`;
            setLogoUrl(url);
          } else {
            setLogoUrl(null);
          }
        }
      } catch (err) {
        console.error('Erro ao buscar logo:', err);
      }
    };
    fetchLogo();
    
    // Polling para atualizar logo (a cada 5 segundos)
    const interval = setInterval(fetchLogo, 5000);
    return () => clearInterval(interval);
  }, []);

  // Buscar saldo total quando usuário está logado
  useEffect(() => {
    if (!user || !token) {
      setTotalBalance(null);
      return;
    }

    const fetchTotalBalance = async () => {
      try {
        const res = await fetch(`${API_URL}/api/auth/available-balance`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          // Exibir saldo total (inclui bônus) no header
          setTotalBalance(data.our_balance || data.total_balance || user.balance);
        }
      } catch (err) {
        // Silenciar erros - usar saldo do user como fallback
        setTotalBalance(user.balance);
      }
    };

    fetchTotalBalance();
    // Atualizar a cada 10 segundos
    const interval = setInterval(fetchTotalBalance, 10000);
    return () => clearInterval(interval);
  }, [user, token]);

  return (
    <header className="w-full bg-[#0a4d3e] text-white sticky top-0 z-40 shadow-md">
      <div className="w-full px-2 md:px-4 py-2 md:py-3">
        <div className="flex items-center justify-between gap-1 md:gap-3">
          {/* Logo e Menu Mobile */}
          <div className="flex items-center gap-1 md:gap-3 flex-shrink-0">
            {onMenuClick && (
              <button
                onClick={onMenuClick}
                className="md:hidden p-1 hover:bg-[#0d5d4b] rounded transition-colors flex-shrink-0"
                aria-label="Abrir menu"
              >
                <MenuIcon size={18} />
              </button>
            )}
            <a href="/" className="flex items-center gap-1 hover:opacity-80 transition-opacity flex-shrink-0">
              {logoUrl ? (
                <img src={logoUrl} alt="Lux Bet" className="w-8 h-8 md:w-12 md:h-12 object-contain" />
              ) : (
                <>
                  <div className="text-base md:text-2xl font-bold tracking-tight">LUX</div>
                  <div className="text-sm md:text-xl font-semibold hidden sm:block">BET</div>
                </>
              )}
              <Gift className="text-[#d4af37] w-3 h-3 md:w-5 md:h-5 flex-shrink-0" />
            </a>
          </div>
          
          {/* Navegação CASSINO - Na mesma linha */}
          <nav className="hidden md:flex items-center gap-6 flex-shrink-0">
            <a 
              href="/cassino" 
              className="py-2 px-3 border-b-2 border-[#ff6b35] text-white font-medium text-sm md:text-base hover:text-[#d4af37] transition-colors"
            >
              CASSINO
            </a>
          </nav>

          {/* Botões de Ação */}
          <div className="flex items-center gap-1 md:gap-3 flex-shrink-0 min-w-0">
            {user ? (
              <>
                {/* Saldo - Mobile e Desktop */}
                <button
                  onClick={() => navigate('/conta')}
                  className="flex items-center gap-1 md:gap-2 px-1.5 md:px-3 py-1 md:py-1.5 bg-[#0d5d4b] hover:bg-[#0f6d5b] rounded-md transition-colors flex-shrink-0"
                  title="Ver saldo completo"
                >
                  <Wallet size={14} className="md:w-[18px] md:h-[18px] text-[#d4af37] flex-shrink-0" />
                  <span className="text-[10px] md:text-sm font-semibold whitespace-nowrap">
                    R$ {(totalBalance !== null ? totalBalance : user.balance).toFixed(2).replace('.', ',')}
                  </span>
                </button>
                {/* Perfil */}
                <button
                  onClick={() => navigate('/conta')}
                  className="p-1.5 md:p-2 hover:bg-[#0d5d4b] rounded transition-colors flex-shrink-0"
                  aria-label="Minha conta"
                >
                  <User size={18} className="md:w-5 md:h-5" />
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={onLoginClick}
                  className="px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-base hover:text-[#d4af37] transition-colors font-medium"
                >
                  Entrar
                </button>
                <button 
                  onClick={onRegisterClick}
                  className="px-2 md:px-6 py-1.5 md:py-2 bg-[#ff6b35] rounded-md hover:bg-[#ff7b35] transition-colors font-semibold text-xs md:text-base"
                >
                  Registre-se
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
