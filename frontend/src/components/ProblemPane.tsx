import React from 'react';
import type { ProblemDetail } from '../types';

interface ProblemPaneProps {
  problem: ProblemDetail | null;
  loading: boolean;
}

export const ProblemPane: React.FC<ProblemPaneProps> = ({ problem, loading }) => {
  if (loading || !problem) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-900/50 p-6 text-slate-500 text-xs animate-pulse">
        Loading problem description...
      </div>
    );
  }

  const difficultyColor = {
    Easy: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    Medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    Hard: 'text-rose-400 bg-rose-500/10 border-rose-500/20'
  }[problem.difficulty] || 'text-slate-400';

  return (
    <div className="h-full flex flex-col bg-slate-900 border-r border-slate-800 overflow-y-auto">
      <div className="p-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${difficultyColor}`}>
            {problem.difficulty}
          </span>
          {problem.tags.map((t) => (
            <span key={t} className="text-[11px] font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
              {t}
            </span>
          ))}
        </div>
        <h1 className="text-base font-bold text-white tracking-tight">{problem.title}</h1>
      </div>

      <div className="p-4 space-y-4 text-xs text-slate-300 leading-relaxed">
        <p className="whitespace-pre-line">{problem.description}</p>

        <div className="space-y-2 pt-2">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Examples</h3>
          {problem.visible_test_cases.map((tc, idx) => (
            <div key={idx} className="bg-slate-900 rounded-lg p-3 border border-slate-800 font-mono text-[11px] space-y-1">
              <div>
                <span className="text-slate-500 select-none">Input: </span>
                <span className="text-cyan-300">{JSON.stringify(tc.input)}</span>
              </div>
              <div>
                <span className="text-slate-500 select-none">Expected: </span>
                <span className="text-emerald-300">{JSON.stringify(tc.expected)}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-2">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-2">Constraints</h3>
          <ul className="list-disc list-inside space-y-1 text-slate-400 font-mono text-[11px]">
            {problem.constraints.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
