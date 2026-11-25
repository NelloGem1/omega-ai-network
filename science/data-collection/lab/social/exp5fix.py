import networkx as nx, numpy as np, json
rng=np.random.default_rng(3)
G=nx.barabasi_albert_graph(5000,3,seed=3)
deg=np.array([d for _,d in G.degree()])
# proper power-law fit k>=kmin
for kmin in [3,5,10,20]:
    ks,cts=np.unique(deg[deg>=kmin],return_counts=True)
    coef=np.polyfit(np.log(ks),np.log(cts/5000),1)
    print("kmin",kmin,"exponent",round(-coef[0],2))
order_deg=sorted(G.nodes(),key=lambda x:-G.degree(x))
order_rand=list(G.nodes()); rng.shuffle(order_rand)
def frag(order):
    H=G.copy(); fr=[]
    for k,node in enumerate(order,1):
        if node not in H: continue
        H.remove_node(node)
        if k%100==0:
            comps=sorted((len(c) for c in nx.connected_components(H)),reverse=True)
            fr.append([k,round(comps[0]/5000,3)])
        if k>=1200: break
    return fr
ft=frag(order_deg); fr=frag(order_rand)
print("targeted:",ft)
print("random:",fr)
json.dump({"attack_targeted":ft,"attack_random":fr},open("/home/neilh/science_lab/social/exp5fix.json","w"))
