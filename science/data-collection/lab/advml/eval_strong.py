# Round 2: strong PGD (alpha=0.05, steps=30, eps=0.3) eval of all defenses.
# Retrains models identically (same seeds) then evaluates spec-PGD(10,0.01) AND strong-PGD.
import torch, torch.nn as nn, torch.nn.functional as F
import torchvision, torchvision.transforms as T
import numpy as np, json, time

torch.manual_seed(0); np.random.seed(0)
DEV='cpu'; EPS=0.3; BS=128
TRAIN_N=20000; TEST_N=3000; EPOCHS=4; AT_EPOCHS=3

tr=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
ts=T.Compose([T.ToTensor(), T.Lambda(lambda x:(x-0.1307)/0.3081)])
dtr=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=True,download=True,transform=tr)
dte=torchvision.datasets.MNIST('/home/neilh/science_lab/advml/data',train=False,download=True,transform=ts)
idx=np.random.RandomState(1).permutation(len(dtr))[:TRAIN_N]
tr_loader=torch.utils.data.DataLoader(torch.utils.data.Subset(dtr,idx),batch_size=BS,shuffle=True)
te=torch.utils.data.DataLoader(torch.utils.data.Subset(dte,np.arange(TEST_N)),batch_size=256)
Xte=torch.cat([b[0] for b in te]); yte=torch.cat([b[1] for b in te])

class MLP(nn.Module):
    def __init__(s):
        super().__init__()
        s.net=nn.Sequential(nn.Flatten(),nn.Linear(784,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU(),nn.Linear(128,10))
    def forward(s,x): return s.net(x)

def train(model, loader, epochs, at=None):
    opt=torch.optim.Adam(model.parameters(),lr=1e-3)
    for ep in range(epochs):
        model.train()
        for x,y in loader:
            x,y=x.to(DEV),y.to(DEV)
            if at is None:
                opt.zero_grad(); loss=F.cross_entropy(model(x),y); loss.backward(); opt.step()
            else:
                xa=x.clone().detach()+torch.empty_like(x).uniform_(-EPS,EPS)
                xa=xa.clamp(x-EPS,x+EPS)
                steps=1 if at=='fgsm' else 10
                alpha=EPS if at=='fgsm' else 0.01
                for _ in range(steps):
                    xa.requires_grad_(True)
                    loss=F.cross_entropy(model(xa),y)
                    g=torch.autograd.grad(loss,xa)[0]
                    xa=(xa.detach()+alpha*g.sign()).clamp(x-EPS,x+EPS)
                xa=xa.detach()
                opt.zero_grad(); loss=F.cross_entropy(model(xa),y); loss.backward(); opt.step()

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

def pgd(model,X,y,eps=EPS,alpha=0.01,steps=10,pre=None):
    model.eval(); X=X.clone().detach()
    Xp=X+torch.empty_like(X).uniform_(-eps,eps); Xp=Xp.clamp(X-eps,X+eps)
    for _ in range(steps):
        Xp.requires_grad_(True)
        inp=pre(Xp) if pre else Xp
        loss=F.cross_entropy(model(inp),y)
        g=torch.autograd.grad(loss,Xp)[0]
        Xp=(Xp.detach()+alpha*g.sign()).clamp(X-eps,X+eps)
    return Xp.detach()

def bitdepth(x,bits=3):
    lo,hi=-3.0,3.0; q=2**bits-1
    xc=x.clamp(lo,hi); xq=torch.round((xc-lo)/(hi-lo)*q)/q*(hi-lo)+lo
    return x+(xq-x).detach()

def smooth(x):
    z=x.reshape(-1,1,28,28)
    z=F.avg_pool2d(z,3,stride=1,padding=1)
    z=F.interpolate(z,size=(28,28),mode='bilinear',align_corners=False)
    return z.reshape(x.shape)

res={}
def evaluate(tag,m,pre=None):
    c=acc(m,Xte,yte,pre)
    Xf=fgsm(m,Xte,yte); fa=acc(m,Xf,yte,pre)
    Xp1=Xte.clone().requires_grad_(True)
    loss=F.cross_entropy(m(pre(Xp1)) if pre else m(Xp1),yte)
    g=torch.autograd.grad(loss,Xp1)[0]
    Xa=(Xp1.detach()+EPS*g.sign())
    fa2=acc(m,Xa,yte,pre)
    p10=pgd(m,Xte,yte,alpha=0.01,steps=10,pre=pre); pa10=acc(m,p10,yte,pre)
    pS=pgd(m,Xte,yte,alpha=0.05,steps=30,pre=pre); paS=acc(m,pS,yte,pre)
    res[tag]={'clean':c,'fgsm':fa,'fgsm_adaptive':fa2,'pgd10':pa10,'pgd30s':paS}
    print(tag,res[tag],flush=True)

print('TRAIN baseline'); m=MLP().to(DEV); train(m,tr_loader,EPOCHS); evaluate('baseline',m)
print('TRAIN fgsm-AT'); mf=MLP().to(DEV); train(mf,tr_loader,EPOCHS,at='fgsm'); evaluate('fgsm_at',mf)
print('TRAIN pgd-AT'); mp=MLP().to(DEV); train(mp,tr_loader,AT_EPOCHS,at='pgd'); evaluate('pgd_at',mp)
evaluate('baseline+bitdepth3',m,bitdepth)
evaluate('baseline+smooth3',m,smooth)
json.dump(res,open('/home/neilh/science_lab/advml/results2.json','w'),indent=2)
print('DONE')
