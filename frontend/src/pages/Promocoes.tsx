import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gift, Calendar, Percent, DollarSign, ArrowRight } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Promotion {
  id: number;
  title: string;
  description: string;
  short_description?: string;
  type: string;
  banner_url?: string;
  is_featured: boolean;
  start_date: string;
  end_date: string;
  min_deposit: number;
  bonus_percentage: number;
  max_bonus: number;
  cashback_percentage: number;
  terms_and_conditions?: string;
  link_url?: string;
  button_text: string;
}

export default function Promocoes() {
  const navigate = useNavigate();
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [featuredOnly, setFeaturedOnly] = useState(false);

  useEffect(() => {
    fetchPromotions();
  }, [featuredOnly]);

  const fetchPromotions = async () => {
    setLoading(true);
    try {
      const url = featuredOnly 
        ? `${API_URL}/api/public/promotions?featured=true&limit=50`
        : `${API_URL}/api/public/promotions?limit=50`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setPromotions(data);
      }
    } catch (err) {
      console.error('Erro ao buscar promoções:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      bonus: 'Bônus',
      cashback: 'Cashback',
      free_spins: 'Free Spins',
      tournament: 'Torneio',
      reload: 'Reload',
      other: 'Promoção'
    };
    return labels[type] || 'Promoção';
  };

  const handlePromotionClick = (promo: Promotion) => {
    if (promo.link_url) {
      if (promo.link_url.startsWith('http')) {
        window.open(promo.link_url, '_blank');
      } else {
        navigate(promo.link_url);
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e0f] text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0a4d3e] to-[#0d5d4b] py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="flex items-center gap-4 mb-4">
            <Gift className="text-[#d4af37]" size={48} />
            <div>
              <h1 className="text-4xl md:text-5xl font-black mb-2">Promoções</h1>
              <p className="text-gray-300 text-lg">Aproveite nossas ofertas exclusivas!</p>
            </div>
          </div>
          
          {/* Filtro */}
          <div className="flex gap-4 mt-6">
            <button
              onClick={() => setFeaturedOnly(false)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                !featuredOnly 
                  ? 'bg-[#d4af37] text-black font-semibold' 
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setFeaturedOnly(true)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                featuredOnly 
                  ? 'bg-[#d4af37] text-black font-semibold' 
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              Em Destaque
            </button>
          </div>
        </div>
      </div>

      {/* Lista de Promoções */}
      <div className="container mx-auto max-w-6xl px-4 py-8">
        {loading ? (
          <div className="text-center py-16">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#d4af37]"></div>
            <p className="mt-4 text-gray-400">Carregando promoções...</p>
          </div>
        ) : promotions.length === 0 ? (
          <div className="text-center py-16">
            <Gift className="mx-auto text-gray-600 mb-4" size={64} />
            <h2 className="text-2xl font-bold mb-2">Nenhuma promoção disponível</h2>
            <p className="text-gray-400">Volte em breve para novas ofertas!</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {promotions.map((promo) => (
              <div
                key={promo.id}
                className={`bg-gray-800 rounded-xl overflow-hidden border-2 transition-all hover:scale-105 cursor-pointer ${
                  promo.is_featured 
                    ? 'border-yellow-500 shadow-lg shadow-yellow-500/20' 
                    : 'border-gray-700 hover:border-gray-600'
                }`}
                onClick={() => handlePromotionClick(promo)}
              >
                {/* Banner */}
                {promo.banner_url && (
                  <div className="h-48 bg-gradient-to-br from-[#0a4d3e] to-[#0d5d4b] relative overflow-hidden">
                    <img
                      src={promo.banner_url.startsWith('http') ? promo.banner_url : `${API_URL}${promo.banner_url}`}
                      alt={promo.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                    {promo.is_featured && (
                      <div className="absolute top-2 right-2 bg-yellow-500 text-black px-3 py-1 rounded-full text-xs font-bold">
                        DESTAQUE
                      </div>
                    )}
                  </div>
                )}
                
                {/* Conteúdo */}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-[#d4af37]/20 text-[#d4af37] text-xs font-semibold rounded">
                      {getTypeLabel(promo.type)}
                    </span>
                    {promo.bonus_percentage > 0 && (
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-semibold rounded flex items-center gap-1">
                        <Percent size={12} />
                        {promo.bonus_percentage}%
                      </span>
                    )}
                  </div>
                  
                  <h3 className="text-xl font-bold mb-2">{promo.title}</h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {promo.short_description || promo.description}
                  </p>
                  
                  {/* Informações */}
                  <div className="space-y-2 mb-4 text-sm">
                    {promo.min_deposit > 0 && (
                      <div className="flex items-center gap-2 text-gray-300">
                        <DollarSign size={16} />
                        <span>Depósito mínimo: R$ {promo.min_deposit.toFixed(2)}</span>
                      </div>
                    )}
                    {promo.max_bonus > 0 && (
                      <div className="flex items-center gap-2 text-gray-300">
                        <DollarSign size={16} />
                        <span>Bônus máximo: R$ {promo.max_bonus.toFixed(2)}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-gray-400">
                      <Calendar size={16} />
                      <span>Até {formatDate(promo.end_date)}</span>
                    </div>
                  </div>
                  
                  {/* Botão */}
                  <button className="w-full bg-[#ff6b35] hover:bg-[#ff7b35] text-white font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2">
                    {promo.button_text}
                    <ArrowRight size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
