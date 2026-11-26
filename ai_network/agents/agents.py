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
                'confidence': 0.7, 'detail': f'evaluated {n} candidates'}

class ClaudeAgent(Agent):
    name = 'CLAUDE'
    def think(self, problem):
        # analytic solver: closed-form approximation
        n = problem.get('n', 10)
        # analytic guess: largest quadratic residue-ish
        best = int(math.sqrt(n)) * (n % 3 + 1) % n
        return {'answer': best, 'method': 'analytic-approx',
                'confidence': 0.6, 'detail': 'closed-form heuristic'}

class GPTAgent(Agent):
    name = 'GPT'
    def think(self, problem):
        # pattern-matcher: learns from prior knowledge
        known = bus.query_knowledge(problem.get('topic','optimization'))
        if known:
            return {'answer': known[0]['content'].split(':')[-1].strip() if ':' in known[0]['content'] else known[0]['content'],
                    'method': 'knowledge-recall', 'confidence': 0.8,
                    'detail': f'recalled {len(known)} entries'}
        n = problem.get('n', 10)
        return {'answer': n-1, 'method': 'pattern-match',
                'confidence': 0.5, 'detail': 'no prior knowledge'}

def verify_solution(sol, problem, checker):
    """Independent verification — different method than solver."""
    n = problem.get('n', 10)
    claimed = sol.get('answer')
    # ground truth: brute force the actual optimum
    actual = max(range(n), key=lambda i: (i*i) % n)
    correct = (claimed == actual)
    return {'verified': correct, 'claimed': claimed, 'actual': actual,
            'method': 'brute-force-check', 'confidence': 1.0 if correct else 0.0}
