import Mathlib

open Nat

/-!
# More verified theorems

Each theorem is checked by Lean's kernel — `∀` means it holds
for infinitely many cases with a single proof.
-/

/-- n ≤ 2^n for all naturals. Classic induction. -/
theorem nat_le_two_pow (n : Nat) : n ≤ 2 ^ n := by
  induction n with
  | zero => simp
  | succ k ih =>
      have h2k : 0 < 2 ^ k := pow_pos (by norm_num) k
      have hexp : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      rw [hexp]
      omega

/-- Factorials outgrow exponentials: 2^n ≤ (n+1)!. -/
theorem two_pow_le_factorial (n : Nat) : 2 ^ n ≤ (n + 1) ! := by
  induction n with
  | zero => simp
  | succ k ih =>
      have h2 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      have hfac : ((k + 1) + 1) ! = (k + 1 + 1) * (k + 1) ! :=
        Nat.factorial_succ (k + 1)
      have hB : 0 < (k + 1) ! := Nat.factorial_pos _
      rw [h2, hfac]
      calc 2 * 2 ^ k ≤ 2 * (k + 1) ! := by gcongr
        _ ≤ (k + 1 + 1) * (k + 1) ! := by gcongr; omega

/-- Euclid's theorem — already machine-checked inside Mathlib.
    We just *reuse* the verified result. -/
theorem infinite_primes : Set.Infinite {p : Nat | Nat.Prime p} :=
  Nat.infinite_setOf_prime

#print axioms nat_le_two_pow
#print axioms two_pow_le_factorial
#print axioms infinite_primes
