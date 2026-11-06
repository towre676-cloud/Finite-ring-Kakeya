# Analytic exclusion of the second support-19 maximum-12 profile

## Exact scope

This proof excludes every residue placement and every tangent-fibre realization, over either Z/4Z or F_2[epsilon]/(epsilon^2), of the n=5 fibre-weight multiset

    [12,8,8,8,8,8,8,6,5,4,2,2,2,2,2,2,2,2,2].

There are nineteen pair-active fibres, with total size 93. No other fibres are occupied in this exact profile. The proof also excludes configurations obtained by decreasing any of these fibre sizes at fixed residues, because every necessary coverage bound only decreases.

The heavy set T consists of the eight residue labels whose fibre weights are

    [12,8,8,8,8,8,8,6].

The remaining eleven low fibres have weights [5,4,2,2,2,2,2,2,2,2,2].

## Lemma 1: eight residues leave at least six missing directions

Every eight-point subset T of F_2^5 contains an affine plane. To see this, form the six-by-eight matrix with columns (1,t), t in T. Its binary kernel has dimension at least two. Its nonzero vectors have even weight, and cannot have weight two because the columns are distinct. If there were no affine plane, no kernel vector could have weight four, so every nonzero kernel vector would have weight at least six.

Choose independent kernel vectors u,v. The three vectors u,v,u+v would then have total Hamming weight at least eighteen. However, at each of the eight coordinates, their three bits contain either zero or two ones, so the total weight is at most sixteen. This contradiction proves the assertion.

There are twenty-eight unordered pairs of T. A contained affine plane produces three directions with at least two pairs each. Hence at most twenty-five nonzero directions occur as pair differences. The set F of missing heavy-heavy directions therefore has size r>=6.

## Lemma 2: the extremal six missing directions form an affine three-flat minus a line

Suppose T has exactly twenty-five nonzero pair differences. Choose an affine plane in T and translate it to a two-dimensional linear space U. Its three nonzero directions consume the entire excess

    28-25=3

of pair multiplicity over distinct differences. Thus those three directions each have exactly two pairs; every other occurring direction has exactly one pair. In particular, this affine plane is unique.

Write the four points outside U as x_1,x_2,x_3,x_4. They lie in distinct nonzero cosets of U: if two occupied the same coset, their difference would belong to U and produce a third pair in one of its three directions.

Their images in V/U=F_2^3 are sumfree. If the sum of two images equalled a third, then the corresponding outside pair would have its difference in the same U-coset as that third point. Every direction in that coset already occurs as a cross-pair between U and the third point, producing a repeated direction outside U, which is impossible.

Four distinct nonzero sumfree vectors in F_2^3 must be an affine plane avoiding zero. Indeed, any three are linearly independent, and the fourth cannot be zero, one of those three, or the sum of any two; it must be the sum of all three.

Choose the first three outside points as c,d,e. They are independent modulo U, so together with any basis of U they form a basis of V. The fourth outside point has the form

    h+c+d+e,       h in U.

We have h!=0, since otherwise the four outside points would themselves form a second affine plane. Choose b in U\<h>. Thus

    T = U union {c,d,e,h+c+d+e},
    U = <h,b>.

The occurring directions are precisely:

- the three nonzero directions of U;
- all four directions in each coset U+c, U+d, U+e, U+c+d+e;
- the two directions `{0,h}+v` in each coset indexed by
  `v in {c+d,c+e,d+e}`.

Consequently the six missing directions are

    F = {b,b+h}+{c+d,c+e,d+e}
      = (b+<h,c+d,c+e>) \ (b+<h>).

In particular, F is an affine three-flat minus an affine line. All its vectors lie in the character halfspace ell=1, where

    ell(b)=1,     ell(h)=ell(c)=ell(d)=ell(e)=0.

Thus F is sumfree, and every pair whose difference belongs to F crosses the two ell-halfspaces.

This classification proves the needed extremal geometry directly. It does not use the finite census of eight-point affine orbits.

## Lemma 3: missing heavy directions require at least 4r-2 low pairs

For a nonzero direction d, write p_a(d) for the tangent d-pair count in fibre a. The necessary Kakeya coverage inequality in dimension five is

    sum_{residue edges {a,a+d}} p_a(d)p_{a+d}(d) >=16.

For d in F there is no heavy-heavy residue edge. Let

    m_d = sum_{low residues a} p_a(d).

All heavy fibres except the twelve-point fibre have pair count at most four. The twelve-point fibre has pair count at most six, while every low fibre has pair count at most two.

Let q_d be the low endpoint's pair count on the edge incident to the twelve-point fibre, if that edge has a low endpoint; otherwise let q_d=0. Then every possible coverage configuration satisfies

    16 <= 4m_d+2q_d,       0<=q_d<=2.

Indeed, a nonhub heavy-low edge contributes at most four times its low pair count, the twelve-point edge contributes at most six times its low pair count, and a low-low edge contributes at most four times the sum of its two low pair counts. Low pair counts whose partner residue is empty only enlarge this upper bound.

If m_d<=2, the right side is at most twelve, a contradiction. If m_d=3, the inequality can hold only when q_d=2. Only the five-point and four-point low fibres can have two pairs, and each has exactly one residue direction connecting it to the twelve-point fibre. Therefore at most two directions in F can use m_d=3. Every other direction requires m_d>=4, giving

    sum_{d in F} m_d >=4r-2.                                (3.1)

On the other hand, the total pair mass of the low fibres in all directions is

    binom(5,2)+binom(4,2)+9*binom(2,2)=10+6+9=25.

Thus 4r-2<=25, so r<=6. Lemma 1 forces r=6 exactly.

## Final contradiction

By Lemma 2, the six directions in F all lie in one character halfspace ell=1. In a w-point tangent fibre, the number of unordered pairs crossing that halfspace cut is at most

    floor(w^2/4),

because splitting the fibre into populations x and w-x yields x(w-x) cross-pairs. Therefore the total low pair mass in F is at most

    floor(5^2/4)+floor(4^2/4)+9*floor(2^2/4)
       =6+4+9=19.

But (3.1) requires at least

    4*6-2=22.

The contradiction 19<22 excludes the entire profile, uniformly over all residue arrangements and tangent shapes, in both rings.

## Independent agreement

The middle-maxima agent independently derived the same missing-direction classification and exclusion. Its coordinate-free description of F as an affine three-flat minus a line agrees with the normal form above. The producer/root's demand argument was independently checked here, including the fact that there are at most two three-pair exceptions, not two exceptions per direction.
