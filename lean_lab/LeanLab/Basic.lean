import Mathlib

/-!
# Lean Lab — first verified proofs (Mathlib edition)
-/

/-- Sum of the first n natural numbers: 0 + 1 + ... + (n-1). -/
def sumTo : Nat → Nat
  | 0 => 0
  | n+1 => sumTo n + (n + 1)

/-- Twice the sum equals n*(n+1). -/
theorem two_mul_sumTo (n : Nat) : 2 * sumTo n = n * (n + 1) := by
  induction n with
  | zero => rfl
  | succ k ih =>
      simp only [sumTo, Nat.mul_add]
      rw [ih]
      ring

/-- The famous closed form: sumTo n = n*(n+1)/2. -/
theorem sumTo_eq (n : Nat) : sumTo n = n * (n + 1) / 2 := by
  have h := two_mul_sumTo n
  omega
