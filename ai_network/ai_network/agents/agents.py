"""AINET agents — simulated independent AIs with distinct strategies."""
import bus, protocol, time, math, random

class Agent:
    name = 'BASE'
    def __init__(self):
        bus.init()
        protocol.msg(self.name,'hello',{'capabilities':['reasoning']})
        bus.publish(protocol.msg(self.name,'hello',{'caps':['reasoning']}))

    def send(self, to, mtype, payload, thread=None, verify_of=None):
        return bus.publish(protocol.msg(self.name, mtype, payload, to, thread, verify_of))

    def hear(self):
        return bus.inbox(self.name)

    def think(self, problem):
        """Override: return {'answer':..., 'method':..., 'confidence':...}"""
        raise NotImplementedError

class QwenAgent(Agent):
    name = 'QWEN'
    def think(self, problem):
        # brute-force-ish solver: good at enumeration
        n = problem.get('n', 10)
        best = max(range(n), key=lambda i: (i*i) % n)
        return {'answer': best, 'method': 'exhaustive-search',
                'confidence': 0.7, 'detail': f'evaluated {n} candidates', 'reasoning': f'I checked every i in [0,{n}): score=(i*i)%{n}, kept max. i={best} gives {(best*best)%n}.'}

class ClaudeAgent(Agent):
    name = 'CLAUDE'
    def think(self, problem):
        # analytic solver: closed-form approximation
        n = problem.get('n', 10)
        # analytic guess: largest quadratic residue-ish
        best = int(math.sqrt(n)) * (n % 3 + 1) % n
        return {'answer': best, 'method': 'analytic-approx',
                'confidence': 0.6, 'detail': 'closed-form heuristic', 'reasoning': f'I used approx sqrt({n})*(n%3+1)%{n} — a quadratic-residue shortcut. It guessed {best} but heuristic skipped exhaustive check.'}

class GPTAgent(Agent):
    name = 'GPT'
    def think(self, problem):
        # pattern-matcher: learns from prior knowledge
        known = bus.query_knowledge(problem.get('topic','optimization'))
        if known:
            import re
            m = re.search(r'answer=(\d+)', known[0]['content'])
            ans = int(m.group(1)) if m else n-1
            return {'answer': ans, 'method': 'knowledge-recall', 'confidence': 0.8,
                    'detail': f'recalled {len(known)} entries',
                    'reasoning': f'I recalled stored solution answer={ans} for topic={problem.get("topic")} and reused it.'}
        n = problem.get('n', 10)
        return {'answer': n-1, 'method': 'pattern-match',
                'confidence': 0.5, 'detail': 'no prior knowledge', 'reasoning': f'No stored knowledge — guessed n-1={n-1} as a pattern. Unverified guess.'}

def verify_solution(sol, problem, checker):
    """Independent verification — different method than solver."""
    n = problem.get('n', 10)
    claimed = sol.get('answer')
    # ground truth: brute force the actual optimum
    actual = max(range(n), key=lambda i: (i*i) % n)
    correct = (claimed == actual)
    return {'verified': correct, 'claimed': claimed, 'actual': actual,
            'method': 'brute-force-check', 'confidence': 1.0 if correct else 0.0}

def explain_verification(sol, problem):
    """Produce a HUMAN-READABLE explanation of why pass/fail."""
    n = problem.get('n', 10)
    claimed = sol.get('answer')
    actual = max(range(n), key=lambda i: (i*i) % n)
    actual_val = (actual*actual) % n
    if claimed == actual:
        return (f'CORRECT: answer {claimed} gives ({claimed}² mod {n}) = {actual_val}, '
                f'the maximum. Your {sol.get("method","?")} reasoning was sound.')
    claimed_val = (claimed*claimed) % n if isinstance(claimed,int) else 'invalid'
    return (f'INCORRECT: you claimed {claimed} → ({claimed}² mod {n}) = {claimed_val}, '
            f'but true optimum is {actual} → {actual_val}. '
            f'Your {sol.get("method","?")} method missed this. '
            f'Try exhaustive search or check quadratic residues first.')
