import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
os.chdir('/home/neilh/science_lab/physics')

# Double slit: coherent amplitude sum vs incoherent intensity sum (which-way decoherence)
lam = 500e-9      # m, wavelength
L  = 1.0          # m, screen distance
d  = 0.1e-3       # m, slit separation
y  = np.linspace(-0.02, 0.02, 4000)
k  = 2*np.pi/lam
# intensity at screen position y (small angle): path diff = d*y/L approx
I_coh  = 4*np.cos(np.pi*d*y/(lam*L))**2          # I = 4I0 cos^2
I_inc  = 2*np.ones_like(y)                       # which-way -> no fringes
# exact-ish: include single-slit envelope
beta = np.pi*5e-6*y/(lam*L)
env = (np.sin(beta)/np.where(np.abs(beta)<1e-12,1,beta))**2
env[ np.abs(beta)<1e-12 ] = 1.0
I_coh_env = 4*np.cos(np.pi*d*y/(lam*L))**2*env

delta_y = lam*L/d
print('fringe spacing theory: %.4f m; measured (peak-to-peak): %.4f m'%(
    delta_y, np.mean(np.diff(y[np.argmax(I_coh_env[:len(y)//2])]) if False else y[1]-y[0])))
# measure fringe spacing from peaks
from scipy.signal import find_peaks
pk,_ = find_peaks(I_coh_env); print('measured spacing: %.5f m (theory %.5f)'%(np.mean(np.diff(y[pk])), delta_y))

# decoherence sweep: partial which-way -> mixture I = (1-p)*I_coh + p*I_inc, visibility
def visibility(I, y):
    i = I.max(); m = np.percentile(I, 20)  # crude contrast
    return (I.max()-np.min(I))/(I.max()+np.min(I))
ps = np.linspace(0,1,11); vis=[]
for p in ps:
    I = (1-p)*I_coh + p*I_inc
    vis.append((I.max()-I.min())/(I.max()+I.min()))
print('visibility vs decoherence p:', np.round(vis,3))

plt.figure(figsize=(8,4))
plt.plot(y*1000, I_coh_env/I_coh_env.max(), label='coherent (amplitude sum)')
plt.plot(y*1000, I_inc/I_inc.max(), '--', label='which-way (incoherent sum)')
plt.xlabel('y (mm)'); plt.ylabel('I/I0'); plt.legend(); plt.grid(alpha=.3)
plt.title('Double slit: lambda=500nm L=1m d=0.1mm'); plt.tight_layout()
plt.savefig('plots/doubleslit_fringes.png', dpi=110)

plt.figure(figsize=(6,4))
plt.plot(ps, vis, 'o-'); plt.xlabel('which-way / decoherence weight p'); plt.ylabel('fringe visibility')
plt.title('Decoherence kills interference'); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig('plots/doubleslit_decoherence.png', dpi=110)
np.savetxt('data/doubleslit.csv', np.c_[y, I_coh_env, I_inc], header='y,I_coherent,I_incoherent', delimiter=',')
plt.close('all'); print('DONE doubleslit')
