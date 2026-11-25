import Mathlib

open Finset BigOperators

/-!
# The Last-Digit Law — Neilbert's theorem, formally verified

Claim discovered via the 0–9 digit table: every prime > 5 ends in 1, 3, 7, or 9.
This is a REAL theorem — a necessary condition for primality.
-/

/-- Every prime greater than 5 has last digit in {1,3,7,9}.
    Proof: last digit even ⟹ divisible by 2; last digit 5 ⟹ divisible by 5.
    Only residues coprime to 10 survive. -/
theorem prime_gt_five_last_digit (p : ℕ) (hp : p.Prime) (h5 : 5 < p) :
    p % 10 = 1 ∨ p % 10 = 3 ∨ p % 10 = 7 ∨ p % 10 = 9 := by
  -- p is odd (prime > 2)
  have h2 : p % 2 = 1 := Nat.odd_iff.mp (hp.odd_of_ne_two (by omega))
  -- 5 ∤ p (p prime, p > 5)
  have h5dvd : ¬ 5 ∣ p := by
    intro h
    have he := (Nat.prime_dvd_prime_iff_eq (by norm_num : Nat.Prime 5) hp).mp h
    omega
  have h5m : p % 5 ≠ 0 := by
    intro hm
    exact h5dvd (Nat.dvd_iff_mod_eq_zero.mpr hm)
  omega

/-- Equivalent formulation: the last digit is coprime to 10. -/
theorem prime_gt_five_last_digit_coprime (p : ℕ) (hp : p.Prime) (h5 : 5 < p) :
    Nat.Coprime (p % 10) 10 := by
  rcases prime_gt_five_last_digit p hp h5 with h | h | h | h <;> rw [h] <;> decide

-- Sanity check the theorem against all primes ≤ 200 by computation
example : ∀ p ∈ (Finset.range 201).filter Nat.Prime,
    5 < p → p % 10 = 1 ∨ p % 10 = 3 ∨ p % 10 = 7 ∨ p % 10 = 9 := by
  native_decide

#print axioms prime_gt_five_last_digit
