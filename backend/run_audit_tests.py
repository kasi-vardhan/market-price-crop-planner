"""
Quality Audit Test Runner
Executes all formal test suites and prints detailed results:
- test_suite_comprehensive.py
- app/evaluation suite (5 test files)
- test_api_endpoints.py
- test_recommendation.py
- test_crop_suitability.py
"""

import sys
import unittest
import io
import time

def run_test_module(module_name):
    print(f"\n=======================================================")
    print(f"RUNNING TEST MODULE: {module_name}")
    print(f"=======================================================")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(module_name)
    runner = unittest.TextTestRunner(verbosity=2)
    start = time.time()
    result = runner.run(suite)
    elapsed = time.time() - start
    return {
        "module": module_name,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "elapsed_seconds": round(elapsed, 3),
        "success": result.wasSuccessful(),
    }

if __name__ == "__main__":
    modules = [
        "test_suite_comprehensive",
        "app.evaluation.test_financial_integrity",
        "app.evaluation.test_financial_edge_cases",
        "app.evaluation.test_profit_tool_production",
        "app.evaluation.test_profit_tool_integration",
        "app.evaluation.test_consistency_checks",
        "test_api_endpoints",
    ]
    
    summary = []
    for mod in modules:
        try:
            res = run_test_module(mod)
            summary.append(res)
        except Exception as e:
            print(f"Error loading {mod}: {e}")
            summary.append({
                "module": mod,
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "skipped": 0,
                "elapsed_seconds": 0,
                "success": False,
                "error_msg": str(e)
            })

    print("\n" + "="*70)
    print("AUDIT EXECUTION SUMMARY")
    print("="*70)
    total_run = sum(s["tests_run"] for s in summary)
    total_failures = sum(s["failures"] for s in summary)
    total_errors = sum(s["errors"] for s in summary)
    total_skipped = sum(s["skipped"] for s in summary)
    
    for s in summary:
        status = "PASSED" if s["success"] else "FAILED"
        print(f"[{status}] {s['module']}: {s['tests_run']} tests, {s['failures']} fails, {s['errors']} errors, {s['skipped']} skips ({s['elapsed_seconds']}s)")
    
    print("-" * 70)
    print(f"TOTAL: {total_run} tests run, {total_failures} failures, {total_errors} errors, {total_skipped} skipped.")
    print("="*70)
