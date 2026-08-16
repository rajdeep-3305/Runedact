import React from 'react';
import type { ProblemDetail } from '../types';

interface ProblemPaneProps {
  problem: ProblemDetail | null;
  loading: boolean;
}

export const ProblemPane: React.FC<ProblemPaneProps> = ({ problem, loading }) => {
  if (loading || !problem) {
    return (
      <div className="space-y-3 p-5">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="h-3 animate-pulse rounded bg-zinc-800/70"
            style={{ width: `${85 - i * 9}%` }}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-zinc-950">
      <div className="border-b border-zinc-800/70 p-5">
        <h1 className="font-sans text-lg font-semibold tracking-tight text-zinc-100">
          {problem.title}
        </h1>
        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <span className="rounded border border-amber-400/25 bg-amber-400/10 px-1.5 py-0.5 font-mono text-[10px] text-amber-300">
            {problem.difficulty.toLowerCase()}
          </span>
          {problem.tags.map((t) => (
            <span key={t} className="font-mono text-[10px] text-zinc-500">
              #{t.toLowerCase().replace(/\s+/g, '-')}
            </span>
          ))}
        </div>
      </div>

      <div className="space-y-6 p-5 text-[13px] leading-relaxed text-zinc-300">
        {/* statement */}
        <div className="border-l-2 border-zinc-800 pl-4">
          <p className="whitespace-pre-line">{problem.description}</p>
        </div>

        {/* examples */}
        <section>
          <h3 className="mb-2.5 font-mono text-[10px] uppercase tracking-widest text-zinc-500">
            examples
          </h3>
          <ol className="space-y-2.5">
            {problem.visible_test_cases.map((tc, idx) => (
              <li
                key={idx}
                className="rounded-md border border-zinc-800/80 bg-zinc-900/40 p-3 font-mono text-[11px]"
              >
                <div className="text-zinc-500">
                  <span className="text-zinc-600">in </span>
                  <span className="text-zinc-300">{JSON.stringify(tc.input)}</span>
                </div>
                <div>
                  <span className="text-zinc-600">out </span>
                  <span className="text-emerald-400/90">{JSON.stringify(tc.expected)}</span>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {/* constraints */}
        <section>
          <h3 className="mb-2.5 font-mono text-[10px] uppercase tracking-widest text-zinc-500">
            constraints
          </h3>
          <ul className="space-y-1 font-mono text-[11px] text-zinc-400">
            {problem.constraints.map((c, i) => (
              <li key={i}>
                <span className="text-zinc-600">{i + 1}. </span>
                {c.replace(/\^/g, '^')}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
};
