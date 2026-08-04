import React, { useCallback, useEffect, useState } from 'react';
import type { EvalReport, EvalRunSummary } from '../types';
import { BarChart2, RefreshCw, X } from 'lucide-react';

interface EvalDashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EvalDashboardModal: React.FC<EvalDashboardModalProps> = ({ isOpen, onClose }) => {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [history, setHistory] = useState<EvalRunSummary[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/evals/history');
      if (res.ok) {
        setHistory(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch eval history:', err);
    }
  }, []);

  const handleRunEvals = async () => {
    setIsRunning(true);
    try {
      const res = await fetch('/api/v1/evals/run', { method: 'POST' });
      if (res.ok) {
        setReport(await res.json());
        fetchHistory();
      }
    } catch (err) {
      console.error('Failed to run eval benchmark:', err);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen, fetchHistory]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <BarChart2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">Evaluation Dashboard</h2>
              <p className="text-[11px] text-slate-400">Run the benchmark to check hint quality.</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRunEvals}
              disabled={isRunning}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
              <span>{isRunning ? 'Running Evals...' : 'Run Benchmark'}</span>
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto space-y-6 text-xs flex-1">
          {report ? (
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/60">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block mb-1">Solution Leak Rate</span>
                <div className="flex items-baseline gap-1">
                  <span className={`text-xl font-bold font-mono ${report.leak_rate_percentage === 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {report.leak_rate_percentage}%
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">(target: 0.0%)</span>
                </div>
              </div>

              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/60">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block mb-1">Hint Quality</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-bold text-indigo-300 font-mono">{report.quality_score}</span>
                  <span className="text-[10px] text-slate-500 font-mono">/ 100</span>
                </div>
              </div>

              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/60">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block mb-1">Relevance</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-bold text-cyan-300 font-mono">{report.answer_relevance_score}</span>
                  <span className="text-[10px] text-slate-500 font-mono">/ 100</span>
                </div>
              </div>

              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/60">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block mb-1">Avg Hint Latency</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-bold text-amber-300 font-mono">{report.avg_latency_ms}</span>
                  <span className="text-[10px] text-slate-500 font-mono">ms</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-slate-500">
              No results yet. Run the benchmark to see hint quality metrics.
            </div>
          )}

          {report && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                Sample Breakdown ({report.results.length} cases)
              </h3>
              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left font-mono text-[11px]">
                  <thead className="bg-slate-800 text-slate-400 border-b border-slate-800 text-[10px] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Case</th>
                      <th className="py-2.5 px-3">Problem</th>
                      <th className="py-2.5 px-3">Bug Injected</th>
                      <th className="py-2.5 px-3">Leak Guard</th>
                      <th className="py-2.5 px-3">Quality</th>
                      <th className="py-2.5 px-3">Latency</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {report.results.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-800/40 transition">
                        <td className="py-2 px-3 text-indigo-300 font-semibold">{r.id}</td>
                        <td className="py-2 px-3 text-slate-300">{r.problem_id}</td>
                        <td className="py-2 px-3 text-slate-400 max-w-xs truncate">{r.expected_flaw}</td>
                        <td className="py-2 px-3">
                          {r.leaked_solution ? (
                            <span className="text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20 text-[10px]">
                              LEAKED
                            </span>
                          ) : (
                            <span className="text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20 text-[10px]">
                              PASSED
                            </span>
                          )}
                        </td>
                        <td className="py-2 px-3 text-cyan-300 font-bold">{r.quality_score}</td>
                        <td className="py-2 px-3 text-slate-400">{r.latency_ms}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {history.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Past Runs</h3>
              <div className="space-y-1.5">
                {history.slice(0, 5).map((h) => (
                  <div key={h.id} className="flex items-center justify-between p-2 rounded-lg border border-slate-800 bg-slate-800/40 text-[11px] font-mono">
                    <span className="text-slate-300 font-semibold">
                      Run #{h.id} - {h.benchmark_name}
                    </span>
                    <div className="flex items-center gap-4 text-slate-400">
                      <span>Leak: <strong className="text-emerald-400">{h.leak_rate_percentage}%</strong></span>
                      <span>Quality: <strong className="text-indigo-300">{h.quality_score}</strong></span>
                      <span>Latency: <strong className="text-amber-300">{h.avg_latency_ms}ms</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
