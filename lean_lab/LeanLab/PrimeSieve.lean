import Mathlib

open Finset BigOperators

/-!
# The Prime Sieve — deeper than last digits

Level up from `prime_gt_five_last_digit`: primes > 5 must avoid
divisors 2, 3, AND 5 — leaving only 8 residue classes mod 30.
This is the actual sieve pattern. Plus: Euclid's proof, OUR version.
-/

section Sieve

variable {p : ℕ}

/-- Prime > 5 is not divisible by 2. -/
theorem not_dvd_two (hp : p.Prime) (h5 : 5 < p) : ¬ 2 ∣ p := by
  intro h
  have he := (Nat.prime_dvd_prime_iff_eq (by norm_num : Nat.Prime 2) hp).mp h
  omega

/-- Prime > 5 is not divisible by 3. -/
theorem not_dvd_three (hp : p.Prime) (h5 : 5 < p) : ¬ 3 ∣ p := by
  intro h
  have he := (Nat.prime_dvd_prime_iff_eq (by norm_num : Nat.Prime 3) hp).mp h
  omega

/-- Prime > 5 is not divisible by 5. -/
theorem not_dvd_five (hp : p.Prime) (h5 : 5 < p) : ¬ 5 ∣ p := by
  intro h
  have he := (Nat.prime_dvd_prime_iff_eq (by norm_num : Nat.Prime 5) hp).mp h
  omega

/-- **The Sieve Theorem**: every prime > 5 lands in one of only
    8 residue classes mod 30: {1,7,11,13,17,19,23,29}.
    That's the real lattice primes live on — 73% of numbers excluded. -/
theorem prime_mod30 (hp : p.Prime) (h5 : 5 < p) :
    p % 30 = 1 ∨ p % 30 = 7 ∨ p % 30 = 11 ∨ p % 30 = 13 ∨
    p % 30 = 17 ∨ p % 30 = 19 ∨ p % 30 = 23 ∨ p % 30 = 29 := by
  have h2 : p % 2 = 1 := Nat.odd_iff.mp (hp.odd_of_ne_two (by omega))
  have h3m : p % 3 ≠ 0 := by
    intro hm; exact not_dvd_three hp h5 (Nat.dvd_iff_mod_eq_zero.mpr hm)
  have h5m : p % 5 ≠ 0 := by
    intro hm; exact not_dvd_five hp h5 (Nat.dvd_iff_mod_eq_zero.mpr hm)
  generalize hgen : p % 30 = m
  have hm30 : m < 30 := by
    have := Nat.mod_lt p (show 0 < 30 by norm_num)
    rwa [hgen] at this
  interval_cases m <;> omega

end Sieve

/-! ## Euclid's theorem — proved by us, not imported -/

/-- Given any finite set of primes, there is a prime outside it.
    Proof: N = (product of the set) + 1 has a prime factor q;
    q can't divide the product, so q isn't in the set. -/
theorem exists_prime_not_mem (s : Finset ℕ) (hs : ∀ p ∈ s, p.Prime) :
    ∃ q, q.Prime ∧ q ∉ s := by
  classical
  set P := s.prod id with hP
  have hprod : 1 ≤ P := by
    rw [hP]
    have hpos : 0 < s.prod id := Finset.prod_pos (fun x hx => (hs x hx).pos)
    omega
  obtain ⟨q, hqP, hqN⟩ := Nat.exists_prime_and_dvd (n := P + 1) (by omega)
  refine ⟨q, hqP, ?_⟩
  intro hqs
  have hqprod : q ∣ P := by
    rw [hP]
    exact Finset.dvd_prod_of_mem (f := id) hqs
  have hsub : q ∣ P + 1 - P := Nat.dvd_sub hqN hqprod
  have hdiff : P + 1 - P = 1 := by omega
  rw [hdiff] at hsub
  have hq1 : q ≤ 1 := Nat.le_of_dvd (by norm_num) hsub
  have := hqP.two_le
  omega

/-- Corollary: there are infinitely many primes — OUR proof. -/
theorem infinite_primes_ours : Set.Infinite {p : ℕ | p.Prime} := by
  by_contra hfin
  rw [Set.not_infinite] at hfin
  obtain ⟨s, hs⟩ := hfin.exists_finset
  obtain ⟨q, hqP, hqnot⟩ := exists_prime_not_mem s (fun p hp => (hs p).mp hp)
  have hqs : q ∈ s := (hs q).mpr hqP
  exact hqnot hqs

#print axioms prime_mod30
#print axioms infinite_primes_ours
