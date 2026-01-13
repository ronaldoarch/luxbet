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
import LoginModal from './components/LoginModal';
import RegisterModal from './components/RegisterModal';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [registerOpen, setRegisterOpen] = useState(false);
  const [filters, setFilters] = useState({ query: '', provider: '' });
  const [providers, setProviders] = useState<string[]>([]);

  const handleFiltersChange = (partial: { query?: string; provider?: string }) => {
    setFilters((prev) => ({ ...prev, ...partial }));
  };

  return (
    <div className="min-h-screen bg-[#0a0e0f] text-white">
      <PromoBanner />
      <Header 
        onMenuClick={() => setSidebarOpen(true)}
        onLoginClick={() => {
          setRegisterOpen(false);
          setLoginOpen(true);
        }}
        onRegisterClick={() => {
          setLoginOpen(false);
          setRegisterOpen(true);
        }}
      />
      <div className="flex">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          filters={filters}
          onFiltersChange={handleFiltersChange}
          providers={providers}
        />
        <div className="flex-1 min-w-0 md:ml-[220px]">
          <main className="pb-20 md:pb-0">
            <HeroBanner />
            <SearchBar />
            <GameCards />
            <NovidadesSection
              filters={filters}
              onProvidersLoaded={(items) => setProviders(items)}
            />
          </main>
          <Footer />
        </div>
      </div>
      <BottomNav />
      <ChatWidget />
      
      {/* Modais */}
      <LoginModal 
        isOpen={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSwitchToRegister={() => {
          setLoginOpen(false);
          setRegisterOpen(true);
        }}
      />
      <RegisterModal 
        isOpen={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onSwitchToLogin={() => {
          setRegisterOpen(false);
          setLoginOpen(true);
        }}
      />
    </div>
  );
}

export default App;
