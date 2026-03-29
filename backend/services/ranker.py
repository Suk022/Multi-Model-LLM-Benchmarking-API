from typing import List, Optional, TypeVar, Callable
import logging
from schemas.benchmark import ModelResult, BenchmarkSummary

T = TypeVar('T')

def safe_min(items: List[T], key: Optional[Callable[[T], float]] = None) -> Optional[T]:
    return min(items, key=key) if items else None

def rank_results(results: List[ModelResult], criteria: str) -> BenchmarkSummary:
    successful_results = [r for r in results if r.status == "success"]
    
    if not successful_results:
        logging.warning("All model calls failed in benchmark")
        return BenchmarkSummary(
            fastest=None,
            cheapest=None,
            recommended=None,
            criteria_used=criteria
        )
    
    # Fastest - based on latency_ms
    results_with_latency = [r for r in successful_results if r.latency_ms is not None]
    fastest_result = safe_min(results_with_latency, key=lambda x: x.latency_ms)
    fastest = fastest_result.model_key if fastest_result else None
    
    # Cheapest - based on estimated_cost_usd (ignore None values)
    results_with_cost = [r for r in successful_results if r.estimated_cost_usd is not None]
    cheapest_result = safe_min(results_with_cost, key=lambda x: x.estimated_cost_usd)
    cheapest = cheapest_result.model_key if cheapest_result else None
    
    if not results_with_cost:
        logging.warning("No cost data available in benchmark results")
    
    # Recommended - based on criteria
    if criteria == "fastest":
        recommended = fastest
    elif criteria == "cheapest":
        recommended = cheapest
    else:  # balanced
        # Only use results that have both latency and cost data
        balanced_candidates = [
            r for r in successful_results 
            if r.latency_ms is not None and r.estimated_cost_usd is not None
        ]
        
        if not balanced_candidates:
            # Fall back to fastest if no balanced candidates
            recommended = fastest
        else:
            min_latency = min(r.latency_ms for r in balanced_candidates)
            max_latency = max(r.latency_ms for r in balanced_candidates)
            min_cost = min(r.estimated_cost_usd for r in balanced_candidates)
            max_cost = max(r.estimated_cost_usd for r in balanced_candidates)
            
            def balanced_score(result):
                latency_norm = (result.latency_ms - min_latency) / (max_latency - min_latency) if max_latency != min_latency else 0
                cost_norm = (result.estimated_cost_usd - min_cost) / (max_cost - min_cost) if max_cost != min_cost else 0
                return 0.5 * latency_norm + 0.5 * cost_norm
            
            balanced_result = min(balanced_candidates, key=balanced_score)
            recommended = balanced_result.model_key
    
    return BenchmarkSummary(
        fastest=fastest,
        cheapest=cheapest,
        recommended=recommended,
        criteria_used=criteria
    )
