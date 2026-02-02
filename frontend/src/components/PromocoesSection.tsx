import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Gift, ChevronRight } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Promotion {
  id: number;
  title: string;
  short_description?: string;
  type: string;
  banner_url?: string;
  is_featured: boolean;
  end_date: string;
  button_text: string;
  link_url?: string;
}

export default function PromocoesSection() {
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPromotions = useCallback(async () => {
    try {
      const cacheBust = `&_t=${Date.now()}`;
      let res = await fetch(`${API_URL}/api/public/promotions?featured=true&limit=6${cacheBust}`, {
        cache: 'no-cache',
        headers: { 'Cache-Control': 'no-cache' }
      });
      if (res.ok) {
        const data = await res.json();
        let list = Array.isArray(data) ? data : (data.promotions || []);
        if (list.length === 0) {
          res = await fetch(`${API_URL}/api/public/promotions?limit=6${cacheBust}`, {
            cache: 'no-cache',
            headers: { 'Cache-Control': 'no-cache' }
          });
          if (res.ok) {
            const dataAll = await res.json();
            list = Array.isArray(dataAll) ? dataAll : (dataAll.promotions || []);
          }
        }
        setPromotions(list);
      }
    } catch (err) {
      console.warn('Erro ao buscar promoções:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchPromotions();
  }, []);

  // Refetch quando usuário volta para a aba (ex: atualizou promoção no admin)
  useEffect(() => {
    const onVisibility = () => {
      if (!document.hidden) fetchPromotions();
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, [fetchPromotions]);

  if (loading && promotions.length === 0) {
    return (
      <div className="w-full bg-gradient-to-b from-[#0d1415] to-[#0a0e0f] py-10 md:py-12 px-4">
        <div className="container mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-black text-white flex items-center gap-3">
              <span>PROMOÇÕES</span>
              <Gift className="text-[#d4af37]" size={28} />
            </h2>
          </div>
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-[#d4af37]"></div>
          </div>
        </div>
      </div>
    );
  }

  if (promotions.length === 0) {
    return null;
  }

  return (
    <div className="w-full bg-gradient-to-b from-[#0d1415] to-[#0a0e0f] py-10 md:py-12 px-4">
      <div className="container mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 md:mb-8 gap-4">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-black text-white flex items-center gap-3">
            <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">PROMOÇÕES</span>
            <Gift className="text-[#d4af37]" size={32} />
          </h2>
          <Link
            to="/promocoes"
            className="text-[#d4af37] hover:text-[#ffd700] transition-all font-bold flex items-center gap-2 text-sm md:text-base"
          >
            Ver todas <ChevronRight size={20} />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {promotions.map((promo) => (
            <Link
              key={promo.id}
              to={promo.link_url && !promo.link_url.startsWith('http') ? promo.link_url : '/promocoes'}
              onClick={(e) => {
                if (promo.link_url?.startsWith('http')) {
                  e.preventDefault();
                  window.open(promo.link_url, '_blank');
                }
              }}
              className="group block bg-gray-800/90 rounded-xl overflow-hidden border border-gray-700/50 hover:border-[#d4af37]/60 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-[#d4af37]/10"
            >
              {promo.banner_url ? (
                <div className="aspect-[3/2] bg-gradient-to-br from-[#0a4d3e] to-[#0d5d4b] relative overflow-hidden">
                  <img
                    src={promo.banner_url.startsWith('http') ? promo.banner_url : `${API_URL}${promo.banner_url}`}
                    alt={promo.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                  {promo.is_featured && (
                    <div className="absolute top-2 right-2 bg-[#d4af37] text-black px-2 py-1 rounded-full text-xs font-bold">
                      DESTAQUE
                    </div>
                  )}
                </div>
              ) : (
                <div className="aspect-[3/2] bg-gradient-to-br from-[#0a4d3e] to-[#0d5d4b] flex items-center justify-center relative">
                  <Gift className="text-[#d4af37]/50" size={48} />
                  {promo.is_featured && (
                    <div className="absolute top-2 right-2 bg-[#d4af37] text-black px-2 py-1 rounded-full text-xs font-bold">
                      DESTAQUE
                    </div>
                  )}
                </div>
              )}
              <div className="p-4">
                <h3 className="text-white font-bold text-lg mb-1 group-hover:text-[#d4af37] transition-colors">
                  {promo.title}
                </h3>
                {promo.short_description && (
                  <p className="text-gray-400 text-sm line-clamp-2 mb-3">{promo.short_description}</p>
                )}
                <span className="inline-flex items-center gap-1 text-[#d4af37] font-semibold text-sm">
                  {promo.button_text}
                  <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
