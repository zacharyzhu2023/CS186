Lecture 13: Query Optimization


Intro to Query Optimization/Parsing
- Idea: Queries are first translated into their relational algebra form, which can be representd via a tree. Each operator that we
  use can be implemented concretely in different ways & applied in dif orders than originally listed
- 3 primary concerns of query optimization: 1. Plan space (how can we actually execute a given query), 2. Cost estimation (how do we figure out
  IOs associated w/ each way of executing a query), 3. Search Strategy (how do we efficiently look through potential plans)
	- While we would like to find the plan w/ the lowest actual cost, we need to use heuristics to find query plan w/ lowest estimated cost


Relational Algebra Equivalence
- Selection cascades: σ_(c1^c2...)(R) = σ_c1(σ_c2...(R)) meaning applying AND of predicates is the same as nesting select on predicates
- Selection commutes: σ_c1(σ_c2(R)) = σ_c2(σ_c1(R)) meaning order by which we filter out rows does not matter in end result
- Projection cascades: π_a1(R) = π_a1(π_(a1...an)(R)), allowing us to nest multiple projctions
- Cartesian product is commutative, R*S = S*R and is associative, R*(S*T) = (R*S)*T since we are finding all possible combos across all tables
- Can think of joins as cartesian products on which we apply selections but need to be careful about how we apply commutivity and associativity
	- Example: R(a, z), S(a, b), T(b, y) in which R and S share column a, meanwhile S and T share column b
	- Ex 1: (S TJ_(b=b) T) TJ_(a=a) R != S TJ_(b=b) (T TJ_(a=a) R) since the RHS is not legal since tables T, R do not share columns
	- Ex 2: (S TJ_(b=b) T) TJ_(a=a) R != S TJ_(b=b) (T x R) since RHS does not preserve the predicate on A when joining
	- Ex 3: (S TJ_(b=b) T) TJ_(a=a) R = S TJ_(b=b and a=a) (T x R) is indeed the same since we are applying the same end predicates when
	  filtering out the rows that we do not want
- Ultimately, some join queries will lend themselves to cross products while this will not always be the case

Relational Algebra Heuristics
- Selection cascade/pushdown: once we know which columns we want to preserve, then we automatically will apply selections
	- Ex: π_name(σ_(bid=100^rating>5) R TJ_(sid=sid) S) --> π_name(σ_(bid=100)(R) TJ_(sid=sid) σ_(rating>5)(S)) since once we know
	  that we are filtering on bid & rating, we know that we can apply those filters beforehand to the relevant tables before joining
	  - This makes the inputs to the join smaller (implicitly assumes that joins are the more expensive operations)
- Projection cascade/pushdown: preserve only the columns that we need to use in future evaluations
	- Ex: π_name(σ_(bid=100^rating>5) (R TJ_(sid=sid) S)) = π_name(π_sid(σ_(bid=100)(R))) TJ_(sid=sid) π_(name,sid)(σ_(rating>5) S)
		- LHS: upon filtering out on boatID = 100, we only want the SID associated w/ table R. Thus, we can apply the selection
		  on that filtered table to only keep SID & join against name & SID & name of the S table upon filtering that as well, before joining
- Other general heuristics: want to avoid performing a cartesian products whenever possible, perfering theta-joins as a less-costly alternative
	- Ex: R(a,b), S(b, c), T(c,d): (R TJ S) TJ T is better than (R x T) TJ S since the 1st option avoids having to use a cross-product

Physical Equivalence
- Idea: we want to figure out what the equivalent ways of implementing a given algorithm might be
- Ex 1: With a single given table, we might want to perform a heap scan or an index scan (requires us to have an index operating over a given column)
- Equijoin: as previously discussed, we have multiple potential algorithms: block nested loop (is simple & just scans 2 tables on the block/chunk level), 
  index nested loop (useful when 1 table is much larger relative to the other & has an index), sort merge join (useful when we do not have much memory
  to work w/ & have approximately same sized tables), grace hash join (better when 1 of the tables is smaller)
- However, if we are not using an equijoin in the case of a different equijoin, then we are left w/ a single option: block nested loop

Example Setup
- Example query: Select S.sname From R, S Where R.sid = S.sid and R.bid = 100 and S.rating > 5
- Setup: Assume we have the following schema: S (sid: int, name: text, rating: int, age: real) R: (sid: int, bid: int, day: date, name: text)
	- R will have records of size 40 bytes, 100 tuples/page, 1000 pages w/ 100 unique boats. 
	- S: 50 byte records, 80 records/page, 500 pages, w/ 100 unique ratings
	- We will also be operating over 5 pages when conducting our join operations. As such, B = number of buffers = 5

Plan 1: Scan, Filter, Nested Loop Join
- We can do the following: scan through S, scan through R, perform a theta join on SID w/ page nested loops, then filter by rating > 5,
  apply filter of bid = 100, and finally select the name from the merged table
- IO cost: scanning sailors cost 500 IOs, need to scan each page of sailors against each of the pages of reserves = 500 * 1000 = 500,000 IOs
	- We can perform the filtering "on the fly"--that is to say, as we are merging the to tables together, we check to see if each resultant
	  query obeys the given conditions, bid = 100 & rating > 5, in order to not include them in the end result
- Still, this clearly suffers from inefficiency due to it not capitalizing on pushing down selection & not taking advantage of any index
- Main objective: we want to use the optimizations that were previously listed in order to minimize the IO cost of such an operation

Example: Plan 2-4 (Selection Pushdown)
- Plan 2: Assume instead we use the following: as we scan through sailors, we only preserve entries that have a rating > 5, then theta-join w/ reserves
  (which we need to scan through), before filtering on bid & keeping the name in the end table
  - Under this plan, assume that 250/500 sailors obey rating > 5. Thus, new IO cost becomes: 500 + 250*1,000 = 250,500 IOs
- Plan 3: If we also pushed down bid = 100: for each page of sailors, we filter reserves that do not obey bid = 100. Still need to scan through all the pages of R
  for each relevant page in S in order to generate the end result --> 250,500 IOs (same cost as above)
  - Idea: pushing selection on the righthand side of a nested loop will not save any IOs
- Plan 4: Assume we first scan bid = 100 records in R, then merged against S records that obey rating > 5: initial scan would cost 1000. Then, assume that 
  10/500 of the records in R obey bid = 100 --> Total IO cost = 1000 + 10*500 = 6000 IOs
  	- We saw before that pushing down the rating > 5 filtering query did not make an impact on IOs (would still result in 6000 IOs)
  	- However, let us assume instead we include this "materialization" operator on rating, which preserves only the results of the filtered out table
  		- As such, we still need to scan through R to get (bid = 100) --> 1000 IOs. Scan through all of S to get (rating > 5) --> 500 IOs. Producing the materialization
  		  table w/ relevant S records costs 250 write IOs. To merge 10 pages against 250 pages --> 2500 IOs, costing total = 1000 + 500 + 250 + 2500 = 4250 IOs
- Plan 5: assume that we scan S to get records obeying rating > 5. Then scan R to get bid = 100, saving the result in the "materialization" table to be theta-joined.
	- IO cost: Scanning S table costs 500 IOs. Scanning R table costs 1000 IOs. Write filtered R table costs 10 IOs. Theta-joining the 10 against the 250
	  pages costs 2500 IOs -> Total = 500 + 1000 + 10 + 2500 = 4010 using the page nested loops
- Plan 6: same scheme as above only instead of using page nested loops we use sort merge join as our chosen algorithm instead
	- Scan S (1000 IOs, preserving 10 records), Scan R (500 IOs, preserving 250 records), Sort S , Sort R, merge based on the number of passes
		- Sorting S: P0: 10 records from select -> (2 runs of size 5 each), P1: (2 x 5) -> (1 run of size 10) --> 10 + 2 * 10 = 30
		- Sorting R: P0: (1 x 250) from select, P1: (1 x 250) -> (4 x 63), P2: (4 x 63) -> (16 x 16), P3: (16 x 16) -> (64 x 4), P4: (64 x 4) -> (1 x 256)
		  which requires 4 passes, but similarly, the initial pass does not require a read since the input is fed in via select:250 + 3*2*250 = 1750
		- Merge S and R: since we have 250 records in S, 10 records in R --> merging requires 260 IOs to write the merged output
	- Total IO cost = (1000+500) + (30 + 1750) + 260 = 3540 IOs
- Plan 7: scan S (500), write materialized table t1 (250), scan reserves (1000), write materialized table t2 (10), sort t1 (2000), sort t2 (40), merge (260)
	- Sort R, Sort S: same as above but incur the initial read cost (S = 10, R = 250) as we are no longer handed R, S filtered records from select
	- Also incurred the additional 260 IOs as a result of us writing t1, t2 compared to before
- Plan 8: 1. Scan S filtering on rating > 5, 2. Scan R filtering on bid = 100, 3. Save results of R filtering to materialized table T1, 4. Merge the results
  via block nested loop on sid = sid, 5. Preserve only the name column
  - Scan S: 500 (keeps 250 records), Scan R: 1000 (keep 10 records), Write T1 (10 IOs), Block Nested Loop: ceil(250/4) * 10 = 630 IOs
  - We go through S on the block level, since we have 4 buffers, we can read 4 pages at a time -> have ceil(250/4) = 63 pages, scanned against each of the 10
    preserved records in R

Projection Pushdown
- Plan 9: 1. Scan R, filtering by bid = 100 & keeping only SID column, 2. Scan S, filtering on rating > 5, preserving only SID and name columns, 3. Join the results
  using a block nested loop join on SID, 4. Keep only the name column of the final table
  	- Idea: Preserving vid = 100 already reduces the size of the table by a factor of 100 and since the original size of each record was 40 and bid is
  	  an integer field of size 4, we can reduce the space needed per record by a factor of 10, so total reduction is by a factor of 1/1000. Ultimately, this
  	  produces a single page that we scan against the S table --> Total IOs = 500 + 1000 = 1500

Index Scan
- Plan 10: 1. Index Scan R, filtering on bid = 100, 2. Scan S using an index scan, 3. Index nested loop join on SID, filtering on rating > 5 as we go
	- Assume that R.bid is clustered, S.sid is unclustered (but SID is the primary key anyway, so each entry would need to be on separate page anyhow)
	- Index scan of R: we only care about records that meet bid = 100 --> 1000 records across 10 pages
	- For each of the tuples in R, find matching S record (1 IO for each of the 1000 records) --> 1010 IOs in total





