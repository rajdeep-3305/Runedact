import React, { useState } from 'react';
import type { MentorMessage } from '../types';
import { Clock, Lightbulb, Send, ShieldCheck, Sparkles } from 'lucide-react';

interface AIMentorPaneProps {
  messages: MentorMessage[];
  onRequestHint: (hintLevel: number, userQuery: string) => void;
  isLoading: boolean;
}

const HINT_LEVELS = [
  { level: 1, label: 'L1: Concept' },
  { level: 2, label: 'L2: Algorithm' },
  { level: 3, label: 'L3: Targeted' }
];

export const AIMentorPane: React.FC<AIMentorPaneProps> = ({ messages, onRequestHint, isLoading }) => {
  const [activeHintLevel, setActiveHintLevel] = useState<number>(1);
  const [userQuery, setUserQuery] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onRequestHint(activeHintLevel, userQuery);
    setUserQuery('');
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 overflow-hidden">
      <div className="p-3.5 border-b border-slate-800">
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-white tracking-tight">AI Mentor</span>
          </div>

          <div className="flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            <ShieldCheck className="w-3 h-3" />
            <span>Guard</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
          {HINT_LEVELS.map((h) => (
            <button
              key={h.level}
              type="button"
              onClick={() => setActiveHintLevel(h.level)}
              className={`py-1 px-1.5 rounded text-[11px] font-semibold transition cursor-pointer ${
                activeHintLevel === h.level
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {h.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 p-3.5 overflow-y-auto space-y-3.5 text-xs">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 text-slate-500 space-y-2">
            <Lightbulb className="w-6 h-6 text-amber-400/60" />
            <p className="text-slate-400 font-medium">No guidance requested yet.</p>
            <p className="text-[11px] text-slate-500 max-w-xs">Stuck? Ask for a hint.</p>
            <button
              onClick={() => onRequestHint(activeHintLevel, 'I am stuck. Where should I begin?')}
              disabled={isLoading}
              className="mt-2 text-xs font-semibold px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition cursor-pointer"
            >
              Ask for a hint
            </button>
          </div>
        ) : (
          messages.map((m) => {
            const isUser = m.role === 'user';
            return (
              <div key={m.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1`}>
                <div
                  className={`max-w-[90%] rounded-xl p-3 text-xs leading-relaxed ${
                    isUser
                      ? 'bg-indigo-600 text-white rounded-tr-none'
                      : 'bg-slate-800/90 text-slate-200 border border-slate-700/70 rounded-tl-none shadow-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>

                {!isUser && (
                  <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono px-1">
                    {m.hintLevel && <span>Level {m.hintLevel}</span>}
                    {m.wasBlocked && <span className="text-amber-400">guarded</span>}
                    {m.latencyMs !== undefined && (
                      <span className="flex items-center gap-0.5">
                        <Clock className="w-2.5 h-2.5" />
                        {m.latencyMs}ms
                      </span>
                    )}
                    {m.provider && <span className="text-slate-600">({m.provider})</span>}
                  </div>
                )}
              </div>
            );
          })
        )}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
            <div className="w-3.5 h-3.5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-800 flex gap-2">
        <input
          type="text"
          value={userQuery}
          onChange={(e) => setUserQuery(e.target.value)}
          placeholder={`Ask the mentor, or leave blank for a level ${activeHintLevel} hint...`}
          className="flex-1 bg-slate-800 text-slate-200 text-xs rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-2 rounded-lg font-medium transition disabled:opacity-50 flex items-center justify-center cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
