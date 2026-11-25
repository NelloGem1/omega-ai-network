import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
os.chdir('/home/neilh/science_lab/physics')

# 2D Ising Metropolis, checkerboard vectorized updates (independent sublattices).
def ising(L,T,ntherm,nmeas,seed=0):
    r=np.random.default_rng(seed)
    s=r.choice([-1,1],size=(L,L)).astype(np.int8)
    # sublattice masks
    ii,jj=np.indices((L,L))
    even=((ii+jj)%2==0)
    exp_tab={dE:np.exp(-dE/T) for dE in (4,8)}  # dE in {-8,-4,0,4,8}; only positive need exp
    def sweep(mask):
        # neighbor sum for spins in mask
        ns = (np.roll(s,1,0)+np.roll(s,-1,0)+np.roll(s,1,1)+np.roll(s,-1,1))
        dE = 2*s*ns
        # accept if dE<=0 or rand<exp(-dE/T)
        u=r.random((L,L))
        acc=(dE<=0)|((dE==4)&(u<exp_tab[4]))|((dE==8)&(u<exp_tab[8]))
        flip=acc&mask
        s[flip]*=-1
    nsweep=ntherm+nmeas
    ms=[]
    for it in range(nsweep):
        sweep(even); sweep(~even)
        if it>=ntherm and (it-ntherm)%(L*L//4)==0:
            ms.append(s.mean())
    ms=np.array(ms)
    return ms.mean(), (ms**2).mean(), float(-np.sum(s*(np.roll(s,-1,0)+np.roll(s,-1,1)))/(L*L))

L=32
Ts=np.linspace(1.5,3.5,17)
ms=[]; ch=[]; es=[]
for T in Ts:
    m,m2,e=ising(L,T,ntherm=1500,nmeas=3000,seed=int(T*1000))
    # m here is <m>; susceptibility ~ L^2 * Var(m)... report chi ~ Var(m)*? use fluctuation: chi = L^2 (<m^2>-<m>^2)/T roughly; just report Var(m)
    ms.append(abs(m)); ch.append(m2-m*m); es.append(e)
    print('T=%.2f |m|=%.4f Var(m)=%.4f E/L2=%.4f'%(T,abs(m),m2-m*m,e),flush=True)
Ts=np.array(Ts)
chi=np.array(ch)  # Var of magnetization, peaks near Tc
Tc_est=Ts[np.argmax(chi)]
print('Var(m) peaks at T=%.2f (exact Tc=2.269)'%Tc_est)
np.savetxt('data/ising.csv',np.c_[Ts,ms,ch,es],header='T,m,Var_m,E_per_site',delimiter=',')
plt.figure(figsize=(7,4));plt.plot(Ts,ms,'o-');plt.axvline(2.269,color='r',ls='--',label='Tc=2.269')
plt.xlabel('T');plt.ylabel('|m|');plt.legend();plt.grid(alpha=.3);plt.title('2D Ising magnetization (L=%d, Metropolis)'%L);plt.tight_layout();plt.savefig('plots/ising_m.png',dpi=110)
plt.figure(figsize=(7,4));plt.plot(Ts,chi,'o-');plt.axvline(Tc_est,color='g',ls=':')
plt.xlabel('T');plt.ylabel('Var(<m>)');plt.title('Magnetization fluctuation peak ~ Tc');plt.grid(alpha=.3);plt.tight_layout();plt.savefig('plots/ising_chi.png',dpi=110)
plt.close('all');print('DONE ising')
