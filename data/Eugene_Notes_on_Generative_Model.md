Our generative model (so far)

a milk statement is a single line of milk. (a predicate and its arguments)
a milk action is a milk statement  where the predicate is NOT a ``create''
a milk description (of an ingrediant) is its create statement, or, if it does not have one
the create statements of the ingrediates that were used in its formation.

1) partition milk actions into sentence groups according to p(partition | action predicates)
     This is done by the HMM.

For  each  sentence group

2) Pick # of verb phrases according to p(#|sentence=group predicates)
3) Parition group predicates into # VP-groups

For each VP group

4) pick verb accound to p(verb| vp-group prediates and the ingrediant descriptions)
5) pick a verb case-frame according to p(case-frame | vp-group predicates , recency of ing.)

For each NP in verb case frame

6)  generate NP

7) For each sentence group choose how to combine vp's into a single sentence
