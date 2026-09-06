import ast
import json
from typing import Any, Dict, List, Optional, Set


class ASTAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.functions_defined: List[str] = []
        self.current_function: Optional[str] = None
        self.max_loop_depth = 0
        self.current_loop_depth = 0

        self.has_recursion = False
        self.recursive_functions: Set[str] = set()
        self.recursion_branch_count = 0
        self.is_memoized = False
        self.unmemoized_tree_flag = False

        self.data_structures_used: Set[str] = set()
        self.anti_patterns: List[str] = []
        self.cyclomatic_complexity = 1

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_func = self.current_function
        self.current_function = node.name
        self.functions_defined.append(node.name)

        for dec in node.decorator_list:
            name = dec.func.id if isinstance(dec, ast.Call) else dec.id if isinstance(dec, ast.Name) else getattr(dec, "attr", None)
            if name in ("lru_cache", "cache"):
                self.is_memoized = True

        if any(arg.arg.lower() in ("memo", "cache", "dp") for arg in node.args.args):
            self.is_memoized = True

        # only catches calls to the current function — misses mutual
        # recursion between two functions, but that's niche for now
        recursive_calls = sum(
            1
            for child in ast.walk(node)
            if isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == node.name
        )
        if recursive_calls:
            self.has_recursion = True
            self.recursive_functions.add(node.name)
            self.recursion_branch_count = max(self.recursion_branch_count, recursive_calls)
            if recursive_calls >= 2 and not self.is_memoized:
                self.unmemoized_tree_flag = True
                self.anti_patterns.append(
                    f"Un-memoized recursive execution tree in '{node.name}' "
                    f"({recursive_calls} recursive branches; possible exponential blowup)."
                )

        self.generic_visit(node)
        self.current_function = prev_func

    def _enter_loop(self, node, kind: str):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.cyclomatic_complexity += 1

        if self.current_loop_depth >= 2:
            self.anti_patterns.append(
                f"Nested loop at line {node.lineno} (depth {self.current_loop_depth}; potential O(N²) bottleneck)."
            )

        if self.current_function:
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Name)
                    and child.func.id == self.current_function
                    and not self.is_memoized
                ):
                    self.unmemoized_tree_flag = True
                    self.anti_patterns.append(
                        f"Recursive call inside loop at line {node.lineno} without memoization; "
                        "potential exponential complexity."
                    )

        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                if child.func.attr == "index":
                    self.anti_patterns.append(
                        f"Linear search 'list.index()' inside loop at line {node.lineno} "
                        "(results in accidental O(N²) time complexity)."
                    )

        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_For(self, node: ast.For):
        self._enter_loop(node, "for")

    def visit_While(self, node: ast.While):
        self._enter_loop(node, "while")

    def visit_If(self, node: ast.If):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict):
        self.data_structures_used.add("dict (O(1) hash map)")
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set):
        self.data_structures_used.add("set (O(1) hash set)")
        self.generic_visit(node)

    def visit_List(self, node: ast.List):
        self.data_structures_used.add("list (dynamic array)")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in ("dict", "set"):
                self.data_structures_used.add(f"{node.func.id} (O(1) lookup table)")
            elif node.func.id in ("sorted", "sort"):
                self.data_structures_used.add("sorting (O(N log N))")
        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in ("pop", "append", "extend"):
                self.data_structures_used.add(f"list.{attr} (LIFO stack operation)")
            elif attr in ("get", "keys", "values", "items"):
                self.data_structures_used.add("hash table lookup")
            elif attr == "sort":
                self.data_structures_used.add("in-place sort (O(N log N))")
        self.generic_visit(node)


def analyze_code_ast(code: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "syntax_valid": False,
            "syntax_error_msg": f"Line {e.lineno}: {e.msg}",
            "max_loop_depth": 0,
            "has_recursion": False,
            "recursion_branch_count": 0,
            "is_memoized": False,
            "unmemoized_tree_flag": False,
            "data_structures": [],
            "functions_defined": [],
            "cyclomatic_complexity": 0,
            "anti_patterns": ["Syntax Error in code."],
            "estimated_complexity": "Syntax Error",
            "structured_prompt_block": '{\n  "syntax_valid": false,\n  "error": "Syntax Error"\n}',
        }

    analyzer = ASTAnalyzer()
    analyzer.visit(tree)

    if analyzer.unmemoized_tree_flag:
        estimated = "O(2^N) Exponential (Un-memoized Recursion)"
    elif analyzer.has_recursion and analyzer.is_memoized:
        estimated = "O(N) Memoized Recursion / DP"
    elif analyzer.has_recursion:
        estimated = "O(N) Linear Recursion"
    elif analyzer.max_loop_depth >= 3:
        estimated = "O(N³) Cubic"
    elif analyzer.max_loop_depth == 2:
        estimated = "O(N²) Quadratic"
    elif analyzer.max_loop_depth == 1:
        if "sorting (O(N log N))" in analyzer.data_structures_used or "in-place sort (O(N log N))" in analyzer.data_structures_used:
            estimated = "O(N log N)"
        else:
            estimated = "O(N) Linear"
    else:
        estimated = "O(1) Constant"

    anti_patterns = list(dict.fromkeys(analyzer.anti_patterns))

    return {
        "syntax_valid": True,
        "syntax_error_msg": "",
        "max_loop_depth": analyzer.max_loop_depth,
        "has_recursion": analyzer.has_recursion,
        "recursive_functions": sorted(analyzer.recursive_functions),
        "recursion_branch_count": analyzer.recursion_branch_count,
        "is_memoized": analyzer.is_memoized,
        "unmemoized_tree_flag": analyzer.unmemoized_tree_flag,
        "data_structures": sorted(analyzer.data_structures_used),
        "functions_defined": analyzer.functions_defined,
        "cyclomatic_complexity": analyzer.cyclomatic_complexity,
        "anti_patterns": anti_patterns,
        "estimated_complexity": estimated,
        "structured_prompt_block": json.dumps(
            {
                "ast_metrics": {
                    "estimated_time_complexity": estimated,
                    "max_nested_loop_depth": analyzer.max_loop_depth,
                    "recursion_branches": analyzer.recursion_branch_count,
                    "is_memoized": analyzer.is_memoized,
                    "unmemoized_tree_alert": analyzer.unmemoized_tree_flag,
                    "data_structures_detected": sorted(analyzer.data_structures_used),
                    "detected_anti_patterns": anti_patterns,
                }
            },
            indent=2,
        ),
    }
