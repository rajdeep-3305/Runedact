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
    if (!selectedProblemId) return;
    setIsRunning(true);
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
        const data: RunCodeResponse = await res.json();
        setExecutionResult(data);
      }
    } catch (err) {
      console.error('Failed to run code:', err);
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
        const data: ASTAnalysisResponse = await res.json();
        setAstData(data);
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
        const assistantMsg: MentorMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: data.content,
          hintLevel: data.hint_level,
          wasBlocked: data.leaked_solution,
          latencyMs: data.latency_ms,
          provider: data.provider,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (err) {
      console.error('Failed to get hint:', err);
    } finally {
      setIsMentorLoading(false);
    }
  };

  const handleResetCode = () => {
    if (currentProblem) {
      setCode(currentProblem.starter_code['python'] || '');
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-950 overflow-hidden font-sans">
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

      <main className="flex-1 flex overflow-hidden">
        <div className="w-1/4 h-full min-w-[320px]">
          <ProblemPane problem={currentProblem} loading={loadingProblem} />
        </div>

        <div className="flex-1 h-full flex flex-col border-r border-slate-800 min-w-[400px]">
          <div className="h-[62%] w-full">
            <CodeEditorPane code={code} onChange={setCode} onReset={handleResetCode} />
          </div>
          <div className="h-[38%] w-full">
            <ExecutionPane result={executionResult} isRunning={isRunning} />
          </div>
        </div>

        <div className="w-[30%] h-full min-w-[340px]">
          <AIMentorPane
            messages={messages}
            onRequestHint={handleRequestHint}
            isLoading={isMentorLoading}
          />
        </div>
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
