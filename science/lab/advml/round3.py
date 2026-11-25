import torch, torch.nn as nn, torch.nn.functional as F
import torchvision, torchvision.transforms as T
import numpy as np, json
torch.manual_seed(0); np.random.seed(0)
DEV='cpu'; EPS=0.3; BS=128; TRAIN_N=20000; TEST_N=3000
tr=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
ts=tr
dtr=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=True,download=True,transform=tr)
dte=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=False,download=True,transform=ts)
idx=np.random.RandomState(1).permutation(len(dtr))[:TRAIN_N]
tr_loader=torch.utils.data.DataLoader(torch.utils.data.Subset(dtr,idx),batch_size=BS,shuffle=True)
te=torch.utils.data.DataLoader(torch.utils.data.Subset(dte,np.arange(TEST_N)),batch_size=256)
Xte=torch.cat([b[0] for b in te]); yte=torch.cat([b[1] for b in te])
class MLP(nn.Module):
    def __init__(s):
        super().__init__(); s.net=nn.Sequential(nn.Flatten(),nn.Linear(784,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU(),nn.Linear(128,10))
    def forward(s,x): return s.net(x)
def acc(m,X,y):
    m.eval()
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()
def fgsm(m,X,y,eps=EPS):
    m.eval(); Xp=X.clone().requires_grad_(True)
    g=torch.autograd.grad(F.cross_entropy(m(Xp),y),Xp)[0]
    return (Xp+eps*g.sign()).detach()
def pgd(m,X,y,eps=EPS,alpha=0.05,steps=30):
    m.eval(); X=X.clone().detach()
    Xp=(X+torch.empty_like(X).uniform_(-eps,eps)).clamp(X-eps,X+eps)
    for _ in range(steps):
        Xp.requires_grad_(True)
        g=torch.autograd.grad(F.cross_entropy(m(Xp),y),Xp)[0]
        Xp=(Xp.detach()+alpha*g.sign()).clamp(X-eps,X+eps)
    return Xp.detach()
# PGD-AT with STRONG inner attack: alpha=0.03, steps=20, 4 epochs
m=MLP().to(DEV); opt=torch.optim.Adam(m.parameters(),lr=1e-3)
EPS_IN,AL_IN,ST_IN=0.3,0.03,20
for ep in range(4):
    m.train()
    for x,y in tr_loader:
        x,y=x.to(DEV),y.to(DEV)
        xa=(x+torch.empty_like(x).uniform_(-EPS_IN,EPS_IN)).clamp(x-EPS_IN,x+EPS_IN)
        for _ in range(ST_IN):
            xa.requires_grad_(True)
            g=torch.autograd.grad(F.cross_entropy(m(xa),y),xa)[0]
            xa=(xa.detach()+AL_IN*g.sign()).clamp(x-EPS_IN,x+EPS_IN)
        xa=xa.detach()
        opt.zero_grad(); loss=F.cross_entropy(m(xa),y); loss.backward(); opt.step()
    with torch.no_grad():
        print('ep',ep,'train_adv_acc',acc(m,xa,y),flush=True)
res={'clean':acc(m,Xte,yte),
     'fgsm':acc(m,fgsm(m,Xte,yte),yte),
     'pgd10':acc(m,pgd(m,Xte,yte,alpha=0.01,steps=10),yte),
     'pgd30s':acc(m,pgd(m,Xte,yte,alpha=0.05,steps=30),yte)}
print('pgdAT_strong',res)
json.dump(res,open('/home/neilh/science_lab/advml/results3.json','w'))
