import CarryBridge

/-!
Common affine tangent shears preserve the actual primitive-line condition,
including the Z/4 carry.  This extends the earlier coordinate-line bridge.
It does not verify the Python CNF encoder or construct a linear interpolant
from a basis.  The anchor theorem takes that interpolant as a hypothesis.
-/

namespace KakeyaRound7
open KakeyaRound5

def shearVector {I : Type*} (t : Vector I) (L : Vector I → Vector I)
    (a u : Vector I) : Vector I := vxor u (vxor t (L a))

def shearFibres {I : Type*} (A : Vector I → Set (Vector I))
    (t : Vector I) (L : Vector I → Vector I) : Vector I → Set (Vector I) :=
  fun a => {u | shearVector t L a u ∈ A a}

def XorLinear {I : Type*} (L : Vector I → Vector I) : Prop :=
  ∀ a d, L (vxor a d) = vxor (L a) (L d)

theorem xor_cancel_right {I : Type*} (u z : Vector I) :
    vxor (vxor u z) z = u := by
  funext i
  change Bool.xor (Bool.xor (u i) (z i)) (z i) = u i
  cases u i <;> cases z i <;> rfl

theorem shear_involution {I : Type*} (t : Vector I) (L : Vector I → Vector I)
    (a u : Vector I) : shearVector t L a (shearVector t L a u) = u := by
  exact xor_cancel_right u (vxor t (L a))

def shearEquiv {I : Type*} (t : Vector I) (L : Vector I → Vector I)
    (a : Vector I) : Vector I ≃ Vector I where
  toFun := shearVector t L a
  invFun := shearVector t L a
  left_inv := shear_involution t L a
  right_inv := shear_involution t L a

theorem shear_pair_vector {I : Type*} (t : Vector I) (L : Vector I → Vector I)
    (a u d : Vector I) :
    shearVector t L a (vxor u d) = vxor (shearVector t L a u) d := by
  funext i
  simp only [shearVector, vxor]
  cases u i <;> cases d i <;> cases t i <;> cases (L a) i <;> rfl

theorem shear_pair_iff {I : Type*} (A : Vector I → Set (Vector I))
    (t : Vector I) (L : Vector I → Vector I) (a d u : Vector I) :
    HasPair (shearFibres A t L a) d u ↔
      HasPair (A a) d (shearVector t L a u) := by
  change (shearVector t L a u ∈ A a ∧ shearVector t L a (vxor u d) ∈ A a) ↔ _
  rw [shear_pair_vector]
  rfl

theorem shear_endpoint {I : Type*} (r : RingKind) (t : Vector I)
    (L : Vector I → Vector I) (hL : XorLinear L) (a u d v : Vector I) :
    shearVector t L (vxor a d) (endpoint r a u d v) =
      endpoint r a (shearVector t L a u) d (vxor v (L d)) := by
  unfold shearVector
  rw [hL a d]
  funext i
  simp only [endpoint, vxor, vcarry]
  cases u i <;> cases v i <;> cases carryBit r (a i) (d i) <;>
    cases t i <;> cases (L a) i <;> cases (L d) i <;> rfl

theorem lineContained_shear_iff {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) (t : Vector I)
    (L : Vector I → Vector I) (hL : XorLinear L) (a u d v : Vector I) :
    LineContained r (shearFibres A t L) a u d v ↔
      LineContained r A a (shearVector t L a u) d (vxor v (L d)) := by
  rw [lineContained_iff_two_pairs, lineContained_iff_two_pairs]
  rw [shear_pair_iff, shear_pair_iff, shear_endpoint r t L hL]

theorem line_exists_shear_iff {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) (t : Vector I)
    (L : Vector I → Vector I) (hL : XorLinear L) (d v : Vector I) :
    (∃ a u, LineContained r (shearFibres A t L) a u d v) ↔
      ∃ a u, LineContained r A a u d (vxor v (L d)) := by
  constructor
  · rintro ⟨a, u, h⟩
    exact ⟨a, shearVector t L a u, (lineContained_shear_iff r A t L hL a u d v).mp h⟩
  · rintro ⟨a, u, h⟩
    refine ⟨a, shearVector t L a u, ?_⟩
    apply (lineContained_shear_iff r A t L hL a (shearVector t L a u) d v).mpr
    simpa only [shear_involution] using h

def BinaryKakeya {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) : Prop :=
  ∀ d, d ≠ vzero → ∀ v, ∃ a u, LineContained r A a u d v

theorem binaryKakeya_shear_iff {I : Type*} (r : RingKind)
    (A : Vector I → Set (Vector I)) (t : Vector I)
    (L : Vector I → Vector I) (hL : XorLinear L) :
    BinaryKakeya r (shearFibres A t L) ↔ BinaryKakeya r A := by
  constructor
  · intro h d hd v
    have hshift := h d hd (vxor v (L d))
    have horiginal := (line_exists_shear_iff r A t L hL d (vxor v (L d))).mp hshift
    simpa only [xor_cancel_right] using horiginal
  · intro h d hd v
    exact (line_exists_shear_iff r A t L hL d v).mpr (h d hd (vxor v (L d)))

theorem shear_anchor {I : Type*} (A : Vector I → Set (Vector I))
    (t : Vector I) (L : Vector I → Vector I) (a p : Vector I)
    (hp : p ∈ A a) (hanchor : L a = vxor t p) :
    vzero ∈ shearFibres A t L a := by
  change shearVector t L a vzero ∈ A a
  have heq : shearVector t L a vzero = p := by
    unfold shearVector
    rw [hanchor]
    funext i
    simp only [vzero, vxor]
    cases t i <;> cases p i <;> rfl
  rw [heq]
  exact hp

end KakeyaRound7

#print axioms KakeyaRound7.xor_cancel_right
#print axioms KakeyaRound7.shear_involution
#print axioms KakeyaRound7.shearEquiv
#print axioms KakeyaRound7.shear_pair_vector
#print axioms KakeyaRound7.shear_pair_iff
#print axioms KakeyaRound7.shear_endpoint
#print axioms KakeyaRound7.lineContained_shear_iff
#print axioms KakeyaRound7.line_exists_shear_iff
#print axioms KakeyaRound7.binaryKakeya_shear_iff
#print axioms KakeyaRound7.shear_anchor
