import React, { useEffect, useMemo, useState } from 'react';
import { ExternalLink, Play, Search } from 'lucide-react';
import type { LeetCodeProblemDetail, LeetCodeProblemSummary } from '../types';
import { Modal } from './Modal';
import { difficultyClasses } from '../lib/ui';

interface LeetCodeBrowserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPractice: (problem: LeetCodeProblemDetail) => void;
}

type View =
  | { kind: 'list' }
  | { kind: 'detail'; problem: LeetCodeProblemDetail };

function DifficultyPill({ difficulty }: { difficulty: string }) {
  return (
    <span className={`min-w-[70px] justify-center ${difficultyClasses(difficulty)}`}>
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          difficulty === 'Easy'
            ? 'bg-lime-300'
            : difficulty === 'Medium'
              ? 'bg-amber-300'
              : 'bg-orange-400'
        }`}
      />
      {difficulty.toLowerCase()}
    </span>
  );
}

export const LeetCodeBrowserModal: React.FC<LeetCodeBrowserModalProps> = ({
  isOpen,
  onClose,
  onPractice
}) => {
  const [problems, setProblems] = useState<LeetCodeProblemSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [query, setQuery] = useState<string>('');
  const [view, setView] = useState<View>({ kind: 'list' });
  const [seenOpen, setSeenOpen] = useState<boolean>(false);

  // reopening the browser starts from the list again
  if (isOpen !== seenOpen) {
    setSeenOpen(isOpen);
    if (isOpen) setView({ kind: 'list' });
  }

  // fetch the catalog each time the browser opens
  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch('/api/v1/leetcode?limit=50');
        if (cancelled) return;
        if (res.ok) {
          setProblems(await res.json());
        } else {
          setLoadError('leetcode is unreachable right now — try again later');
        }
      } catch {
        if (!cancelled) setLoadError('could not reach the server');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isOpen]);

  const filtered = useMemo(
    () =>
      problems.filter((p) =>
        (p.title + ' ' + p.tags.join(' ')).toLowerCase().includes(query.trim().toLowerCase())
      ),
    [problems, query]
  );

  const openDetail = async (slug: string) => {
    setLoadError(null);
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/leetcode/${encodeURIComponent(slug)}`);
      if (res.ok) {
        setView({ kind: 'detail', problem: await res.json() });
      } else {
        setLoadError('problem unavailable — it may be premium or unreachable');
      }
    } catch {
      setLoadError('could not reach the server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="leetcode browser"
      subtitle="read-only statement viewer — practice happens on the built-in catalog"
      maxWidth="max-w-3xl"
    >
      <div className="flex h-[60vh] min-h-0 flex-col text-[13px]">
        {view.kind === 'list' ? (
          <>
            {/* search */}
            <div className="flex items-center gap-2 border-b border-zinc-800/80 px-4 py-2.5">
              <Search className="h-3.5 w-3.5 text-zinc-600" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="filter by title or tag…"
                className="min-w-0 flex-1 bg-transparent font-mono text-xs text-zinc-200 outline-none placeholder:text-zinc-600"
              />
              <span className="font-mono text-[10px] text-zinc-600">
                {filtered.length}/{problems.length}
                {loading && ' · loading…'}
              </span>
            </div>

            {/* body */}
            <div className="min-h-0 flex-1 overflow-y-auto">
              {loadError && (
                <div className="m-4 rounded-md border border-rose-500/25 bg-rose-500/[0.07] px-3 py-2 font-mono text-xs text-rose-300">
                  {loadError}
                </div>
              )}
              {loading && problems.length === 0 && !loadError && (
                <div className="space-y-2 p-4">
                  {[...Array(8)].map((_, i) => (
                    <div
                      key={i}
                      className="h-9 animate-pulse rounded bg-zinc-800/60"
                      style={{ width: `${96 - i * 3}%` }}
                    />
                  ))}
                </div>
              )}
              <ul className="divide-y divide-zinc-800/60">
                {filtered.map((p) => (
                  <li key={p.id}>
                    <button
                      onClick={() => openDetail(p.id)}
                      className="flex w-full items-center gap-3 px-4 py-2.5 text-left transition hover:bg-zinc-900/50 cursor-pointer"
                    >
                      <DifficultyPill difficulty={p.difficulty} />
                      <span className="min-w-0 flex-1 truncate text-zinc-200">{p.title}</span>
                      {p.paid_only && (
                        <span className="font-mono text-[10px] text-amber-400/80">premium</span>
                      )}
                      <span className="hidden max-w-[180px] truncate font-mono text-[10px] text-zinc-600 sm:inline">
                        {p.tags.slice(0, 3).map((t) => `#${t.toLowerCase().replace(/\s+/g, '-')}`).join(' ')}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
              {!loading && !loadError && filtered.length === 0 && (
                <div className="p-8 text-center font-mono text-xs text-zinc-600">no matches</div>
              )}
            </div>
          </>
        ) : (
          <>
            {/* detail header */}
            <div className="flex items-center gap-3 border-b border-zinc-800/80 px-4 py-3">
              <button
                onClick={() => setView({ kind: 'list' })}
                className="rounded px-1.5 py-0.5 font-mono text-[11px] text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-200 cursor-pointer"
              >
                ← back
              </button>
              <DifficultyPill difficulty={view.problem.difficulty} />
              <span className="min-w-0 flex-1 truncate font-semibold text-zinc-100">
                {view.problem.title}
              </span>
              <a
                href={`https://leetcode.com/problems/${view.problem.id}/`}
                target="_blank"
                rel="noreferrer"
                title="solve on leetcode.com"
                className="flex items-center gap-1 rounded px-1.5 py-0.5 font-mono text-[11px] text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-200 cursor-pointer"
              >
                <ExternalLink className="h-3 w-3" />
                leetcode
              </a>
            </div>

            {/* statement */}
            <div className="min-h-0 flex-1 overflow-y-auto p-4">
              {view.problem.description ? (
                <p className="whitespace-pre-line leading-relaxed text-zinc-300">
                  {view.problem.description}
                </p>
              ) : (
                <div className="rounded-md border border-amber-400/25 bg-amber-400/[0.06] px-3 py-2 text-xs text-amber-200/90">
                  this problem is behind leetcode's paywall — open it on leetcode.com to read the
                  full statement.
                </div>
              )}

              {view.problem.hints.length > 0 && (
                <div className="mt-4">
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-zinc-600">
                    official hints
                  </div>
                  <ul className="space-y-1.5">
                    {view.problem.hints.map((h, i) => (
                      <li
                        key={i}
                        className="border-l-2 border-zinc-800 pl-3 text-xs leading-relaxed text-zinc-400"
                      >
                        {h}
                      </li>
                    ))}
                  </ul>
                  <p className="mt-2 font-mono text-[10px] text-zinc-700">
                    hints are spoily — try the problem before reading them.
                  </p>
                </div>
              )}

              {/* practice affordance */}
              {view.problem.practice ? (
                <div className="mt-5 rounded-md border border-amber-400/25 bg-amber-400/[0.06] p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-amber-200/90">practice on runedact</p>
                      <p className="mt-0.5 text-[11px] leading-relaxed text-zinc-500">
                        graded against the {view.problem.practice.test_cases.length} statement
                        example{view.problem.practice.test_cases.length === 1 ? '' : 's'} — leetcode
                        keeps its full test set private.
                      </p>
                    </div>
                    <button
                      onClick={() => onPractice(view.problem)}
                      className="flex shrink-0 items-center gap-1.5 rounded-md bg-amber-400 px-2.5 py-1.5 text-xs font-semibold text-zinc-950 transition hover:bg-amber-300 cursor-pointer"
                    >
                      <Play className="h-3 w-3" />
                      solve here
                    </button>
                  </div>
                </div>
              ) : (
                <div className="mt-5 rounded-md border border-zinc-800 bg-zinc-900/40 px-3 py-2.5 text-[11px] leading-relaxed text-zinc-500">
                  this one can't be imported for practice — its examples aren't plain python
                  values (linked lists, trees, graphs) or it has none to parse. follow the
                  leetcode link above to solve it there.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </Modal>
  );
};
