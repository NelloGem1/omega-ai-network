import networkx as nx, numpy as np, json
rng=np.random.default_rng(11)

def metrics(G,name):
    if not nx.is_connected(G): G=G.subgraph(max(nx.connected_components(G),key=len)).copy()
    deg=[d for _,d in G.degree()]
    cc=nx.average_clustering(G)
    asp=nx.average_shortest_path_length(G)
    print(f"{name:12s} n={G.number_of_nodes():5d} m={G.number_of_edges():7d} avgdeg={np.mean(deg):.2f} "
          f"maxdeg={max(deg):4d} clust={cc:.3f} ASP={asp:.2f} diam={nx.diameter(G)}")
    return {"n":G.number_of_nodes(),"m":G.number_of_edges(),"avg_deg":float(np.mean(deg)),
            "max_deg":int(max(deg)),"clustering":float(cc),"asp":float(asp),"diameter":int(nx.diameter(G))}

n=1000
G_er=nx.erdos_renyi_graph(n,6/n,seed=1)
G_ws=nx.watts_strogatz_graph(n,6,0.1,seed=1)
G_ba=nx.barabasi_albert_graph(n,3,seed=1)
res={}
for G,name in [(G_er,"ER"),(G_ws,"WS"),(G_ba,"BA")]:
    res[name]=metrics(G,name)
deg=np.array([d for _,d in G_ba.degree()])
cnt=np.bincount(deg); ks=np.arange(len(cnt)); mask=(ks>0)&(cnt>0)
coef=np.polyfit(np.log(ks[mask]),np.log(cnt[mask]/n),1)
print("BA power-law exponent ~",round(-coef[0],2))
res["BA"]["pl_exponent"]=float(-coef[0])

print("--- six degrees (ASP vs log n) ---")
for model in ["ba","er"]:
    row=[]
    for nn in [100,300,1000,3000]:
        G=(nx.barabasi_albert_graph(nn,3,seed=2) if model=="ba" else nx.erdos_renyi_graph(nn,6/nn,seed=2))
        if not nx.is_connected(G): G=G.subgraph(max(nx.connected_components(G),key=len)).copy()
        asp=nx.average_shortest_path_length(G)
        row.append([nn,round(asp,2),round(asp/np.log(nn),2)])
        print(model,nn,"ASP",round(asp,2),"ASP/logn",round(asp/np.log(nn),2))
    res["six_"+model]=row

G=nx.barabasi_albert_graph(5000,3,seed=3)
order_deg=sorted(G.nodes(),key=lambda x:-G.degree(x))
order_rand=list(G.nodes()); rng.shuffle(order_rand)
def frag(order,steps=12):
    H=G.copy(); fr=[]
    step=max(1,len(order)//steps)
    for k,node in enumerate(order,1):
        H.remove_node(node)
        if k%step==0:
            comps=sorted((len(c) for c in nx.connected_components(H)),reverse=True)
            fr.append([k,round(comps[0]/5000,3) if comps else 0])
        if k>800: break
    return fr
ft=frag(order_deg); fr=frag(order_rand)
print("targeted attack (remove highest degree): k removed -> largest comp fraction")
for k,f in ft: print("  ",k,f)
print("random attack:")
for k,f in fr: print("  ",k,f)
res["attack"]={"targeted":ft,"random":fr}

def deffuant(G,eps,n=300,mu=0.5,iters=3000,stubborn=None):
    nodes=list(G.nodes())[:n]
    sub=G.subgraph(nodes)
    x=rng.uniform(0,1,len(nodes))
    idx={v:i for i,v in enumerate(nodes)}
    edges=[(idx[u],idx[v]) for u,v in sub.edges()]
    fixed={}
    if stubborn:
        for v,val in stubborn.items():
            if v in idx: fixed[idx[v]]=val; x[idx[v]]=val
    for it in range(iters):
        order=rng.permutation(len(edges))
        for ei in order:
            i,j=edges[ei]
            if abs(x[i]-x[j])<eps:
                m=(x[i]+x[j])/2
                if i not in fixed: x[i]+=mu*(m-x[i])
                if j not in fixed: x[j]+=mu*(m-x[j])
    return x

def count_clusters(x,gap):
    xs=np.sort(x); return int(len(np.where(np.diff(xs)>gap)[0])+1)

Gw=nx.watts_strogatz_graph(300,8,0.1,seed=5)
print("--- Deffuant: clusters vs tolerance epsilon ---")
eps_sweep={}
for eps in [0.1,0.2,0.3,0.4,0.5]:
    x=deffuant(Gw,eps)
    cl=count_clusters(x,eps)
    hist,_=np.histogram(x,bins=50,range=(0,1))
    eps_sweep[str(eps)]={"clusters_gap":cl,"nonempty_bins":int((hist>0).sum()),
                         "xrange":[round(float(x.min()),2),round(float(x.max()),2)]}
    print("eps",eps,"clusters",cl,"bins",int((hist>0).sum()),"range",round(float(x.min()),2),round(float(x.max()),2))
res["deffuant"]=eps_sweep

stub={0:0.0,1:1.0,2:0.0,3:1.0}
xpol=deffuant(Gw,0.5,stubborn=stub)
xbase=deffuant(Gw,0.5)
res["deffuant"]["stubborn"]={"clusters_with_stub":count_clusters(xpol,0.2),
                             "clusters_baseline":count_clusters(xbase,0.2),
                             "mean_abs_dev_stub":float(np.mean(np.abs(xpol-0.5))),
                             "mean_abs_dev_base":float(np.mean(np.abs(xbase-0.5)))}
print("stubborn eps=0.5: clusters",count_clusters(xpol,0.2),"vs baseline",count_clusters(xbase,0.2))

print("--- signaling: cheap talk pure NE enumeration ---")
msgs=["G","B"]; acts=["I","N"]
def act_map(rG,rB): return {"G":rG,"B":rB}
def evI(msg,sG,sB):
    tot=0;w=0
    for st in ["G","B"]:
        m=sG if st=="G" else sB
        if m==msg:
            tot+=(2 if st=="G" else -1); w+=1
    return tot/w if w else None
nes=[]
for sG in msgs:
    for sB in msgs:
        for rG in acts:
            for rB in acts:
                am=act_map(rG,rB); ok=True
                for msg,r in [("G",rG),("B",rB)]:
                    e=evI(msg,sG,sB)
                    if e is None: continue
                    best="I" if e>0 else "N"   # N payoff 0; I EV e
                    if abs(e)<1e-9: best="I"  # indifferent: allow either
                    if r!=best: ok=False
                if not ok: continue
                pay={"G":1.0 if am["G"]=="I" else 0.0,"B":1.0 if am["B"]=="I" else 0.0}
                bg=max(pay.values())
                if pay[sG]<bg-1e-9 or pay[sB]<bg-1e-9: ok=False
                if ok: nes.append([sG,sB,rG,rB])
print("NEs (sGmsg,sBmsg,rGact,rBact):",nes)
res["signaling"]={"cheap_talk_NE":nes,
  "note":"babbling: both types send same msg; receiver learns nothing, invests iff EV>=0"}

json.dump(res,open("/home/neilh/science_lab/social/exp567_results.json","w"),indent=1)
print("DONE")
