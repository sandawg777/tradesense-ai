"""
Evaluation suite to measure AI quality.
Run with: python -m api.evals
"""
import os
from typing import List
from datetime import datetime


EVAL_DATASET = [
    {
        "question": "What is RSI and how is it used?",
        "expected_keywords": ["overbought", "oversold", "70", "30", "momentum"]
    },
    {
        "question": "Analyze NVDA",
        "expected_keywords": ["NVDA", "price", "market cap", "P/E"]
    },
    {
        "question": "What sectors are hot right now?",
        "expected_keywords": ["sector", "performance", "%"]
    },
    {
        "question": "Explain stage 2 breakout",
        "expected_keywords": ["breakout", "base", "volume", "accumulation"]
    },
    {
        "question": "Find small cap gainers",
        "expected_keywords": ["small cap", "ticker"]
    }
]


def keyword_match_score(answer: str, expected_keywords: List[str]) -> float:
    """Simple eval - how many expected keywords appear in answer."""
    if not answer:
        return 0.0
    answer_lower = answer.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return matches / len(expected_keywords)


def relevance_score(answer: str, question: str) -> float:
    """Check answer length and basic relevance."""
    if not answer or len(answer) < 50:
        return 0.0
    if "error" in answer.lower()[:20]:
        return 0.0
    return min(len(answer) / 500, 1.0)


def run_eval_suite():
    """Run full eval suite and return results."""
    from api.agent import analyze

    results = []
    print("\n" + "=" * 60)
    print("TRADESENSE AI - EVAL SUITE")
    print("=" * 60)

    for i, test in enumerate(EVAL_DATASET, 1):
        print(f"\n[{i}/{len(EVAL_DATASET)}] {test['question']}")
        try:
            answer = analyze(test["question"], session_id=f"eval_{i}")
            keyword_score = keyword_match_score(answer, test["expected_keywords"])
            relevance = relevance_score(answer, test["question"])
            overall = (keyword_score + relevance) / 2

            results.append({
                "question": test["question"],
                "keyword_score": keyword_score,
                "relevance_score": relevance,
                "overall_score": overall,
                "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer
            })

            status = "PASS" if overall >= 0.6 else "FAIL"
            print(f"  Keywords: {keyword_score:.2f} | Relevance: {relevance:.2f} | Overall: {overall:.2f} [{status}]")
        except Exception as e:
            results.append({
                "question": test["question"],
                "error": str(e),
                "overall_score": 0.0
            })
            print(f"  ERROR: {e}")

    avg_score = sum(r["overall_score"] for r in results) / len(results)
    pass_count = sum(1 for r in results if r["overall_score"] >= 0.6)

    print("\n" + "=" * 60)
    print(f"RESULTS: {pass_count}/{len(results)} passed | Avg score: {avg_score:.2f}")
    print("=" * 60 + "\n")

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": len(results),
        "passed": pass_count,
        "average_score": avg_score,
        "results": results
    }


if __name__ == "__main__":
    run_eval_suite()
