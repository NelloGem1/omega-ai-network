import numpy as np, itertools, json
rng=np.random.default_rng(7)

def pure_nes(A):
    # A: (n,m,2) payoffs; returns list of (i,j)
    n,m,_=A.shape; nes=[]
    for i in range(n):
        for j in range(m):
            u1=A[i,j,0]; u2=A[i,j,1]
            if all(u1>=A[i,jj,0] for jj in range(m)) and all(u2>=A[ii,j,1] for ii in range(n)):
                nes.append((i,j))
    return nes

def verify_ne(A,i,j):
    n,m,_=A.shape
    return all(A[i,j,0]>=A[i,jj,0] for jj in range(m)) and all(A[i,j,1]>=A[ii,j,1] for ii in range(n))

# random 2x2 and 3x3 games
stats={}
for size in [2,3]:
    counts=[]; examples=[]
    for _ in range(20000):
        A=rng.integers(0,10,size=(size,size,2))
        nes=pure_nes(A)
        counts.append(len(nes))
        if len(nes)==0 and len(examples)<2: examples.append(A.tolist())
    stats[size]={'mean_ne':float(np.mean(counts)),'dist':{int(k):int(v) for k,v in zip(*np.unique(counts,return_counts=True))},'no_ne_examples':examples}
    print(f'{size}x{size}: mean pure NE={np.mean(counts):.2f}, P(no pure NE)={np.mean(np.array(counts)==0):.3f}')

# Matching Pennies -> mixed NE
# row player maximizes p mix; indifference gives p=(0.5,0.5)
MP=np.array([[[1,-1],[-1,1]],[[-1,1],[1,-1]]])
print('Matching Pennies pure NE:',pure_nes(MP))
# mixed: row mixes (p,1-p) s.t. col indifferent: col payoff for L = p*1+(1-p)*(-1)=2p-1 ; R = p*(-1)+(1-p)*1=1-2p -> p=0.5; same for row -> (0.5,0.5)
print('Matching Pennies mixed NE: sigma_row=(0.5,0.5), sigma_col=(0.5,0.5), EV=0')

# general 2x2 mixed NE solver: find p,q where each mixes
def mixed_ne_2x2(A):
    a=A[0,0,0]; b=A[0,1,0]; c=A[1,0,0]; d=A[1,1,0]  # row payoffs
    # row indifferent over col mix q: q*a+(1-q)*b = q*c+(1-q)*d -> q=(d-b)/(a-b-c+d)... derive: q(a-b)+b = q(c-d)+d -> q=(d-b)/(a-b-c+d)? do numerically
    # col payoffs: e=A[0,0,1],f=A[0,1,1],g=A[1,0,1],h=A[1,1,1]
    e=A[0,0,1]; f=A[0,1,1]; g=A[1,0,1]; h=A[1,1,1]
    # q (prob col plays col0): row indiff: q*a+(1-q)*b = q*c+(1-q)*d
    den=(a-b)-(c-d)
    if abs(den)<1e-9: return None
    q=((d-b))/den
    # p (prob row plays row0): col indiff: p*e+(1-p)*g = p*f+(1-p)*h
    den2=(e-g)-(f-h)
    if abs(den2)<1e-9: return None
    p=((h-g))/den2
    if 0<p<1 and 0<q<1: return p,q
    return None

tested=0; found=0; ex=None
for _ in range(5000):
    A=rng.integers(0,10,size=(2,2,2))
    if pure_nes(A): continue
    tested+=1
    r=mixed_ne_2x2(A)
    if r:
        found+=1
        if ex is None: ex=(A.tolist(),r)
print(f'2x2 games w/o pure NE: {tested}; with fully-mixed NE: {found}')
if ex:
    A=np.array(ex[0]); p,q=ex[1]
    # verify indifference numerically
    ev_row0=q*A[0,0,0]+(1-q)*A[0,1,0]; ev_row1=q*A[1,0,0]+(1-q)*A[1,1,0]
    ev_col0=p*A[0,0,1]+(1-p)*A[1,0,1]; ev_col1=p*A[0,1,1]+(1-p)*A[1,1,1]
    print('example game payoffs row/col:'); print(A); print('mix p,q=',p,q)
    print('row EVs (should be ~equal):',ev_row0,ev_row1,'col EVs:',ev_col0,ev_col1)
json.dump({'stats':stats},open('/home/neilh/science_lab/social/exp2_results.json','w'),default=str,indent=1)
