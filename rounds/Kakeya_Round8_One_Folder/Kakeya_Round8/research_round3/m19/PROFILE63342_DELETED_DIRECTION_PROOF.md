# A deleted-direction exclusion of support11 parent63342

The profile has a19-point hub, seven own-zero fibres of weight8, two own-positive fibres of weight3, and one own-positive fibre of weight12. Its total size is93.

Choose the hub0 and the12-point residue b as heavy, and delete their joining direction e=b. The other30 residue directions still require30*16=480 quotient lifts, or doubled capacity960. Every remaining fibre has cap at most4.

At a remaining residue a, write p=p_A(a), q=p_A(a+b), and t=p_A(b). These are counts in the three nonzero directions of a binary two-plane. The total pair mass outside the deleted direction is C(w,2)-t. Heavy-light contributions are at most M(p,9) and M(q,6); light-light contributions obey2M(x,y)<=4(x+y). Hence the entire doubled remaining capacity is at most the sum of

    R=4*(C(w,2)-t)+2M(p,9)+2M(q,6)-4*(p+q)

over all nine light fibres. The only heavy-heavy edge was in the deleted direction.

For an own-zero weight8 fibre, p=0, q<=4, and t>=0. Therefore

    R <= 112 + max_{0<=q<=4}(2M(q,6)-4q) = 128.

For an own-positive weight3 fibre, p=1 and q,t are0 or1. If q=1, its three points force the third pair direction to be b, so t=1. If q=0, the displayed expression is at most26. If q=t=1, it is exactly30. Therefore R<=30.

Summing gives

    doubled remaining capacity <=7*128+2*30=956<960.

This excludes the whole weight/own-direction profile for both rings, uniformly over support placement and fibre shapes. It needs no affine census or optimization certificate. The complete binary-plane triple catalogue was used to discover the bound, but the displayed inequalities suffice to verify this particular exclusion.

The profile survived the prior common-shape stage, so this is one additional disjoint exclusion. It leaves9,828 support11 profiles and3,038 support12 profiles, total12,866.
