"""EXP3: Protein analysis — fetch real proteins (insulin, lysozyme) + synthetic TM test."""
import urllib.request
import numpy as np
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio.Seq import Seq

def fetch_uniprot(acc):
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.fasta"
    txt = urllib.request.urlopen(url, timeout=20).read().decode()
    return "".join(l.strip() for l in txt.splitlines() if not l.startswith(">"))

# Real proteins: insulin (P01308, 110 aa incl signal peptide removed -> B chain etc.)
insulin = fetch_uniprot("P01308")
lysozyme = fetch_uniprot("P00698")  # hen egg lysozyme, 129 aa
print(f"insulin len={len(insulin)}  lysozyme len={len(lysozyme)}")

def analyze(name, seq):
    pa = ProteinAnalysis(Seq(seq))
    mw = pa.molecular_weight()
    charge7 = pa.charge_at_pH(7.0)
    hyd = pa.hydrophobicity_profile  # Kyte-Doolittle-ish via ProtParam
    # ProtParam.hydrophobicity_profile uses a sliding window; here it's per-residue? use Bio.SeqUtils.ProtParam
    instab = pa.instability_index()
    print(f"\n=== {name} ===")
    print(f"MW={mw:.1f} Da  charge@pH7={charge7:+.2f}  instability={instab:.1f} ({'stable' if instab<40 else 'unstable'})")
    print(f"amino-acid composition top5: {pa.count_amino_acids()}")
    return pa

pa_i = analyze("human insulin (P01308)", insulin)
pa_l = analyze("hen lysozyme (P00698)", lysozyme)

# --- Hydrophobicity profile via Kyte-Doolittle window 9 ---
KD = {
 'A':1.8,'C':2.5,'D':-3.5,'E':-3.5,'F':2.8,'G':-0.4,'H':-3.2,'I':4.5,
 'K':-3.9,'L':3.8,'M':1.9,'N':-3.5,'P':-1.6,'Q':-3.5,'R':-4.5,'S':-0.8,
 'T':-0.7,'V':4.2,'W':-0.9,'Y':-1.3}
def kd_profile(seq, w=9):
    vals = [KD.get(a, 0) for a in seq]
    prof = []
    for i in range(len(vals) - w + 1):
        prof.append(sum(vals[i:i+w]) / w)
    return np.array(prof)

for name, seq in [("insulin", insulin), ("lysozyme", lysozyme)]:
    prof = kd_profile(seq)
    print(f"\n{name}: hydrophobicity window mean={prof.mean():.2f} min={prof.min():.2f} max={prof.max():.2f}")
    # crude TM prediction: contiguous windows with mean > 1.6 (KD scale) of length>=15
    tm = []
    run = 0
    for v in prof:
        if v > 1.6: run += 1
        else:
            if run >= 15: tm.append(run*9)
            run = 0
    print(f"  candidate TM helices (KD>1.6, >=15 res): {tm}")

# --- BREAK: shuffle destroys hydrophobic clustering ---
rng = np.random.default_rng(0)
seq_list = list(lysozyme)
rng.shuffle(seq_list)
shuf = "".join(seq_list)
pa_s = analyze("SHUFFLED lysozyme", shuf)
prof_s = kd_profile(shuf)
prof_r = kd_profile(lysozyme)
# signal = autocorrelation of hydrophobicity at lag 1..10
def autocorr(p, lag):
    return np.corrcoef(p[:-lag], p[lag:])[0,1]
print("\n=== BREAK: hydrophobicity autocorrelation ===")
for lag in [1,3,5,10]:
    print(f"lag {lag}: real={autocorr(prof_r,lag):+.3f}  shuffled={autocorr(prof_s,lag):+.3f}")
