import React, { useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  maxWidth?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  maxWidth = 'max-w-xl',
  actions,
  children
}) => {
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-[2px]"
      onClick={onClose}
    >
      <div
        className={`flex max-h-[85vh] w-full ${maxWidth} flex-col overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950 shadow-2xl shadow-black/60`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex shrink-0 items-center justify-between border-b border-zinc-800/80 px-4 py-3">
          <div>
            <h2 className="text-sm font-semibold text-zinc-100">{title}</h2>
            {subtitle && <p className="mt-0.5 font-mono text-[10px] text-zinc-500">{subtitle}</p>}
          </div>
          <div className="flex items-center gap-2">
            {actions}
            <button
              onClick={onClose}
              className="grid h-6 w-6 place-items-center rounded text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-200 cursor-pointer"
              title="Close (esc)"
            >
              <svg className="h-3.5 w-3.5" viewBox="0 0 14 14" fill="none">
                <path d="M3.5 3.5l7 7M10.5 3.5l-7 7" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};
