'use client';

import Link from 'next/link';
import { Menu, Activity, Wallet, User, MessageCircle } from 'lucide-react';

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-[#0a4d3e] text-white border-t border-[#0d5d4b] z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-around py-3">
          <Link href="/menu" className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors">
            <Menu size={24} />
            <span className="text-xs">Menu</span>
          </Link>
          <Link href="/esportes" className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors">
            <Activity size={24} />
            <span className="text-xs">Esportes</span>
          </Link>
          <Link href="/depositar" className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors">
            <div className="bg-[#ff6b35] p-2 rounded-lg">
              <Wallet size={20} className="text-white" />
            </div>
            <span className="text-xs">Depositar</span>
          </Link>
          <Link href="/conta" className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors">
            <User size={24} />
            <span className="text-xs">Conta</span>
          </Link>
          <Link href="/ao-vivo" className="flex flex-col items-center gap-1 hover:text-[#d4af37] transition-colors">
            <MessageCircle size={24} />
            <span className="text-xs">Ao vivo</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}
