#!/usr/bin/env python3
"""
NelloGem DIFFUSION LAB — minimal DDPM on MNIST (CPU-friendly).
Mission: prove diffusion works — noise → digits.

Usage:
  python ddpm_mnist.py --smoke      # 60s proof-of-life
  python ddpm_mnist.py --epochs 3   # real toy training
  python ddpm_mnist.py --sample     # generate from saved checkpoint
"""
import argparse, math, os, sys, time
import torch, torch.nn as nn, torch.nn.functional as F
import torchvision, torchvision.transforms as T
from torchvision.utils import save_image

DEV = "cpu"  # WSL fleet — CPU lane (Colab T4 for the big version)
ROOT = "/home/neilh/science_lab/diffusion"
CKPT = os.path.join(ROOT, "ddpm.pt")

def get_data(subset=None):
    tf = T.Compose([T.ToTensor(), T.Normalize((0.5,), (0.5,))])
    ds = torchvision.datasets.MNIST("/home/neilh/data", train=True,
                                     download=True, transform=tf)
    if subset:
        ds = torch.utils.data.Subset(ds, range(subset))
    return torch.utils.data.DataLoader(ds, batch_size=64, shuffle=True,
                                       num_workers=0, drop_last=True)

# ---------------- tiny time-conditioned U-Net ----------------
class TinyUNet(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.ch = ch
        self.temb = nn.Sequential(nn.Linear(1, ch*4), nn.SiLU(), nn.Linear(ch*4, ch*4))
        self.e1 = nn.Conv2d(1, ch, 3, padding=1)
        self.d1 = nn.Conv2d(ch, ch*2, 3, 2, padding=1)   # 14
        self.d2 = nn.Conv2d(ch*2, ch*4, 3, 2, padding=1) # 7
        self.mid = nn.Conv2d(ch*4, ch*4, 3, padding=1)
        self.u1 = nn.ConvTranspose2d(ch*4, ch*2, 2, 2)   # 14
        self.u2 = nn.ConvTranspose2d(ch*2, ch, 2, 2)     # 28
        self.out = nn.Conv2d(ch, 1, 3, padding=1)

    def forward(self, x, t):
        B = x.shape[0]
        te = self.temb(t.view(B,1).float()/1000.0)
        temb_lo = te[:, :self.ch].view(B,self.ch,1,1)     # 32ch for early layers
        temb_hi = te.view(B,self.ch*4,1,1)           # 128ch for bottleneck
        a = F.silu(self.e1(x) + temb_lo)                    # 28 ch
        b = F.silu(self.d1(a))                           # 14 ch*2
        c = F.silu(self.d2(b))                           # 7 ch*4
        c = F.silu(self.mid(c) + temb_hi)
        u = F.silu(self.u1(c) + b)                      # skip: 14x14 ch*2
        u = F.silu(self.u2(u) + a)                      # skip: 28x28 ch
        return self.out(u)

# ---------------- diffusion schedule ----------------
T_STEPS = 200
def betas():
    return torch.linspace(1e-4, 0.02, T_STEPS)
BETA = betas()
ALPHA = 1 - BETA
ABAR = torch.cumprod(ALPHA, 0)

def q_sample(x0, t, noise):
    a = ABAR[t].view(-1,1,1,1)
    return a.sqrt()*x0 + (1-a).sqrt()*noise

def p_sample(model, x, t):
    with torch.no_grad():
        eps = model(x, t)
        b = BETA[t].view(-1,1,1,1)
        a = ALPHA[t].view(-1,1,1,1)
        ab = ABAR[t].view(-1,1,1,1)
        mean = (x - b/(1-ab).sqrt()*eps) / a.sqrt()
        if t[0] > 0:
            noise = torch.randn_like(x)
            at   = ABAR[t]                    # (n,)
            ap   = ABAR[t-1]                  # (n,)
            bt   = BETA[t]                    # (n,)
            var = ((1-ap)/(1-at)*bt).clamp_min(0).view(-1,1,1,1)
            x = mean + var.sqrt()*noise
        else:
            x = mean
    return x

# ---------------- train ----------------
def train(epochs, subset, smoke=False):
    ld = get_data(subset)
    model = TinyUNet().to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3)
    step = 0
    t0 = time.time()
    for ep in range(epochs):
        model.train(); tot = 0; nb = 0
        for x, _ in ld:
            x = x.to(DEV)
            t = torch.randint(0, T_STEPS, (x.shape[0],), device=DEV)
            eps = torch.randn_like(x)
            xt = q_sample(x, t, eps)
            pred = model(xt, t)
            loss = F.mse_loss(pred, eps)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item(); nb += 1; step += 1
            if smoke and step >= 40: break
        print(f"ep{ep}: loss={tot/nb:.4f} ({time.time()-t0:.0f}s)", flush=True)
        if smoke and step >= 40: break
    torch.save(model.state_dict(), CKPT)
    print(f"saved → {CKPT}")
    sample(model, 16)

# ---------------- sample ----------------
def sample(model, n=16):
    model.eval()
    x = torch.randn(n,1,28,28)
    for t in reversed(range(T_STEPS)):
        tt = torch.full((n,), t, dtype=torch.long)
        x = p_sample(model, x, tt)
        if t % 50 == 0: print(f"  denoise t={t}", flush=True)
    x = (x.clamp(-1,1)+1)/2
    os.makedirs(ROOT, exist_ok=True)
    save_image(x, os.path.join(ROOT, "samples.png"), nrow=4)
    print(f"samples → {ROOT}/samples.png")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--subset", type=int, default=None)
    ap.add_argument("--sample", action="store_true")
    a = ap.parse_args()

    if a.sample:
        m = TinyUNet()
        if os.path.exists(CKPT):
            m.load_state_dict(torch.load(CKPT, map_location=DEV))
            sample(m, 16)
        else:
            print("no checkpoint — train first")
        return
    train(epochs=1 if a.smoke else a.epochs,
          subset=a.subset or (2000 if a.smoke else None),
          smoke=a.smoke)

if __name__ == "__main__":
    main()
