import numpy as np, itertools, json
rng = np.random.default_rng(42)

# PD payoffs: T=5,R=3,P=1,S=0 ; action 0=C,1=D
def payoff(a,b):
    if a==0 and b==0: return 3,3
    if a==0 and b==1: return 0,5
    if a==1 and b==0: return 5,0
    return 1,1

class AlwaysC:  name='always_cooperate'
class AlwaysD:  name='always_defect'
class TFT:
    name='tit_for_tat'
    def __init__(s): s.prev=None
    def act(s,hist):
        return hist[-1][1] if hist else 0
class Grim:
    name='grim_trigger'
    def __init__(s): s.defected=False
    def act(s,hist):
        if any(a==1 or b==1 for a,b in hist): s.defected=True
        return 1 if s.defected else 0
class Random:
    name='random';
    def act(s,hist): return int(rng.random()<0.5)

def mk(name):
    return {'always_cooperate':AlwaysC(),'always_defect':AlwaysD(),'tit_for_tat':TFT(),'grim_trigger':Grim(),'random':Random()}[name]
NAMES=['always_cooperate','always_defect','tit_for_tat','grim_trigger','random']
ROUNDS=100; MATCHES=1000; NOISE=0.0

# FIX: each player receives ONLY its own history (own_action, opp_action).
# Previously both players got (ha,hb) and the wrapper always read hb[-1][1],
# so seat-A TFT saw its OWN last action -> degenerated to always-cooperate.
def play(sa,sb,noise):
    ha,hb=[],[]; ta=tb=0
    for _ in range(ROUNDS):
        a,b=sa.act(ha,hb), sb.act(ha,hb)
        if noise and rng.random()<noise: a=1-a
        if noise and rng.random()<noise: b=1-b
        pa,pb=payoff(a,b); ta+=pa; tb+=pb
        ha.append((a,b)); hb.append((b,a))
    return ta,tb

def wrap(s, seat):
    # seat 'A' -> own history is ha (entries (a,b)); seat 'B' -> hb (entries (b,a))
    # in both cases hist[-1][1] is the OPPONENT's last action
    class W:
        name=s.name if hasattr(s,'name') else 'x'
        def act(self,ha,hb):
            hist = ha if seat=='A' else hb
            if isinstance(s,AlwaysC): return 0
            if isinstance(s,AlwaysD): return 1
            if isinstance(s,TFT): return hist[-1][1] if hist else 0
            if isinstance(s,Grim):
                if any(x==1 or y==1 for x,y in hist): self._d=True
                return 1 if getattr(self,'_d',False) else 0
            if isinstance(s,Random): return int(rng.random()<0.5)
    return W()

def run(noise):
    tot={n:0.0 for n in NAMES}; cnt={n:0 for n in NAMES}
    for i,na in enumerate(NAMES):
        for nb in NAMES[i:]:
            for m in range(MATCHES):
                # fresh strategy objects each match for stateful ones
                sa=wrap(mk(na),'A'); sb=wrap(mk(nb),'B')
                ta,tb=play(sa,sb,noise)
                tot[na]+=ta; cnt[na]+=ROUNDS
                tot[nb]+=tb; cnt[nb]+=ROUNDS
    return {n:tot[n]/cnt[n] for n in NAMES}

res={}
for noise in [0.0,0.05]:
    r=run(noise); res[str(noise)]=r
    print('noise',noise)
    for n,v in sorted(r.items(),key=lambda x:-x[1]): print(f'  {n:20s} {v:.3f}')
json.dump(res,open('/home/neilh/science_lab/social/exp1_results_fixed.json','w'),indent=1)
