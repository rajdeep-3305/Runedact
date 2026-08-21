import React, { useState } from 'react';
import type { RunCodeResponse } from '../types';
import { runKeyLabel } from '../lib/keys';

interface ExecutionPaneProps {
  result: RunCodeResponse | null;
  isRunning: boolean;
  error: string | null;
}

export const ExecutionPane: React.FC<ExecutionPaneProps> = ({ result, isRunning, error }) => {
  const [selectedTab, setSelectedTab] = useState<number>(0);
  const [seenResult, setSeenResult] = useState<RunCodeResponse | null>(null);

  // adjust state during render: snap to the first failing case on each new run
  if (result !== seenResult && result) {
    setSeenResult(result);
    const firstFail = result.test_results.findIndex((tc) => !tc.passed);
    setSelectedTab(firstFail >= 0 ? firstFail : 0);
  }

  if (isRunning) {
    return (
      <div className="flex h-full items-center justify-center gap-3 bg-zinc-950">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-amber-400/80 border-t-transparent" />
        <span className="font-mono text-xs text-zinc-500">running in sandbox…</span>
      </div>
    );
  }

  if (!result) {
    if (error) {
      return (
        <div className="flex h-full items-center justify-center bg-zinc-950 px-6">
          <div className="rounded-md border border-rose-500/25 bg-rose-500/[0.07] px-3 py-2 font-mono text-[11px] text-rose-300">
            {error}
          </div>
        </div>
      );
    }
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 bg-zinc-950 text-zinc-600">
        <span className="font-mono text-[11px]">$ waiting for a run</span>
        <span className="text-xs text-zinc-700">
          press <span className="kbd">{runKeyLabel}</span> or hit run
        </span>
      </div>
    );
  }

  const summary = result.passed_count === result.total_count
    ? `ok · ${result.passed_count}/${result.total_count}`
    : result.passed_count === 0
      ? `failed · 0/${result.total_count}`
      : `partial · ${result.passed_count}/${result.total_count}`;
  const summaryTone = result.passed_count === result.total_count
    ? 'text-emerald-400'
    : 'text-amber-400';

  const statusText: Record<string, string> = {
    accepted: 'accepted',
    wrong_answer: 'wrong answer',
    time_limit_exceeded: 'time limit exceeded',
    memory_limit_exceeded: 'memory limit exceeded',
    runtime_error: 'runtime error',
    compilation_error: 'syntax error',
    error: 'sandbox error'
  };

  const activeTest = result.test_results[selectedTab];

  return (
    <div className="flex h-full flex-col overflow-hidden border-t border-zinc-800/80 bg-zinc-950 text-xs">
      {/* test tab strip */}
      <div className="flex h-9 shrink-0 items-center gap-1 border-b border-zinc-800/80 px-3">
        <span className="mr-2 font-mono text-[10px] uppercase tracking-widest text-zinc-600">
          tests
        </span>
        {result.test_results.map((tc, idx) => (
          <button
            key={idx}
            onClick={() => setSelectedTab(idx)}
            className={`flex items-center gap-1.5 rounded px-2 py-1 font-mono text-[11px] transition cursor-pointer ${
              selectedTab === idx
                ? 'bg-zinc-800 text-zinc-100'
                : 'text-zinc-500 hover:bg-zinc-900 hover:text-zinc-300'
            }`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${tc.passed ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            case {idx + 1}
            {tc.hidden && <span className="text-[9px] text-zinc-600">hidden</span>}
          </button>
        ))}
      </div>

      {/* body */}
      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {error && (
          <div className="mb-3 rounded-md border border-rose-500/25 bg-rose-500/[0.07] px-3 py-2 font-mono text-[11px] text-rose-300">
            {error}
          </div>
        )}
        {result.status !== 'accepted' && result.status !== 'wrong_answer' && (
          <div className="mb-3 rounded-md border border-rose-500/25 bg-rose-500/[0.07] px-3 py-2 font-mono text-[11px] text-rose-300">
            {statusText[result.status] ?? result.status}
          </div>
        )}

        {activeTest && (
          <div className="space-y-2">
            {activeTest.error ? (
              <pre className="rounded-md border border-rose-500/20 bg-rose-500/[0.06] p-3 font-mono text-[11px] leading-relaxed text-rose-300/90">
                {activeTest.error}
              </pre>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-md border border-zinc-800/80 bg-zinc-900/40 p-2.5">
                  <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-zinc-600">
                    yours
                  </div>
                  <div className={`font-mono text-[11px] ${activeTest.passed ? 'text-emerald-400/90' : 'text-rose-300'}`}>
                    {JSON.stringify(activeTest.got)}
                  </div>
                </div>
                <div className="rounded-md border border-zinc-800/80 bg-zinc-900/40 p-2.5">
                  <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-zinc-600">
                    expected
                  </div>
                  <div className="font-mono text-[11px] text-zinc-300">
                    {JSON.stringify(activeTest.expected)}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {result.stderr && (
          <div className="mt-3">
            <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-zinc-600">
              stderr
            </div>
            <pre className="rounded-md border border-zinc-800/80 bg-black/50 p-3 font-mono text-[11px] leading-relaxed text-rose-300/80">
              {result.stderr}
            </pre>
          </div>
        )}

        {result.stdout && (
          <div className="mt-3">
            <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-zinc-600">
              stdout
            </div>
            <pre className="rounded-md border border-zinc-800/80 bg-black/50 p-3 font-mono text-[11px] leading-relaxed text-zinc-400">
              {result.stdout}
            </pre>
          </div>
        )}
      </div>

      {/* status bar */}
      <div className="flex h-7 shrink-0 items-center justify-between border-t border-zinc-800/80 bg-zinc-900/50 px-3 font-mono text-[10px]">
        <span className={summaryTone}>● {summary}</span>
        <div className="flex items-center gap-3 text-zinc-500">
          <span>{result.execution_time_ms} ms</span>
          <span>exit {result.exit_code}</span>
        </div>
      </div>
    </div>
  );
};
