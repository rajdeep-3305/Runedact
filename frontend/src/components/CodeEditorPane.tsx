import React from 'react';
import Editor from '@monaco-editor/react';
import { RotateCcw, ScanSearch } from 'lucide-react';
import type { ASTAnalysisResponse } from '../types';

interface CodeEditorPaneProps {
  code: string;
  onChange: (value: string) => void;
  onReset: () => void;
  insights: ASTAnalysisResponse | null;
  onOpenInsights: () => void;
}

export const CodeEditorPane: React.FC<CodeEditorPaneProps> = ({
  code,
  onChange,
  onReset,
  insights,
  onOpenInsights
}) => {
  return (
    <div className="flex h-full flex-col bg-[#141417]">
      {/* tab strip */}
      <div className="flex h-8 shrink-0 items-center border-b border-zinc-800/80 bg-zinc-900/60 pr-2">
        <div className="flex items-center gap-1.5 self-stretch border-r border-zinc-800/80 bg-[#141417] pl-3 pr-3">
          <span className="h-2 w-2 rounded-full bg-amber-400/70" />
          <span className="font-mono text-[11px] text-zinc-300">solution.py</span>
          <span className="h-1.5 w-1.5 rounded-full bg-zinc-600" title="unsaved changes" />
        </div>

        <div className="ml-auto flex items-center gap-3 font-mono text-[10px] text-zinc-600">
          {insights?.syntax_valid && (
            <button
              onClick={onOpenInsights}
              title="AST insights"
              className="flex items-center gap-1.5 rounded px-1.5 py-0.5 transition hover:bg-zinc-800 hover:text-amber-300 cursor-pointer"
            >
              <ScanSearch className="h-3 w-3" />
              {insights.estimated_complexity}
              <span className="text-zinc-700">·</span>
              depth {insights.max_loop_depth}
              {insights.anti_patterns.length > 0 && (
                <span className="text-amber-500/80">· {insights.anti_patterns.length} smell{insights.anti_patterns.length > 1 ? 's' : ''}</span>
              )}
            </button>
          )}
          <span>python 3.11 · utf-8 · spaces: 4</span>
          <button
            onClick={onReset}
            className="flex items-center gap-1 rounded px-1.5 py-0.5 text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-300 cursor-pointer"
            title="Reset to starter code"
          >
            <RotateCcw className="h-3 w-3" />
            reset
          </button>
        </div>
      </div>

      {/* editor body */}
      <div className="min-h-0 flex-1">
        <Editor
          height="100%"
          language="python"
          theme="vs-dark"
          value={code}
          onChange={(val) => onChange(val || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 13.5,
            lineHeight: 21,
            fontFamily:
              "'JetBrains Mono', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace",
            fontLigatures: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            cursorBlinking: 'phase',
            cursorSmoothCaretAnimation: 'on',
            smoothScrolling: true,
            padding: { top: 14, bottom: 14 },
            renderLineHighlight: 'none',
            overviewRulerLanes: 0,
            hideCursorInOverviewRuler: true,
            scrollbar: { verticalScrollbarSize: 8, horizontalScrollbarSize: 8 },
            quickSuggestions: false,
            suggestOnTriggerCharacters: false
          }}
        />
      </div>
    </div>
  );
};
