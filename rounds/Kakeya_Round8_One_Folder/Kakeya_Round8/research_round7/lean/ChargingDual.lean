import CubeMaster

/-!
Finite charging certificate behind the new heavy/light profile screens.
The geometry must supply the incidence injections, per-edge prices, and
coverage requirement.  This module verifies that those resources cannot
be counted twice and that a strict dual gap gives a contradiction.
-/

open scoped BigOperators
namespace KakeyaRound7

theorem light_light_price (p q t u capacity : ℝ)
    (hp : 0 ≤ p) (hq : 0 ≤ q) (hpt : p ≤ t) (hqt : q ≤ t)
    (htu : t ≤ u) (hcap : capacity ≤ p * q) :
    2 * capacity ≤ u * (p + q) := by
  have hleft := mul_le_mul_of_nonneg_left hqt hp
  have hright := mul_le_mul_of_nonneg_left hpt hq
  have hprice := mul_le_mul_of_nonneg_right htu (add_nonneg hp hq)
  nlinarith

theorem heavy_light_price (capacity tableBound u q excess : ℝ)
    (hcap : capacity ≤ tableBound)
    (hprice : 2 * tableBound ≤ u * q + excess) :
    2 * capacity ≤ u * q + excess := by
  linarith

theorem two_type_charging_bound
    {LL HL LightSlot HeavySlot : Type*}
    [Fintype LL] [Fintype HL] [Fintype LightSlot] [Fintype HeavySlot]
    (lightSlot : (LL × Bool) ⊕ HL → LightSlot)
    (heavySlot : HL → HeavySlot)
    (lightInjective : Function.Injective lightSlot)
    (heavyInjective : Function.Injective heavySlot)
    (lightCost : LightSlot → ℝ) (heavyCost : HeavySlot → ℝ)
    (lightNonnegative : ∀ x, 0 ≤ lightCost x)
    (heavyNonnegative : ∀ x, 0 ≤ heavyCost x)
    (lightCapacity : LL → ℝ) (mixedCapacity : HL → ℝ)
    (lightBound : ∀ e, 2 * lightCapacity e ≤
      lightCost (lightSlot (.inl (e, true))) +
      lightCost (lightSlot (.inl (e, false))))
    (mixedBound : ∀ e, 2 * mixedCapacity e ≤
      lightCost (lightSlot (.inr e)) + heavyCost (heavySlot e)) :
    2 * ((∑ e, lightCapacity e) + (∑ e, mixedCapacity e)) ≤
      (∑ x, lightCost x) + (∑ x, heavyCost x) := by
  classical
  have hL := KakeyaRound4.sum_injective_resource
    lightSlot lightInjective lightCost lightNonnegative
  have hH := KakeyaRound4.sum_injective_resource
    heavySlot heavyInjective heavyCost heavyNonnegative
  have hLL : (∑ e, 2 * lightCapacity e) ≤
      ∑ e, (lightCost (lightSlot (.inl (e, true))) +
        lightCost (lightSlot (.inl (e, false)))) := by
    exact Finset.sum_le_sum (by intro e _; exact lightBound e)
  have hHL : (∑ e, 2 * mixedCapacity e) ≤
      ∑ e, (lightCost (lightSlot (.inr e)) + heavyCost (heavySlot e)) := by
    exact Finset.sum_le_sum (by intro e _; exact mixedBound e)
  simp only [Fintype.sum_sum_type, Fintype.sum_prod_type, Fintype.sum_bool,
    Finset.sum_add_distrib] at hL
  simp only [Finset.sum_add_distrib, ← Finset.mul_sum] at hLL hHL
  linarith

theorem strict_charging_gap_is_impossible (required supplied resources : ℝ)
    (coverage : required ≤ supplied) (charged : 2 * supplied ≤ resources)
    (gap : resources < 2 * required) : False := by
  linarith

end KakeyaRound7

#print axioms KakeyaRound7.light_light_price
#print axioms KakeyaRound7.heavy_light_price
#print axioms KakeyaRound7.two_type_charging_bound
#print axioms KakeyaRound7.strict_charging_gap_is_impossible
