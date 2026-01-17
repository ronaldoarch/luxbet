'use client';

import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Heart } from 'lucide-react';
import Link from 'next/link';

interface Game {
  id: string;
  title: string;
  provider?: string;
}

export default function NovidadesSection() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [gamesPerPage, setGamesPerPage] = useState(4);
  const [mounted, setMounted] = useState(false);

  const games: Game[] = [
    { id: '1', title: 'Macaco Sortudo', provider: 'pragmatic' },
    { id: '2', title: 'Cachorro Sortudo', provider: 'pragmatic' },
    { id: '3', title: 'Fenix Sortuda', provider: 'pragmatic' },
    { id: '4', title: 'Doom Day Rampage', provider: 'pgsoft' },
    { id: '5', title: 'Touro Sortudo', provider: 'pragmatic' },
    { id: '6', title: 'Tigre Sortudo', provider: 'pragmatic' },
    { id: '7', title: 'Gate of Hades', provider: 'pragmatic' },
    { id: '8', title: 'Incan Wonder', provider: 'pgsoft' },
    { id: '9', title: 'Geisha Revenge', provider: 'pgsoft' },
    { id: '10', title: 'Ratinho Sortudo', provider: 'pragmatic' },
  ];

  useEffect(() => {
    setMounted(true);
    const updateGamesPerPage = () => {
      if (window.innerWidth < 640) {
        setGamesPerPage(2); // Mobile: 2 colunas
      } else if (window.innerWidth < 1024) {
        setGamesPerPage(3); // Tablet: 3 colunas
      } else {
        setGamesPerPage(4); // Desktop: 4 colunas
      }
    };

    updateGamesPerPage();
    window.addEventListener('resize', updateGamesPerPage);
    return () => window.removeEventListener('resize', updateGamesPerPage);
  }, []);

  const maxIndex = Math.max(0, games.length - gamesPerPage);

  const nextSlide = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, maxIndex));
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const displayedGames = games.slice(currentIndex, currentIndex + gamesPerPage);

  return (
    <div className="w-full bg-gradient-to-b from-[#0d1415] to-[#0a0e0f] py-10 md:py-12 px-4">
      <div className="container mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 md:mb-8 gap-4">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-black text-white flex items-center gap-3">
            <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">NOVIDADES</span>
            <span className="text-3xl md:text-4xl animate-pulse">🔥</span>
          </h2>
          <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto justify-between sm:justify-end">
            <div className="flex gap-2">
              <button
                onClick={prevSlide}
                disabled={currentIndex === 0}
                className="p-2.5 bg-gray-800/80 backdrop-blur-sm rounded-xl hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 hover:scale-110 border border-gray-700/50"
                aria-label="Anterior"
              >
                <ChevronLeft size={20} className="text-white" />
              </button>
              <button
                onClick={nextSlide}
                disabled={currentIndex >= maxIndex}
                className="p-2.5 bg-gray-800/80 backdrop-blur-sm rounded-xl hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 hover:scale-110 border border-gray-700/50"
                aria-label="Próximo"
              >
                <ChevronRight size={20} className="text-white" />
              </button>
            </div>
            <Link
              href="/novidades"
              className="text-[#d4af37] hover:text-[#ffd700] transition-all duration-200 font-bold flex items-center gap-2 text-sm md:text-base hover:gap-3"
            >
              Ver todos <span className="text-lg">›</span>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          {displayedGames.map((game) => (
            <Link
              key={game.id}
              href={`/jogo/${game.id}`}
              className="group relative bg-gradient-to-br from-gray-800/90 via-gray-900/90 to-gray-950/90 backdrop-blur-sm rounded-2xl overflow-hidden border border-gray-700/50 hover:border-[#d4af37]/60 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-[#d4af37]/20"
            >
              <div className="aspect-[3/4] bg-gradient-to-br from-gray-700/50 to-gray-800/50 flex items-center justify-center relative overflow-hidden">
                {/* Efeito de brilho no hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#d4af37]/0 to-transparent group-hover:from-[#d4af37]/10 group-hover:to-transparent transition-all duration-300"></div>
                <div className="text-5xl md:text-6xl group-hover:scale-125 group-hover:rotate-12 transition-all duration-300 relative z-10">🎮</div>
                <button
                  className="absolute top-3 right-3 p-2 bg-black/70 backdrop-blur-sm rounded-full hover:bg-red-600/80 transition-all duration-200 opacity-0 group-hover:opacity-100 z-20 hover:scale-110"
                  onClick={(e) => {
                    e.preventDefault();
                    // Adicionar aos favoritos
                  }}
                  aria-label="Adicionar aos favoritos"
                >
                  <Heart size={18} className="text-white" />
                </button>
              </div>
              <div className="p-4 bg-gradient-to-b from-gray-900/90 to-gray-950/90">
                <h3 className="text-white font-bold text-sm md:text-base truncate group-hover:text-[#d4af37] transition-colors duration-300">{game.title}</h3>
                {game.provider && (
                  <p className="text-gray-400 text-xs mt-1.5 font-medium uppercase tracking-wide">{game.provider}</p>
                )}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
