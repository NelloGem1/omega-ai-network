# CORRECTIONS — EXP2 DNA stats (post-autopsy fix)

**Bug:** `exp2_dna.py` L38-41 built `probs` as a list in "ACGT" order but
indexed it with `"TCAG".index(c)` when computing expected codon frequencies.
The index maps T->0(A's freq), A->1(C's), C->2(G's), G->3(T's) — a permutation.
The codon-bias chi-square was therefore computed against a **wrong null
distribution**, invalidating its p-value.

**Fix:** `exp2_dna_fixed.py` — per-base probability dict `pbase` keyed by base
identity; everything else identical. Output: `exp2_dna_fixed.log` (script
prints only; no data artifact). Original untouched.

## Old vs new (NM_000207.3 insulin mRNA, 465 nt)

| quantity | old (buggy null) | new (fixed null) |
|---|---|---|
| codon chi-square | 183.2 | **85.2** |
| codon p-value | 6.67e-19 | **1.92e-4** |
| dinucleotide chi2 / p | 73.7 / 9.63e-10 | unchanged (not affected) |
| GC%, windowed-GC std, shuffle break test | — | unchanged |

Verified independently: recomputed expected codon counts as
p(b1)*p(b2)*p(b3) from scratch -> identical chi2=85.2226, p=1.9237e-4.
Conclusion direction unchanged (codon bias still significant) but the
effect size was inflated ~2.2x by the permuted null.
