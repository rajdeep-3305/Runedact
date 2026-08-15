import React from 'react';
import type { ProblemSummary } from '../types';
import { runKeyLabel } from '../lib/keys';

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
  const selected = problems.find((p) => p.id === selectedProblemId);

  return (
    <header className="h-12 shrink-0 border-b border-zinc-800/80 bg-zinc-950 px-3 flex items-center gap-4 select-none">
      {/* brand */}
      <div className="flex items-center gap-2.5 pr-1">
        <span className="grid h-7 w-7 place-items-center rounded bg-amber-400 font-mono text-base font-bold text-zinc-950">
          ᚱ
        </span>
        <span className="font-sans text-[15px] font-semibold tracking-tight text-zinc-100">
          runedact
        </span>
      </div>

      <div className="h-5 w-px bg-zinc-800" />

      {/* problem picker: title + difficulty left, dropdown affordance right */}
      <div className="relative flex min-w-0 max-w-[340px] flex-1 items-center rounded-md border border-zinc-800 bg-zinc-900/60 hover:border-zinc-700">
        <span className="pointer-events-none absolute left-2.5 font-mono text-[11px] text-zinc-500">
          {selected ? selected.difficulty.toLowerCase() : 'problem'}
        </span>
        <select
          value={selectedProblemId}
          onChange={(e) => onSelectProblem(e.target.value)}
          className="w-full cursor-pointer appearance-none truncate bg-transparent py-1.5 pl-[74px] pr-7 text-xs text-zinc-200 outline-none"
        >
          {problems.map((p) => (
            <option key={p.id} value={p.id} className="bg-zinc-900">
              {p.title}
            </option>
          ))}
        </select>
        <svg
          className="pointer-events-none absolute right-2 h-3 w-3 text-zinc-500"
          viewBox="0 0 12 12"
          fill="none"
        >
          <path d="M2.5 4.5L6 8l3.5-3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
        </svg>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <button
          onClick={onTriggerAST}
          disabled={isAnalyzing}
          className="rounded-md px-2.5 py-1.5 font-mono text-[11px] text-zinc-400 transition hover:bg-zinc-800/70 hover:text-zinc-200 disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
        >
          {isAnalyzing ? 'reading ast…' : 'insights'}
        </button>

        <button
          onClick={onOpenEvals}
          className="rounded-md px-2.5 py-1.5 font-mono text-[11px] text-zinc-400 transition hover:bg-zinc-800/70 hover:text-zinc-200 cursor-pointer"
        >
          benchmarks
        </button>

        <button
          onClick={onRunCode}
          disabled={isRunning}
          className="flex items-center gap-2 rounded-md bg-amber-400 px-3 py-1.5 text-xs font-semibold text-zinc-950 transition hover:bg-amber-300 active:bg-amber-500 disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer"
        >
          {isRunning ? (
            <span className="h-3 w-3 animate-spin rounded-full border-[1.5px] border-zinc-900/30 border-t-zinc-900" />
          ) : (
            <svg className="h-3 w-3" viewBox="0 0 12 12" fill="currentColor">
              <path d="M2.5 1.5v9l8-4.5-8-4.5z" />
            </svg>
          )}
          run
          <span className="kbd border-zinc-900/40 bg-zinc-900/10 text-zinc-900">{runKeyLabel}</span>
        </button>
      </div>
    </header>
  );
};
