'use client';

import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function HeroBanner() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [mounted, setMounted] = useState(false);
  
  const banners = [
    {
      title: 'SAQUES ILIMITADOS',
      subtitle: 'QUANTAS VEZES QUISER NO DIA!',
      cta: 'CADASTRE-SE',
      bgGradient: 'from-[#0a0e0f] via-[#0a1a1a] to-[#0a0e0f]'
    }
  ];

  // Valores fixos para evitar problemas de hidratação
  const coinPositions = [
    { top: 10, left: 15, duration: 4, delay: 0 },
    { top: 20, left: 45, duration: 5, delay: 0.5 },
    { top: 30, left: 75, duration: 6, delay: 1 },
    { top: 40, left: 25, duration: 4.5, delay: 0.3 },
    { top: 50, left: 60, duration: 5.5, delay: 0.8 },
    { top: 60, left: 35, duration: 4.2, delay: 0.2 },
    { top: 70, left: 80, duration: 5.8, delay: 1.2 },
    { top: 15, left: 55, duration: 4.8, delay: 0.4 },
    { top: 25, left: 85, duration: 5.2, delay: 0.6 },
    { top: 35, left: 20, duration: 4.3, delay: 0.1 },
    { top: 45, left: 70, duration: 5.6, delay: 0.9 },
    { top: 55, left: 40, duration: 4.7, delay: 0.7 },
    { top: 65, left: 90, duration: 5.3, delay: 1.1 },
    { top: 75, left: 30, duration: 4.6, delay: 0.5 },
    { top: 85, left: 65, duration: 5.4, delay: 1.0 },
  ];

  useEffect(() => {
    setMounted(true);
  }, []);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % banners.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + banners.length) % banners.length);
  };

  return (
    <div className="relative w-full h-[450px] sm:h-[550px] md:h-[650px] overflow-hidden bg-gradient-to-br from-[#0a0e0f] via-[#0d1a1a] to-[#0a0e0f]">
      {/* Overlay gradiente para profundidade */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#0a0e0f]/80 via-transparent to-[#0a0e0f]/40 z-0"></div>
      
      {/* Moedas de fundo decorativas */}
      {mounted && (
        <div className="absolute inset-0 opacity-15 z-0">
          {coinPositions.map((coin, i) => (
            <div
              key={i}
              className="absolute w-12 h-12 md:w-16 md:h-16 rounded-full bg-gradient-to-br from-[#d4af37] to-[#b8941f] opacity-40 blur-md"
              style={{
                top: `${coin.top}%`,
                left: `${coin.left}%`,
                animation: `float ${coin.duration}s infinite ease-in-out`,
                animationDelay: `${coin.delay}s`
              }}
            />
          ))}
        </div>
      )}

      <div className="relative container mx-auto px-4 h-full flex items-center z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 items-center w-full">
          {/* Lado esquerdo - Texto e CTA */}
          <div className="text-center md:text-left z-10">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#d4af37] via-[#ffd700] to-[#d4af37] mb-4 md:mb-5 drop-shadow-2xl animate-gradient">
              {banners[currentSlide].title}
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-white/90 mb-8 md:mb-10 font-medium leading-relaxed">
              {banners[currentSlide].subtitle}
            </p>
            <button className="group relative bg-gradient-to-r from-[#d4af37] to-[#ffd700] text-black px-8 md:px-10 py-4 md:py-5 rounded-xl text-base md:text-lg font-black hover:from-[#ffd700] hover:to-[#d4af37] transition-all duration-300 shadow-2xl shadow-[#d4af37]/30 hover:shadow-[#d4af37]/50 hover:scale-105 transform">
              <span className="relative z-10">{banners[currentSlide].cta}</span>
              <div className="absolute inset-0 bg-gradient-to-r from-[#ffd700] to-[#d4af37] rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </button>
          </div>

          {/* Lado direito - Imagem do celular (placeholder) */}
          <div className="hidden md:flex justify-center items-center z-10">
            <div className="relative w-52 h-80 lg:w-72 lg:h-[420px] group">
              <div className="absolute inset-0 bg-gradient-to-br from-[#d4af37]/20 to-[#ff6b35]/10 rounded-3xl blur-2xl transform rotate-12 group-hover:rotate-6 transition-transform duration-500"></div>
              <div className="relative w-full h-full bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 rounded-3xl shadow-2xl transform rotate-12 group-hover:rotate-6 group-hover:scale-105 transition-all duration-500 border-2 border-gray-700/50">
                <div className="absolute inset-4 bg-gradient-to-br from-black to-gray-900 rounded-2xl flex flex-col items-center justify-center p-6 border border-gray-800">
                  <div className="text-4xl mb-3">📱</div>
                  <div className="text-[#d4af37] text-sm font-bold mb-2">Pix recebido</div>
                  <div className="text-green-400 text-2xl font-black">R$ 1.000,00</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controles do carousel */}
      <button
        onClick={prevSlide}
        className="absolute left-4 md:left-6 top-1/2 -translate-y-1/2 bg-black/60 backdrop-blur-sm hover:bg-black/80 text-white p-3 rounded-full transition-all z-20 hover:scale-110 shadow-lg"
        aria-label="Banner anterior"
      >
        <ChevronLeft size={24} />
      </button>
      <button
        onClick={nextSlide}
        className="absolute right-4 md:right-6 top-1/2 -translate-y-1/2 bg-black/60 backdrop-blur-sm hover:bg-black/80 text-white p-3 rounded-full transition-all z-20 hover:scale-110 shadow-lg"
        aria-label="Próximo banner"
      >
        <ChevronRight size={24} />
      </button>

      {/* Indicadores */}
      <div className="absolute bottom-4 md:bottom-6 left-1/2 -translate-x-1/2 flex gap-3 z-20">
        {banners.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentSlide 
                ? 'bg-[#ff6b35] shadow-lg shadow-[#ff6b35]/50 scale-125' 
                : 'bg-white/30 hover:bg-white/50'
            }`}
            aria-label={`Ir para banner ${index + 1}`}
          />
        ))}
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
      `}</style>
    </div>
  );
}
