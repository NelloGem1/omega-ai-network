import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
os.chdir('/home/neilh/science_lab/physics')

def deriv(state, mu=1.0, drag=0.0):
    x,y,vx,vy = state
    r = np.hypot(x,y); r3 = r**3
    ax = -mu*x/r3; ay = -mu*y/r3
    if drag>0:
        v = np.hypot(vx,vy)
        ax -= drag*vx*v; ay -= drag*vy*v
    return np.array([vx,vy,ax,ay])

def rk4(state, dt, **kw):
    k1=deriv(state,**kw); k2=deriv(state+0.5*dt*k1,**kw)
    k3=deriv(state+0.5*dt*k2,**kw); k4=deriv(state+dt*k3,**kw)
    return state + dt*(k1+2*k2+2*k3+k4)/6

def energy(state, mu=1.0):
    x,y,vx,vy=state
    return 0.5*(vx*vx+vy*vy) - mu/np.hypot(x,y)

def measure_period(a, mu=1.0, dt=5e-3, norb=3):
    v_c=np.sqrt(mu/a)
    T=2*np.pi*np.sqrt(a**3/mu); n=int(norb*T/dt)+10
    s=np.array([a,0.,0.,v_c]); crossings=[]; py=s[1]
    for i in range(n):
        s=rk4(s,dt,mu=mu)
        if py<0 and s[1]>=0: crossings.append(i*dt)
        py=s[1]
        if len(crossings)>=2: break
    return (crossings[1]-crossings[0]) if len(crossings)>=2 else np.nan

# Kepler 3rd law
mu=1.0; as_=np.array([0.5,1.0,2.0,4.0,8.0]); Ts=[]
for a in as_:
    Ts.append(measure_period(a,mu)); print('a=%.1f  T_meas=%.4f  T_theory=%.4f'%(a,Ts[-1],2*np.pi*np.sqrt(a**3/mu)))
Ts=np.array(Ts); ratio=Ts**2/(4*np.pi**2*as_**3)
print('T^2/(4pi^2 a^3): mean=%.4f std=%.4f (theory 1.0)'%(ratio.mean(),ratio.std()))
np.savetxt('data/orbit_kepler.csv',np.c_[as_,Ts,4*np.pi**2*as_**3],header='a,T_meas,T_theory_K3',delimiter=',')

# Energy over 100 orbits
def run(a,ecc,norb,dt=2e-3,drag=0.0,mu=1.0):
    vc=np.sqrt(mu/a)
    if ecc==0: s0=np.array([a,0.,0.,vc])
    else:
        r0=a*(1+ecc); vp=vc*np.sqrt((1-ecc)/(1+ecc)); s0=np.array([r0,0.,0.,vp])
    T=2*np.pi*np.sqrt(a**3/mu); n=int(norb*T/dt)
    E0=energy(s0,mu); s=s0.copy(); traj=np.empty((n+1,2)); traj[0]=s[:2]
    es=[];rs=[];rec=max(1,n//4000)
    for i in range(n):
        s=rk4(s,dt,mu=mu,drag=drag)
        traj[i+1]=s[:2]
        if i%rec==0: es.append(energy(s,mu)); rs.append(np.hypot(s[0],s[1]))
    return traj,E0,np.array(es),np.array(rs)

traj,E0,es,rs=run(1.0,0,100)
print('E0=%.6f  rel drift over 100 orbits: %.3e'%(E0,(es.max()-es.min())/abs(E0)))
np.savetxt('data/orbit_energy.csv',np.c_[np.linspace(0,100,len(es)),es],header='orbit,energy',delimiter=',')
plt.figure(figsize=(7,4));plt.plot(np.linspace(0,100,len(es)),es);plt.xlabel('orbit');plt.ylabel('E');plt.title('Energy conservation, RK4, a=1, 100 orbits');plt.tight_layout();plt.savefig('plots/orbit_energy.png',dpi=110)
plt.figure(figsize=(6,6));plt.plot(traj[::50,0],traj[::50,1],'.-',ms=2);plt.axis('equal');plt.title('Circular orbit a=1 (100 revs)');plt.tight_layout();plt.savefig('plots/orbit_traj.png',dpi=110);plt.close('all')

traj2,E02,es2,rs2=run(1.5,0.0,60,drag=0.02)
plt.figure(figsize=(6,6));plt.plot(traj2[::20,0],traj2[::20,1],'.-',ms=2);plt.axis('equal');plt.title('BREAK: quadratic drag=0.02 -> decay spiral');plt.tight_layout();plt.savefig('plots/orbit_drag.png',dpi=110)
plt.figure(figsize=(7,4));plt.plot(np.arange(len(rs2)),rs2);plt.xlabel('sample');plt.ylabel('r');plt.title('Radius decay under drag');plt.tight_layout();plt.savefig('plots/orbit_drag_r.png',dpi=110)
np.savetxt('data/orbit_drag_r.csv',rs2)
plt.close('all'); print('DONE orbit')
