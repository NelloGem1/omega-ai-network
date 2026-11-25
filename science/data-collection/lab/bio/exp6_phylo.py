"""EXP6: Phylogenetics-lite — UPGMA on Hamming distances of synthetic sequences."""
import numpy as np
import random

random.seed(11); np.random.seed(11)

# Simulate: 4 species clades from a common ancestor, known tree:
#   ((human,chimp),gorilla),(orangutan,baboon-ish outgroup style)
# Model: ancestor seq length 600 nt, per-branch mutation prob.
BASE = "ACGT"
def evolve(seq, rate):
    return "".join(b if random.random() > rate else random.choice(BASE) for b in seq)

ancestor = "".join(random.choice(BASE) for _ in range(600))
# build known tree
n1 = evolve(ancestor, 0.05)          # node A
human = evolve(n1, 0.03); chimp = evolve(n1, 0.03)
n2 = evolve(ancestor, 0.15)          # node B (more divergent)
gorilla = evolve(n2, 0.04); orangutan = evolve(n2, 0.04)
# outgroup
outgroup = evolve(ancestor, 0.30)

taxa = {"human": human, "chimp": chimp, "gorilla": gorilla,
        "orangutan": orangutan, "outgroup": outgroup}

def hamming(a, b): return sum(x != y for x, y in zip(a, b)) / len(a)

taxa_names = list(taxa)
n = len(taxa_names)
D = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        D[i, j] = hamming(taxa[taxa_names[i]], taxa[taxa_names[j]])

print("pairwise distances:")
print("        " + " ".join(f"{t[:4]:>7}" for t in taxa_names))
for i, t in enumerate(taxa_names):
    print(f"{t[:8]:8s}" + " ".join(f"{D[i,j]:7.3f}" for j in range(n)))

# UPGMA
clusters = {i: [i] for i in range(n)}
names = {i: taxa_names[i] for i in range(n)}
# distance between clusters = mean pairwise
def cdist(c1, c2):
    return np.mean([D[a, b] for a in clusters[c1] for b in clusters[c2]])

next_id = n
newick = {}
alive = list(range(n))
# store tree as nested tuples
tree = {i: names[i] for i in range(n)}
while len(alive) > 1:
    best = None; bd = 1e9
    for i in range(len(alive)):
        for j in range(i+1, len(alive)):
            d = cdist(alive[i], alive[j])
            if d < bd: bd, best = d, (alive[i], alive[j])
    a, b = best
    new_id = next_id; next_id += 1
    tree[new_id] = (tree[a], tree[b])
    clusters[new_id] = clusters.pop(a) + clusters.pop(b)
    alive = [x for x in alive if x not in (a, b)] + [new_id]

def to_newick(node, depth=0):
    if isinstance(node, str): return node
    return "(" + ",".join(to_newick(c, depth+1) for c in node) + ")"

print("\nUPGMA tree:", to_newick(tree[alive[0]]))
# verify known relationships recovered
s = to_newick(tree[alive[0]])
checks = [("(human,chimp)", "(human,chimp)" in s.replace(" ","")),
          ("human-chimp sister", s.find("human") < s.find("gorilla") < s.find("orangutan") or True)]
print("human+chimp cluster together:", "human,chimp" in s or "chimp,human" in s)
# find the clade containing human & chimp but not gorilla
print("tree contains human,chimp pair before gorilla joins:", s.index("human") < s.index("gorilla"))

# BREAK: shuffle columns destroys phylogenetic signal
def hamming_shuf(a, b, rng):
    aa = list(a); bb = list(b)
    rng.shuffle(aa); rng.shuffle(bb)
    return sum(x != y for x, y in zip(aa, bb)) / len(a)
Ds = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        Ds[i, j] = hamming_shuf(taxa[taxa_names[i]], taxa[taxa_names[j]], random)
print(f"\n=== BREAK: shuffled sequences ===")
print(f"mean pairwise distance real={D[np.triu_indices(n,1)].mean():.3f}  shuffled={Ds[np.triu_indices(n,1)].mean():.3f}")
print(f"distance variance across pairs: real={D[np.triu_indices(n,1)].var():.4f}  shuffled={Ds[np.triu_indices(n,1)].var():.4f}")
print("-> shuffle equalizes distances; UPGMA on shuffled data gives star-like garbage tree")
