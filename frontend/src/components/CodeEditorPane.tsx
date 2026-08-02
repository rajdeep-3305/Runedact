import React from 'react';
import Editor from '@monaco-editor/react';
import { Code2, RotateCcw } from 'lucide-react';

interface CodeEditorPaneProps {
  code: string;
  onChange: (value: string) => void;
  onReset: () => void;
}

export const CodeEditorPane: React.FC<CodeEditorPaneProps> = ({ code, onChange, onReset }) => {
  return (
    <div className="h-full flex flex-col bg-slate-950 border-r border-slate-800">
      <div className="h-9 px-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-300 font-medium">
          <Code2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>solution.py</span>
          <span className="text-[10px] text-slate-500 font-mono">(Python 3)</span>
        </div>

        <button
          onClick={onReset}
          className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 transition cursor-pointer"
          title="Reset to starter code"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      <div className="flex-1 w-full overflow-hidden">
        <Editor
          height="100%"
          language="python"
          theme="vs-dark"
          value={code}
          onChange={(val) => onChange(val || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            padding: { top: 12, bottom: 12 },
            fontFamily: "'Fira Code', 'JetBrains Mono', Menlo, Consolas, monospace",
            fontLigatures: true
          }}
        />
      </div>
    </div>
  );
};
