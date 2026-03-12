import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { STRATEGIES } from '../data/strategies';
import { api } from '../api/backtest';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { GitCompare, Loader2, X } from 'lucide-react';

export default function Compare() {
  const [selected, setSelected] = useState([]);
  const universe = 'NIFTY';
  const [start, setStart] = useState('2022-01-01');
  const [end, setEnd] = useState('2024-01-01');
  const [initialCapital, setInitialCapital] = useState(100000);
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);

  const toggleStrategy = (id) => {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : prev.length < 5 ? [...prev, id] : prev
    );
  };

  const runComparison = async () => {
    if (!selected.length) return;
    setLoading(true);
    setResults({});
    try {
      const runs = await Promise.all(
        selected.map(id => api.runBacktest({ strategyId: id, universe, start, end, initialCapital }).then(r => ({ id, data: r })))
      );
      const map = {};
      runs.forEach(({ id, data }) => { map[id] = data; });
      setResults(map);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Merge chart data by date
  const mergedData = (() => {
    if (!Object.keys(results).length) return [];
    const allDates = [...new Set(Object.values(results).flatMap(r => r.chart_data.map(d => d.date)))].sort();
    return allDates.map(date => {
      const row = { date };
      Object.entries(results).forEach(([id, r]) => {
        const point = r.chart_data.find(d => d.date === date);
        if (point) {
          row[id] = point.strategy;
          row['benchmark'] = point.benchmark;
        }
      });
      return row;
    });
  })();

  const inputClass = "bg-[#0d0d15] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-white/30 transition-colors";

  return (
    <div className="min-h-screen" style={{ background: '#08080f' }}>
      <div className="max-w-7xl mx-auto px-6 pt-28 pb-20">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <GitCompare size={24} className="text-indigo-400" />
            <h1 className="text-3xl font-bold text-white">Strategy Comparison</h1>
          </div>
          <p className="text-gray-400 mb-10">Select up to 5 strategies to compare their equity curves head-to-head.</p>

          {/* Strategy Selector */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-8">
            {STRATEGIES.map(s => {
              const isSelected = selected.includes(s.id);
              return (
                <button
                  key={s.id}
                  onClick={() => toggleStrategy(s.id)}
                  className="relative p-4 rounded-xl border text-left transition-all duration-200"
                  style={{
                    borderColor: isSelected ? `${s.color}60` : 'rgba(255,255,255,0.08)',
                    background: isSelected ? `${s.color}12` : '#111118',
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="w-3 h-3 rounded-full" style={{ background: s.color }} />
                    {isSelected && <X size={12} className="text-gray-400" />}
                  </div>
                  <p className="text-xs font-semibold text-white leading-tight">{s.name}</p>
                  <p className="text-[10px] text-gray-500 mt-0.5">{s.type}</p>
                </button>
              );
            })}
          </div>

          {/* Controls */}
          <div className="flex flex-wrap gap-4 items-end mb-8">
            <div>
              <label className="block text-xs text-gray-500 mb-1.5 uppercase tracking-wider">Start</label>
              <input type="date" value={start} onChange={e => setStart(e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1.5 uppercase tracking-wider">End</label>
              <input type="date" value={end} onChange={e => setEnd(e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1.5 uppercase tracking-wider">Capital (₹)</label>
              <input type="number" value={initialCapital} onChange={e => setInitialCapital(Number(e.target.value))} className={inputClass} min="1000" step="1000" />
            </div>
            <motion.button
              whileTap={{ scale: 0.97 }}
              disabled={!selected.length || loading}
              onClick={runComparison}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 disabled:opacity-40 transition-all"
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 0 20px rgba(99,102,241,0.4)' }}
            >
              {loading ? <><Loader2 size={14} className="animate-spin" /> Running...</> : <><GitCompare size={14} /> Compare</>}
            </motion.button>
          </div>

          {/* Comparison Chart */}
          <AnimatePresence>
            {mergedData.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl border border-white/8 bg-[#111118] p-6 mb-8"
              >
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-6">Equity Curves</h3>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mergedData} margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 11 }} tickLine={false} axisLine={false}
                        tickFormatter={v => v.slice(0, 7)} interval="preserveStartEnd" />
                      <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} tickLine={false} axisLine={false}
                        tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} width={55} />
                      <Tooltip
                        contentStyle={{ background: '#1a1a24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontFamily: 'Inter', fontSize: 12 }}
                        formatter={(v) => [`₹${Number(v).toLocaleString('en-IN')}`, '']}
                      />
                      <Legend wrapperStyle={{ fontSize: 12, fontFamily: 'Inter', paddingTop: 16 }} />
                      <Line dataKey="benchmark" name="Benchmark" stroke="#4b5563" strokeWidth={1.5} strokeDasharray="5 3" dot={false} />
                      {selected.map(id => {
                        const s = STRATEGIES.find(x => x.id === id);
                        return <Line key={id} dataKey={id} name={s?.name} stroke={s?.color} strokeWidth={2} dot={false} />;
                      })}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Metrics Table */}
          {Object.keys(results).length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="rounded-2xl border border-white/8 bg-[#111118] overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/8">
                    <th className="text-left px-6 py-4 text-gray-400 font-medium">Strategy</th>
                    <th className="text-right px-4 py-4 text-gray-400 font-medium">Total Return</th>
                    <th className="text-right px-4 py-4 text-gray-400 font-medium">Annual Return</th>
                    <th className="text-right px-4 py-4 text-gray-400 font-medium">Sharpe</th>
                    <th className="text-right px-6 py-4 text-gray-400 font-medium">Max Drawdown</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.map(id => {
                    const s = STRATEGIES.find(x => x.id === id);
                    const m = results[id]?.metrics;
                    if (!m) return null;
                    return (
                      <tr key={id} className="border-b border-white/5 hover:bg-white/2 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-2.5 h-2.5 rounded-full" style={{ background: s?.color }} />
                            <span className="font-medium text-white">{s?.name}</span>
                          </div>
                        </td>
                        <td className={`px-4 py-4 text-right font-semibold ${m.total_return > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {(m.total_return * 100).toFixed(2)}%
                        </td>
                        <td className={`px-4 py-4 text-right ${m.annualized_return > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {(m.annualized_return * 100).toFixed(2)}%
                        </td>
                        <td className={`px-4 py-4 text-right ${m.sharpe_ratio > 1 ? 'text-emerald-400' : m.sharpe_ratio > 0 ? 'text-amber-400' : 'text-red-400'}`}>
                          {m.sharpe_ratio.toFixed(3)}
                        </td>
                        <td className="px-6 py-4 text-right text-red-400">
                          {(m.max_drawdown * 100).toFixed(2)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
