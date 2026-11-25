# AUTOPSY verification: staged, checkpointed re-run of advml attack/defense matrix.
# Writes autopsy_verify.json incrementally after every stage.
import torch, torch.nn as nn, torch.nn.functional as F
import torchvision, torchvision.transforms as T
import numpy as np, json, os, time
torch.set_num_threads(2)
torch.manual_seed(0); np.random.seed(0)
DEV='cpu'; EPS=0.3; BS=128
TRAIN_N=20000; TEST_N=3000
OUT='/home/neilh/science_lab/advml/autopsy_verify.json'
res=json.load(open(OUT)) if os.path.exists(OUT) else {}
def save(): json.dump(res,open(OUT,'w'),indent=2)
def log(*a): print(*a,flush=True)

tr=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
dtr=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=True,download=False,transform=tr)
dte=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=False,download=False,transform=tr)
idx=np.random.RandomState(1).permutation(len(dtr))[:TRAIN_N]
tr_loader=torch.utils.data.DataLoader(torch.utils.data.Subset(dtr,idx),batch_size=BS,shuffle=True)
te=torch.utils.data.DataLoader(torch.utils.data.Subset(dte,np.arange(TEST_N)),batch_size=512)
Xte=torch.cat([b[0] for b in te]); yte=torch.cat([b[1] for b in te])
log('data',Xte.shape)

class MLP(nn.Module):
    def __init__(s):
        super().__init__()
        s.net=nn.Sequential(nn.Flatten(),nn.Linear(784,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU(),nn.Linear(128,10))
    def forward(s,x): return s.net(x)

def acc(model,X,y,pre=None,bs=512):
    model.eval(); tot=0; cor=0
    with torch.no_grad():
        for i in range(0,len(X),bs):
            Xi=X[i:i+bs]; yi=y[i:i+bs]
            if pre: Xi=pre(Xi)
            cor+=(model(Xi).argmax(1)==yi).sum().item(); tot+=len(yi)
    return cor/tot

def fgsm(model,X,y,eps=EPS,pre=None,bs=512):
    # chunked FGSM; returns perturbed X (pre-preprocess space)
    model.eval(); out=[]
    for i in range(0,len(X),bs):
        Xp=X[i:i+bs].clone().requires_grad_(True); yi=y[i:i+bs]
        inp=pre(Xp) if pre else Xp
        loss=F.cross_entropy(model(inp),yi)
        g=torch.autograd.grad(loss,Xp)[0]
        out.append((Xp.detach()+eps*g.sign()).clamp(X[i:i+bs]-eps,X[i:i+bs]+eps))
    return torch.cat(out)

def pgd(model,X,y,eps=EPS,alpha=0.05,steps=30,pre=None,bs=256):
    model.eval(); out=[]
    for i in range(0,len(X),bs):
        Xc=X[i:i+bs]; yi=y[i:i+bs]
        Xp=Xc+torch.empty_like(Xc).uniform_(-eps,eps); Xp=Xp.clamp(Xc-eps,Xc+eps)
        for _ in range(steps):
            Xp.requires_grad_(True)
            inp=pre(Xp) if pre else Xp
            loss=F.cross_entropy(model(inp),yi)
            g=torch.autograd.grad(loss,Xp)[0]
            Xp=(Xp.detach()+alpha*g.sign()).clamp(Xc-eps,Xc+eps)
        out.append(Xp.detach())
    return torch.cat(out)

def bitdepth(x,bits=3):
    lo,hi=-3.0,3.0; q=2**bits-1
    xc=x.clamp(lo,hi); xq=torch.round((xc-lo)/(hi-lo)*q)/q*(hi-lo)+lo
    return x+(xq-x).detach()

def smooth(x):
    z=x.reshape(-1,1,28,28)
    z=F.avg_pool2d(z,3,stride=1,padding=1)
    z=F.interpolate(z,size=(28,28),mode='bilinear',align_corners=False)
    return z.reshape(x.shape)

def train(model, loader, epochs, at=None, at_eps=EPS, at_alpha=0.01, at_steps=10):
    opt=torch.optim.Adam(model.parameters(),lr=1e-3)
    for ep in range(epochs):
        model.train()
        for x,y in loader:
            x,y=x.to(DEV),y.to(DEV)
            if at is None:
                opt.zero_grad(); loss=F.cross_entropy(model(x),y); loss.backward(); opt.step()
            else:
                xa=x.clone().detach()+torch.empty_like(x).uniform_(-at_eps,at_eps)
                xa=xa.clamp(x-at_eps,x+at_eps)
                for _ in range(at_steps):
                    xa.requires_grad_(True)
                    loss=F.cross_entropy(model(xa),y)
                    g=torch.autograd.grad(loss,xa)[0]
                    xa=(xa.detach()+at_alpha*g.sign()).clamp(x-at_eps,x+at_eps)
                xa=xa.detach()
                opt.zero_grad(); loss=F.cross_entropy(model(xa),y); loss.backward(); opt.step()

def evaluate(tag,m,pre=None):
    r={'clean':acc(m,Xte,yte,pre)}
    if pre is not None:
        r['fgsm_naive']=acc(m,fgsm(m,Xte,yte),yte,pre)
    r['fgsm']=acc(m,fgsm(m,Xte,yte,pre=pre),yte,pre)
    r['pgd10']=acc(m,pgd(m,Xte,yte,alpha=0.01,steps=10,pre=pre),yte,pre)
    r['pgd30s']=acc(m,pgd(m,Xte,yte,alpha=0.05,steps=30,pre=pre),yte,pre)
    res[tag]=r; save(); print(tag,r,flush=True)

# STAGE 0: PGD sign sanity on RANDOM weights — attack must REDUCE accuracy / raise loss
log('STAGE0 sign check')
mr=MLP(); mr.eval()
with torch.no_grad():
    c0=(mr(Xte[:512]).argmax(1)==yte[:512]).float().mean().item()
Xp=pgd(mr,Xte[:512],yte[:512],alpha=0.05,steps=10)
with torch.no_grad():
    c1=(mr(Xp).argmax(1)==yte[:512]).float().mean().item()
    l0=F.cross_entropy(mr(Xte[:512]),yte[:512]).item()
    l1=F.cross_entropy(mr(Xp),yte[:512]).item()
res['sign_check']={'clean_acc':c0,'pgd_acc':c1,'clean_loss':l0,'pgd_loss':l1}
save(); log('sign_check',res['sign_check'])

# STAGE 1: baseline
log('STAGE1 baseline'); m=MLP(); train(m,tr_loader,4)
torch.save(m.state_dict(),'/home/neilh/science_lab/advml/autopsy_models/baseline.pt')
evaluate('baseline',m)

# STAGE 2: preprocessing defenses on baseline
log('STAGE2 preproc')
evaluate('baseline+bitdepth3',m,bitdepth)
evaluate('baseline+smooth3',m,smooth)

# STAGE 3: FGSM-AT
log('STAGE3 fgsm-AT'); mf=MLP(); train(mf,tr_loader,4,at='fgsm')
torch.save(mf.state_dict(),'/home/neilh/science_lab/advml/autopsy_models/fgsm_at.pt')
evaluate('fgsm_at',mf)

# STAGE 4: PGD-AT weak inner (alpha .01, 10 steps), 3 epochs
log('STAGE4 pgd-AT weak'); mp=MLP(); train(mp,tr_loader,3,at='pgd')
torch.save(mp.state_dict(),'/home/neilh/science_lab/advml/autopsy_models/pgd_at_weak.pt')
evaluate('pgd_at_weak',mp)

# STAGE 5: PGD-AT strong inner (alpha .03, 20 steps), 4 epochs (round3)
log('STAGE5 pgd-AT strong')
ms=MLP(); train(ms,tr_loader,4,at='pgd',at_alpha=0.03,at_steps=20)
torch.save(ms.state_dict(),'/home/neilh/science_lab/advml/autopsy_models/pgd_at_strong.pt')
evaluate('pgd_at_strong',ms)

log('ALL DONE')
