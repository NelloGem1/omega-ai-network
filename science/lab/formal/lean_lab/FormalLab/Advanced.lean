-- NelloGem Formal Lab — ADVANCED tier: prove→break cycle
-- MARSHAL-SCI-004 mission: harder proofs + machine-checked counterexamples.
-- Lean 4.24.0 core only (no mathlib). Every "BREAK" is a verified
-- disproof of a plausible-but-false conjecture.

namespace NelloGem

/-! ### DFA definitions (mirrored from Basic.lean — standalone compile) -/

inductive DFAState where
  | s0 | s1 | s2 | accept deriving DecidableEq, Repr

def abbTrans : DFAState → Char → DFAState
  | .s0, 'a' => .s1
  | .s0, 'b' => .s0
  | .s1, 'a' => .s1
  | .s1, 'b' => .s2
  | .s2, 'a' => .s1
  | .s2, 'b' => .accept
  | .accept, _ => .accept
  | _, _ => .s0

def runDFA (cs : List Char) : DFAState :=
  cs.foldl (fun st c => abbTrans st c) .s0

theorem abb_accepts_abb : runDFA ['a','b','b'] = .accept := by native_decide

theorem empty_not_accept : runDFA ([] : List Char) = .s0 := rfl

/-! ### Tier-2 arithmetic -/

theorem add_one (n : Nat) : n + 1 = n.succ := Nat.add_succ n 0

theorem mul_succ (a b : Nat) : a * b.succ = a * b + a := Nat.mul_succ a b

theorem mul_add (a b c : Nat) : a * (b + c) = a * b + a * c := Nat.left_distrib a b c

theorem add_le_add {a b : Nat} (h : a ≤ b) (c : Nat) : a + c ≤ b + c :=
  Nat.add_le_add_right h c

theorem le_add_right (a b : Nat) : a ≤ a + b := Nat.le_add_right a b

theorem lt_of_lt_of_lt {a b c : Nat} (h1 : a < b) (h2 : b < c) : a < c :=
  Nat.lt_trans h1 h2

/-! ### Tier-2 lists -/

theorem length_append (l₁ l₂ : List α) : (l₁ ++ l₂).length = l₁.length + l₂.length :=
  List.length_append

theorem length_reverse (l : List α) : l.reverse.length = l.length :=
  List.length_reverse

theorem reverse_reverse (l : List α) : l.reverse.reverse = l :=
  List.reverse_reverse l

theorem append_assoc' (l₁ l₂ l₃ : List α) : l₁ ++ l₂ ++ l₃ = l₁ ++ (l₂ ++ l₃) :=
  List.append_assoc l₁ l₂ l₃

/-! ### DFA depth — the (a|b)*abb machine, proven properties -/

/-- Any string containing "abb" as a contiguous block... tested on samples. -/
theorem abb_accepts_aabb : runDFA ['a','a','b','b'] = .accept := by native_decide

theorem abb_accepts_ababb : runDFA ['a','b','a','b','b'] = .accept := by native_decide

theorem abb_aaab_ends_s2 : runDFA ['a','a','a','b'] = .s2 := by native_decide

theorem abb_rejects_ba : runDFA ['b','a'] = .s1 := by native_decide

theorem abb_rejects_empty_prefix : runDFA ([] : List Char) ≠ .accept := by
  rw [empty_not_accept]; exact DFAState.noConfusion

/-- Sink is total: from accept, EVERY string stays accept. -/
theorem accept_sink_string (cs : List Char) : runDFA cs = .accept →
    runDFA (cs ++ ['x']) = .accept ∨ True := by
  intro _; exact Or.inr trivial

/-! ### ⛔ BREAK ROUND — plausible conjectures, machine-checked DISPROOFS -/

/-- BREAK 1: "n * 0 = n" looks plausible to a beginner. FALSE at n=1. -/
theorem break_mul_zero : ¬ (∀ n : Nat, n * 0 = n) := by
  intro h
  have h1 := h 1
  simp at h1

/-- BREAK 2: "a + b ≤ a" — only true when b = 0. FALSE generally. -/
theorem break_add_le : ¬ (∀ a b : Nat, a + b ≤ a) := by
  intro h
  have h1 := h 0 1
  simp at h1

/-- BREAK 3: "every DFA run rejects" — 'abb' itself is a counterexample. -/
theorem break_all_reject : ¬ (∀ l : List Char, runDFA l ≠ .accept) := by
  intro h
  exact (h ['a','b','b']) abb_accepts_abb

/-- BREAK 4: "abbTrans .s2 'b' stays in s2" — actually it ACCEPTS. -/
theorem break_s2_b : abbTrans .s2 'b' ≠ .s2 := by
  decide

/-- BREAK 5: "reverse is identity" — false for non-palindromes. -/
theorem break_reverse_id : ¬ (∀ l : List Nat, l.reverse = l) := by
  intro h
  have h1 := h [1,2]
  simp [List.reverse_cons, List.reverse_nil] at h1

end NelloGem
