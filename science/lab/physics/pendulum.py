import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
os.chdir('/home/neilh/science_lab/physics')

# Double pendulum: derive EOM symbolically with sympy to avoid sign errors.
import sympy as sp
t1,t2,w1,w2,g,L1,L2,m1,m2=sp.symbols('t1 t2 w1 w2 g L1 L2 m1 m2', real=True)
# positions (pivot at origin, y up = -cos convention: y = -L cos th)
x1=L1*sp.sin(t1); y1=-L1*sp.cos(t1)
x2=x1+L2*sp.sin(t2); y2=y1-L2*sp.cos(t2)
vx1=sp.diff(x1,t1)*w1; vy1=sp.diff(y1,t1)*w1
vx2=sp.diff(x2,t1)*w1+sp.diff(x2,t2)*w2
vy2=sp.diff(y2,t1)*w1+sp.diff(y2,t2)*w2
KE=sp.Rational(1,2)*m1*(vx1**2+vy1**2)+sp.Rational(1,2)*m2*(vx2**2+vy2**2)
PE=m1*g*y1+m2*g*y2
L=KE-PE
# Lagrange equations -> solve for angular accelerations a1,a2
a1,a2=sp.symbols('a1 a2')
eqs=[]
for th,w,a in [(t1,w1,a1),(t2,w2,a2)]:
    dL_dth=sp.diff(L,th); dL_dw=sp.diff(L,w)
    # d/dt(dL/dw) = dL_dw_t + dL_dw_th1*w1'... use chain: dL_dw depends on t1,t2,w1,w2
    dtot=sum(sp.diff(dL_dw,v)*vv for v,vv in [(t1,w1),(t2,w2),(w1,a1),(w2,a2)])
    eqs.append(sp.Eq(dtot-dL_dth,0))
sol=sp.solve(eqs,[a1,a2])
f1=sp.lambdify((t1,t2,w1,w2,g,L1,L2,m1,m2),sol[a1],'numpy')
f2=sp.lambdify((t1,t2,w1,w2,g,L1,L2,m1,m2),sol[a2],'numpy')
print('EOM derived')

def deriv(s):
    th1,th2,w1,w2=s[0],s[2],s[1],s[3]
    return np.array([w1,f1(th1,th2,w1,w2,g,L1,L2,m1,m2),
                     w2,f2(th1,th2,w1,w2,g,L1,L2,m1,m2)])

def energy(s):
    th1,th2,w1,w2=s[0],s[2],s[1],s[3]
    x1=L1*np.sin(th1);y1=-L1*np.cos(th1)
    x2=x1+L2*np.sin(th2);y2=y1-L2*np.cos(th2)
    vx1=L1*np.cos(th1)*w1;vy1=L1*np.sin(th1)*w1
    vx2=vx1+L2*np.cos(th2)*w2;vy2=vy1+L2*np.sin(th2)*w2
    KE=0.5*m1*(vx1**2+vy1**2)+0.5*m2*(vx2**2+vy2**2)
    PE=m1*g*y1+m2*g*y2
    return KE+PE

def rk4(s,dt):
    k1=deriv(s);k2=deriv(s+0.5*dt*k1);k3=deriv(s+0.5*dt*k2);k4=deriv(s+dt*k3)
    return s+dt*(k1+2*k2+2*k3+k4)/6

g=9.81;L1=L2=1.0;m1=m2=1.0
dt=2e-3;T=80.0;n=int(T/dt)
s0=np.array([np.pi/2,0,np.pi/2+0.001,0])  # [th1,w1,th2,w2]
E0=energy(s0);print('E0=%.6f'%E0)
s=s0.copy();s2=s0+np.array([0,0,0,1e-9])
es=[];sep=[];ts=[]
for i in range(n):
    s=rk4(s,dt);s2=rk4(s2,dt)
    if i%200==0:
        es.append(energy(s));ts.append(i*dt)
        sep.append(np.sqrt((s[0]-s2[0])**2+(s[2]-s2[2])**2))
es=np.array(es);sep=np.array(sep);ts=np.array(ts)
print('energy rel drift: %.3e'%(np.ptp(es)/abs(E0) if np.isfinite(es).all() else 'nan'))
print('sep(t=%.0f)=%.3e max=%.3f'%(ts[-1],sep[-1],np.nanmax(sep)))
mask=(sep>1e-13)&(sep<0.5)
if mask.sum()>5:
    print('rough lambda ~ %.3f /time'%np.polyfit(ts[mask],np.log(sep[mask]),1)[0])
np.savetxt('data/pendulum_sep.csv',np.c_[ts,sep,es/es[0]],header='t,sep,Erel',delimiter=',')
plt.figure(figsize=(7,4));plt.plot(ts,es/es[0]);plt.xlabel('t');plt.ylabel('E/E0');plt.title('Double pendulum energy conservation');plt.grid(alpha=.3);plt.tight_layout();plt.savefig('plots/pendulum_energy.png',dpi=110)
plt.figure(figsize=(7,4));plt.semilogy(ts,sep);plt.xlabel('t');plt.ylabel('angular separation');plt.title('Chaos: divergence of 1e-9 rad IC');plt.grid(alpha=.3);plt.tight_layout();plt.savefig('plots/pendulum_lyapunov.png',dpi=110)
plt.close('all');print('DONE pendulum')
