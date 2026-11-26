import Mathlib

/-!
# The Prime Sieve, Level 2 — mod 210

Extends `PrimeSieve.lean`: a prime p > 7 avoids ALL prime factors of
210 = 2*3*5*7, so `gcd(p % 210, 210) = 1`. Since φ(210) = 48, exactly
48 of the 210 residue classes mod 210 can contain primes — the sieve
density drops to 48/210 ≈ 22.9%.

Main theorem: `prime_coprime_210`.
-/

section Sieve210

variable {p : ℕ}

/-- A prime p > 7 cannot divide 210 = 2*3*5*7: every prime divisor of
    210 is one of 2,3,5,7, all < p. -/
theorem not_dvd_210 (hp : p.Prime) (h7 : 7 < p) : ¬ p ∣ 210 := by
  intro hdvd
  have hfac : (210 : ℕ) = 2 * (3 * (5 * 7)) := by norm_num
  rw [hfac] at hdvd
  rcases (hp.dvd_mul.mp hdvd) with h2 | h357
  · have he := (Nat.prime_dvd_prime_iff_eq hp (by norm_num : Nat.Prime 2)).mp h2
    omega
  rcases (hp.dvd_mul.mp h357) with h3 | h57
  · have he := (Nat.prime_dvd_prime_iff_eq hp (by norm_num : Nat.Prime 3)).mp h3
    omega
  rcases (hp.dvd_mul.mp h57) with h5 | h7'
  · have he := (Nat.prime_dvd_prime_iff_eq hp (by norm_num : Nat.Prime 5)).mp h5
    omega
  · have he := (Nat.prime_dvd_prime_iff_eq hp (by norm_num : Nat.Prime 7)).mp h7'
    omega

/-- **The Mod-210 Sieve**: every prime p > 7 is coprime to 210,
    i.e. p % 210 is one of the φ(210) = 48 residue classes coprime to 210. -/
theorem prime_coprime_210 (hp : p.Prime) (h7 : 7 < p) :
    Nat.Coprime (p % 210) 210 := by
  rw [Nat.coprime_iff_gcd_eq_one]
  by_contra hne
  -- d := gcd (p % 210) 210 is a common divisor of p % 210 and 210.
  have hdvdmod : Nat.gcd (p % 210) 210 ∣ p % 210 := Nat.gcd_dvd_left _ _
  have hdvd210 : Nat.gcd (p % 210) 210 ∣ 210 := Nat.gcd_dvd_right _ _
  -- Hence d ∣ p, since p = 210 * (p / 210) + p % 210.
  have hpdvd : Nat.gcd (p % 210) 210 ∣ p := by
    have hdiv : 210 * (p / 210) + p % 210 = p := Nat.div_add_mod p 210
    have hdvdprod : Nat.gcd (p % 210) 210 ∣ 210 * (p / 210) :=
      dvd_mul_of_dvd_left hdvd210 _
    have hdvdsum := Nat.dvd_add hdvdprod hdvdmod
    rwa [hdiv] at hdvdsum
  -- d ≠ 1, so d has a prime factor q.
  obtain ⟨q, hqprime, hqgcd⟩ := Nat.exists_prime_and_dvd hne
  have hq210 : q ∣ 210 := dvd_trans hqgcd hdvd210
  have hqp : q ∣ p := dvd_trans hqgcd hpdvd
  -- q and p are both prime and q ∣ p, so q = p; then p ∣ 210 — contradiction.
  have hqp_eq : q = p := (Nat.prime_dvd_prime_iff_eq hqprime hp).mp hqp
  subst hqp_eq
  exact not_dvd_210 hp h7 hq210

end Sieve210

#print axioms not_dvd_210
#print axioms prime_coprime_210
