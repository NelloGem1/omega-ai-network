import argparse, json, time, os, random
import torch, torch.nn as nn, torch.nn.functional as F
import torchvision
import timm
from torch.utils.data import DataLoader

ROOT = '/home/neilh/science_lab/vit'
DATA = ROOT + '/data'
torch.manual_seed(0)

def set_seed(s):
    random.seed(s); torch.manual_seed(s)

def load_dataset(name, split):
    if name == 'fashion':
        ds = torchvision.datasets.FashionMNIST(DATA, train=(split=='train'), download=True)
    else:
        ds = torchvision.datasets.CIFAR10(DATA, train=(split=='train'), download=True)
    arr = ds.data
    if hasattr(arr, 'numpy'):
        arr = arr.numpy()
    xs = torch.from_numpy(arr).float()
    if xs.ndim == 4:  # H,W,C (CIFAR)
        xs = xs.permute(0,3,1,2)
    else:            # H,W (MNIST)
        xs = xs.unsqueeze(1)
    xs = xs/255.0
    ys = torch.tensor(list(ds.targets) if not torch.is_tensor(ds.targets) else ds.targets)
    return xs, ys

def prep(x, kind, img_size):
    # x: B,C,H,W in [0,1] -> model input
    if kind == 'vit':
        if x.shape[-1] != img_size:
            x = F.interpolate(x, size=(img_size,img_size), mode='bilinear', align_corners=False)
        if x.shape[1] == 1:
            x = x.repeat(1,3,1,1)
    x = (x - 0.5) / 0.5
    if kind == 'mlp':
        x = x.flatten(1)
    return x

def build_model(kind, img_size, in_shape, num_classes=10):
    if kind == 'mlp':
        flat = in_shape[0]*in_shape[1]*in_shape[2]
        m = nn.Sequential(
            nn.Linear(flat,512), nn.ReLU(),
            nn.Linear(512,256), nn.ReLU(),
            nn.Linear(256,num_classes))
        return m
    if kind == 'cnn':
        cin = in_shape[0]
        class CNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(cin,32,3,padding=1), nn.BatchNorm2d(32), nn.ReLU(),
                    nn.Conv2d(32,64,3,padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Conv2d(64,128,3,padding=1), nn.BatchNorm2d(128), nn.ReLU(),
                    nn.AdaptiveAvgPool2d(1))
                self.fc = nn.Linear(128,num_classes)
            def forward(self,x):
                return self.fc(self.features(x).flatten(1))
        return CNN()
    if kind == 'vit':
        return timm.create_model('vit_tiny_patch16_224', img_size=img_size, num_classes=num_classes, pretrained=False)
    if kind == 'vit_small':
        return timm.create_model('vit_small_patch16_224', img_size=img_size, num_classes=num_classes, pretrained=False)
    raise ValueError(kind)

def kind_of(model_name):
    return 'vit' if model_name.startswith('vit') else model_name

def get_loader(xs, ys, idxs, batch, shuffle, workers=0):
    class DS(torch.utils.data.Dataset):
        def __len__(self): return len(idxs)
        def __getitem__(self,i):
            j = int(idxs[i])
            return xs[j], ys[j]
    return DataLoader(DS(), batch_size=batch, shuffle=shuffle, num_workers=workers)

def run_train(args):
    set_seed(args.seed)
    xs_tr, ys_tr = load_dataset(args.dataset,'train')
    xs_te, ys_te = load_dataset(args.dataset,'test')
    g = torch.Generator().manual_seed(args.seed)
    perm_tr = torch.randperm(len(xs_tr), generator=g)[:args.ntrain]
    perm_te = torch.randperm(len(xs_te), generator=g)[:args.ntest]
    in_shape = tuple(xs_tr[0].shape)
    model = build_model(args.model, args.img_size, in_shape, num_classes=args.num_classes)
    nparams = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.05)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    lossf = nn.CrossEntropyLoss()
    tr_loader = get_loader(xs_tr, ys_tr, perm_tr, args.batch, True)
    model.train()
    ep_times=[]
    t0=time.time()
    kind = kind_of(args.model)
    for ep in range(args.epochs):
        te=time.time(); tot=0; corr=0
        for x,y in tr_loader:
            xp = prep(x, kind, args.img_size)
            out = model(xp)
            loss = lossf(out,y)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()*len(y); corr += (out.argmax(1)==y).sum().item()
        sched.step(); ep_times.append(time.time()-te)
        print(f'[{args.tag}] epoch {ep+1}/{args.epochs} loss={tot/len(perm_tr):.4f} acc={corr/len(perm_tr):.4f} t={ep_times[-1]:.1f}s', flush=True)
        os.makedirs(os.path.join(ROOT,'results',args.tag), exist_ok=True)
        torch.save(model.state_dict(), os.path.join(ROOT,'results',args.tag,'last.pt'))
    train_time = time.time()-t0
    model.eval()
    te_loader = get_loader(xs_te, ys_te, perm_te, 128, False)
    corr=0; n=0
    with torch.no_grad():
        for x,y in te_loader:
            xp = prep(x, kind, args.img_size)
            corr += (model(xp).argmax(1)==y).sum().item(); n += len(y)
    clean_acc = corr/n
    t=time.time(); n=0
    with torch.no_grad():
        for x,y in te_loader:
            xp = prep(x, kind, args.img_size)
            model(xp); n += len(y)
    infer_s = time.time()-t
    metrics = dict(tag=args.tag, model=args.model, dataset=args.dataset, img_size=args.img_size,
                   ntrain=int(len(perm_tr)), ntest=int(len(perm_te)), epochs=args.epochs, batch=args.batch,
                   lr=args.lr, seed=args.seed, params=int(nparams),
                   clean_acc=float(clean_acc), train_time_s=float(train_time),
                   epoch_times_s=[float(t) for t in ep_times],
                   infer_time_s=float(infer_s), infer_ms_per_img=float(infer_s/n*1000),
                   in_shape=[int(v) for v in in_shape], num_classes=args.num_classes)
    outdir = os.path.join(ROOT,'results',args.tag); os.makedirs(outdir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(outdir,'model.pt'))
    with open(os.path.join(outdir,'metrics.json'),'w') as f: json.dump(metrics,f,indent=2)
    print('SAVED', json.dumps(metrics), flush=True)

def run_attack(args):
    resdir = os.path.join(ROOT,'results',args.tag)
    with open(os.path.join(resdir,'metrics.json')) as f: met = json.load(f)
    xs_te, ys_te = load_dataset(met['dataset'],'test')
    g = torch.Generator().manual_seed(met['seed'])
    perm_te = torch.randperm(len(xs_te), generator=g)[:args.n]
    model = build_model(met['model'], met['img_size'], tuple(met['in_shape']), num_classes=met['num_classes'])
    model.load_state_dict(torch.load(os.path.join(resdir,'model.pt'), map_location='cpu'))
    model.eval()
    kind = kind_of(met['model'])
    loader = get_loader(xs_te, ys_te, perm_te, 64, False)
    eps = args.eps
    clean_corr=adv_corr=n=0
    lossf = nn.CrossEntropyLoss()
    for x,y in loader:
        x = x.clone().requires_grad_(True)
        xp = prep(x, kind, met['img_size'])
        out = model(xp)
        loss = lossf(out,y)
        loss.backward()
        x_adv = (x + eps*torch.sign(x.grad)).clamp(0,1).detach()
        with torch.no_grad():
            clean_corr += (model(prep(x.detach(),kind,met['img_size'])).argmax(1)==y).sum().item()
            adv_corr += (model(prep(x_adv,kind,met['img_size'])).argmax(1)==y).sum().item()
        n += len(y)
    res = dict(tag=met['tag'], model=met['model'], dataset=met['dataset'], eps=eps, n=n,
               clean_acc=clean_corr/n, adv_acc=adv_corr/n, drop=clean_corr/n-adv_corr/n)
    with open(os.path.join(resdir,'attack.json'),'w') as f: json.dump(res,f,indent=2)
    print('ATTACK', json.dumps(res), flush=True)

if __name__=='__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    pt = sub.add_parser('train')
    pt.add_argument('--tag',required=True); pt.add_argument('--model',required=True)
    pt.add_argument('--dataset',default='fashion'); pt.add_argument('--img-size',type=int,default=112)
    pt.add_argument('--ntrain',type=int,default=8000); pt.add_argument('--ntest',type=int,default=2000)
    pt.add_argument('--epochs',type=int,default=3); pt.add_argument('--batch',type=int,default=128)
    pt.add_argument('--lr',type=float,default=1e-3); pt.add_argument('--seed',type=int,default=0)
    pt.add_argument('--num-classes',type=int,default=10)
    pa = sub.add_parser('attack')
    pa.add_argument('--tag',required=True); pa.add_argument('--eps',type=float,default=0.3)
    pa.add_argument('--n',type=int,default=1000)
    args = p.parse_args()
    if args.cmd=='train': run_train(args)
    else: run_attack(args)
