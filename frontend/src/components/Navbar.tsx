import React from 'react';
import { BarChart2, Cpu, Play } from 'lucide-react';
import type { ProblemSummary } from '../types';

interface NavbarProps {
  problems: ProblemSummary[];
  selectedProblemId: string;
  onSelectProblem: (id: string) => void;
  onRunCode: () => void;
  isRunning: boolean;
  onOpenEvals: () => void;
  onTriggerAST: () => void;
  isAnalyzing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  problems,
  selectedProblemId,
  onSelectProblem,
  onRunCode,
  isRunning,
  onOpenEvals,
  onTriggerAST,
  isAnalyzing
}) => {
  return (
    <header className="h-14 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between select-none">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center font-bold text-white shadow-md shadow-indigo-500/20">
            Σ
          </div>
          <span className="font-semibold text-white tracking-tight text-sm">Runedact</span>
        </div>

        <div className="h-5 w-px bg-slate-800 mx-1" />

        <select
          value={selectedProblemId}
          onChange={(e) => onSelectProblem(e.target.value)}
          className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg px-3 py-1.5 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
        >
          {problems.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title} ({p.difficulty})
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2.5">
        <button
          onClick={onTriggerAST}
          disabled={isAnalyzing}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition disabled:opacity-50 cursor-pointer"
          title="Analyze Code"
        >
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Code'}</span>
        </button>

        <button
          onClick={onOpenEvals}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 rounded-lg border border-amber-500/30 transition cursor-pointer"
        >
          <BarChart2 className="w-3.5 h-3.5 text-amber-400" />
          <span>Benchmarks</span>
        </button>

        <button
          onClick={onRunCode}
          disabled={isRunning}
          className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-sm shadow-emerald-700/30 transition disabled:opacity-50 cursor-pointer"
        >
          <Play className={`w-3.5 h-3.5 fill-current ${isRunning ? 'animate-pulse' : ''}`} />
          <span>{isRunning ? 'Running...' : 'Run Code'}</span>
        </button>
      </div>
    </header>
  );
};
