import json, os, glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT='/home/neilh/science_lab/vit'
res=os.path.join(ROOT,'results')
rows=[]
for d in sorted(glob.glob(os.path.join(res,'*'))):
    mj=os.path.join(d,'metrics.json')
    if not os.path.exists(mj): continue
    m=json.load(open(mj)); m['dir']=os.path.basename(d)
    aj=os.path.join(d,'attack.json')
    if os.path.exists(aj):
        a=json.load(open(aj)); m['adv_acc']=a['adv_acc']; m['adv_drop']=a['drop']
    rows.append(m)

# bar chart: clean acc vs adv acc, log inference time
fig,axs=plt.subplots(1,3,figsize=(15,4.5))
tags=[r['tag'] for r in rows]
accs=[r['clean_acc'] for r in rows]
axs[0].bar(tags,accs,color='steelblue'); axs[0].set_title('Clean test accuracy'); axs[0].set_ylim(0,1)
for i,v in enumerate(accs): axs[0].text(i,v+0.01,f'{v:.2f}',ha='center',fontsize=8)
axs[0].tick_params(axis='x',rotation=30)

adv=[r.get('adv_acc') for r in rows]
axs[1].bar(tags,[a if a is not None else 0 for a in adv],color='salmon')
axs[1].set_title('FGSM eps=0.3 adversarial accuracy'); axs[1].set_ylim(0,1)
for i,(a,r) in enumerate(zip(adv,rows)):
    if a is not None: axs[1].text(i,a+0.01,f'{a:.2f}',ha='center',fontsize=8)
axs[1].tick_params(axis='x',rotation=30)

tt=[r['train_time_s']/60 for r in rows]
it=[r['infer_ms_per_img'] for r in rows]
axs[2].bar(tags,tt,color='seagreen'); axs[2].set_title('Train time (min)'); axs[2].tick_params(axis='x',rotation=30)
ax2=axs[2].twinx(); ax2.plot(tags,it,'o-',color='darkorange'); ax2.set_ylabel('infer ms/img (log)',color='darkorange')
ax2.set_yscale('log')
plt.tight_layout(); plt.savefig(os.path.join(ROOT,'results_summary.png'),dpi=120)

# accuracy vs train time scatter
fig,ax=plt.subplots(figsize=(7,5))
for r in rows:
    ax.scatter(r['train_time_s']/60, r['clean_acc'], s=80)
    ax.annotate(r['tag'],(r['train_time_s']/60, r['clean_acc']),fontsize=8)
ax.set_xlabel('train time (min)'); ax.set_ylabel('clean acc'); ax.set_title('Accuracy vs training time')
plt.tight_layout(); plt.savefig(os.path.join(ROOT,'acc_vs_time.png'),dpi=120)
print('plots done for', len(rows), 'runs')
