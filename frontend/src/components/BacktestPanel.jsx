import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Loader2 } from 'lucide-react';



export default function BacktestPanel({ onRun, loading, strategyColor }) {
  const universe = 'NIFTY';
  const [start, setStart] = useState('2022-01-01');
  const [end, setEnd] = useState('2024-01-01');
  const [initialCapital, setInitialCapital] = useState(100000);

  const inputClass = "w-full bg-[#0d0d15] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-white/30 transition-colors";

  return (
    <div className="rounded-2xl border border-white/8 bg-[#111118] p-6">
      <h3 className="text-lg font-semibold text-white mb-5">Configure Backtest</h3>

      {/* Date Range & Capital */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        <div>
          <label className="block text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">Start Date</label>
          <input type="date" value={start} onChange={e => setStart(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className="block text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">End Date</label>
          <input type="date" value={end} onChange={e => setEnd(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className="block text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">Initial Capital (₹)</label>
          <input
            type="number"
            value={initialCapital}
            onChange={e => setInitialCapital(Number(e.target.value))}
            className={inputClass}
            min="1000"
            step="1000"
          />
        </div>
      </div>

      {/* Run Button */}
      <motion.button
        whileTap={{ scale: 0.97 }}
        disabled={loading}
        onClick={() => onRun({ universe, start, end, initialCapital })}
        className="w-full py-4 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-60"
        style={{
          background: `linear-gradient(135deg, ${strategyColor}, ${strategyColor}cc)`,
          boxShadow: loading ? 'none' : `0 0 30px ${strategyColor}50`
        }}
      >
        {loading ? (
          <><Loader2 size={16} className="animate-spin" /> Running Backtest...</>
        ) : (
          <><Play size={16} /> Run Backtest</>
        )}
      </motion.button>
    </div>
  );
}
