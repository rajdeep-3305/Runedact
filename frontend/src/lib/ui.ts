export type Difficulty = 'Easy' | 'Medium' | 'Hard';

// Semantic colors shared by every difficulty pill. Deliberately not
// emerald/rose — those are reserved for pass/fail results.
export const DIFFICULTY_STYLES: Record<Difficulty, { text: string; border: string; bg: string; dot: string }> = {
  Easy: {
    text: 'text-lime-300',
    border: 'border-lime-300/30',
    bg: 'bg-lime-300/10',
    dot: 'bg-lime-300'
  },
  Medium: {
    text: 'text-amber-300',
    border: 'border-amber-300/30',
    bg: 'bg-amber-300/10',
    dot: 'bg-amber-300'
  },
  Hard: {
    text: 'text-orange-400',
    border: 'border-orange-400/30',
    bg: 'bg-orange-400/10',
    dot: 'bg-orange-400'
  }
};

// difficulty classes at a given size; `sm` is the compact navbar variant
export function difficultyClasses(d: string, size: 'sm' | 'md' = 'md') {
  const s = DIFFICULTY_STYLES[(d as Difficulty) in DIFFICULTY_STYLES ? (d as Difficulty) : 'Easy'];
  const pad = size === 'sm' ? 'gap-1 px-1.5 py-px' : 'gap-1.5 px-1.5 py-0.5';
  return `${pad} inline-flex items-center rounded border ${s.border} ${s.bg} font-mono ${s.text}`;
}

// Medium and Hard read as "costly to brute force", so tint the run time by it
export function latencyTone(ms: number): string {
  if (ms < 150) return 'text-emerald-400/80';
  if (ms < 600) return 'text-amber-300/80';
  return 'text-orange-400/80';
}
