import { Menu, Wallet, User, MessageCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface BottomNavProps {
  onMenuClick?: () => void;
}

export default function BottomNav({ onMenuClick }: BottomNavProps) {
  const navigate = useNavigate();

  const handleMenuClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onMenuClick) {
      onMenuClick();
    }
  };

  const handleSupportClick = (e: React.MouseEvent) => {
    e.preventDefault();
    // Scroll para o topo e abrir chat ou redirecionar para suporte
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Tentar abrir o chat widget se existir
    const chatButton = document.querySelector('[aria-label="Abrir chat"]') as HTMLElement;
    if (chatButton) {
      chatButton.click();
    } else {
      // Fallback: redirecionar para home onde o chat está disponível
      navigate('/');
    }
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-[#0a4d3e] text-white border-t border-[#0d5d4b] z-50 md:hidden">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-around py-3">
          {/* Menu - Abre o sidebar */}
          <button
            onClick={handleMenuClick}
            className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors"
            aria-label="Abrir menu"
          >
            <Menu size={24} />
            <span className="text-xs">Menu</span>
          </button>
          
          {/* Depositar - OK */}
          <a
            href="/depositar"
            onClick={(e) => {
              e.preventDefault();
              navigate('/depositar');
            }}
            className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors"
          >
            <div className="bg-[#ff6b35] p-2 rounded-lg">
              <Wallet size={20} className="text-white" />
            </div>
            <span className="text-xs">Depositar</span>
          </a>
          
          {/* Conta */}
          <a
            href="/conta"
            onClick={(e) => {
              e.preventDefault();
              navigate('/conta');
            }}
            className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors"
          >
            <User size={24} />
            <span className="text-xs">Conta</span>
          </a>
          
          {/* Suporte */}
          <button
            onClick={handleSupportClick}
            className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors"
            aria-label="Suporte"
          >
            <MessageCircle size={24} />
            <span className="text-xs">Suporte</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
