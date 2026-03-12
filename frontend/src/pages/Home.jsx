import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { STRATEGIES, STRATEGY_TYPES } from '../data/strategies';
import StrategyCard from '../components/StrategyCard';
import FilterPills from '../components/FilterPills';
import { Sparkles } from 'lucide-react';

const TICKER = ['AAPL +2.4%', 'MSFT +1.1%', 'TSLA -0.8%', 'NVDA +3.2%', 'AMZN +0.6%', 'GOOGL +1.8%', 'META +2.1%', 'JPM -0.3%', 'WMT +0.5%', 'KO +0.2%', 'DIS -1.2%', 'V +0.9%'];

export default function Home() {
  const [activeFilter, setActiveFilter] = useState('All');

  const filtered = useMemo(() =>
    activeFilter === 'All' ? STRATEGIES : STRATEGIES.filter(s => s.type === activeFilter),
    [activeFilter]
  );

  return (
    <div className="min-h-screen hero-gradient">
      {/* Ticker tape */}
      <div className="fixed top-16 left-0 right-0 z-40 overflow-hidden border-b border-white/5"
           style={{ background: 'rgba(8,8,15,0.9)', height: '32px' }}>
        <div className="ticker-inner flex items-center h-full gap-8 whitespace-nowrap"
             style={{ width: 'max-content' }}>
          {[...TICKER, ...TICKER].map((t, i) => (
            <span key={i} className={`text-xs font-mono font-medium ${t.includes('-') ? 'text-red-400' : 'text-emerald-400'}`}>
              {t}
            </span>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 pt-36 pb-20">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium mb-6">
            <Sparkles size={14} />
            10 Algorithmic Trading Strategies
          </div>
          <h1 className="text-5xl md:text-6xl font-black text-white mb-4 leading-tight tracking-tight">
            Understand the Markets.<br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Backtest Any Strategy.
            </span>
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Explore professional-grade trading strategies used by hedge funds and quantitative traders.
            Learn how each one works, then run it against real market data.
          </p>
        </motion.div>

        {/* Filter Pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <FilterPills types={STRATEGY_TYPES} active={activeFilter} onChange={setActiveFilter} />
        </motion.div>

        {/* Strategy count */}
        <p className="text-sm text-gray-500 mb-6">
          Showing <span className="text-white font-medium">{filtered.length}</span> strategies
          {activeFilter !== 'All' && ` · ${activeFilter}`}
        </p>

        {/* Strategy Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filtered.map((strategy, i) => (
            <StrategyCard key={strategy.id} strategy={strategy} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
