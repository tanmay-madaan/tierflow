import ast
import re
from typing import Dict, Any, List, Optional
import math

class BenchmarkEvaluator:
    """
    Deterministic reference-based evaluator for empirical LLM benchmark evaluation.
    Evaluates responses against ground-truth references using domain-specific rubrics.
    Produces scores on a standardized 0.0 - 10.0 scale.
    Guarantees 100% reproducible scoring without random or hardcoded values.
    """

    def evaluate(self, item: Dict[str, Any], response: str) -> Dict[str, Any]:
        """
        Evaluate a single benchmark item response against its reference answer.
        """
        if not response or not response.strip():
            return {
                "correctness": 0.0,
                "relevance": 0.0,
                "completeness": 0.0,
                "reasoning_quality": 0.0,
                "overall_score": 0.0,
                "evaluation_method": "deterministic_reference",
                "details": "Empty response received."
            }

        eval_type = item.get("eval_type", "factual_match")
        metadata = item.get("metadata", {})
        reference = item.get("reference_answer", "")

        if eval_type == "math_numeric":
            return self._evaluate_math(response, reference, metadata)
        elif eval_type == "factual_match":
            return self._evaluate_factual(response, reference, metadata)
        elif eval_type == "reasoning_choice":
            return self._evaluate_reasoning(response, reference, metadata)
        elif eval_type == "code_eval":
            return self._evaluate_code(response, reference, metadata)
        elif eval_type == "summary_overlap":
            return self._evaluate_summary(response, reference, metadata)
        else:
            return self._evaluate_factual(response, reference, metadata)

    def _evaluate_math(self, response: str, reference: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate numeric mathematical reasoning."""
        target_num = metadata.get("numeric_target")
        if target_num is None:
            # Try to extract integer from reference
            nums = re.findall(r"[-+]?\d*\.?\d+", reference.replace(",", ""))
            target_num = float(nums[0]) if nums else 0.0

        # Clean response and search for numbers
        clean_resp = response.replace(",", "")
        found_nums = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", clean_resp)]

        target_float = float(target_num)
        exact_match = any(math.isclose(n, target_float, rel_tol=1e-5, abs_tol=1e-5) for n in found_nums)

        # Check if the final extracted number matches the target
        final_match = len(found_nums) > 0 and math.isclose(found_nums[-1], target_float, rel_tol=1e-5, abs_tol=1e-5)

        if exact_match and (final_match or f"#### {int(target_float) if target_float.is_integer() else target_float}" in clean_resp):
            score = 10.0
            details = f"Exact numeric target {target_num} matched in final solution."
        elif exact_match:
            score = 6.0
            details = f"Numeric target {target_num} appeared in working steps but was not confirmed final answer."
        else:
            score = 2.0 if len(found_nums) > 0 else 0.0
            details = f"Target {target_num} not found. Extracted numbers: {found_nums[:5]}"

        return {
            "correctness": score,
            "relevance": min(10.0, score + 1.0) if score > 0 else 2.0,
            "completeness": score,
            "reasoning_quality": score,
            "overall_score": score,
            "evaluation_method": "deterministic_numeric_extraction",
            "details": details
        }

    def _evaluate_factual(self, response: str, reference: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate factual question answering via alias match and token overlap with word boundaries."""
        resp_lower = response.lower()
        ref_lower = reference.lower()
        aliases = [ref_lower] + [a.lower() for a in metadata.get("aliases", [])]

        # Check exact alias match using word boundaries to prevent substring leakage
        alias_matched = any(bool(re.search(rf"\b{re.escape(alias)}\b", resp_lower)) for alias in aliases)
        if alias_matched:
            return {
                "correctness": 10.0,
                "relevance": 10.0,
                "completeness": 9.5,
                "reasoning_quality": 9.0,
                "overall_score": 10.0,
                "evaluation_method": "deterministic_alias_match",
                "details": f"Target reference '{reference}' or accepted alias identified in response."
            }

        # Compute token overlap F1
        ref_tokens = set(re.findall(r"\w+", ref_lower))
        resp_tokens = set(re.findall(r"\w+", resp_lower))

        if not ref_tokens:
            return {"correctness": 5.0, "relevance": 5.0, "completeness": 5.0, "reasoning_quality": 5.0, "overall_score": 5.0, "evaluation_method": "fallback", "details": ""}

        common = ref_tokens & resp_tokens
        precision = len(common) / len(resp_tokens) if resp_tokens else 0.0
        recall = len(common) / len(ref_tokens)
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        score = round(min(10.0, recall * 8.0 + f1 * 2.0), 2)
        return {
            "correctness": score,
            "relevance": round(min(10.0, recall * 9.0), 2),
            "completeness": round(min(10.0, recall * 10.0), 2),
            "reasoning_quality": round(min(10.0, recall * 8.0), 2),
            "overall_score": score,
            "evaluation_method": "deterministic_token_overlap",
            "details": f"Token overlap recall: {recall:.2f}, F1: {f1:.2f} against reference '{reference}'."
        }

    def _evaluate_reasoning(self, response: str, reference: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate logical and causal deduction."""
        resp_lower = response.lower()
        expected_decision = metadata.get("expected_decision", "").lower()
        required_concept = metadata.get("required_concept", "").lower()

        has_decision = expected_decision in resp_lower if expected_decision else True
        has_concept = required_concept in resp_lower if required_concept else True

        if has_decision and has_concept:
            score = 10.0
            details = f"Correct conclusion '{expected_decision}' and core mechanism '{required_concept}' present."
        elif has_decision:
            score = 7.5
            details = f"Correct decision '{expected_decision}' reached with partial rationale."
        elif has_concept:
            score = 4.0
            details = f"Relevant concept '{required_concept}' discussed but incorrect final conclusion."
        else:
            score = 1.0
            details = "Neither target decision nor core reasoning concept detected."

        return {
            "correctness": score,
            "relevance": min(10.0, score + 1.5) if score > 0 else 2.0,
            "completeness": score,
            "reasoning_quality": score,
            "overall_score": score,
            "evaluation_method": "deterministic_reasoning_rubric",
            "details": details
        }

    def _extract_python_code(self, response: str) -> str:
        """Extract Python code blocks from markdown fences or bare code."""
        code_blocks = re.findall(r"```(?:python)?\s*(.*?)\s*```", response, re.DOTALL)
        if code_blocks:
            return "\n".join(code_blocks)
        # Fallback: lines that look like Python code
        code_lines = [
            line for line in response.splitlines()
            if line.startswith("def ") or line.startswith("    ") or line.startswith("import ") or line.startswith("return ")
        ]
        return "\n".join(code_lines) if code_lines else response

    def _evaluate_code(self, response: str, reference: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate code implementation by checking AST syntax and signature definitions."""
        code_str = self._extract_python_code(response)
        func_name = metadata.get("function_name", "")

        # 1. Parse AST to verify Python syntax
        try:
            tree = ast.parse(code_str)
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False

        if not syntax_valid:
            return {
                "correctness": 0.0,
                "relevance": 3.0,
                "completeness": 2.0,
                "reasoning_quality": 2.0,
                "overall_score": 0.0,
                "evaluation_method": "deterministic_ast_parser",
                "details": "SyntaxError: Output does not contain valid executable Python code."
            }

        # 2. Check if required function name is defined in AST
        defined_functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        has_required_function = func_name in defined_functions if func_name else bool(defined_functions)

        # 3. Check for return statement
        has_return = any(isinstance(node, ast.Return) for node in ast.walk(tree))

        if has_required_function and has_return:
            score = 10.0
            details = f"Valid Python AST syntax; defined target function '{func_name}' with return statement."
        elif has_required_function:
            score = 7.0
            details = f"Valid AST syntax and function '{func_name}' defined, but no explicit return statement."
        elif syntax_valid:
            score = 5.0
            details = f"Valid syntax but target function '{func_name}' was not defined in the code block."
        else:
            score = 1.0
            details = "Invalid implementation."

        return {
            "correctness": score,
            "relevance": score,
            "completeness": score,
            "reasoning_quality": score,
            "overall_score": score,
            "evaluation_method": "deterministic_ast_parser",
            "details": details
        }

    def _evaluate_summary(self, response: str, reference: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate summarization using unigram/bigram overlap and target keyword coverage."""
        resp_lower = response.lower()
        ref_lower = reference.lower()

        keywords = [k.lower() for k in metadata.get("keywords", [])]
        matched_keywords = sum(1 for k in keywords if bool(re.search(rf"\b{re.escape(k)}\b", resp_lower)))
        keyword_recall = matched_keywords / len(keywords) if keywords else 1.0

        # Unigram overlap F1
        resp_words = re.findall(r"\w+", resp_lower)
        ref_words = re.findall(r"\w+", ref_lower)

        resp_set = set(resp_words)
        ref_set = set(ref_words)

        common = resp_set & ref_set
        precision = len(common) / len(resp_set) if resp_set else 0.0
        recall = len(common) / len(ref_set) if ref_set else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Bigram overlap
        ref_bigrams = set(zip(ref_words[:-1], ref_words[1:])) if len(ref_words) > 1 else set()
        resp_bigrams = set(zip(resp_words[:-1], resp_words[1:])) if len(resp_words) > 1 else set()
        common_bi = ref_bigrams & resp_bigrams
        bi_recall = len(common_bi) / len(ref_bigrams) if ref_bigrams else 0.0

        # Score blending
        score = round(min(10.0, (keyword_recall * 0.4 + recall * 0.3 + f1 * 0.2 + bi_recall * 0.1) * 10.0), 2)

        return {
            "correctness": score,
            "relevance": round(min(10.0, keyword_recall * 10.0), 2),
            "completeness": round(min(10.0, recall * 10.0), 2),
            "reasoning_quality": round(min(10.0, (keyword_recall * 0.6 + f1 * 0.4) * 10.0), 2),
            "overall_score": score,
            "evaluation_method": "deterministic_summary_metrics",
            "details": f"Keyword coverage: {matched_keywords}/{len(keywords)}, n-gram recall: {recall:.2f}, F1: {f1:.2f}."
        }
