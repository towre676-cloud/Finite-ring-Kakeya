# A systematic integer dual and a sharp eight-vertex improvement

## The dual inequality

Work in the dimension-five binary residue space. Let H be any chosen set
of heavy support vertices. Every remaining fibre must have weight at
most a chosen ceiling ell; write t=floor(ell/2). Heavy vertices may also
have smaller weights. Put

    D(H)={a+b : a,b in H, a!=b}.

Choose an integer price u>=t. Let M(p,q) be a valid upper bound on the
cardinality of the sumset of p and q pair classes in the sixteen-element
direction quotient. The previously reproduced exact capacity table is
one such choice. Define

    g(p)=max(0, max over 1<=q<=t of [2M(p,q)-u*q]).

For a fibre A let G(A)=sum over d!=0 of g(p_A(d)). Then every Kakeya set
with the stated heavy/light assignment satisfies

    32(31-|D(H)|)
       <= u * sum over light fibres of C(weight,2)
          + sum over heavy fibres A of G(A).                 (1)

### Proof

In a residue direction outside D(H) no edge joins two heavy vertices.
For a heavy-light edge, let p be the heavy pair count and q the light
pair count. If q=0 the edge contributes zero. Otherwise q<=t, and the
definition of g gives twice the edge capacity at most u*q+g(p).

For a light-light edge with pair counts p,q<=t, twice its capacity is at
most 2pq<=t(p+q)<=u(p+q). Charge each endpoint's displayed pair resource.

Each vertex participates in at most one edge in any one direction.
Therefore no light directional pair resource is charged twice and no
heavy g(p) resource is charged twice. Summing over all directions outside
D(H), and enlarging the nonnegative resource sums to all directions,
proves (1), since every direction needs sixteen quotient lift labels.
Finally sum_d p_A(d)=C(|A|,2). Ring carry translations preserve sumset
cardinalities, so the same inequality holds in both rings.

## Exact finite dual certificates for weight profiles

For each weight w, the reproduced complete pair-spectrum census gives

    G_w = max over weight-w census histograms h of sum_p h[p]*g(p).

Replacing G(A) by G_w is an upper bound. If a profile and a choice of H
give a right side strictly smaller than a universal lower bound for the
left side, the entire profile is excluded in every placement and in both
rings. This is a finite integer dual certificate; a SAT solver is not
needed for this deduction. The census and capacity table remain explicit
finite dependencies.

For a fixed ceiling and price, all vertices of weight greater than ell
must be heavy. Other vertices may optionally be promoted to H. Starting
with mandatory heavy vertices, the cost change from promoting a vertex
of weight w is

    delta_w = G_w - u*C(w,2).

For a fixed final number of heavy vertices, choosing the eligible vertices
with the smallest deltas minimizes the right side. Testing the first h
entries of the sorted list is therefore sufficient within this family;
no enumeration of all subsets is needed. Each published certificate still
lists its exact heavy positions and can be verified directly without
trusting the optimization algorithm.

## A sharp difference bound for eight heavy residues

For h<=7 the elementary bound |D(H)|<=C(h,2) suffices. For h=8 in F₂⁵
there is the stronger, sharp bound

    |D(H)| <= 25.                                           (2)

If the affine rank is at most four, all differences lie in a space with
at most sixteen points, giving at most fifteen nonzero differences.
Otherwise translate and apply an invertible linear map so that six of
the eight points are 0,e1,e2,e3,e4,e5. Call the two additional vectors
v and w. Their Hamming weights are between two and five.

An additional vector of weight two forms a four-point affine plane with
zero and its two basis vectors. One of weight three forms a plane with
its three basis vectors. If both extras have weight four or five, they
cannot both have weight five. Two distinct weight-four vectors differ in
two basis coordinates, yielding a plane with those two basis vectors.
A weight-four and weight-five vector differ in one coordinate, yielding
a plane with zero and that basis vector. Thus every eight-point set
contains an affine plane.

Such a plane has three directions, each realized by two of its unordered
pairs. Each of those directions saves at least one from the possible
number of distinct pair differences. The twenty-eight unordered pairs
of H consequently yield at most 28-3=25 distinct differences.

The set {0,1,2,3,4,8,16,29} attains twenty-five, so the bound is sharp.
`difference8_bound.py` also checks all 325 normalized rank-five choices;
their difference counts are twenty, twenty-two, or twenty-five.

In (1), using eight heavy vertices therefore gives a left side of at
least 32(31-25)=192, in place of the coarser 32(31-28)=96.

## Artifacts and status

`dual_profile_screen.py` implements the original binomial bound and records
both mandatory and optional-heavy diagnostics. The separately identified
refined script uses (2). Neither script changes the inherited profile
ledger. Every emitted witness is re-evaluated using ordinary Python
integers, and its input/census/capacity hashes are recorded. The `--verify`
route does not require NumPy, which is used only to accelerate discovery.

These are mathematical/code proofs with finite census dependencies, not a
full proof-assistant formalization. The proposed exclusions should be
merged only after the independent audit of their exact witness records.
