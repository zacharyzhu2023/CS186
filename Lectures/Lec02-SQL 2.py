Lecture 2: SQL 2

Join Queries
- Basic syntax w/ 1 table: Select [distinct] <cols> from <table> where <pred> group by <cols> having <pred> order by
  <cols> limit <integer>;
  - Behind the hood, this takes the cross product of tables provided, eliminate rows based on where clause, form groups
    based on group by clause, eliminate duplicates if distinct is present, select cols in select, eliminate groups based
    on what is included in having clause
- Sample join queries: Select * from <table1 as t1, ... tableN as tn> where <pred> group by <cols>;
	- This produces the cross product of all n tables: every possible row is merged w/ all the rows from every other table
- Select S.sid from Sailors as S, Reserves as R where S.sid = R.sid
	- This query first creates the cross product of the sailors & reserves table, then filtering out all the rows in which
	  the sid from sailors table does not match sid from reserves table

Other Operations
1. Select x.sname, x.age, y.sname, y.age from Sailors as x, Sailors as y where x.age > y.age
	- We can provide aliases for both the table names and the column names. Need to provide aliases whenever a column
	  name is in both tables to eliminate ambiguity
	- This example will provide age & name combos where age of person1 is greater than age of person2
2. Select s1.age-5 as age1, 2*s1.age as age2, log(1000) as col3 from s1, s2 where s1.rating = s2.rating - 1
	- Can include math operations in where/select clauses but need to provide col name if in select
3. Select S.sname from S where S.sname ~ '^B.*'
	- In new SQL syntax, we can use REGEX syntax. Above, look for names starting w/ B, followed by anything

Boolean Logic: Combining Predicates
1. Select R.id from B, R where R.bid = B.bid and (B.color = 'red' or B.color = 'green')
	- Makes use of the and/or okperators in order to select reserve IDs that have a corresponding red/green boat
	- Alternate syntax that does the same thing: Select R.id from B, R where R.bid = B.bid and B.color = 'red'
	  UNION ALL Select R.id from B, R where R.bid = B.bid and B.color = 'green'
2. Select R.id from B, R where R.bid = B.bid and (B.color = 'red' and B.month = 'Jan')	  
	- Alternative: Select R.id from B, R where R.bid = B.bid and (B.color = 'red') INTERSECT
	  Select R.id from B, R where R.bid = B.bid  and B.month = 'Jan'
3. Select S.sid from S except Select S.sid from S, R where S.sid = R.sid
	- First take all the sailors, then subtract those that have an ID matching a reservation ID, leaving those w/o reservation

Sets
- Set: collection of unique elements, w/ the following operations: union, intersect, except
- Example: R = {a,a,a,a,b,b,c,d}, S = {a,a,b,b,b,c,e}
	--> Union: {a,b,c,d,e} giving all unique elements present in either one or both sets, Intersect: {a,b,c} giving all elements
	    that appear in both sets at least once, Except: {d} as the elements in R but not in S
- Can represent R, S as a multiset by providing the frequency of each element: R = {A,4; B,2; C,1; D,1}, S = {A,2; B,3; C,1; E,1}
	- Union all: Sums the cardinality of each element --> R Union All S = {a6, b5, c2, d1, e1}
	- Intersect All: takes the min of cardinalities --> R Intersect All S = {A2, B2, C1}
	- Except All: takes the dif in cardinality (cannot be negative) --> R Except All S = {a2, d}

Nested Queries
1. Select s.name From s Where s.id in (Select R.id From R where R.bid = 102)
	- This is an instance of a subquery, in which we check the presence of sailor ID among reserve IDs w/ a specific boat ID
	- Can use the same syntax w/ not in front of it to find sailors who have not reserved boat 103:
	  Select s.name From s Where s.id not in (Select R.id From R where R.bid = 102)
2. Select S.name From S Where Exists (Select R.id From R Where R.bid = 103)
	- The exists query returns true when there is 1+ rows remaining in a table
3. Select S.name From S Where Exists (Select * From R Where R.bid = 102 and S.id = R.id)
	- Inner query preserves reserves that have a boat ID of 102 and was reserved by a sailor
	- Since the inner query utilizes an aspect of the table in the outer table, it needs to get recalculated across
	  every row of original S table
4. Select * From S Where S.rating > Any(Select S2.rating From S2 where S2.name = 'Pop')
	- Any/All are examples of other set operators; Any: check if value obeys operation relative to 1+ rows in table and
	  All: checks if value obeys operation to every row w/in the table
	- In this example, we obtain all columns of a table that have a rating greater than all of the ratings of those named Pop
5. Select S.name From S Where Not Exists (Select B.bid From B Where Not Exists (Select R.bid From R Where R.bid = B.bid And R.id = S.id))
	- Innermost query: Check for boat IDs w/ a reservation by a sailor --> need to make sure that does not exist
	- Middle layer: obtain the boat ID for which a reservation is not present given a sailor and all of R --> taking the negative of that, 
	  this means that there is not a boat that remains unreserved by a sailor
	- Putting this together, the query provides all the sailor names that have reserved all boats



Argmax Implementation
- Faulty 1: Select Max(S.rating) From S; # Fails b/c provides the max rating + not the entry that corresponds to
- Faulty 2: Select S*, Max(S.rating) From S; # This fails b/c we cannot have an aggregated + non-aggregated column in select
1. Select * From S Where S.rating >= All(Select S2.rating From S2)
	- Inner query keeps every rating --> then only keep the row if its rating >= every other rating in the table
2. Select * From S Where S.rating = (Select Max(S2.rating) From S2)
	- First compute the max rating, then match that against all the entries w/in the table (accurate results)
3. Select * From S order by rating DESC Limit 1;
	- This will provide a row w/ highest rating but can only provide a single entry (thus might be flawed in that regard)

Alternate Joins
1. Select S.*, R.bid From S Inner Join R On S.sid = R.sid VS Select S.*, R.bid From S, R Where S.sid = R.sid
	- Both these queries are equivalent since inner join takes the cross product that have matching values specified in ON clause
	  while 1st version takes cross product and preserves only entries which have matching SID (same as V1)
2. Select <cols> From <t1> [Inner/Natural/Left/Right/Full] Join <t2> On <Qualifications> Where...
	- Inner is the default join version, but all the other joins are w/ dif specified keyword
3. Select s.id, s.name, r.bid From s Left Outer Join r On S.id = R.id;
	- Gives all matched rows overall plus all unmatched rows in left table, giving null values in unmatched values
	- In this example, that means every sailor/corresponding bid across all boats
4. Select r.id, b.bid, b.name From r Right Outer Join b on r.bid = b.bid;
	- Gives all the matched rows and any entry in right table that is not matched gets filled w/ null values
	- In this example, if a boat does not have a reservation, new table id becomes null
5. Select r.id, b.bid, b.name From r Full Outer Join b on r.bid = b.bid
	- Compute cross product, preserve only entries w/ matching boat/reservation, every other reservation/boat will then
	  be filled w/ null values if no match

Named Queries/Views
- Syntax to create a view, which is a query that is named: Create View [name] As [Select... From... ]
	- Typically used to ease development, inc security to control access (such as reading a table)
	- Views also are not directly computed until the view is used in a query
1. Create View V1 As Select B.bid, Count(*) As Count From B, R Where R.bid = B.Bid Group by B.bid;
	--> Select * From v1; # Actually computes redcount: will provide the tuples defined in the view
	--> Select bname, C From R, B Where R.bid = B.bid And Count < 10; # Should give boat name + count of boats/R values satisfying the query
2. Select bname, C From B, (Select B.bid, Count(*) As Count From B, R Where R.bid = B.Bid and Count < 10 Group by B.bid As Reds) Where Red.bid = B.bid;
	- This query acts in the same way as the 2nd query of the view defined in 1, but w/o needing to create a view
3. With Reds(bid, C) As (Select B.bid, Count(*) As C From B, R Where R.bid = B.Bid and Count < 10 Group by B.bid As Reds)
   Select bname, C From B, Reds Where Reds.bid = B.bid;
   	- In this version, we use a common table expression, in which a table is initially defined; the table can then be used by
   	  the rest of the query
4. With Reds([Defined in 3]), Unpopular As (Select bname, Count From B, Reds Where Reds.bid = B.bid And Count < 10) Select * From Unpopular;
	- Can define multiple tables in a With statement. Unpopular actually relies on the 1st table that was defined w/in in the same
	  With statement
5. With MaxRatings(age, maxrating) As (Select age, max(rating) From S Group By age)
   Select S.* From S, MaxRatings m Where S.age = m.age And S.rating = m.maxrating;
   	- First, we define a table grouped by age w/ highest rating of each group. Then, merge that w/ all the sailors
   	  matched against age and then keeping only the entry of that table w/ the highest rating

Null
- SQL uses Null when the value is unknown; can be used to replace any data type
- Example of a tuple w/ Null: Insert Into S Values (11, 'Zach', Null, 35)
- Null in comparators: COLNAME <, >, =, >=, <= NULL will return False across all the comparators
- To check if a given value is null, use the following: IS NULL, IS NOT NULL
- If Where clause evaluates to Null, SQL treats it as False
- Null boolean logic: !N = N, T&N = N, F&N = N, T|N = T, F|N = N using the shortcircuiting behavior
- Null entries are ignored in all aggregation functions (Sum, Count(col), Avg) Except Count(*) in which it will be used

