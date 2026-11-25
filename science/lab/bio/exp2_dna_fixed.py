"""EXP2 FIXED: DNA sequence statistics — fetch human insulin CDS + synthetic control.
Fix: codon expected frequencies now use per-base probabilities keyed by base
identity (was indexing a list built in 'ACGT' order with 'TCAG' positions ->
permuted base probs -> invalid chi-square p-value)."""
import urllib.request, io, random
import numpy as np
from scipy.stats import chisquare
from Bio import SeqIO
from Bio.Seq import Seq

url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
       "db=nuccore&id=NM_000207.3&rettype=fasta_cds_aa&retmode=text")
url_dna = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
           "db=nuccore&id=NM_000207.3&rettype=fasta&retmode=text")
seq = "".join(l.strip() for l in urllib.request.urlopen(url_dna, timeout=20)
              .read().decode().splitlines() if not l.startswith(">"))
seq = seq.upper()
print(f"fetched NM_000207.3 length = {len(seq)} nt")
print(f"header check: first 60nt {seq[:60]}")

rng = np.random.default_rng(42)
counts = {b: seq.count(b) for b in "ACGT"}
total = sum(counts.values())
probs = [counts[b] / total for b in "ACGT"]          # list, order A,C,G,T (for rng.choice)
pbase = {b: counts[b] / total for b in "ACGT"}       # FIX: dict keyed by base identity
synth = "".join(rng.choice(list("ACGT"), size=len(seq), p=probs))

def gc(s): return 100 * (s.count("G") + s.count("C")) / len(s)
print(f"\nGC content: real={gc(seq):.2f}%  synthetic(iid)={gc(synth):.2f}%")

codons = [seq[i:i+3] for i in range(0, len(seq) - len(seq) % 3, 3)]
from collections import Counter
cc = Counter(codons)
print(f"\nTop 10 codons in insulin CDS: {cc.most_common(10)}")
# expected under base-freq independence — FIX: use pbase[c] not probs['TCAG'.index(c)]
codon_exp = {}
for c1 in "TCAG":
    for c2 in "TCAG":
        for c3 in "TCAG":
            codon_exp[c1+c2+c3] = pbase[c1]*pbase[c2]*pbase[c3]
n_cod = len(codons)
exp_counts = np.array([codon_exp.get(c, 0) * n_cod for c in cc])
obs = np.array([cc[c] for c in cc])
mask = exp_counts > 0.5
e2 = exp_counts[mask]; e2 = e2/e2.sum()*obs[mask].sum()
chi2, p = chisquare(obs[mask], e2)
print(f"chi-square codon bias vs iid: chi2={chi2:.1f}, df={mask.sum()-1}, p={p:.3g}")

di = Counter(seq[i:i+2] for i in range(len(seq) - 1))
bp = [seq.count(b) / len(seq) for b in "ACGT"]
exp_di = {}
for a in "ACGT":
    for b in "ACGT":
        exp_di[a+b] = bp["ACGT".index(a)] * bp["ACGT".index(b)] * (len(seq) - 1)
keys = sorted(di)
o = np.array([di[k] for k in keys])
e = np.array([exp_di[k] for k in keys])
chi2d, pd_ = chisquare(o, e)
print(f"\ndinucleotide chi-square: chi2={chi2d:.1f}, df={len(keys)-1}, p={pd_:.3g}")
ratio = sorted(((di[k]/exp_di[k], k) for k in keys), reverse=True)
print("over-represented:", [(k, round(r,2)) for r,k in ratio[:4]])
print("under-represented:", [(k, round(r,2)) for r,k in ratio[-4:]])

kmers = Counter(seq[i:i+4] for i in range(len(seq) - 3))
print(f"\n4-mer spectrum: {len(kmers)} distinct, top5={kmers.most_common(5)}")

shuffled = list(seq)
rng.shuffle(shuffled)
shuffled = "".join(shuffled)
print(f"\n=== BREAK TEST ===")
print(f"GC after shuffle: {gc(shuffled):.2f}% (unchanged: {abs(gc(shuffled)-gc(seq))<0.01})")
di_s = Counter(shuffled[i:i+2] for i in range(len(shuffled) - 1))
o_s = np.array([di_s[k] for k in keys])
chi2s, ps = chisquare(o_s, e)
print(f"dinucleotide chi2 after shuffle: {chi2s:.1f}, p={ps:.3g} (was p={pd_:.3g})")
w = 100
gc_real = [gc(seq[i:i+w]) for i in range(0, len(seq)-w, w)]
gc_shuf = [gc(shuffled[i:i+w]) for i in range(0, len(shuffled)-w, w)]
print(f"windowed-GC std: real={np.std(gc_real):.2f}  shuffled={np.std(gc_shuf):.2f}")
print("-> shuffle kills dinucleotide signal & local GC heterogeneity; GC% survives")
