Lecture 14: Query Optimization Cost & Search

Intro/Needs of Query Optimization
- Start w/ a closed set of operators (select, join) & tables to apply them to & how we will actually physically implement those
  operators (can use grace hash join, page nested loop approach, etc.)
  1. First, need to develop a plan space: what are the various ways in which we can order & choose physical implementations of operators
  2. Then, need to estimate cost, based on cost formulas & engage in cost estimation based on catalog info & selectivity estimation, which
     determines size of inputs to downstream operators
  3. Ultimately, go through plan space w/ their cost estimates to find the cheapest method
- We are working w/ System R optimizers, though query optimization is still an iterative process
	- System R estimation works well w/ 10-15 joins, but beyond that we need to use heuristics instead
- We know that the plan space is too large to parse completely, so we can prune subtrees w/ subplans that are suboptimal
	- Can also improve performance by using heuristics of using left deep plans & not using any cartesian products
- When estimating cost, typically will not end up w/ actual cost, but in practice this estimation is fine
	- Usually use CPU & IO costs in estimates, based on statistics provided in the system catalogs

Plan Space
- Want to break down query blocks into its subcomponents, then perform optimizations a single block at a time
- Uncorrelated query blocks (do not reference outer blocks) can be run a single time. Meanwhile, correlated query blocks need to be
  recomputed across all the records for the outer block
- Within a block, each plan contains: all possible access methods & left deep join trees, join trees where right branch is the table we
  start w/, bearing in mind various ways of ordering & implementing the joins

Example Setup
- Example query: Select S.sname From R, S Where R.sid = S.sid and R.bid = 100 and S.rating > 5
- Setup: Assume we have the following schema: S (sid: int, name: text, rating: int, age: real) R: (sid: int, bid: int, day: date, name: text)
	- R will have records of size 40 bytes, 100 tuples/page, 1000 pages w/ 100 unique boats. 
	- S: 50 byte records, 80 records/page, 500 pages, w/ 100 unique ratings
	- We will also be operating over 5 pages when conducting our join operations. As such, B = number of buffers = 5

Physical Properties of Query Plans
- Output physical properties: output is either sorted or not & output can be hashed (matches can be grouped together)
- Certain operators create these properties: index scan & generic sort creates sorted, hashing will create hash grouping
- Certain operators need these as inputs: merge join (takes in sorted input in order to join the results)
- Operators preserving input properties: merge join takes in sorted input, and creates an output sorted in same fashion. INLJ
  meanwhile willkeep sort order of outer input

Queries Across >1 Table
- Saw before that we only want to consider left deep join trees to dec search space, since they include fully pipelined plans which do not
  require use of materialized, intermediate tables
  - Does not include trees that do not have left subbranch as having greatest height and not having plans that we can prune along the way
- Given an SQL query, can use relational algebra equivalence & fashions of physical implementation to generate a full plan space
	- Then, prune space based on discussed properties of optimizing for selection/projection pushdown, preserving only the left deep
	  trees, and not using any cross products in our table

Cost Estimation
- With any plan, we need to consider the cost of all the various operations included in a plan tree, which depends on the
  size of the initial inputs, which we have previously analyzed across various operations (scans, joins, etc.)
  - Each time, we need to find the size of the end result of applying an operation in the tree, as results may be used downstream
- System R (which we are using), the cost is determined by: number of IOs + CPUfactor * number of records
- Catalogs typically contain the following info: number of tuples (NTuples), number of disk pages in table (NPages), minimum and max
  value held in a given column (low/high),  number of distinct values in a column, index height (IHeight), number of disk pages in a
  index (INPages)
  - Need to periodically update pages to reflect insertions/deletions since we cannot afford to constantly update
  - In reality, most systems track much more info than what was listed in the catalogs. Might keep info about distribution of values in a column
- Estimate size: we know the size of possible outputs cannot exceed the product of all the sizes of the inputs (assuming no selections)
- For each join/select predicates, need selectivity (sel) of each term, which is this ratio: |output|/|input| (how much did we reduce output cardinality by from max)
	- Higher selectivity means the cardinality of output, |output|, is larger, which means that we filtered out less of the input

Result Size Estimation
- Estimate result size: |result| = max num tuples * product across all selectivities, so we need to find selectivity of each individual term
	- Ex 1: col = val --> selectivity = 1/NKeys(l) since we are reducing number of possibilities by a factor of number of keys of a column
	- Ex 2: col1 = col2 --> selectivity = 1/max(NKeys(l1), NKeys(l2)), taking larger of the number of keys of each column
	- Ex 3: col > val --> selectivity = (High(l) - value)/(High(l) - Low(l) + 1) --> selectivity finds proportion of records that fall w/in a range, so
	  we find the range of the query divided by the size of the entirety of the range
- Also have default values to use w/ selectivity estimates if none provided: Col = val: 0.005, Col < val: 1/3, etc.

Selectivity With Histograms
- Assume we store a histogram of values for each column, in which we store the frequency of range of values across a given column in a table
	- Can either use equiwidth (bin size are equal) or equidepth (adjust size of bins so that same number of records are in each bin)
	- Idea of equidepth: the more frequent, concentrated data still have their own partition, allowing us to get better granularity in analysis
- Ex 1: We have 100 records, and want to select p > 99 based off of a histogram. Assume that 50 of the tuples obey this condition --> selectivity = 50/100
- Ex 2: assume we have histogram of age w/ bins of size 5 w/ ages from 5-60. Want to estimate age < 26: since we do not have that level of granularity, we
  use uniformity assumption (each value w/in a bin is equally likely) to compute the estimate (assume 46%)
- Ex 3: assume we want to find p > 99 and age < 26: assuming that these predicates are independent, then we can multiply the selection factors of
  each of these to find the total shrinkage/selectivity: 0.5 * 0.46 = 23%
- Ex 4: want to find selectivity of p > 99 or age < 26: need to bear in mind that there are potentially overlapping results, so we know that 23% overlap,
  50% satisfy first, 46% satisfy second --> 73% satisfy one or the either by subtracting overlap
- Ex 5: (R TJ_p σ_p(S)), given that we are handed selectivity of p as s_p and selectivity of q as s_q & want to find overall selectivity
	- Known: (R TJ_p S = σ_p(R x S)), since theta-joining 2 tables on a specific column is equivalent to finding cross product & filtering out irrelevants
	- As such, we know that the join selectivity must be s_p over the entirety of the input (which is |R| x |S|), producing s_p*|R|x|S| sized output
	- (R TJ_p σ_q(S)) = σ_p(R x σ_q(S)) = σ_(p^q)(RxS) --> Selectivity = s_p * s_q * |R|x|S| since we can multiply the selectiity factors
	- Key takeaway: when we have join operations, find selectivity of individual predicates, multiply by product of original table sizes

Column Equality
- Assume we want to find: T.col1 = T.col2, assuming uniformity w/in bins but the distribution across bins is given by the histograms
- P(T.col1 = v) = height(bin_col1(v))/n * 1/width(bin_col1(v)) where across all values in either histogram, need to find the width/height of the bin that
  contains that value, w/ a taller bin being weighted more and a wider bin being weighted less (less likely to take on a specific value)
  - Can calculate the col2 probability in exact same way: P(T.col2 = v) = height(bin_col2(v))/n * 1/width(bin_col2(v))
- P(T.col1 = v, T.col2 = v) = P(T.col1 = v) * P(T.col2 = v) & add up across all possible values of v across the 2 columns

Search Algorithm
- 2 primary cases to enumerate "other" plans: single table plans and w/ plans involving multiple tables
	- Single table plan: can include selections, projections, groupby/aggregationsin which we consider all possible
	  paths to reach end goal & pick one that has lowest estimated cotst, in which selection/projection are performed
	  as we use other techniques along the way
1. Index on primary key matching selection has following cost: (Height of index + 1) + 1, traversing to leaf node and retrieving record from the leaf
2. Clustered index w/ matching selection cost = (NPages(I) + NPages(R)) * (selection factor product), since HeapFilePages * selectivity provides
   number of pages that we need to analyze in the heap file. IndexPages * selection comes from pages examined at leaf level, constituting majority of index reads
3. Unclustered Indx w/ > 1 selects Cost = (NPages(I) + NRecords(R)) * (selection factor product), since this is an unclustered index we need to go through
   all the records in the heap file (there is no coherent ordering, need 1 IO per matching tuple)
4. Sequential Scan of a File: NPages(R) as we need to just go through all the pages in the original heap file (still only accessing data)

Example: Select S.sid From S Where S.rating = 8 (using index on rating)
- Cardinality of output = (1/NKeys(I)) * NTuples(R) = 1/10 * 40000 = 4000 records, since there are 10 possible ratings & we only preserve 1/10 of them
- Clustered Index = 1/(NKeys(I)) * (NPages(I) + NPages(R)) = 1/10*(50+500) = 55 pages (1 read each), based off the formula/intuition for the clustered index above
- Unclustered Index = 1/(NKeys(I)) * (NPages(I) + NRecords(R)) = 1/10*(50+40000) = 4005 pages (still 1 read each)
- Assume instead we now had an index on SID as well: still need to get all the original records/pages, but now incur cost of reading the index
  pages as well. Thus, this would incur cost of 50 + 500 = 550 IOs using clustered index, but 50 + 40,000 IOs for unclustered index since for each
  record that we read, we need to read a different page

Enumeration of Left Deep Plans
- Left deep plans are only different in the ordering of tables (still same shape of tree), access method (index scan, heap scan, etc.) & join method
- Do not want to have to use all trees, so instead we can filter out trees based off of common subtrees/subplans
- Principal of Optimality: uses fact that the optimal plan will be the composite of all the best subplans conjoined
	- Idea: assume that we want to optimally join ABC --> solution must be: 1. (bestJoin A, B) TJ C, 2. (bestJoin A, C) TJ B, 3. (bestJoin B, C) TJ A
	- Under this presumption, when dealing w/ optimizing (A TJ B), we can ignore how that result will be used downstream
	- Meanwhile, w/ the "higher calling" (A TJ B) TJ C, we assume that A TJ B automatically hands us the best result
- Principal of Optimality Algorithm: 1. Find best plan of height 1 recording results, 2. Find best plans of height 2 based on joining of
  plans of height 1, then keep iterating until we end up w/ composite tree
- Need to account for physical properties breaking principal of optimality. A suboptimal plan might have certain properties, such as sort order,
  which will save work for downstream operations
  - Thus, the "best" substructure needs to account for physical properties beyond the initial set of tables
  - Consider relevance of a table ordering if the intermediate results can be used by a downstream uery involving order by/group by/joins
- Dynamic programming table is updated to include preserves tables & ordering of columns, for which we obtain the best plan based of dif orderings
- Initially, figure out scan/join ordering, avoiding cartesian products, preserving subplans only when there is a join condition b/w them or when all predicates
  in WHERE clause have been exhausted leaving only predicates of the FROM clause
  - Deal w/ order by, group by, aggregation functions only after dealing w/ the initial scans/joins

















