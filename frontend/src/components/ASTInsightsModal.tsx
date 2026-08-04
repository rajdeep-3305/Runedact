import React from 'react';
import type { ASTAnalysisResponse } from '../types';
import { AlertTriangle, CheckCircle2, Cpu, X } from 'lucide-react';

interface ASTInsightsModalProps {
  isOpen: boolean;
  onClose: () => void;
  astData: ASTAnalysisResponse | null;
}

export const ASTInsightsModal: React.FC<ASTInsightsModalProps> = ({ isOpen, onClose, astData }) => {
  if (!isOpen || !astData) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-xl w-full shadow-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold text-white tracking-tight">Code Analysis</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4 text-xs">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-800/70 p-3 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Estimated Time</span>
              <span className="text-sm font-bold text-cyan-300 font-mono mt-0.5 block">
                {astData.estimated_complexity}
              </span>
            </div>

            <div className="bg-slate-800/70 p-3 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Max Loop Depth</span>
              <span className="text-sm font-bold text-amber-300 font-mono mt-0.5 block">
                {astData.max_loop_depth} {astData.max_loop_depth >= 2 ? '(Nested)' : ''}
              </span>
            </div>

            <div className="bg-slate-800/70 p-3 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Complexity</span>
              <span className="text-sm font-bold text-indigo-300 font-mono mt-0.5 block">
                {astData.cyclomatic_complexity}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between p-2.5 rounded-lg border border-slate-800 bg-slate-900">
              <span className="text-slate-300 font-medium">Recursive Calls Detected:</span>
              <span className={`font-semibold font-mono ${astData.has_recursion ? 'text-amber-400' : 'text-slate-400'}`}>
                {astData.has_recursion ? 'Yes' : 'No'}
              </span>
            </div>

            <div className="p-2.5 rounded-lg border border-slate-800 bg-slate-900">
              <span className="text-slate-300 font-medium block mb-1.5">Data Structures In Use:</span>
              <div className="flex flex-wrap gap-1.5">
                {astData.data_structures.length > 0 ? (
                  astData.data_structures.map((ds, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 font-mono text-[11px]">
                      {ds}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500 italic">None detected</span>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-1.5">
            <span className="text-slate-300 font-medium block">Issues Found:</span>
            {astData.anti_patterns.length > 0 ? (
              <div className="space-y-1.5">
                {astData.anti_patterns.map((issue, i) => (
                  <div key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-200">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{issue}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>No major issues found.</span>
              </div>
            )}
          </div>
        </div>

        <div className="px-5 py-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
