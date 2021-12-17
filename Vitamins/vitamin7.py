Vitamin 7: Query Optimization

1.1: (R TJ S) != (S TJ R) --FALSE
- Idea: we can treat a theta-join as the composition of a selection on cross-product: select_(id = id) (R X S)
- Cartesian products are commutative/associative, meaning order of tables does not matter
	- Easy to see why from there that the end result will be the same, since we are filtering from the same rows

1.2: Pushing down selections changes cost of query--TRUE
- Example: Using the Sailors & Reserves table, saw that if we push down selection and use a materialized table,
  this can affect the number of write operations that we need to take
  	- As such, filtering earlier (pushing down selection) can impact IO cost

1.3: Pushing down selection affects end result of a query--FALSE
- Again, if the ultimate table w/o the selection is goingt o be the same, does not matter when we apply filter
  we still get rid of the same values
  - Selections can be cascaded (meaning "and" the predicates is equivalent to applying multiple selections)

1.4: Order of join affects IO cost of a query--TRUE
- Block nested loop join IO cost = NumPages(R) + NumPages(S) * NumRecords(R) so clearly order changes IO cost

Question 2: Query Optimization

2.1: Query optimizer converts a query plan into another query plan
	- Idea: we just take in the tree representation of the operations that we want to engage in and then turn
	  that into a better sequence of operations to execute from IO perspective

2.2: IO Cost of joining n tables --> O(n!)
	- Need to consider all the different orders in which we can join the relation (A TJ B TJ C) vs. (B TJ A TJ C)...
		- This gets further magnified when we consider the different join algorithms that we can use in each instance

2.3: Left Query Plans across n tables --> O(n!)
- Left deep plans have the same tree structure, but differ in terms of table ordering, join algorithm type, and how table is scanned
- Already saw above that there are n! orderings of the original table, magnified by different join algorithms

2.4: Number of plans considered by Selinger Optimizer in arbitrary pass i: O(2^n)
- Selinger Optimizer is exponential in the number of plans that it has to consider
- At pass i: Selinger optimizer is handed (n choose (i-1)) plans from previous iterations
	- Want to check ~n tables for each of these plans (joining another unjoined table)
	- (n choose i) * n --> (n * (n-1) * (n-2)...) * n ~ O(2^n)




