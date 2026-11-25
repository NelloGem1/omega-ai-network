# Replicate eval_strong pgd-AT weak stage ONLY, fresh RNG (seed 0) - variance probe.
import torch, torch.nn as nn, torch.nn.functional as F
import torchvision, torchvision.transforms as T
import numpy as np, json
torch.set_num_threads(2); torch.manual_seed(0); np.random.seed(0)
DEV='cpu'; EPS=0.3; BS=128; TRAIN_N=20000; TEST_N=3000
tr=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
dtr=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=True,download=False,transform=tr)
dte=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=False,download=False,transform=tr)
idx=np.random.RandomState(1).permutation(len(dtr))[:TRAIN_N]
tr_loader=torch.utils.data.DataLoader(torch.utils.data.Subset(dtr,idx),batch_size=BS,shuffle=True)
te=torch.utils.data.DataLoader(torch.utils.data.Subset(dte,np.arange(TEST_N)),batch_size=512)
Xte=torch.cat([b[0] for b in te]); yte=torch.cat([b[1] for b in te])
class MLP(nn.Module):
    def __init__(s):
        super().__init__(); s.net=nn.Sequential(nn.Flatten(),nn.Linear(784,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU(),nn.Linear(128,10))
    def forward(s,x): return s.net(x)
def acc(model,X,y,bs=512):
    model.eval(); c=t=0
    with torch.no_grad():
        for i in range(0,len(X),bs):
            c+=(model(X[i:i+bs]).argmax(1)==y[i:i+bs]).sum().item(); t+=len(y[i:i+bs])
    return c/t
def fgsm(model,X,y,eps=EPS,bs=512):
    model.eval(); out=[]
    for i in range(0,len(X),bs):
        Xp=X[i:i+bs].clone().requires_grad_(True)
        g=torch.autograd.grad(F.cross_entropy(model(Xp),y[i:i+bs]),Xp)[0]
        out.append((Xp.detach()+eps*g.sign()).clamp(X[i:i+bs]-eps,X[i:i+bs]+eps))
    return torch.cat(out)
def pgd(model,X,y,eps=EPS,alpha=0.05,steps=30,bs=256):
    model.eval(); out=[]
    for i in range(0,len(X),bs):
        Xc=X[i:i+bs]; Xp=Xc+torch.empty_like(Xc).uniform_(-eps,eps); Xp=Xp.clamp(Xc-eps,Xc+eps)
        for _ in range(steps):
            Xp.requires_grad_(True)
            g=torch.autograd.grad(F.cross_entropy(model(Xp),y[i:i+bs]),Xp)[0]
            Xp=(Xp.detach()+alpha*g.sign()).clamp(Xc-eps,Xc+eps)
        out.append(Xp.detach())
    return torch.cat(out)
m=MLP(); opt=torch.optim.Adam(m.parameters(),lr=1e-3)
for ep in range(3):
    m.train()
    for x,y in tr_loader:
        xa=x.clone().detach()+torch.empty_like(x).uniform_(-EPS,EPS); xa=xa.clamp(x-EPS,x+EPS)
        for _ in range(10):
            xa.requires_grad_(True)
            g=torch.autograd.grad(F.cross_entropy(m(xa),y),xa)[0]
            xa=(xa.detach()+0.01*g.sign()).clamp(x-EPS,x+EPS)
        xa=xa.detach()
        opt.zero_grad(); loss=F.cross_entropy(m(xa),y); loss.backward(); opt.step()
r={'clean':acc(m,Xte,yte),'fgsm':acc(m,fgsm(m,Xte,yte),yte),
   'pgd30s':acc(m,pgd(m,Xte,yte,alpha=0.05,steps=30),yte)}
print('pgd_at_weak_seed0',r,flush=True)
