import { Link, useLocation } from 'react-router-dom';
import { TrendingUp, BarChart3, GitCompare } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 backdrop-blur-xl"
         style={{ background: 'rgba(8,8,15,0.85)' }}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <TrendingUp size={16} className="text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            Trade<span className="text-indigo-400">Lab</span>
          </span>
        </Link>

        {/* Nav Links */}
        <div className="flex items-center gap-1">
          <Link to="/"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive('/') ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}>
            Strategies
          </Link>
          <Link to="/compare"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
              isActive('/compare') ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}>
            <GitCompare size={14} /> Compare
          </Link>
        </div>
      </div>
    </nav>
  );
}
