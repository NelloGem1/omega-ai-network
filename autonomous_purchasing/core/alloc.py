"""Resource allocation intelligence — budget distribution."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

def allocate_budget(needs, total_budget):
    """Distribute budget across needs proportional to gap_score.
    Returns {need_id: allocated_amount}."""
    if not needs:
        return {}
    total_gap = sum(n['gap_score'] for n in needs) or 1
    alloc = {}
    for n in needs:
        share = n['gap_score'] / total_gap
        alloc[n['need_id']] = round(total_budget * share, 2)
    return alloc

def rebalance(portfolio_underperformers, active_needs):
    """Suggest freeing budget from dead assets toward active needs."""
    freed = sum(a['cost'] for a in portfolio_underperformers)
    return {'freed_budget': round(freed, 2),
            'suggestion': 'reallocate to highest-gap active needs' if freed > 0 else 'no action'}
