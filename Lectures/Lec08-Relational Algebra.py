Lecture 8: Relational Algebra

Intro to Relational Algebra
- Query parser parses a SQL query to provide a more efficient way to run the initial query
- Query parser translates initial query into relational algebra, which can be represented as a tree of operators/operands,
  (also called a logical query plan) which then get converted into the optimized version by the optimizer
- SQL vs relational algebra: SQl is strictly declarative (describes end result). Relational algebra is operational: informs
  us the operations that we need to actually take to execute a given query
- Sample SQL query: Select S.name From R, S Where R.sid = S.sid and R.bid = 100
	- SQL has the benefits of being declarative (do not need to think about how the results are obtained) and utilizes relational calculus
- Relational calculus formed basis for SQL, which describes results of computation using first order logic
- Meanwhile, relational algebra is based on sets & provides operations & ordering to obtain the results
- Codd Theorem: determined how to go b/w relational calculus and relational algebra, which is critical b/c it allows us
  to connect declarative & operational version


Operators
- We will apply algebra operators on instances of relations. Imperatively, the result of applying operator on a 
  relation will be a relation which allows us to nest operators
- Relational algebra has the property of being typed, which allows us to determine if queries are legal before running them
- Unary operators: operate on a single relation. Example operations include: projection, selection, renaming
	- Projection: keep only desired columns, Selection: preserve subset of rows, Renaming: give names to relations/attributes
- Binary operators: applied on on pair of relations, which includes union, set difference, and cross product
	- Union: include relations in either R1 or R2, Set Difference: preserve elements in R1 that are not in R2, Cross Product:
	  combine the 2 relations by taking all possible combos of each
- Compound operators: allow us essentially to apply macros of the above
	- Intersection: keep rows in R1 and R2, Join: combine rows that obey certain predicates

Unary Operators: Projection, Selection, Rename
- Projection, denoted by π, corresponds w/ select query and chooses a subset of the columns given a table
	- Ex: π_name, age (S2): provides a relation S2 that keeps the name & age columns from the table we are working w/
	  - The schema of the new table is determined by the original table (name is VARCHAR, age is an int)
- Projection automatically removes duplicates b/c it is operating under set semantics, which does not allow for duplicates
- Selection, denoted by 𝜎, corresponds to the where clause in SQL, w/ an output matching the schema of the input
	- Does not require elimination b/c original table cannot have duplicates & takes a subset of that
	- Ex: 𝜎(rating>8, S2) will provide the all the columns in the table who have a rating > 8 based on original table
- Composing Select/Project Ex 1: π_name(𝜎_rating>8(S2)) will first keep only rows that have a rating > 8 --> then we select a single
  column from the resulting table
- Composing Select, Project Ex 2: s_rating>8(pi_name(S2)) will cause an error since the output of the inner relation does not
  have a rating column hich is used by the select query
- Rename (𝜌): renames relations & attributes which operates on schema level (does not change the data itself)
	- 𝜌(temp1(1->sid1, 4->sid2), r1*s1) means we change column1 name to sid1, column2 name to sid2.The 2nd argument is just the
	  relation to which we want to rename something, temp1 = name of the output relation we desire

Binary Operators: Union, Set Difference, Cross Product
- In order to apply the union operator, relations need the same number of fields w/ the same corresponding type. Is union operator in SQL
- Union/Union All Difference: union all will not eliminate duplicates unlike UNION operator
- Set difference: same criteria as union for compatibility, same as except in SQL (no need for duplicate elimination)
	- Except vs. Except All: except all does not remove duplicates when preserving the elements in the original table
- Cross Product: r1 * r2 provides all possible concactenation of rows from R1 and rows from R2
	- Results in |r1|*|r2| rows, does not require both tables to have same schema, and ensures no duplicates get generated since
	  the original tables that we worked w/ had no duplicates anyway

Compound Operators: Intersection, Join
- Intersection requires input relations to be compatible (same schema) --> outputs rows in both S1 and S2 (overlap)
	- As a compound operator, IntersectionResults = S1 - (S1 - S2) since S1 - S2 provides elements exclusively in S1, so subtracting
	  that from original S1 will provide elements in S1 that are also in S2
- Join is another compound operator that can take the fom of theta-join, equi-join, or natural joins
	- Theta join: cross product followed by any logical expression to filter, equi-join: theta join that uses conjunction of equalities,
	  natural join: form of equi-join whose conjunctions are on columns of same name b/w tables
- Theta join example: R1 theta_join(sid) S1 matches sid from R1 and R2 to find the conjoined table
	- Can also use: S1 theta_join(age1 > age2) S1 will provide pairs of sailors who have an older and younger one
- Natural Join: case of natural join where equality is based on all fields that occur in both tables, and gets rid of the duplicate
  field/column in new table
  - Ex: R natural_join S = R * S on all their overlapping columns

Groupby/Summary
- Group By/Aggregation(𝛾) allows us to aggregate by some columns and then preserve subset w/ aggregate-level selection function
	- 𝛾_age,ave(rating) (Sailors) --> provides a table grouped by age, which includes the average rating of that group
	- 𝛾_age,ave(rating), Count(*) > 2 (Sailors) --> same as above but only keep groups w/ 2+ entries
- Relational algebra provides a set of operators that translate an input relation into an output relation
	- Relational algebra is operation, which means order of operators does indeed matter
	- Also operating w/ a closed set, meaning that input is a relation, and output is also a relation
	- Operators include: project, select, rename, union, set difference, cross product, join



print(clock(4, 'apropercoppercoffeepot'))
