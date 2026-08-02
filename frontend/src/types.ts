export interface ProblemSummary {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  tags: string[];
}

export interface TestCase {
  input: Record<string, any>;
  expected: any;
  hidden?: boolean;
}

export interface ProblemDetail {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  tags: string[];
  description: string;
  constraints: string[];
  starter_code: Record<string, string>;
  visible_test_cases: TestCase[];
}

export interface TestCaseResult {
  test_idx: number;
  passed: boolean;
  got?: any;
  expected?: any;
  error?: string;
  hidden: boolean;
}

export type ExecutionStatus =
  | 'accepted'
  | 'wrong_answer'
  | 'time_limit_exceeded'
  | 'memory_limit_exceeded'
  | 'runtime_error'
  | 'compilation_error'
  | 'error';

export interface RunCodeResponse {
  status: ExecutionStatus;
  exit_code: number;
  execution_time_ms: number;
  stdout: string;
  stderr: string;
  test_results: TestCaseResult[];
  passed_count: number;
  total_count: number;
}

export interface ASTAnalysisResponse {
  syntax_valid: boolean;
  syntax_error_msg: string;
  max_loop_depth: number;
  has_recursion: boolean;
  data_structures: string[];
  functions_defined: string[];
  cyclomatic_complexity: number;
  anti_patterns: string[];
  estimated_complexity: string;
}

export interface MentorMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  hintLevel?: number;
  wasBlocked?: boolean;
  latencyMs?: number;
  provider?: string;
  timestamp: string;
}

export interface EvalCaseResult {
  id: string;
  problem_id: string;
  expected_flaw: string;
  hint_generated: string;
  leaked_solution: boolean;
  quality_score: number;
  latency_ms: number;
}

export interface EvalReport {
  benchmark_name: string;
  total_samples: number;
  leak_rate_percentage: number;
  faithfulness_score: number;
  answer_relevance_score: number;
  context_recall_score: number;
  quality_score: number;
  avg_latency_ms: number;
  results: EvalCaseResult[];
}

export interface EvalRunSummary {
  id: number;
  benchmark_name: string;
  total_samples: number;
  leak_rate_percentage: number;
  quality_score: number;
  avg_latency_ms: number;
  created_at: string | null;
}
