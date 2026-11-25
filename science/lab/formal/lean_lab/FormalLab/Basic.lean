-- NelloGem Formal Lab — Lean 4.24.0 core theorems
-- MARSHAL-SCI-004 mission: real proofs, no sorry.

namespace NelloGem

/-! ### Arithmetic foundations -/

theorem add_zero (n : Nat) : n + 0 = n := Nat.add_zero n

theorem zero_add (n : Nat) : 0 + n = n := Nat.zero_add n

theorem add_comm' (a b : Nat) : a + b = b + a := Nat.add_comm a b

theorem add_assoc' (a b c : Nat) : a + b + c = a + (b + c) := Nat.add_assoc a b c

theorem mul_comm' (a b : Nat) : a * b = b * a := Nat.mul_comm a b

theorem mul_zero (n : Nat) : n * 0 = 0 := Nat.mul_zero n

theorem zero_mul (n : Nat) : 0 * n = 0 := Nat.zero_mul n

theorem succ_ne_zero (n : Nat) : n.succ ≠ 0 := Nat.succ_ne_zero n

theorem add_succ (a b : Nat) : a + b.succ = (a + b).succ := Nat.add_succ a b

/-! ### Order / inequalities -/

theorem le_refl' (n : Nat) : n ≤ n := Nat.le_refl n

theorem lt_of_lt_of_le {a b c : Nat} (h1 : a < b) (h2 : b ≤ c) : a < c :=
  Nat.lt_of_lt_of_le h1 h2

theorem not_succ_le_self (n : Nat) : ¬ n.succ ≤ n := Nat.not_succ_le_self n

/-! ### Logic / decidability -/

theorem iff_of_eq {a b : Prop} (h : a = b) : a ↔ b := Iff.of_eq h

theorem and_comm' {a b : Prop} (h : a ∧ b) : b ∧ a := ⟨h.2, h.1⟩

theorem or_comm' {a b : Prop} (h : a ∨ b) : b ∨ a := h.elim (fun l => Or.inr l) (fun r => Or.inl r)

/-! ### Lists / strings (for automata groundwork) -/

theorem list_append_nil (l : List α) : l ++ [] = l := List.append_nil l

theorem list_nil_append (l : List α) : [] ++ l = l := List.nil_append l

theorem mem_append {a : α} {l₁ l₂ : List α} : a ∈ l₁ ++ l₂ ↔ a ∈ l₁ ∨ a ∈ l₂ :=
  List.mem_append

/-! ### The (a|b)*abb DFA — state invariant lemmas -/
/-- States 0,1,2 track the longest suffix of the input seen so far
    that is a prefix of "abb". State 3 = accepted (seen "abb"). -/
inductive DFAState where
  | s0 | s1 | s2 | accept deriving DecidableEq, Repr

/-- The transition function for pattern "abb" over alphabet {a,b}. -/
def abbTrans : DFAState → Char → DFAState
  | .s0, 'a' => .s1
  | .s0, 'b' => .s0
  | .s1, 'a' => .s1   -- "aa": longest suffix-prefix match stays 1
  | .s1, 'b' => .s2
  | .s2, 'a' => .s1   -- "aba": suffix "a" matches prefix len 1
  | .s2, 'b' => .accept -- "abb": MATCH
  | .accept, _ => .accept  -- sink: once matched, stays matched (any char)
  | _, _ => .s0

/-- Run the DFA over a string, left-to-right, starting at s0. -/
def runDFA (cs : List Char) : DFAState :=
  cs.foldl (fun st c => abbTrans st c) .s0

/-- Key lemma 1: reading "abb" reaches accept. -/
theorem abb_accepts_abb : runDFA ['a','b','b'] = .accept := by
  native_decide

/-- Key lemma 2: "ab" alone does NOT accept (ends in state s2). -/
theorem abb_rejects_ab : runDFA ['a','b'] = .s2 := by
  native_decide

/-- Key lemma 3: "b" alone does NOT accept. -/
theorem abb_rejects_b : runDFA ['b'] = .s0 := by
  native_decide

/-- Key lemma 4: once accepted, stays accepted (sink property, any char). -/
theorem accept_sink (c : Char) : abbTrans .accept c = .accept := by
  cases c <;> rfl

/-- Key lemma 5: empty string starts at s0, not accepted. -/
theorem empty_not_accept : runDFA ([] : List Char) = .s0 := rfl

end NelloGem
