# Rigidity of nine residues with twenty-eight differences

**Theorem.** If T subset F_2^5 has nine points and exactly twenty-eight distinct nonzero pair differences, then, after an affine change of coordinates,

    T=(H\{0,d}) union {x,y,x+y},

where H is a three-dimensional linear subspace, d is a nonzero element of H, and V=H direct-sum <x,y>.

Its three missing directions are

    F={d+x,d+y,d+x+y}.

They are linearly independent. Among the twenty-three residues outside T, the number of heavy neighbours through directions F is distributed as follows:

| Number of neighbours in T through F | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| Number of outside residues | 1 | 18 | 3 | 1 |

In particular, exactly one residue has three such neighbours, and the four residues with at least two neighbours form an affine plane.

## Proof of the normal form

For a nonzero direction z, write p(z) for the number of unordered z-pairs in T. A direction with four pairs would make T consist of four full <z>-cosets and one singleton. Its difference set would then have at most one within-pair direction, twelve directions between the four full cosets, and eight singleton-to-pair directions, totaling at most21. Hence p(z)<=3.

Let n_j count directions with p(z)=j. Total pair mass is36 and total represented directions28, so

    n_2+2n_3=8.

Every zero-sum four-subset is an affine plane and contributes three pair partitions. Therefore

    n_2+3n_3

is divisible by three. It follows that n_3=1 or n_3=4.

If n_3=4, then n_2=0. For two distinct directions z,w with three pairs, use the symmetric-difference distance D(u)=9-2p(u). Its triangle inequality gives D(z+w)<=6. The value is positive odd, so D(z+w)<=5 and p(z+w)>=2. Since no direction has pair count two or four, p(z+w)=3. Thus zero together with the four three-pair directions would form a linear subspace of order five, impossible.

Consequently there is exactly one direction d with three pairs, six directions with two pairs, and twenty-one with one pair.

The six points participating in the three d-pairs form an affine three-flat with one d-coset removed. Translate the missing coset so that these six points become B=H\{0,d}, with H linear of dimension three. Their pair spectrum is three in direction d and two in every other nonzero H-direction. These already account for every repeated direction in T.

Each of the remaining three points lies outside H: adding either missing point in H would produce a seven-point subset of H, with seven directions having three pairs. Moreover, the three outside points lie in distinct H-cosets. Two in the same coset would create an additional pair in H, increasing the existing count three to four or a count two to a second count three.

Call the outside points x,y,z. They occupy the three nonzero cosets of V/H, so sigma=x+y+z belongs to H. The pair x+y has difference z+sigma. The six cross-pairs between z and B already represent z+B, and no direction outside H can repeat. Therefore sigma is in the missing coset {0,d}.

Translate all points by sigma. The set B is unchanged because sigma belongs to its period subgroup {0,d}; the three translated outside points now have xor zero. They can be written x,y,x+y. Their images modulo H are independent, giving V=H direct-sum <x,y>. This proves the normal form.

The missing directions are precisely d+x,d+y,d+x+y. Their sum is d!=0, and no pair sums to the third, so they are independent.

## Proof of the neighbour distribution

Write H=<d> direct-sum U, where U has dimension two, and W=<x,y>. Every residue a has a unique form alpha*d+u+v with alpha in F_2, u in U and v in W.

If u!=0, the translate a+F can meet T only in H\{0,d}, and only when v!=0. In that case exactly one of its three points has W-coordinate zero. There are3*2*3=18 such residues, each with one neighbour; the six with v=0 are already in T.

If u=0 and alpha=0, then a+F has d-coordinate one and cannot meet T; among these four residues, the three nonzero elements of W are in T and the sole outside residue is0.

If u=0 and alpha=1, then a+F is the translate v+(W\{0}). It meets T's W-triangle in all three points when v=0, and in two points when v!=0. Thus a=d is the unique three-neighbour residue, while d+x,d+y,d+x+y are the three two-neighbour residues. Together they form d+W.

All assertions follow. The proof is analytic and has no affine-orbit census dependency.
