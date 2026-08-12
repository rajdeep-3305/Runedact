import React, { useState } from 'react';
import type { MentorMessage } from '../types';

interface AIMentorPaneProps {
  messages: MentorMessage[];
  onRequestHint: (hintLevel: number, userQuery: string) => void;
  isLoading: boolean;
}

const HINT_LEVELS = [
  { level: 1, label: 'concept' },
  { level: 2, label: 'approach' },
  { level: 3, label: 'targeted' }
];

const SUGGESTIONS = ['why does a hidden case fail?', 'how do i make this faster?', "i'm stuck, where do i start?"];

export const AIMentorPane: React.FC<AIMentorPaneProps> = ({ messages, onRequestHint, isLoading }) => {
  const [activeHintLevel, setActiveHintLevel] = useState<number>(1);
  const [userQuery, setUserQuery] = useState<string>('');

  const send = (query: string) => {
    onRequestHint(activeHintLevel, query);
    setUserQuery('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(userQuery);
  };

  return (
    <div className="flex h-full flex-col overflow-hidden bg-zinc-950">
      {/* header */}
      <div className="border-b border-zinc-800/80 p-3">
        <div className="mb-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="grid h-5 w-5 place-items-center rounded border border-amber-400/30 bg-amber-400/10 font-mono text-[11px] text-amber-300">
              ᚱ
            </span>
            <span className="text-xs font-semibold text-zinc-200">mentor</span>
          </div>
          <span className="font-mono text-[10px] text-zinc-600">
            {messages.length === 0 ? 'no messages' : `${messages.length} messages`}
          </span>
        </div>

        {/* hint levels */}
        <div className="grid grid-cols-3 gap-1 rounded-md border border-zinc-800 bg-zinc-900/50 p-1">
          {HINT_LEVELS.map((h) => (
            <button
              key={h.level}
              type="button"
              onClick={() => setActiveHintLevel(h.level)}
              className={`flex items-center justify-center gap-1.5 rounded py-1 font-mono text-[10px] transition cursor-pointer ${
                activeHintLevel === h.level
                  ? 'bg-amber-400/15 text-amber-300'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <span className={activeHintLevel === h.level ? 'text-amber-400' : 'text-zinc-600'}>
                {h.level}
              </span>
              {h.label}
            </button>
          ))}
        </div>
      </div>

      {/* messages */}
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-3.5 text-xs">
        {messages.length === 0 && !isLoading ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <span className="font-mono text-2xl text-zinc-800">ᚱ</span>
            <p className="max-w-[220px] text-[11px] leading-relaxed text-zinc-600">
              hints, not answers. pick a level and ask — or send an empty message for a nudge.
            </p>
            <div className="flex flex-col gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-md border border-zinc-800 px-2.5 py-1 font-mono text-[10px] text-zinc-400 transition hover:border-zinc-700 hover:text-zinc-200 cursor-pointer"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => {
            const isUser = m.role === 'user';
            return isUser ? (
              <div key={m.id} className="flex justify-end">
                <div className="max-w-[85%] rounded-lg rounded-br-sm border border-amber-400/25 bg-amber-400/10 px-3 py-2 text-[12px] leading-relaxed text-amber-100/90">
                  {m.content}
                </div>
              </div>
            ) : (
              <div key={m.id} className="border-l-2 border-zinc-800 pl-3">
                <p className="whitespace-pre-wrap text-[12px] leading-relaxed text-zinc-300">
                  {m.content}
                </p>
                <div className="mt-1.5 flex items-center gap-2 font-mono text-[9px] text-zinc-600">
                  <span>level {m.hintLevel}</span>
                  {m.wasBlocked && <span className="text-amber-500">· guarded</span>}
                  {m.latencyMs !== undefined && <span>· {m.latencyMs}ms</span>}
                  {m.provider && <span className="text-zinc-700">· {m.provider}</span>}
                </div>
              </div>
            );
          })
        )}

        {isLoading && (
          <div className="flex items-center gap-1.5 font-mono text-[10px] text-zinc-500">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-amber-400/80 [animation-delay:0ms]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-amber-400/80 [animation-delay:120ms]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-amber-400/80 [animation-delay:240ms]" />
            reading your code…
          </div>
        )}
      </div>

      {/* input */}
      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-zinc-800/80 p-2.5">
        <input
          type="text"
          value={userQuery}
          onChange={(e) => setUserQuery(e.target.value)}
          placeholder="ask, or send empty for a nudge…"
          className="min-w-0 flex-1 rounded-md border border-zinc-800 bg-zinc-900/60 px-3 py-2 text-xs text-zinc-200 outline-none transition placeholder:text-zinc-600 focus:border-amber-400/40"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="grid h-[34px] w-[34px] shrink-0 place-items-center rounded-md bg-amber-400 text-zinc-950 transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer"
          title="Send"
        >
          <svg className="h-3.5 w-3.5" viewBox="0 0 14 14" fill="none">
            <path d="M2 7h9M7.5 3.5L11 7l-3.5 3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </form>
    </div>
  );
};
