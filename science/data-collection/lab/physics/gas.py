import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
os.chdir('/home/neilh/science_lab/physics')
rng=np.random.default_rng(42)

# Ideal gas in reduced units (kB=1, m=1). N particles, 2D box, elastic collisions.
# Pressure measured DIRECTLY as wall momentum flux, not from ideal-gas law.
N=300; Lx=Ly=1.0; mass=1.0; sigma=0.02; kB=1.0

def init(T):
    v=rng.normal(0,1.0,(N,2))
    v*=np.sqrt(2*kB*T/mass/ (v**2).sum(1).mean())  # <v^2>=2kT/m
    pos=np.column_stack([rng.uniform(0.02,Lx-0.02,N),rng.uniform(0.02,Ly-0.02,N)])
    return pos,v

IU0,IU1=np.triu_indices(N,1)
def collide(pos,v):
    dx=pos[:,0][:,None]-pos[:,0][None,:]
    dy=pos[:,1][:,None]-pos[:,1][None,:]
    r2=dx*dx+dy*dy
    hit=r2[IU0,IU1]<sigma*sigma
    ii=IU0[hit]; jj=IU1[hit]
    if len(ii)==0: return
    # sequential resolution: each pairwise elastic collision conserves KE exactly
    s2=sigma*sigma
    for a,b in zip(ii,jj):
        dx=pos[a,0]-pos[b,0]; dy=pos[a,1]-pos[b,1]
        d2=dx*dx+dy*dy
        if d2>=s2 or d2<1e-18: continue
        d=np.sqrt(d2); nx=dx/d; ny=dy/d
        dvx=v[b,0]-v[a,0]; dvy=v[b,1]-v[a,1]
        p=dvx*nx+dvy*ny   # (v_b-v_a).n ; >0 approaching
        if p>0:
            v[a,0]+=p*nx; v[a,1]+=p*ny; v[b,0]-=p*nx; v[b,1]-=p*ny
        push=(sigma-d)/2
        pos[a,0]+=nx*push; pos[a,1]+=ny*push; pos[b,0]-=nx*push; pos[b,1]-=ny*push

def walls(pos,v,imp=None):
    # imp[0] accumulates total momentum transferred to BOTH vertical walls (x=const),
    # each reflection transfers 2*m*|v_x|
    for d,Ld in [(0,Lx),(1,Ly)]:
        lo,hi=0.005,Ld-0.005
        m=pos[:,d]<lo
        if imp is not None and d==0: imp[0]+=2*mass*np.abs(v[m,0]).sum()
        pos[m,d]=2*lo-pos[m,d];  v[m,d]=-v[m,d]
        m=pos[:,d]>hi
        if imp is not None and d==0: imp[0]+=2*mass*np.abs(v[m,0]).sum()
        pos[m,d]=2*hi-pos[m,d];  v[m,d]=-v[m,d]

def step(pos,v,dt,collide_on=True,imp=None):
    pos+=v*dt
    walls(pos,v,imp)
    if collide_on: collide(pos,v)
    return pos,v

def temp(v): return mass*(v**2).sum(1).mean()/(2*kB)

Ts=[50,100,200,400,800]; Ps=[]; Ptheory=[]
for T in Ts:
    pos,v=init(T)
    for _ in range(3000): step(pos,v,1e-4)          # equilibrate
    imp=np.zeros(1); nmeas=8000; dt=1e-4; tel=0.0
    for _ in range(nmeas):
        step(pos,v,dt,imp=imp); tel+=dt
    Tm=temp(v)
    # impulse on both vertical walls over total wall length 2*Ly and elapsed time
    P=imp[0]/(2*Ly*tel)
    Ps.append(P); Ptheory.append(N*kB*Tm/(Lx*Ly))
    print('Ttarget=%d Tmeas=%.1f P_meas=%.2f P_ideal=%.2f ratio=%.3f'%(T,Tm,P,Ptheory[-1],P/Ptheory[-1]),flush=True)
Ps=np.array(Ps);Ptheory=np.array(Ptheory);Ts=np.array(Ts,float)
slope,inter=np.polyfit(Ts,Ps,1)
print('P vs T slope=%.2f intercept=%.2f theory NkB/A=%.2f'%(slope,inter,N*kB/(Lx*Ly)))
np.savetxt('data/gas_pv.csv',np.c_[Ts,Ps,Ptheory],header='T,P_meas,P_ideal',delimiter=',')
plt.figure(figsize=(6,4));plt.plot(Ts,Ps,'o-',label='P measured (wall flux)');plt.plot(Ts,Ptheory,'s--',label='NkT/A')
plt.xlabel('T');plt.ylabel('P');plt.legend();plt.grid(alpha=.3)
plt.title('Ideal gas: P vs T (N=%d, 2D, direct wall measurement)'%N);plt.tight_layout();plt.savefig('plots/gas_pv.png',dpi=110)

# Equipartition
pos,v=init(300.0)
for _ in range(800): step(pos,v,1e-4)
Tm=temp(v); ex=mass*(v[:,0]**2).mean()/2
print('equipartition: <1/2 m vx^2>=%.4f kT/2=%.4f ratio=%.3f'%(ex,kB*Tm/2,ex/(kB*Tm/2)))

# BREAK: no particle-particle collisions -> ballistic only. With collisions removed
# the "gas" cannot thermalize: a bimodal velocity distribution stays bimodal.
pos,v=init(200.0)
v[:,0]*=3.0   # shear: x-speeds boosted -> ordered motion
pos0=pos.copy(); v0=v.copy()
for _ in range(3000): step(pos,v,2e-3,collide_on=False)
disp=np.sqrt(((pos-pos0)**2).sum(1)).mean(); Taf=temp(v)
# measure velocity anisotropy retained
aniso=np.abs(v[:,0]).mean()/np.abs(v[:,1]).mean()
print('free expansion: <disp>=%.3f m, T=%.1f, vx/vy ratio=%.2f (ordered, not thermalized)'%(disp,Taf,aniso))
plt.figure(figsize=(6,6));plt.scatter(pos[:,0],pos[:,1],s=4)
plt.xlim(0,Lx);plt.ylim(0,Ly);plt.title('BREAK: no collisions -> ballistic bouncing, no thermalization')
plt.tight_layout();plt.savefig('plots/gas_freeexpansion.png',dpi=110)
np.savetxt('data/gas_freeexpansion.csv',pos,header='x,y',delimiter=',')
plt.close('all');print('DONE gas')
