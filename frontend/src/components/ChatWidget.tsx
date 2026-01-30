import { useState, useEffect } from 'react';
import { MessageCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface SupportConfig {
  whatsapp_link?: string;
  welcome_message?: string;
}

export default function ChatWidget() {
  const [supportConfig, setSupportConfig] = useState<SupportConfig | null>(null);

  useEffect(() => {
    const fetchSupport = async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/support-config`);
        if (res.ok) {
          const data = await res.json();
          setSupportConfig({
            whatsapp_link: data.whatsapp_link || '',
            welcome_message: data.welcome_message
          });
        }
      } catch {
        setSupportConfig(null);
      }
    };
    fetchSupport();
  }, []);

  const handleClick = () => {
    if (supportConfig?.whatsapp_link) {
      window.open(supportConfig.whatsapp_link, '_blank', 'noopener,noreferrer');
    }
    // Se não houver link configurado no painel admin, nada acontece (configure em Admin > Suporte)
  };

  return (
    <div className="fixed bottom-16 md:bottom-20 right-2 md:right-4 z-40">
      <button
        type="button"
        onClick={handleClick}
        className="bg-green-500 text-white px-3 py-2.5 md:px-4 md:py-3 rounded-lg shadow-lg hover:bg-green-600 transition-colors flex items-center gap-2"
        aria-label="Abrir chat"
      >
        <MessageCircle size={18} className="md:w-5 md:h-5" />
        <span className="text-xs md:text-sm font-medium hidden lg:block">
          Bem Vindo a Lux Bet, em que posso ajudar?
        </span>
        <span className="text-xs md:text-sm font-medium lg:hidden">Chat</span>
      </button>
    </div>
  );
}
