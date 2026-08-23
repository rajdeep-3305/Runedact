import React from 'react';
import type { ASTAnalysisResponse } from '../types';
import { Modal } from './Modal';

interface ASTInsightsModalProps {
  isOpen: boolean;
  onClose: () => void;
  astData: ASTAnalysisResponse | null;
}

export const ASTInsightsModal: React.FC<ASTInsightsModalProps> = ({ isOpen, onClose, astData }) => {
  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="static insights"
      subtitle="ast walk of the current editor contents"
      maxWidth="max-w-lg"
    >
      {!astData ? (
        <div className="p-6 text-center font-mono text-xs text-zinc-600">
          no analysis yet — press insights in the top bar
        </div>
      ) : (
        <div className="space-y-5 p-4 text-[13px]">
          {/* metric strip */}
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
              <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                time
              </div>
              <div className="mt-1 truncate font-mono text-sm font-semibold text-amber-300" title={astData.estimated_complexity}>
                {astData.estimated_complexity}
              </div>
            </div>
            <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
              <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                loop depth
              </div>
              <div className="mt-1 font-mono text-sm font-semibold text-zinc-200">
                {astData.max_loop_depth}
                {astData.max_loop_depth >= 2 && <span className="ml-1 text-[11px] text-rose-400">nested</span>}
              </div>
            </div>
            <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-3">
              <div className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                cyclomatic
              </div>
              <div className="mt-1 font-mono text-sm font-semibold text-zinc-200">
                {astData.cyclomatic_complexity}
              </div>
            </div>
          </div>

          {/* recursion + data structures */}
          <div className="space-y-2">
            <div className="flex items-center justify-between rounded-md border border-zinc-800/80 bg-zinc-900/30 px-3 py-2">
              <span className="text-zinc-400">recursive calls</span>
              <span className={`font-mono text-xs ${astData.has_recursion ? 'text-amber-300' : 'text-zinc-500'}`}>
                {astData.has_recursion ? 'detected' : 'none'}
              </span>
            </div>
            <div className="rounded-md border border-zinc-800/80 bg-zinc-900/30 px-3 py-2.5">
              <div className="mb-2 text-[13px] text-zinc-400">data structures in use</div>
              <div className="flex flex-wrap gap-1.5">
                {astData.data_structures.length > 0 ? (
                  astData.data_structures.map((ds, i) => (
                    <span
                      key={i}
                      className="rounded border border-zinc-700/80 bg-zinc-800/60 px-1.5 py-0.5 font-mono text-[11px] text-zinc-300"
                    >
                      {ds}
                    </span>
                  ))
                ) : (
                  <span className="font-mono text-[11px] text-zinc-600">none detected</span>
                )}
              </div>
            </div>
          </div>

          {/* issues */}
          <div>
            <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-zinc-600">
              {astData.anti_patterns.length > 0 ? `${astData.anti_patterns.length} issues` : 'issues'}
            </div>
            {astData.anti_patterns.length > 0 ? (
              <ul className="space-y-1.5">
                {astData.anti_patterns.map((issue, i) => (
                  <li
                    key={i}
                    className="rounded-md border border-amber-400/20 bg-amber-400/[0.06] px-3 py-2 text-xs leading-relaxed text-amber-200/90"
                  >
                    {issue}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="rounded-md border border-emerald-400/20 bg-emerald-400/[0.06] px-3 py-2 text-xs text-emerald-300/90">
                nothing flagged — clean walk
              </div>
            )}
          </div>

          {/* syntax footer */}
          {!astData.syntax_valid && (
            <div className="rounded-md border border-rose-500/25 bg-rose-500/[0.07] px-3 py-2 font-mono text-xs text-rose-300">
              syntax error · {astData.syntax_error_msg}
            </div>
          )}
        </div>
      )}
    </Modal>
  );
};
