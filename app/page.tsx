'use client';

import { useState } from 'react';
import PromoBanner from './components/PromoBanner';
import Header from './components/Header';
import HeroBanner from './components/HeroBanner';
import SearchBar from './components/SearchBar';
import GameCards from './components/GameCards';
import NovidadesSection from './components/NovidadesSection';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import BottomNav from './components/BottomNav';
import ChatWidget from './components/ChatWidget';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0a0e0f] text-white">
      <PromoBanner />
      <Header onMenuClick={() => setSidebarOpen(true)} />
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="flex-1 min-w-0 md:ml-[220px]">
          <main className="pb-20 md:pb-8">
            <HeroBanner />
            <SearchBar />
            <GameCards />
            <NovidadesSection />
          </main>
          <Footer />
        </div>
      </div>
      <BottomNav />
      <ChatWidget />
    </div>
  );
}
