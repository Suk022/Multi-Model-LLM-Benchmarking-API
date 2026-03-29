from typing import List, Optional
from schemas.benchmark import ModelResult, BenchmarkSummary

def rank_results(results: List[ModelResult], criteria: str) -> BenchmarkSummary:
    successful_results = [r for r in results if r.status == "success"]
    
    if not successful_results:
        return BenchmarkSummary(
            fastest=None,
            cheapest=None,
            recommended=None,
            criteria_used=criteria
        )
    
    fastest_result = min(successful_results, key=lambda x: x.latency_ms or float('inf'))
    fastest = fastest_result.model_key
    
    cheapest_result = min(
        successful_results, 
        key=lambda x: x.estimated_cost_usd if x.estimated_cost_usd and x.estimated_cost_usd > 0 else float('inf')
    )
    
    if cheapest_result.estimated_cost_usd == 0.0:
        cheapest = fastest
    else:
        cheapest = cheapest_result.model_key
    
    if criteria == "fastest":
        recommended = fastest
    elif criteria == "cheapest":
        recommended = cheapest
    else:  # balanced
        min_latency = min(r.latency_ms for r in successful_results if r.latency_ms)
        max_latency = max(r.latency_ms for r in successful_results if r.latency_ms)
        min_cost = min(r.estimated_cost_usd for r in successful_results if r.estimated_cost_usd)
        max_cost = max(r.estimated_cost_usd for r in successful_results if r.estimated_cost_usd)
        
        def balanced_score(result):
            latency_norm = (result.latency_ms - min_latency) / (max_latency - min_latency) if max_latency != min_latency else 0
            cost_norm = (result.estimated_cost_usd - min_cost) / (max_cost - min_cost) if max_cost != min_cost else 0
            return 0.5 * latency_norm + 0.5 * cost_norm
        
        balanced_result = min(successful_results, key=balanced_score)
        recommended = balanced_result.model_key
    
    return BenchmarkSummary(
        fastest=fastest,
        cheapest=cheapest,
        recommended=recommended,
        criteria_used=criteria
    )
