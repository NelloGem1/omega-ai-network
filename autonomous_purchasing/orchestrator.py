#!/usr/bin/env python3
"""Autonomous Purchasing Intelligence Engine — orchestrator."""
import os, sys, json, argparse, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'core'))
import ledger, needs, discovery, evaluate, pay, risk, improve
import portfolio, subscriptions, alloc, negotiation

DATA = os.path.join(ROOT, 'data')

def frozen():
    return os.path.exists(os.path.join(DATA, 'FROZEN'))

def cmd_run(args):
    if frozen():
        print('ENGINE FROZEN — remove data/FROZEN to resume'); return
    provider = pay.get_provider(getattr(args, 'provider', 'simulated'), cash=args.cash)
    detected = needs.detect_needs()
    print(f'== NEEDS ({len(detected)}) ==')
    for n in detected:
        print(f"  {n['need_id']}: {n['capability']} gap={n['gap_score']} "
              f"({n['current']}→{n['target']})")
    if not detected:
        print('No gaps — all objectives met.'); return
    budget_map = alloc.allocate_budget(detected, args.budget)
    for n in detected:
        offers = discovery.discover(n)
        if not offers:
            print(f"\n== {n['need_id']}: NO OFFERS in catalog =="); continue
        decision = evaluate.decide(n, offers)
        best = decision['chosen']
        print(f"\n== {n['need_id']} ==")
        print(f"  CHOSEN: {best['item']} @ {best['price']} ({best['vendor']})")
        print(f"  score={best['score']} roi_est={best['roi_est']}")
        print(f"  {decision['reasoning']}")
        # risk gate
        ok, reasons = risk.risk_check(best, n)
        if not ok:
            print(f"  RISK BLOCK: {'; '.join(reasons)}"); continue
        # spend (may pend for approval)
        result = provider.spend(best, n)
        if result.get('pending_approval'):
            print(f"  PENDING APPROVAL txn#{result['txn_id']} "
                  f"(${best['price']} > ${pay.APPROVAL_THRESHOLD} threshold)")
            ledger.decision_note = None
            continue
        if not result.get('ok'):
            print(f"  SPEND FAILED: {result.get('reason')}"); continue
        # success → log + measure
        improve.log_purchase(result['txn_id'], best, decision, provider.name)
        m = improve.measure(result['txn_id'])
        portfolio.add_asset(best, result['txn_id'])
        subscriptions.add_subscription(best, result['txn_id'])
        print(f"  SETTLED txn#{result['txn_id']} | ROI={m['roi_score']} "
              f"capability now {m['new_capability_level']}")
    print('\n== LEDGER ==')
    print(' ', ledger.status(provider.c))

def cmd_status(args):
    c = ledger.init_cash(0)
    print(json.dumps(ledger.status(c), indent=2))
    print('capabilities:', needs.load('capabilities.json', {}))
    print('portfolio assets:', len(portfolio.load()['assets']))
    print('subscriptions:', len(subscriptions.load()['subscriptions']))
    print('improve report:', improve.report())

def cmd_ledger(args):
    c = ledger.init_cash(0)
    rows = c.execute("""SELECT t.id,t.ts,t.vendor,t.amount,t.purpose,t.status
                        FROM transactions t ORDER BY t.id DESC LIMIT 20""").fetchall()
    for r in rows:
        print(f"#{r['id']:>3} {r['status']:>8} {r['amount']:>8.2f} {r['vendor']:<15} {r['purpose'][:60]}")
    print('books_balanced:', ledger.check_balance(c))

def cmd_approve(args):
    c = ledger.init_cash(0)
    p = pay.get_provider('simulated', cash=0)
    p.c = c
    ok = p.capture_approved(args.txn_id)
    ledger.decision_note = None
    if ok:
        t = c.execute("SELECT * FROM transactions WHERE id=?", (args.txn_id,)).fetchone()
        improve.log_purchase(args.txn_id,
            {'offer_id':'manual','vendor':t['vendor'],'item':t['purpose'],
             'price':t['amount'],'capability':t['capability_tag'] or 'general',
             'capability_gain':0.1,'recurring':False,'risk_score':0.1,'reputation':1.0,'specs':{}},
            None, 'manual')
        improve.measure(args.txn_id, realized_gain=0.1)
        print(f'txn#{args.txn_id} APPROVED + settled')
    else:
        print('not found or not pending')

def cmd_creds(args):
    p = pay.ApiKeyProvider()
    print(json.dumps(p.credentials_report(), indent=2))

def cmd_freeze(args):
    open(os.path.join(DATA, 'FROZEN'), 'w').write('frozen by operator')
    print('ENGINE FROZEN')

def cmd_unfreeze(args):
    p = os.path.join(DATA, 'FROZEN')
    if os.path.exists(p): os.remove(p)
    print('ENGINE UNFROZEN')

def main():
    ap = argparse.ArgumentParser(description='Autonomous Purchasing Engine')
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('--cash', type=float, default=10000)
    r.add_argument('--budget', type=float, default=2000)
    r.add_argument('--provider', default='simulated', choices=['simulated', 'apikey']); r.set_defaults(f=cmd_run)
    sub.add_parser('status').set_defaults(f=cmd_status)
    sub.add_parser('ledger').set_defaults(f=cmd_ledger)
    a = sub.add_parser('approve'); a.add_argument('txn_id', type=int); a.set_defaults(f=cmd_approve)
    sub.add_parser('credentials').set_defaults(f=cmd_creds)
    sub.add_parser('freeze').set_defaults(f=cmd_freeze)
    sub.add_parser('unfreeze').set_defaults(f=cmd_unfreeze)
    args = ap.parse_args()
    args.f(args)

if __name__ == '__main__':
    main()
