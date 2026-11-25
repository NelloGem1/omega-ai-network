import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
os.chdir('/home/neilh/science_lab/physics')

# 1D wave equation u_tt = c^2 u_xx, fixed ends, leapfrog.
def wave(c, dx, dt, tmax, u0_kind='pulse', record=False):
    # stability: c*dt/dx <= 1 (CFL)
    L=1.0; Nx=int(L/dx)+1; x=np.linspace(0,L,Nx)
    u=np.zeros(Nx); up=np.zeros(Nx)
    if u0_kind=='pulse':
        u=np.exp(-((x-0.3)/0.05)**2)
    elif u0_kind=='two':  # two separated pulses -> superposition demo
        u=np.exp(-((x-0.25)/0.04)**2)+0.7*np.exp(-((x-0.7)/0.04)**2)
    elif u0_kind=='mode':
        u=np.sin(np.pi*x/L)
    cfl=c*dt/dx
    nsteps=int(tmax/dt)
    snaps=[]; times=[]
    rec_every=max(1,nsteps//40)
    for n in range(nsteps):
        un=2*u-up
        un[1:-1]+=cfl**2*(u[2:]-2*u[1:-1]+u[:-2])
        un[0]=un[-1]=0
        up,u=u,un
        if record and n%rec_every==0:
            snaps.append(u.copy()); times.append(n*dt)
    return x,u,up,cfl,np.array(times),snaps

# superposition: two pulses pass through each other (linear)
x,u,up,cfl,t,sn=wave(1.0,0.005,0.004,1.0,'two',record=True)
plt.figure(figsize=(8,4))
for k in [0,len(sn)//2,len(sn)-1]:
    plt.plot(x,sn[k],label='t=%.2f'%t[k])
plt.legend();plt.xlabel('x');plt.ylabel('u');plt.title('Superposition: pulses pass through unchanged')
plt.tight_layout();plt.savefig('plots/wave_superposition.png',dpi=110)
print('superposition: max |u| at t=%.2f = %.3f (bounded)'%(t[-1],np.abs(sn[-1]).max()))

# standing wave mode n=3
x,u,up,cfl,t,sn=wave(1.0,0.01,0.009,1.5,'mode',record=True)
plt.figure(figsize=(8,4))
for k in [0,len(sn)//2,len(sn)-1]:
    plt.plot(x,np.sin(3*np.pi*x),':',alpha=.4)
    plt.plot(x,sn[k],label='t=%.2f'%t[k])
plt.legend();plt.xlabel('x');plt.ylabel('u');plt.title('Standing-wave check (mode shape sin(pi x))')
plt.tight_layout();plt.savefig('plots/wave_mode.png',dpi=110)

# CFL violation: cfl = 1.5 -> blow up
dt_bad=1.5*0.01/1.0
x,u,up,cfl,t,sn=wave(1.0,0.01,dt_bad,0.5,'pulse',record=True)
print('CFL number=%.2f'%cfl)
plt.figure(figsize=(8,4))
for k in [0,len(sn)//2,len(sn)-1]:
    plt.plot(x,sn[k],label='t=%.3f'%t[k])
plt.legend();plt.yscale('symlog');plt.xlabel('x');plt.ylabel('u');plt.title('BREAK: CFL=1.5 -> numerical instability blow-up')
plt.tight_layout();plt.savefig('plots/wave_cfl_blowup.png',dpi=110)
print('max|u| at end=%.3e (grew from ~1)'%np.abs(sn[-1]).max())
np.savetxt('data/wave_cfl.csv',np.c_[t,[np.abs(s).max() for s in sn]],header='t,maxu',delimiter=',')
plt.close('all');print('DONE wave')
