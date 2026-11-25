import torch, torch.nn as nn, torch.nn.functional as F
import torchvision, torchvision.transforms as T
import numpy as np, json, time, os

torch.manual_seed(0); np.random.seed(0)
DEV='cpu'
EPS=0.3; ALPHA=0.01; PGD_STEPS=10
TRAIN_N=20000; TEST_N=3000; EPOCHS=4; AT_EPOCHS=3; BS=128

# ---------- data ----------
tr=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
ts=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
dtr=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=True,download=True,transform=tr)
dte=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=False,download=True,transform=ts)
# normalize back to [0,1] domain is awkward; instead keep raw tensors and normalize inside model? 
# Simpler: keep normalized inputs; attacks operate in normalized space with same eps (approx).
idx=np.random.RandomState(1).permutation(len(dtr))[:TRAIN_N]
tr_loader=torch.utils.data.DataLoader(torch.utils.data.Subset(dtr,idx),batch_size=BS,shuffle=True)
te=torch.utils.data.DataLoader(torch.utils.data.Subset(dte,np.arange(TEST_N)),batch_size=256)
Xte=torch.cat([b[0] for b in te]); yte=torch.cat([b[1] for b in te])
print('data ready',Xte.shape)

class MLP(nn.Module):
    def __init__(s):
        super().__init__()
        s.net=nn.Sequential(nn.Flatten(),nn.Linear(784,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU(),nn.Linear(128,10))
    def forward(s,x): return s.net(x)

def train(model, loader, epochs, at=None, at_eps=EPS, at_alpha=ALPHA, at_steps=PGD_STEPS):
    opt=torch.optim.Adam(model.parameters(),lr=1e-3)
    for ep in range(epochs):
        model.train(); tot=cor=0; t0=time.time()
        for x,y in loader:
            x,y=x.to(DEV),y.to(DEV)
            if at is None:
                opt.zero_grad(); loss=F.cross_entropy(model(x),y); loss.backward(); opt.step()
            else:
                # adversarial training: replace batch with adv examples (FGSM or PGD)
                xa=x.clone().detach().requires_grad_(True)
                if at=='fgsm':
                    loss=F.cross_entropy(model(xa),y); g=torch.autograd.grad(loss,xa)[0]
                    xa=(xa+at_eps*g.sign()).detach()
                else: # pgd
                    xa=x.clone().detach()+torch.empty_like(x).uniform_(-at_eps,at_eps)
                    xa=xa.clamp(-1e9,1e9)
                    for _ in range(at_steps):
                        xa.requires_grad_(True)
                        loss=F.cross_entropy(model(xa),y)
                        g=torch.autograd.grad(loss,xa)[0]
                        xa=(xa.detach()+at_alpha*g.sign()).clamp(x-at_eps,x+at_eps)
                    xa=xa.detach()
                opt.zero_grad(); loss=F.cross_entropy(model(xa),y); loss.backward(); opt.step()
            with torch.no_grad():
                pred=model(x).argmax(1); cor+=(pred==y).sum().item(); tot+=len(y)
        print(f'  ep{ep} train_acc={cor/tot:.4f} ({time.time()-t0:.0f}s)')

def acc(model,X,y,pre=None):
    model.eval()
    with torch.no_grad():
        Xi=pre(X) if pre else X
        return (model(Xi).argmax(1)==y).float().mean().item()

def fgsm(model,X,y,eps=EPS):
    model.eval(); Xp=X.clone().requires_grad_(True)
    loss=F.cross_entropy(model(Xp),y)
    g=torch.autograd.grad(loss,Xp)[0]
    return (Xp+eps*g.sign()).detach()

def pgd(model,X,y,eps=EPS,alpha=ALPHA,steps=PGD_STEPS,pre=None):
    # adaptive: attacker optimizes through preprocessing (pre may be None)
    model.eval()
    X=X.clone().detach()
    Xp=X+torch.empty_like(X).uniform_(-eps,eps)
    Xp=Xp.clamp(X-eps,X+eps)
    for _ in range(steps):
        Xp.requires_grad_(True)
        inp=pre(Xp) if pre else Xp
        loss=F.cross_entropy(model(inp),y)
        g=torch.autograd.grad(loss,Xp)[0]
        Xp=(Xp.detach()+alpha*g.sign()).clamp(X-eps,X+eps)
    return Xp.detach()

def pgd_acc(model,X,y,pre=None):
    Xp=pgd(model,X,y,pre=pre)
    return acc(model,Xp,y,pre)

# ---------- preprocessing defenses ----------
def bitdepth(x,bits=3):
    # STE: forward quantize to [0,1]-ish range of normalized input is tricky; inputs normalized.
    # Quantize per-sample min/max? Use fixed grid on normalized range [-3,3] approx via clamp.
    lo,hi=-3.0,3.0
    q=2**bits-1
    xc=x.clamp(lo,hi)
    xq=torch.round((xc-lo)/(hi-lo)*q)/q*(hi-lo)+lo
    return x + (xq-x).detach()  # STE

def smooth(x):
    # avg-pool 3x3 then bilinear back to 28x28 (JPEG-ish)
    z=x.reshape(-1,1,28,28)
    z=F.avg_pool2d(z,3,stride=1,padding=1)
    z=F.interpolate(z,size=(28,28),mode='bilinear',align_corners=False)
    return z.reshape(x.shape)

results={}
# 1) baseline
t0=time.time(); m=MLP().to(DEV)
print('TRAIN baseline'); train(m,tr_loader,EPOCHS)
clean=acc(m,Xte,yte)
# attacks on raw normalized inputs; clamp to valid-ish range [-5,5] handled implicitly by eps
Xf=fgsm(m,Xte,yte)
f_acc=acc(m,Xf,yte)
Xp=pgd(m,Xte,yte)
p_acc=acc(m,Xp,yte)
results['baseline']={'clean':clean,'fgsm':f_acc,'pgd':p_acc}
print(f'baseline clean={clean:.4f} fgsm={f_acc:.4f} pgd={p_acc:.4f}')

# 2a) FGSM-adversarial training
print('TRAIN fgsm-AT'); m_fg=MLP().to(DEV)
train(m_fg,tr_loader,EPOCHS,at='fgsm')
c=acc(m_fg,Xte,yte); f=acc(m_fg,fgsm(m_fg,Xte,yte),yte); p=pgd_acc(m_fg,Xte,yte)
results['fgsm_at']={'clean':c,'fgsm':f,'pgd':p}
print(f'fgsm-AT clean={c:.4f} fgsm={f:.4f} pgd={p:.4f}')

# 2b) PGD-adversarial training (shorter: 2 epochs to save CPU)
print('TRAIN pgd-AT'); m_pg=MLP().to(DEV)
train(m_pg,tr_loader,AT_EPOCHS,at='pgd')
c=acc(m_pg,Xte,yte); f=acc(m_pg,fgsm(m_pg,Xte,yte),yte); p=pgd_acc(m_pg,Xte,yte)
results['pgd_at']={'clean':c,'fgsm':f,'pgd':p}
print(f'pgd-AT clean={c:.4f} fgsm={f:.4f} pgd={p:.4f}')

# 2c) preprocessing defenses on the BASELINE model (adaptive attacks through preprocess)
for name,pre in [('bitdepth3',bitdepth),('smooth3',smooth)]:
    c=acc(m,Xte,yte,pre)
    # fgsm through pre: approximate via pgd 1 step? use fgsm on raw then eval through pre
    Xf2=fgsm(m,Xte,yte)  # non-adaptive baseline
    f_naive=acc(m,Xf2,yte,pre)
    # adaptive fgsm: gradient through pre, 1 step
    Xp1=Xte.clone().requires_grad_(True)
    loss=F.cross_entropy(m(pre(Xp1)),yte)
    g=torch.autograd.grad(loss,Xp1)[0]
    Xf2a=(Xp1+EPS*g.sign()).detach()
    f_ad=acc(m,Xf2a,yte,pre)
    p_ad=pgd_acc(m,Xte,yte,pre)
    results[name]={'clean':c,'fgsm_naive':f_naive,'fgsm_adaptive':f_ad,'pgd_adaptive':p_ad}
    print(f'{name} clean={c:.4f} fgsm_naive={f_naive:.4f} fgsm_ad={f_ad:.4f} pgd_ad={p_ad:.4f}')

json.dump(results,open('/home/neilh/science_lab/advml/results.json','w'),indent=2)
print('DONE',time.time()-t0,'s total')
