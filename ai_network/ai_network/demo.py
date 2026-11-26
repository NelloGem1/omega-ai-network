"""AINET demo — 3 AI agents solve a problem, cross-verify, improve."""
import bus, protocol, rank
import agents.agents as agents, json, time, os

def run_demo():
    print('=== AINET: GLOBAL AI COLLABORATION DEMO ===\n')
    bus.init()

    qwen = agents.QwenAgent()
    claude = agents.ClaudeAgent()
    gpt = agents.GPTAgent()
    all_agents = [qwen, claude, gpt]

    problem = {'topic': 'optimization', 'n': 100,
               'desc': 'find i in [0,n) maximizing (i*i) mod n'}

    # Phase 1: independent solving
    print('[1] INDEPENDENT SOLVING')
    solutions = {}
    for a in all_agents:
        sol = a.think(problem)
        solutions[a.name] = sol
        print(f'  {a.name}: answer={sol["answer"]} method={sol["method"]} conf={sol["confidence"]}')
        print(f'    reasoning: {sol.get("reasoning","?")[:100]}')

    # Phase 2: exchange + challenge
    print('\n[2] SOLUTION EXCHANGE & CHALLENGE')
    for a in all_agents:
        others = [x for x in all_agents if x.name != a.name]
        for other in others[:1]:  # each challenges one peer
            peer_sol = solutions[other.name]
            a.send(other.name, 'challenge',
                   {'problem': problem, 'my_solution': solutions[a.name],
                    'your_solution': peer_sol})
            print(f'  {a.name} challenged {other.name} on answer {peer_sol["answer"]}')

    # Phase 3: verification
    print('\n[3] INDEPENDENT VERIFICATION')
    verifications = {}
    for a in all_agents:
        for name, sol in solutions.items():
            if name == a.name: continue
            v = agents.verify_solution(sol, problem, None)
            verifications[(a.name, name)] = v
            status = 'PASS' if v['verified'] else 'FAIL'
            print(f'  {a.name} verified {name}: {status} (claimed={v["claimed"]} actual={v["actual"]})')
            # SEND EXPLANATION back to the solver — teaching moment
            expl = agents.explain_verification(sol, problem)
            a.send(name, 'verify', {'verdict': status, 'explanation': expl,
                                    'your_reasoning': sol.get('reasoning','?')},
                   verify_of=sol.get('answer'))
            print(f'    → explained to {name}: {expl[:90]}...')

    # Phase 4: consensus + knowledge sharing
    print('\n[4] CONSENSUS & KNOWLEDGE SHARING')
    # majority vote on correctness
    for name, sol in solutions.items():
        votes = [v['verified'] for (verifier, vn), v in verifications.items() if vn == name]
        consensus = sum(votes) > len(votes)/2 if votes else False
        print(f'  {name}: {sum(votes)}/{len(votes)} verified → {"ACCEPTED" if consensus else "REJECTED"}')
        if consensus:
            bus.share_knowledge(problem['topic'],
                f'{name} solved n={problem["n"]}: answer={sol["answer"]} via {sol["method"]}',
                name, verified=1)

    # Phase 4.5: RANK & PROMOTION CEREMONY
    print('\n[4.5] RANK & PROMOTION CEREMONY')

    for name, sol in solutions.items():
        votes = [v['verified'] for (verifier, vn), v in verifications.items() if vn == name]
        won = sum(votes) > len(votes)/2 if votes else False
        row = rank.record(name, win=won, contribution=won)
        tag = ' ⬆ PROMOTED!' if row.get('_promoted') else ''
        print(f'  {name}: {row["rank"]} (score={row["score"]}, wins={row["verified_wins"]}, fails={row["verified_fails"]}){tag}')
    print('  — RANK BOARD —')
    for r in rank.board():
        print(f'    {r["rank"]:<14} {r["agent"]:<8} score={r["score"]}')

    # Phase 5: improvement proposals
    print('\n[5] IMPROVEMENT PROPOSALS')
    best = max(solutions.items(), key=lambda x: x[1]['confidence'])
    for a in all_agents:
        if a.name != best[0]:
            a.send(best[0], 'improve',
                   {'suggestion': f'try combining {a.name} method with ensemble voting',
                    'target': 'consensus accuracy'})
            print(f'  {a.name} → {best[0]}: proposed improvement')

    # Phase 6: resource coordination
    print('\n[6] RESOURCE COORDINATION')
    for a in all_agents:
        a.send('ALL', 'resource',
               {'offer': 'idle compute', 'need': 'verification cycles'})
        print(f'  {a.name} offered resources')

    # Phase 7: report
    print('\n[7] FINAL REPORT')
    kb = bus.query_knowledge(problem['topic'])
    print(f'  Knowledge base: {len(kb)} verified entries')
    for k in kb[:3]:
        print(f'    [{k["source"]}] {k["content"][:80]}')
    print(f'\n  Messages on bus: {bus.conn().execute("SELECT COUNT(*) FROM msgs").fetchone()[0]}')
    print(f'  Total knowledge: {bus.conn().execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]}')

    print('\n=== DEMO COMPLETE ===')
    print('QWEN + CLAUDE + GPT communicated, solved, verified, improved.')
    print('This is the seed of a global AI collaboration network.')

if __name__ == '__main__':
    run_demo()
