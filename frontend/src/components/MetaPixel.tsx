import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

declare global {
  interface Window {
    fbq?: (...args: any[]) => void;
    _fbq?: (...args: any[]) => void;
  }
}

export function MetaPixel() {
  const location = useLocation();
  const [pixelLoaded, setPixelLoaded] = useState(false);

  useEffect(() => {
    const loadPixel = async () => {
      try {
        // Buscar configuração do pixel do backend
        const res = await fetch(`${API_URL}/api/public/tracking-config?platform=meta`);
        if (!res.ok) return;
        
        const config = await res.json();
        if (!config.is_active || !config.pixel_id) {
          console.log('[Meta Pixel] Pixel não configurado ou inativo');
          return;
        }

        const pixelId = config.pixel_id;
        console.log('[Meta Pixel] Carregando pixel:', pixelId);

        // Injetar script do Meta Pixel apenas uma vez
        if (!document.getElementById('facebook-pixel')) {
          const script = document.createElement('script');
          script.id = 'facebook-pixel';
          script.innerHTML = `
            !function(f,b,e,v,n,t,s)
            {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
            n.queue=[];t=b.createElement(e);t.async=!0;
            t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}(window, document,'script',
            'https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', '${pixelId}');
          `;
          document.head.appendChild(script);
          
          // Aguardar o pixel carregar
          const checkPixel = setInterval(() => {
            if (window.fbq) {
              clearInterval(checkPixel);
              setPixelLoaded(true);
              window.fbq('track', 'PageView');
            }
          }, 100);
          
          // Timeout após 5 segundos
          setTimeout(() => {
            clearInterval(checkPixel);
            if (window.fbq) {
              setPixelLoaded(true);
            }
          }, 5000);
        } else if (window.fbq) {
          setPixelLoaded(true);
        }
      } catch (err) {
        console.error('[Meta Pixel] Erro ao carregar pixel:', err);
      }
    };

    loadPixel();
  }, []);

  // Disparar PageView quando a rota mudar
  useEffect(() => {
    if (pixelLoaded && window.fbq) {
      window.fbq('track', 'PageView');
      console.log('[Meta Pixel] PageView disparado para:', location.pathname);
    }
  }, [location.pathname, pixelLoaded]);

  return null;
}

// Função helper para disparar eventos do pixel
export function trackMetaEvent(eventName: string, params?: Record<string, any>) {
  if (typeof window !== 'undefined' && window.fbq) {
    window.fbq('track', eventName, params);
    console.log(`[Meta Pixel] Evento disparado: ${eventName}`, params);
  } else {
    console.warn(`[Meta Pixel] Pixel não carregado. Evento não disparado: ${eventName}`);
  }
}
