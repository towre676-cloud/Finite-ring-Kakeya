import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
# Finite incidence bookkeeping for the Kakeya cube master bound

This module formalizes the finite-sum and real-algebra deduction, including
the disjoint use of remaining-endpoint energy and the seven incidence slots
of each selected cube. It does not formalize the geometric construction of
those injections, the quotient-sumset capacity lemmas, Mantel's theorem, or
the bridge from an actual binary subset to its pair counts.

`RR`, `CC`, and `CR` index the three kinds of active edges. Each `RR` edge
has two remaining endpoints, each `CC` edge has two cube endpoints, and a
`CR` edge has one endpoint of each kind. Injective incidence-slot maps encode
the prohibition on spending a (fibre,direction) twice.
-/

open scoped BigOperators

namespace KakeyaRound4

theorem pair_capacity_energy (capacity p q : ℝ)
    (hcap : capacity ≤ p * q) :
    2 * capacity ≤ p ^ 2 + q ^ 2 := by
  nlinarith [sq_nonneg (p - q)]

/-- Weighted AM-GM with its positive denominator cleared. For theta>0,
division by theta gives 2c <= theta*p^2 + theta^{-1}*q^2. -/
theorem weighted_pair_capacity_energy (capacity p q theta : ℝ)
    (htheta : 0 ≤ theta) (hcap : capacity ≤ p * q) :
    2 * theta * capacity ≤ (theta * p) ^ 2 + q ^ 2 := by
  have hscaled := mul_le_mul_of_nonneg_left hcap htheta
  nlinarith [sq_nonneg (theta * p - q)]

/-- Injective assignment to nonnegative resource slots cannot spend more
than the total resource. This is the finite-sum non-double-counting lemma. -/
theorem sum_injective_resource
    {I Slot : Type*} [Fintype I] [Fintype Slot]
    (slot : I → Slot) (hinj : Function.Injective slot)
    (weight : Slot → ℝ) (hnonneg : ∀ s, 0 ≤ weight s) :
    (∑ i, weight (slot i)) ≤ ∑ s, weight s := by
  classical
  calc
    (∑ i, weight (slot i)) = ∑ s ∈ Finset.univ.image slot, weight s := by
      rw [Finset.sum_image]
      intro a _ b _ hab
      exact hinj hab
    _ ≤ ∑ s, weight s := by
      exact Finset.sum_le_sum_of_subset_of_nonneg
        (Finset.subset_univ _) (by intro s _ _; exact hnonneg s)

/-- RR capacities and the energy reserved at CR endpoints are disjoint
parts of the remaining fibres' energy. The slot type can be R × Direction. -/
theorem remaining_energy_budget
    {RR CR Slot : Type*} [Fintype RR] [Fintype CR] [Fintype Slot]
    (slot : (RR × Bool) ⊕ CR → Slot)
    (hinj : Function.Injective slot)
    (weight : Slot → ℝ) (hnonneg : ∀ s, 0 ≤ weight s)
    (rrCapacity : RR → ℝ)
    (hrr : ∀ e, 2 * rrCapacity e ≤
      weight (slot (.inl (e, true))) + weight (slot (.inl (e, false)))) :
    2 * (∑ e, rrCapacity e) + (∑ e, weight (slot (.inr e)))
      ≤ ∑ s, weight s := by
  classical
  have hslots := sum_injective_resource slot hinj weight hnonneg
  simp only [Fintype.sum_sum_type, Fintype.sum_prod_type, Fintype.sum_bool] at hslots
  have hsum : (∑ e, 2 * rrCapacity e) ≤
      ∑ e, (weight (slot (.inl (e, true))) + weight (slot (.inl (e, false)))) := by
    exact Finset.sum_le_sum (by intro e _; exact hrr e)
  rw [← Finset.mul_sum] at hsum
  exact le_trans (add_le_add_right hsum _) hslots

/-- An injection into seven slots per cube proves the incidence budget.
The two Bool endpoints of every CC edge are counted separately. -/
theorem cube_incidence_count
    {Cube CC CR : Type*} [Fintype Cube] [Fintype CC] [Fintype CR]
    (slot : (CC × Bool) ⊕ CR → Cube × Fin 7)
    (hinj : Function.Injective slot) :
    2 * Fintype.card CC + Fintype.card CR ≤ 7 * Fintype.card Cube := by
  have h := Fintype.card_le_of_injective slot hinj
  simpa [Fintype.card_sum, Fintype.card_prod, Nat.mul_comm] using h

/-- After paying eleven doubled units for each cube incidence, an ordinary
CC edge costs at most zero extra; an expensive edge costs at most ten. -/
theorem cube_edge_budget
    {CC : Type*} [Fintype CC]
    (capacity : CC → ℝ) (expensive : CC → Prop) [DecidablePred expensive]
    (hcap : ∀ e, capacity e ≤ 16)
    (hcheap : ∀ e, ¬ expensive e → capacity e ≤ 8) :
    2 * (∑ e, capacity e) ≤
      22 * (Fintype.card CC : ℝ) +
      10 * ((Finset.univ.filter expensive).card : ℝ) := by
  classical
  have hp : ∀ e, 2 * capacity e ≤ 22 + if expensive e then (10 : ℝ) else 0 := by
    intro e
    by_cases he : expensive e
    · simp only [he, if_true]
      linarith [hcap e]
    · simp only [he, if_false, add_zero]
      linarith [hcheap e he]
  have hs := Finset.sum_le_sum (s := Finset.univ) (by intro e _; exact hp e)
  have hb : (∑ e, if expensive e then (10 : ℝ) else 0) =
      10 * ((Finset.univ.filter expensive).card : ℝ) := by
    calc
      (∑ e, if expensive e then (10 : ℝ) else 0) =
          ∑ e, 10 * (if expensive e then (1 : ℝ) else 0) := by
        apply Finset.sum_congr rfl
        intro e _
        by_cases he : expensive e <;> simp [he]
      _ = 10 * (∑ e, if expensive e then (1 : ℝ) else 0) := by
        rw [Finset.mul_sum]
      _ = 10 * ((Finset.univ.filter expensive).card : ℝ) := by
        rw [Finset.sum_boole]
  rw [← Finset.mul_sum, Finset.sum_add_distrib, hb] at hs
  simpa [mul_comm] using hs

/-- A cube-to-other product/capacity bound supplies the local surplus row.
The expression is the doubled form at lambda = 11/2. -/
theorem cube_other_surplus_row (capacity q : ℝ)
    (hcap : capacity ≤ min 16 (4 * q)) :
    2 * capacity ≤ q ^ 2 + 11 +
      max 0 (2 * min 16 (4 * q) - q ^ 2 - 11) := by
  have hm := le_max_right (0 : ℝ) (2 * min 16 (4 * q) - q ^ 2 - 11)
  linarith

def doubledSurplus (q : ℝ) : ℝ :=
  max 0 (2 * min 16 (4 * q) - q ^ 2 - 11)

theorem small_surplus_table :
    doubledSurplus 0 = 0 ∧ doubledSurplus 1 = 0 ∧
    doubledSurplus 2 = 1 ∧ doubledSurplus 3 = 4 ∧
    doubledSurplus 4 = 5 := by
  norm_num [doubledSurplus]

theorem surplus_zero_of_ge_five (q : ℝ) (hq : 5 ≤ q) :
    doubledSurplus q = 0 := by
  have hmin : 16 ≤ 4 * q := by linarith
  unfold doubledSurplus
  rw [min_eq_left hmin]
  apply max_eq_left
  nlinarith [sq_nonneg (q - 5)]

/-- The general certificate aggregation theorem. The expensive-edge count
bound B is an explicit input: applying Mantel is a separate geometric step.
The conclusion is the doubled master bound E_R + 77 r + 10 B + sum gains. -/
theorem cube_master_bound
    {Cube RR CC CR Slot : Type*}
    [Fintype Cube] [Fintype RR] [Fintype CC] [Fintype CR] [Fintype Slot]
    (remainingSlot : (RR × Bool) ⊕ CR → Slot)
    (hremaining : Function.Injective remainingSlot)
    (cubeSlot : (CC × Bool) ⊕ CR → Cube × Fin 7)
    (hcube : Function.Injective cubeSlot)
    (weight : Slot → ℝ) (hnonneg : ∀ s, 0 ≤ weight s)
    (rrCapacity : RR → ℝ) (ccCapacity : CC → ℝ) (crCapacity gain : CR → ℝ)
    (expensive : CC → Prop) [DecidablePred expensive]
    (B : ℕ)
    (hrr : ∀ e, 2 * rrCapacity e ≤
      weight (remainingSlot (.inl (e, true))) +
      weight (remainingSlot (.inl (e, false))))
    (hcc : ∀ e, ccCapacity e ≤ 16)
    (hcheap : ∀ e, ¬ expensive e → ccCapacity e ≤ 8)
    (hexpensive : (Finset.univ.filter expensive).card ≤ B)
    (hcr : ∀ e, 2 * crCapacity e ≤
      weight (remainingSlot (.inr e)) + 11 + gain e) :
    2 * ((∑ e, rrCapacity e) + (∑ e, ccCapacity e) + (∑ e, crCapacity e)) ≤
      (∑ s, weight s) + 77 * (Fintype.card Cube : ℝ) +
      10 * (B : ℝ) + (∑ e, gain e) := by
  classical
  have hr := remaining_energy_budget remainingSlot hremaining weight hnonneg rrCapacity hrr
  have hccsum := cube_edge_budget ccCapacity expensive hcc hcheap
  have hcNat := cube_incidence_count cubeSlot hcube
  have hcReal : 2 * (Fintype.card CC : ℝ) + (Fintype.card CR : ℝ) ≤
      7 * (Fintype.card Cube : ℝ) := by
    have hcast : ((2 * Fintype.card CC + Fintype.card CR : ℕ) : ℝ) ≤
        ((7 * Fintype.card Cube : ℕ) : ℝ) := Nat.cast_le.mpr hcNat
    simpa only [Nat.cast_add, Nat.cast_mul, Nat.cast_ofNat] using hcast
  have heReal : ((Finset.univ.filter expensive).card : ℝ) ≤ (B : ℝ) :=
    Nat.cast_le.mpr hexpensive
  have hcrsum := Finset.sum_le_sum (s := Finset.univ) (by intro e _; exact hcr e)
  have hcrsum' : 2 * (∑ e, crCapacity e) ≤
      (∑ e, weight (remainingSlot (.inr e))) +
      11 * (Fintype.card CR : ℝ) + (∑ e, gain e) := by
    rw [← Finset.mul_sum, Finset.sum_add_distrib, Finset.sum_add_distrib] at hcrsum
    simpa [mul_comm] using hcrsum
  linarith

/-- The critical Round3 arithmetic, stated over exact integers. -/
theorem critical_profile_arithmetic :
    (388 + 77 * 6 + 10 * (6 ^ 2 / 4) + 51 : ℕ) = 991 := by
  norm_num

/-- All six final cube-profile arithmetic bounds. The geometric premises
that justify these residual energies and gains are not asserted here. -/
theorem six_boundary_arithmetic :
    (458 + 77 * 5 + 10 * (5 ^ 2 / 4) + 69 : ℕ) < 992 ∧
    (388 + 77 * 6 + 10 * (6 ^ 2 / 4) + 51 : ℕ) < 992 ∧
    (445 + 77 * 5 + 10 * (5 ^ 2 / 4) + 64 : ℕ) < 992 ∧
    (375 + 77 * 6 + 10 * (6 ^ 2 / 4) + 45 : ℕ) < 992 ∧
    (450 + 77 * 5 + 10 * (5 ^ 2 / 4) + 67 : ℕ) < 992 ∧
    (380 + 77 * 6 + 10 * (6 ^ 2 / 4) + 48 : ℕ) < 992 := by
  norm_num

/-- Once the finite-incidence theorem has supplied the bound991, doubled
coverage demand992 is impossible. No geometric premise is hidden here. -/
theorem critical_profile_exclusion (capacity : ℝ)
    (hupper : 2 * capacity ≤ 388 + 77 * 6 + 10 * 9 + 51)
    (hcoverage : 992 ≤ 2 * capacity) : False := by
  linarith

end KakeyaRound4

#print axioms KakeyaRound4.pair_capacity_energy
#print axioms KakeyaRound4.weighted_pair_capacity_energy
#print axioms KakeyaRound4.sum_injective_resource
#print axioms KakeyaRound4.remaining_energy_budget
#print axioms KakeyaRound4.cube_incidence_count
#print axioms KakeyaRound4.cube_edge_budget
#print axioms KakeyaRound4.cube_other_surplus_row
#print axioms KakeyaRound4.small_surplus_table
#print axioms KakeyaRound4.surplus_zero_of_ge_five
#print axioms KakeyaRound4.cube_master_bound
#print axioms KakeyaRound4.critical_profile_arithmetic
#print axioms KakeyaRound4.six_boundary_arithmetic
#print axioms KakeyaRound4.critical_profile_exclusion
