import Mathlib.Data.Fintype.Card

/-!
Canonical-coordinate soundness bridge for the two four-element rings.

The Z/4 coordinate operations are tied to literal arithmetic modulo4 by
kernel-checked finite truth tables. The dual-number operations are their
defining coefficient operations. The dimension-independent theorem then
equates membership of the full four-point line with the two tangent pairs,
including the Z/4 carry. It is not a theorem about the unavailable Claude CNF.
-/

namespace KakeyaRound5

inductive RingKind | dual | z4 deriving DecidableEq

abbrev Coeff := Bool × Bool

def bit (b : Bool) : Nat := if b then 1 else 0
def encode (x : Coeff) : Nat := bit x.1 + 2 * bit x.2
def carryBit (r : RingKind) (a d : Bool) : Bool :=
  match r with
  | .dual => false
  | .z4 => a && d

def addCoeff (r : RingKind) (x y : Coeff) : Coeff :=
  (Bool.xor x.1 y.1, Bool.xor (Bool.xor x.2 y.2) (carryBit r x.1 y.1))

def mulCoeff (x y : Coeff) : Coeff :=
  (x.1 && y.1, Bool.xor (x.1 && y.2) (x.2 && y.1))

theorem encode_injective : Function.Injective encode := by
  rintro ⟨a,u⟩ ⟨b,v⟩ h
  cases a <;> cases u <;> cases b <;> cases v <;> simp_all [encode,bit]
theorem encode_lt_four : ∀ x : Coeff, encode x < 4 := by
  rintro ⟨a,u⟩
  cases a <;> cases u <;> decide
theorem z4_add_encoding : ∀ x y : Coeff,
    encode (addCoeff .z4 x y) = (encode x + encode y) % 4 := by
  rintro ⟨a,u⟩ ⟨b,v⟩
  cases a <;> cases u <;> cases b <;> cases v <;> decide
theorem z4_mul_encoding : ∀ x y : Coeff,
    encode (mulCoeff x y) = (encode x * encode y) % 4 := by
  rintro ⟨a,u⟩ ⟨b,v⟩
  cases a <;> cases u <;> cases b <;> cases v <;> decide

def coordLine (r : RingKind) (a u d v : Bool) (t : Coeff) : Coeff :=
  addCoeff r (a,u) (mulCoeff t (d,v))

theorem z4_line_encoding : ∀ a u d v : Bool, ∀ t : Coeff,
    encode (coordLine .z4 a u d v t) =
      (encode (a,u) + encode t * encode (d,v)) % 4 := by
  rintro a u d v ⟨t,s⟩
  cases a <;> cases u <;> cases d <;> cases v <;> cases t <;> cases s <;> decide

theorem coordinate_corners (r : RingKind) : ∀ a u d v : Bool,
    coordLine r a u d v (false,false) = (a,u) ∧
    coordLine r a u d v (false,true) = (a,Bool.xor u d) ∧
    coordLine r a u d v (true,false) =
      (Bool.xor a d, Bool.xor (Bool.xor u v) (carryBit r a d)) ∧
    coordLine r a u d v (true,true) =
      (Bool.xor a d, Bool.xor (Bool.xor (Bool.xor u v) (carryBit r a d)) d) := by
  cases r <;> decide

abbrev Vector (I : Type*) := I → Bool
def vxor {I : Type*} (x y : Vector I) : Vector I := fun i => Bool.xor (x i) (y i)
def vzero {I : Type*} : Vector I := fun _ => false
def vcarry {I : Type*} (r : RingKind) (a d : Vector I) : Vector I :=
  fun i => carryBit r (a i) (d i)
def endpoint {I : Type*} (r : RingKind) (a u d v : Vector I) : Vector I :=
  vxor (vxor u v) (vcarry r a d)

def linePoint {I : Type*} (r : RingKind) (a u d v : Vector I) (t : Coeff) :
    Vector I × Vector I :=
  (fun i => (coordLine r (a i) (u i) (d i) (v i) t).1,
   fun i => (coordLine r (a i) (u i) (d i) (v i) t).2)

theorem linePoint_zero {I : Type*} (r : RingKind) (a u d v : Vector I) :
    linePoint r a u d v (false,false) = (a,u) := by
  apply Prod.ext
  · funext i
    exact congrArg Prod.fst ((coordinate_corners r (a i) (u i) (d i) (v i)).1)
  · funext i
    exact congrArg Prod.snd ((coordinate_corners r (a i) (u i) (d i) (v i)).1)

theorem linePoint_nilpotent {I : Type*} (r : RingKind) (a u d v : Vector I) :
    linePoint r a u d v (false,true) = (a,vxor u d) := by
  apply Prod.ext
  · funext i
    exact congrArg Prod.fst ((coordinate_corners r (a i) (u i) (d i) (v i)).2.1)
  · funext i
    exact congrArg Prod.snd ((coordinate_corners r (a i) (u i) (d i) (v i)).2.1)

theorem linePoint_one {I : Type*} (r : RingKind) (a u d v : Vector I) :
    linePoint r a u d v (true,false) = (vxor a d,endpoint r a u d v) := by
  apply Prod.ext
  · funext i
    exact congrArg Prod.fst ((coordinate_corners r (a i) (u i) (d i) (v i)).2.2.1)
  · funext i
    exact congrArg Prod.snd ((coordinate_corners r (a i) (u i) (d i) (v i)).2.2.1)

theorem linePoint_one_add_nilpotent {I : Type*} (r : RingKind) (a u d v : Vector I) :
    linePoint r a u d v (true,true) =
      (vxor a d,vxor (endpoint r a u d v) d) := by
  apply Prod.ext
  · funext i
    exact congrArg Prod.fst ((coordinate_corners r (a i) (u i) (d i) (v i)).2.2.2)
  · funext i
    exact congrArg Prod.snd ((coordinate_corners r (a i) (u i) (d i) (v i)).2.2.2)

def HasPair {I : Type*} (A : Set (Vector I)) (d u : Vector I) : Prop :=
  u ∈ A ∧ vxor u d ∈ A

def LineContained {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) (a u d v : Vector I) : Prop :=
  ∀ t : Coeff, (linePoint r a u d v t).2 ∈ A (linePoint r a u d v t).1

/-- The actual four coefficient values reduce line containment to two pairs.
The Z/4 carry is already part of the second pair's location. -/
theorem lineContained_iff_two_pairs {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) (a u d v : Vector I) :
    LineContained r A a u d v ↔
      HasPair (A a) d u ∧ HasPair (A (vxor a d)) d (endpoint r a u d v) := by
  constructor
  · intro h
    have h0 := h (false,false)
    have hn := h (false,true)
    have h1 := h (true,false)
    have hb := h (true,true)
    rw [linePoint_zero] at h0
    rw [linePoint_nilpotent] at hn
    rw [linePoint_one] at h1
    rw [linePoint_one_add_nilpotent] at hb
    exact ⟨⟨h0,hn⟩,⟨h1,hb⟩⟩
  · rintro ⟨⟨h0,hn⟩,⟨h1,hb⟩⟩ ⟨t,s⟩
    cases t <;> cases s
    · simpa only [linePoint_zero] using h0
    · simpa only [linePoint_nilpotent] using hn
    · simpa only [linePoint_one] using h1
    · simpa only [linePoint_one_add_nilpotent] using hb

theorem vxor_eq_self_forces_zero {I : Type*} (x d : Vector I)
    (h : vxor x d = x) : d = vzero := by
  funext i
  have hi := congrFun h i
  change Bool.xor (x i) (d i) = x i at hi
  change d i = false
  cases hx : x i <;> cases hd : d i <;> simp [hx,hd] at hi ⊢

theorem primitive_pair_distinct {I : Type*} (x d : Vector I)
    (hd : d ≠ vzero) : vxor x d ≠ x := by
  intro h
  exact hd (vxor_eq_self_forces_zero x d h)

theorem endpoint_involution {I : Type*} (r : RingKind)
    (a u d v : Vector I) : endpoint r a u d (endpoint r a u d v) = v := by
  funext i
  simp only [endpoint,vxor,vcarry]
  cases r <;> cases ha : a i <;> cases hu : u i <;> cases hd : d i <;>
    cases hv : v i <;> simp [carryBit]

/-- Exact witness bridge: a line with prescribed low/high direction exists
precisely when two tangent pairs have the corresponding carry-shifted sum.
The expression `endpoint r a u d w` is u xor w xor carry(r,a,d). -/
theorem line_exists_iff_pair_sum {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) (a d v : Vector I) :
    (∃ u, LineContained r A a u d v) ↔
      ∃ u w, HasPair (A a) d u ∧ HasPair (A (vxor a d)) d w ∧
        endpoint r a u d w = v := by
  constructor
  · rintro ⟨u,h⟩
    have pairs := (lineContained_iff_two_pairs r A a u d v).mp h
    exact ⟨u,endpoint r a u d v,pairs.1,pairs.2,endpoint_involution r a u d v⟩
  · rintro ⟨u,w,hu,hw,hv⟩
    refine ⟨u,(lineContained_iff_two_pairs r A a u d v).mpr ?_⟩
    refine ⟨hu,?_⟩
    rw [← hv,endpoint_involution]
    exact hw

end KakeyaRound5

#print axioms KakeyaRound5.encode_injective
#print axioms KakeyaRound5.encode_lt_four
#print axioms KakeyaRound5.z4_add_encoding
#print axioms KakeyaRound5.z4_mul_encoding
#print axioms KakeyaRound5.z4_line_encoding
#print axioms KakeyaRound5.coordinate_corners
#print axioms KakeyaRound5.linePoint_zero
#print axioms KakeyaRound5.linePoint_nilpotent
#print axioms KakeyaRound5.linePoint_one
#print axioms KakeyaRound5.linePoint_one_add_nilpotent
#print axioms KakeyaRound5.lineContained_iff_two_pairs
#print axioms KakeyaRound5.vxor_eq_self_forces_zero
#print axioms KakeyaRound5.primitive_pair_distinct
#print axioms KakeyaRound5.endpoint_involution
#print axioms KakeyaRound5.line_exists_iff_pair_sum
