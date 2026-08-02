import React, { useState } from 'react';
import type { RunCodeResponse } from '../types';
import { AlertTriangle, CheckCircle2, Clock, Cpu, Terminal, XCircle } from 'lucide-react';

interface ExecutionPaneProps {
  result: RunCodeResponse | null;
  isRunning: boolean;
}

export const ExecutionPane: React.FC<ExecutionPaneProps> = ({ result, isRunning }) => {
  const [selectedTab, setSelectedTab] = useState<number>(0);

  if (isRunning) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-slate-900/60 p-6 text-slate-400 text-xs gap-3">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="font-mono">Running...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-slate-900/40 p-6 text-slate-500 text-xs gap-2">
        <Terminal className="w-5 h-5 opacity-40" />
        <p>Run your code to see sandbox output and test results.</p>
      </div>
    );
  }

  const statusConfig = {
    accepted: { text: 'Accepted', color: 'text-emerald-400', icon: CheckCircle2 },
    wrong_answer: { text: 'Wrong Answer', color: 'text-rose-400', icon: XCircle },
    time_limit_exceeded: { text: 'Time Limit Exceeded', color: 'text-amber-400', icon: Clock },
    memory_limit_exceeded: { text: 'Memory Limit Exceeded', color: 'text-purple-400', icon: AlertTriangle },
    runtime_error: { text: 'Runtime Error', color: 'text-rose-400', icon: AlertTriangle },
    compilation_error: { text: 'Syntax Error', color: 'text-rose-400', icon: AlertTriangle },
    error: { text: 'Execution Error', color: 'text-rose-400', icon: AlertTriangle }
  }[result.status] || { text: result.status, color: 'text-slate-300', icon: Terminal };

  const StatusIcon = statusConfig.icon;
  const activeTest = result.test_results[selectedTab];

  return (
    <div className="h-full flex flex-col bg-slate-900 border-t border-slate-800 overflow-hidden text-xs">
      <div className="h-10 px-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <StatusIcon className={`w-4 h-4 ${statusConfig.color}`} />
          <span className={`font-bold ${statusConfig.color}`}>{statusConfig.text}</span>
          <span className="text-slate-500 text-[11px] font-mono">
            ({result.passed_count}/{result.total_count} tests passed)
          </span>
        </div>

        <div className="flex items-center gap-3 text-slate-400 font-mono text-[11px]">
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-500" />
            <span>{result.execution_time_ms} ms</span>
          </div>
          <Cpu className="w-3 h-3 text-slate-500" />
        </div>
      </div>

      <div className="flex-1 p-3 overflow-y-auto space-y-3 font-mono">
        {result.test_results.length > 0 && (
          <div className="flex items-center gap-1.5 border-b border-slate-800 pb-2">
            {result.test_results.map((tc, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedTab(idx)}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition cursor-pointer flex items-center gap-1.5 ${
                  selectedTab === idx
                    ? 'bg-slate-700 text-white border border-slate-600'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${tc.passed ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                <span>Case {idx + 1}</span>
                {tc.hidden && <span className="text-[9px] text-slate-500">(hidden)</span>}
              </button>
            ))}
          </div>
        )}

        {activeTest && (
          <div className="space-y-2 text-[11px]">
            {activeTest.error ? (
              <div className="p-2.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300">
                <span className="font-semibold">Error: </span>
                {activeTest.error}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 rounded bg-slate-800 border border-slate-700">
                  <div className="text-slate-500 text-[10px] mb-1 uppercase font-semibold">Your Output</div>
                  <div className={activeTest.passed ? 'text-emerald-300' : 'text-rose-300'}>
                    {JSON.stringify(activeTest.got)}
                  </div>
                </div>
                <div className="p-2.5 rounded bg-slate-800 border border-slate-700">
                  <div className="text-slate-500 text-[10px] mb-1 uppercase font-semibold">Expected Output</div>
                  <div className="text-cyan-300">{JSON.stringify(activeTest.expected)}</div>
                </div>
              </div>
            )}
          </div>
        )}

        {result.stderr && (
          <div className="p-2.5 rounded bg-slate-950 border border-rose-500/20 text-rose-300/90 text-[11px] whitespace-pre-wrap">
            <span className="font-semibold text-rose-400">Stderr / Traceback:</span>
            <div className="mt-1">{result.stderr}</div>
          </div>
        )}

        {result.stdout && (
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-slate-300 text-[11px] whitespace-pre-wrap">
            <span className="font-semibold text-slate-400">Stdout:</span>
            <div className="mt-1">{result.stdout}</div>
          </div>
        )}
      </div>
    </div>
  );
};
