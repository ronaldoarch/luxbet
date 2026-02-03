import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import App from './App';
import Admin from './pages/Admin';
import AdminLogin from './pages/AdminLogin';
import Profile from './pages/Profile';
import Game from './pages/Game';
import Deposit from './pages/Deposit';
import Withdrawal from './pages/Withdrawal';
import AffiliatePanel from './pages/AffiliatePanel';
import ManagerPanel from './pages/ManagerPanel';
import Promocoes from './pages/Promocoes';
import TransactionHistory from './pages/TransactionHistory';
import BetsHistory from './pages/BetsHistory';
import AdminRoute from './components/AdminRoute';
import AdminLoginRoute from './components/AdminLoginRoute';

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/conta" element={<Profile />} />
        <Route path="/depositar" element={<Deposit />} />
        <Route path="/sacar" element={<Withdrawal />} />
        <Route path="/jogo/:gameCode" element={<Game />} />
        <Route path="/afiliado" element={<AffiliatePanel />} />
        <Route path="/gerente" element={<ManagerPanel />} />
        <Route path="/promocoes" element={<Promocoes />} />
        <Route path="/historico" element={<TransactionHistory />} />
        <Route path="/apostas" element={<BetsHistory />} />
        <Route path="/admin/login" element={
          <AdminLoginRoute>
            <AdminLogin />
          </AdminLoginRoute>
        } />
        <Route path="/admin" element={
          <AdminRoute>
            <Admin />
          </AdminRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
