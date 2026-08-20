import React, { useState, useEffect } from 'react';
import type { ProblemSummary, ProblemDetail, RunCodeResponse, ASTAnalysisResponse, MentorMessage } from './types';
import { Navbar } from './components/Navbar';
import { ProblemPane } from './components/ProblemPane';
import { CodeEditorPane } from './components/CodeEditorPane';
import { ExecutionPane } from './components/ExecutionPane';
import { AIMentorPane } from './components/AIMentorPane';
import { ASTInsightsModal } from './components/ASTInsightsModal';
import { EvalDashboardModal } from './components/EvalDashboardModal';

export const App: React.FC = () => {
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [selectedProblemId, setSelectedProblemId] = useState<string>('two-sum');
  const [currentProblem, setCurrentProblem] = useState<ProblemDetail | null>(null);
  const [code, setCode] = useState<string>('');
  const [loadingProblem, setLoadingProblem] = useState<boolean>(true);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [executionResult, setExecutionResult] = useState<RunCodeResponse | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [hintError, setHintError] = useState<string | null>(null);
  const [astData, setAstData] = useState<ASTAnalysisResponse | null>(null);
  const [isAnalyzingAST, setIsAnalyzingAST] = useState<boolean>(false);
  const [isASTModalOpen, setIsASTModalOpen] = useState<boolean>(false);

  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [isMentorLoading, setIsMentorLoading] = useState<boolean>(false);
  const [isEvalModalOpen, setIsEvalModalOpen] = useState<boolean>(false);

  useEffect(() => {
    const fetchProblems = async () => {
      try {
        const res = await fetch('/api/v1/problems');
        if (res.ok) {
          const data: ProblemSummary[] = await res.json();
          setProblems(data);
          if (data.length > 0) {
            setSelectedProblemId((current) => current || data[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to fetch problems:', err);
      }
    };
    fetchProblems();
  }, []);

  useEffect(() => {
    if (!selectedProblemId) return;

    const fetchDetail = async () => {
      setLoadingProblem(true);
      try {
        const res = await fetch(`/api/v1/problems/${selectedProblemId}`);
        if (res.ok) {
          const data: ProblemDetail = await res.json();
          setCurrentProblem(data);
          setCode(data.starter_code['python'] || '');
          setExecutionResult(null);
          setRunError(null);
          setHintError(null);
          setAstData(null);
          setMessages([]);
        }
      } catch (err) {
        console.error('Failed to fetch problem detail:', err);
      } finally {
        setLoadingProblem(false);
      }
    };
    fetchDetail();
  }, [selectedProblemId]);

  const handleRunCode = async () => {
    if (!selectedProblemId || isRunning) return;
    setIsRunning(true);
    setRunError(null);
    try {
      const res = await fetch('/api/v1/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: selectedProblemId,
          code: code
        })
      });
      if (res.ok) {
        setExecutionResult(await res.json());
        // refresh the insights quietly so the complexity chip stays current
        fetch('/api/v1/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code })
        })
          .then((r) => (r.ok ? r.json() : null))
          .then(setAstData)
          .catch(() => {});
      } else if (res.status === 422) {
        setRunError('code is too large to run (64KB limit)');
      } else {
        setRunError(`run failed (${res.status})`);
      }
    } catch {
      setRunError('could not reach the server — is the backend running?');
    } finally {
      setIsRunning(false);
    }
  };

  const handleTriggerAST = async () => {
    setIsAnalyzingAST(true);
    try {
      const res = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      if (res.ok) {
        setAstData(await res.json());
        setIsASTModalOpen(true);
      }
    } catch (err) {
      console.error('Failed to analyze AST:', err);
    } finally {
      setIsAnalyzingAST(false);
    }
  };

  const handleRequestHint = async (hintLevel: number, userQuery: string) => {
    if (!selectedProblemId) return;

    if (userQuery) {
      const userMsg: MentorMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: userQuery,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, userMsg]);
    }

    setIsMentorLoading(true);
    setHintError(null);
    try {
      const res = await fetch('/api/v1/mentor/hint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: selectedProblemId,
          code: code,
          hint_level: hintLevel,
          user_query: userQuery
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: data.content,
            hintLevel: data.hint_level,
            wasBlocked: data.leaked_solution,
            latencyMs: data.latency_ms,
            provider: data.provider,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);
      } else if (res.status === 422) {
        setHintError('your code is too large to send (64KB limit)');
      } else {
        setHintError(`hint request failed (${res.status})`);
      }
    } catch {
      setHintError('could not reach the server — is the backend running?');
    } finally {
      setIsMentorLoading(false);
    }
  };

  const handleResetCode = () => {
    if (currentProblem) {
      setCode(currentProblem.starter_code['python'] || '');
    }
  };

  // run shortcut anywhere, even with focus inside Monaco
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        handleRunCode();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-zinc-950 font-sans text-zinc-200">
      <Navbar
        problems={problems}
        selectedProblemId={selectedProblemId}
        onSelectProblem={setSelectedProblemId}
        onRunCode={handleRunCode}
        isRunning={isRunning}
        onOpenEvals={() => setIsEvalModalOpen(true)}
        onTriggerAST={handleTriggerAST}
        isAnalyzing={isAnalyzingAST}
      />

      <main className="flex min-h-0 flex-1">
        <aside className="h-full w-[300px] shrink-0 overflow-hidden border-r border-zinc-800/80">
          <ProblemPane problem={currentProblem} loading={loadingProblem} />
        </aside>

        <section className="flex min-w-0 flex-1 flex-col">
          <div className="min-h-0 flex-[62]">
            <CodeEditorPane
              code={code}
              onChange={setCode}
              onReset={handleResetCode}
              insights={astData}
              onOpenInsights={() => setIsASTModalOpen(true)}
            />
          </div>
          <div className="min-h-0 flex-[38]">
            <ExecutionPane result={executionResult} isRunning={isRunning} error={runError} />
          </div>
        </section>

        <aside className="h-full w-[320px] shrink-0 overflow-hidden border-l border-zinc-800/80">
          <AIMentorPane
            messages={messages}
            onRequestHint={handleRequestHint}
            isLoading={isMentorLoading}
            error={hintError}
          />
        </aside>
      </main>

      <ASTInsightsModal
        isOpen={isASTModalOpen}
        onClose={() => setIsASTModalOpen(false)}
        astData={astData}
      />
      <EvalDashboardModal
        isOpen={isEvalModalOpen}
        onClose={() => setIsEvalModalOpen(false)}
      />
    </div>
  );
};

export default App;
