import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
os.chdir('/home/neilh/science_lab/physics')

# Finite-difference Schrodinger: particle in a box (infinite well) and finite barrier tunneling.
hbar=1.0; m=1.0
L=10.0; Nx=400; x=np.linspace(0,L,Nx+1); dx=x[1]-x[0]
# Hamiltonian: -hbar^2/(2m) d2/dx2 with Dirichlet BCs -> interior Nx-1 points
n=Nx-1
main= np.full(n, hbar**2/(m*dx**2))
off = np.full(n-1, -hbar**2/(2*m*dx**2))
H=diags([main,off,off],[0,-1,1],format='csc')
evals,evecs=eigsh(H,k=6,which='SA')
order=np.argsort(evals); evals=evals[order]; evecs=evecs[:,order]
analytic=[(np.pi**2*hbar**2/(2*m*L**2))*(k+1)**2 for k in range(6)]
print('eigenvalues numeric :',np.round(evals,5))
print('eigenvalues analytic:',np.round(analytic,5))
print('rel err n=0: %.3e'%(evals[0]/analytic[0]-1))
np.savetxt('data/schrod_eigs.csv',np.c_[evals,analytic],header='numeric,analytic',delimiter=',')

xi=x[1:-1]
plt.figure(figsize=(8,4))
for k in range(3):
    psi=evecs[:,k]; psi/=np.sqrt((psi**2).sum()*dx)
    plt.plot(xi,psi**2,label='n=%d'%k)
plt.legend();plt.xlabel('x');plt.ylabel('|psi|^2');plt.title('Particle in a box: |psi_n|^2')
plt.tight_layout();plt.savefig('plots/schrod_box.png',dpi=110)

# Tunneling: finite square barrier V0 on [a,b], incident energy E<V0.
# Solve via transfer/scattering: build H on bigger domain with absorbing-ish approach:
# simpler: compute transmission through barrier using analytic formula for comparison,
# and numerically via wavefunction matching with scipy solve_bvp-free approach:
# use finite-difference scattering with complex absorbing? Keep it simple:
# Numerically integrate stationary Schrodinger with shooting -> T vs width.
def barrier_T(E,V0,w,Ltot=30.0,Nx2=3000):
    # region: [-L,0] free, [0,w] barrier, [w,Ltot] free; incidence from left.
    xx=np.linspace(-Ltot,w+Ltot,Nx2); h=xx[1]-xx[0]
    V=np.where((xx>=0)&(xx<=w),V0,0.0)
    # solve (H-E)psi=0 with psi(-L)=e^{ikx}+r e^{-ikx}, psi(+inf)=t e^{ikx}
    # use finite difference linear system with boundary conditions via scipy sparse
    from scipy.sparse import diags as dg
    from scipy.sparse.linalg import spsolve
    n2=len(xx)
    main=np.full(n2,hbar**2/(m*h**2)+V-E)
    off=np.full(n2-1,-hbar**2/(2*m*h**2))
    A=dg([main,off,off],[0,-1,1],format='csc').tolil()
    k=np.sqrt(2*m*E)/hbar
    # left BC at i=0: psi= e^{ik x}+r e^{-ikx} -> impose psi'(0)=ik(1-r)... simpler Dirichlet-ish:
    # Use standard approach: set psi_0=1+r unknown; instead impose outgoing at both ends.
    # Left: psi_1 = psi_0 * exp(-ik h)  (right-going+left-going combo) -> use two-sided:
    # We impose: psi[0] free, relation psi[1]-psi[0]e^{-ikh}=0 enforces left-going? Use:
    # incoming+reflected at left ~ (psi[1]-psi[0]) matching. Simplest robust: large box,
    # psi=0 far left isn't physical for scattering. Use known trick: solve with
    # psi[N-1]=exp(ik x_N) (pure transmitted) and at left impose psi[0]=exp(ikx0)+r*exp(-ikx0)
    # Solve by introducing r as unknown -> do it via two solves (linear in source).
    # Even simpler: finite box with psi=0 at both ends gives quasi-bound; instead use
    # R-matrix style: transmission via transfer matrix analytically for piecewise-const V.
    return None

# Analytic rectangular barrier transmission (exact):
def T_exact(E,V0,w):
    if E<=0: return 0.0
    k=np.sqrt(2*m*E)/hbar; q=np.sqrt(2*m*(V0-E))/hbar if V0>E else 1j*np.sqrt(2*m*(E-V0))/hbar
    # T = 1 / (1 + (V0^2 sinh^2(qw))/(4E(V0-E)))  for E<V0
    if E<V0:
        s=np.sinh(q*w)
        return 1.0/(1.0 + (V0**2*s**2)/(4*E*(V0-E)))
    else:
        s=np.sin(q*w)
        return 1.0/(1.0 - (V0**2*s**2)/(4*E*(V0-E)))

# Numerical check: discretize barrier region only, use transfer matrix of FD Hamiltonian
# Build propagator across barrier via scipy: solve scattering with absorbing boundaries
# by adding imaginary potential at edges. Quick approach: finite difference on whole
# line with a source? Use numpy: propagate wavefunction with split-operator? Too heavy.
# Instead verify FD eigenvalue of a finite well vs analytic, and tunneling via WKB-ish
# comparison of exact formula vs a numerical FD solve of the 1D scattering using
# scipy.integrate.solve_bvp is overkill; use exact formula as reference and compute
# numerical T via the "finite box + complex absorbing" (CAP) method:
def T_num(E,V0,w,Ltot=40.0,Nx2=8000,eta=0.05):
    # domain x in [0,Ltot]; barrier at center. Add -i*eta*(x edges) CAP.
    xx=np.linspace(0,Ltot,Nx2); h=xx[1]-xx[0]
    xc=Ltot/2; V=np.where(np.abs(xx-xc)<w/2,V0,0.0)
    cap=eta*((xx/Ltot)**8+(1-xx/Ltot)**8)*V0  # complex absorbing near edges
    n2=len(xx); k=np.sqrt(2*m*E)/hbar
    # Discretize H psi = E psi with outgoing-ish BCs: use psi[0]=exp(ik*0)=1? Use
    # standard: impose at left psi ~ e^{ikx}+r e^{-ikx}; solve linear system for psi
    # with boundary rows enforcing derivative ratio.
    main=(hbar**2/(m*h**2)+V-E) + 1j*cap
    off=np.full(n2-1,-hbar**2/(2*m*h**2))
    A=diags([main,off,off],[0,-1,1],format='lil')
    # left boundary: (psi1-psi0)/h ~ ik(psi0 - 2 Re?) -> simpler Dirichlet psi0=1+r unknown.
    # Trick: set psi0=1 and psi[N-1]=0 -> measures partial; instead use two-boundary
    # outgoing: at right impose psi[N-1]=t e^{ik x_N}: nonlinear. Use the standard
    # "solution via fundamental matrix" is heavy; use WKB check instead.
    return None

# Simpler numeric: solve 1D scattering via scipy solve_bvp? Use transfer matrix built
# from FD Hamiltonian eigen-decomposition is also heavy. Use exact formula + FD check
# of bound state in finite well instead, and tunneling splitting of double well.
# FINITE WELL eigenvalues vs analytic (numerical) — good check.
V0w=-5.0; ww=4.0  # finite well depth/width on [-L,L]
nw=Nx-1
Vw=np.where(np.abs(xi-L/2)<ww/2, V0w, 0.0)
Hw=diags([np.full(nw,hbar**2/(m*dx**2))+Vw, off[:nw-1] if len(off)>=nw-1 else off, off[:nw-1] if len(off)>=nw-1 else off],[0,-1,1],format='csc')
# fix: rebuild properly
Hw=diags([np.full(nw,hbar**2/(m*dx**2))+Vw, np.full(nw-1,-hbar**2/(2*m*dx**2)), np.full(nw-1,-hbar**2/(2*m*dx**2))],[0,-1,1],format='csc')
ew,_=eigsh(Hw,k=4,which='SA')
print('finite well FD eigenvalues:',np.round(np.sort(ew),4))
# analytic finite well (even/odd) solve via root finding
from scipy.optimize import brentq
def well_eigs(V0,w):
    # symmetric well [-a,a], depth V0>0 measured as V=-V0 inside. Bound E in (-V0,0).
    # xi = k a, eta = kappa a, xi^2+eta^2 = R^2 = 2 m V0 a^2 / hbar^2
    a=w/2; R=np.sqrt(2*m*V0*a*a/hbar**2)
    xs=np.linspace(1e-9,R-1e-9,200001)
    eta=np.sqrt(np.maximum(R*R-xs*xs,0))
    fe=xs*np.sin(xs)-eta*np.cos(xs)          # even: xi sin xi = eta cos xi
    fo=xs*np.cos(xs)+eta*np.sin(xs)          # odd : xi cos xi = -eta sin xi
    es=[]
    for f in (fe,fo):
        sg=np.sign(f); idx=np.nonzero(sg[:-1]*sg[1:]<0)[0]
        for i in idx:
            xi=brentq(lambda z: (z*np.sin(z)-np.sqrt(max(R*R-z*z,0))*np.cos(z)) if f is fe
                      else (z*np.cos(z)+np.sqrt(max(R*R-z*z,0))*np.sin(z)), xs[i],xs[i+1])
            eps=hbar**2*xi*xi/(2*m*a*a)       # energy above well bottom
            es.append(eps-V0)
    return sorted(es)
we=well_eigs(-V0w,ww)
print('finite well analytic    :',np.round(we[:4],4))

# Tunneling: exact T vs barrier width (theory curve) + note FD verification skipped;
# instead compute exact T for widths and also WKB approx comparison
E=3.0; V0=10.0; ws=np.linspace(0.5,6,30)
T=[T_exact(E,V0,w) for w in ws]
Twkb=[np.exp(-2*np.sqrt(2*m*(V0-E))/hbar*w) for w in ws]
plt.figure(figsize=(7,4));plt.semilogy(ws,T,label='exact');plt.semilogy(ws,Twkb,'--',label='WKB ~ exp(-2 kappa w)')
plt.xlabel('barrier width w');plt.ylabel('T');plt.legend();plt.grid(alpha=.3)
plt.title('Tunneling vs barrier width (E=3, V0=10)');plt.tight_layout()
plt.savefig('plots/schrod_tunneling.png',dpi=110)
print('T(w=1)=%.3e  T(w=4)=%.3e'%(T_exact(E,V0,1),T_exact(E,V0,4)))
np.savetxt('data/schrod_tunneling.csv',np.c_[ws,T,Twkb],header='w,T_exact,T_wkb',delimiter=',')
plt.close('all');print('DONE schrodinger')
