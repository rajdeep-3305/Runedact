import React, { useEffect, useState } from 'react';
import type { EvalReport, EvalRunSummary } from '../types';
import { Modal } from './Modal';

interface EvalDashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EvalDashboardModal: React.FC<EvalDashboardModalProps> = ({ isOpen, onClose }) => {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [history, setHistory] = useState<EvalRunSummary[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/v1/evals/history');
      if (res.ok) setHistory(await res.json());
    } catch (err) {
      console.error('Failed to fetch eval history:', err);
    }
  };

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

  // refresh past runs whenever the dashboard opens
  useEffect(() => {
    if (!isOpen) return;
    (async () => {
      try {
        const res = await fetch('/api/v1/evals/history');
        if (res.ok) setHistory(await res.json());
      } catch (err) {
        console.error('Failed to fetch eval history:', err);
      }
    })();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="hint benchmark"
      subtitle="runs the mentor over every dataset case and scores the output locally"
      maxWidth="max-w-3xl"
      actions={
        <button
          onClick={handleRunEvals}
          disabled={isRunning}
          className="flex items-center gap-1.5 rounded-md bg-amber-400 px-2.5 py-1 text-xs font-semibold text-zinc-950 transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer"
        >
          {isRunning && (
            <span className="h-2.5 w-2.5 animate-spin rounded-full border-[1.5px] border-zinc-900/30 border-t-zinc-900" />
          )}
          {isRunning ? 'running…' : 'run benchmark'}
        </button>
      }
    >
      <div className="space-y-5 p-4 text-[13px]">
        {!report ? (
          <div className="py-8 text-center">
            <p className="font-mono text-xs text-zinc-500">no results yet</p>
            <p className="mt-1 text-xs text-zinc-600">
              run the benchmark to see leak rate and hint quality.
            </p>
          </div>
        ) : (
          <>
            {/* headline + tiles */}
            <div className="grid grid-cols-4 gap-2">
              <div className="col-span-1 rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
                <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                  leak rate
                </div>
                <div
                  className={`mt-1 font-mono text-xl font-bold ${
                    report.leak_rate_percentage === 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {report.leak_rate_percentage}%
                </div>
                <div className="font-mono text-[10px] text-zinc-600">target 0.0%</div>
              </div>
              <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
                <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                  quality
                </div>
                <div className="mt-1 font-mono text-xl font-bold text-zinc-100">
                  {report.quality_score}
                </div>
                <div className="font-mono text-[10px] text-zinc-600">/100</div>
              </div>
              <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
                <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                  concepts
                </div>
                <div className="mt-1 font-mono text-xl font-bold text-zinc-100">
                  {report.concept_coverage_pct}
                </div>
                <div className="font-mono text-[10px] text-zinc-600">/100</div>
              </div>
              <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
                <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                  latency
                </div>
                <div className="mt-1 font-mono text-xl font-bold text-zinc-100">
                  {report.avg_latency_ms}
                </div>
                <div className="font-mono text-[10px] text-zinc-600">ms avg</div>
              </div>
            </div>

            {/* results table */}
            <div>
              <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                {report.results.length} cases
              </div>
              <div className="overflow-hidden rounded-md border border-zinc-800">
                <table className="w-full text-left font-mono text-xs">
                  <thead className="border-b border-zinc-800 bg-zinc-900/60 text-[10px] uppercase tracking-widest text-zinc-500">
                    <tr>
                      <th className="px-3 py-2">case</th>
                      <th className="px-3 py-2">problem</th>
                      <th className="px-3 py-2">bug</th>
                      <th className="px-3 py-2">guard</th>
                      <th className="px-3 py-2 text-right">quality</th>
                      <th className="px-3 py-2 text-right">latency</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {report.results.map((r) => (
                      <tr key={r.id} className="transition hover:bg-zinc-900/40">
                        <td className="px-3 py-2 text-amber-300/90">{r.id}</td>
                        <td className="px-3 py-2 text-zinc-300">{r.problem_id}</td>
                        <td className="max-w-[220px] truncate px-3 py-2 text-zinc-500" title={r.expected_flaw}>
                          {r.expected_flaw}
                        </td>
                        <td className="px-3 py-2">
                          {r.leaked_solution ? (
                            <span className="text-rose-400">leaked</span>
                          ) : (
                            <span className="text-emerald-400/80">clean</span>
                          )}
                        </td>
                        <td className="px-3 py-2 text-right text-zinc-300">{r.quality_score}</td>
                        <td className="px-3 py-2 text-right text-zinc-500">{r.latency_ms}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* past runs */}
            {history.length > 0 && (
              <div>
                <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                  past runs
                </div>
                <div className="space-y-1">
                  {history.slice(0, 5).map((h) => (
                    <div
                      key={h.id}
                      className="flex items-center justify-between rounded border border-zinc-800/70 bg-zinc-900/30 px-3 py-1.5 font-mono text-[11px]"
                    >
                      <span className="text-zinc-400">
                        #{h.id} · {h.benchmark_name} · n={h.total_samples}
                      </span>
                      <div className="flex items-center gap-3">
                        <span className={h.leak_rate_percentage === 0 ? 'text-emerald-400/80' : 'text-rose-400'}>
                          leak {h.leak_rate_percentage}%
                        </span>
                        <span className="text-zinc-500">q {h.quality_score}</span>
                        <span className="text-zinc-600">{h.avg_latency_ms}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Modal>
  );
};
