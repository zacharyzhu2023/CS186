Note 0: SQL Basics

Terminology
- Databases are composed of tables (another term for this is relations) which contain a sequence of rows and columns
- Structure of a query: SELECT cols FROM table (does not have any determinstic order unless ORDER BY is specified)
- Use the WHERE query to filter out rows: WHERE takes in a predicate and gets rid of entries that do not match it
	- Ex: SELECT name, num_dogs FROM person WHERE age >= 18: keeps only the name/num_dogs from person where that age >= 18
		- By using SELECT, we can specify a subset of the columns that we are interested in
- Can create more complex WHERE queries by combining booleans using NOT/AND/OR
- To remove "null" values, Null rules in SQL: perform any operation w/ null type and still end up w/ null, null is falsey
  in value, and short-circuits boolean value
  - Table: name = [A, A, B, C], age = [20, NULL, NULL, 27], numDogs = [4, 3, NULL, NULL]
  - Query: age <= 20 OR numDogs = 3 --> 1. (20 <= 20 or 4 <= 3 --> True), 2. (NULL <= 20 OR 3 == 3 --> NULL or True --> True)
    3. (NULL <= 20 OR NULL = 3 --> NULL or NULL --> False), 4. (27 <= 20 or NULL <= 3 --> False or NULL --> False)

Overall Query Structure
SELECT cols (allows us to pick & choose which columns we want--use (*) to select all columns)
	- Behind the hood, SELECT is the last operation that occurs b/c it transforms all groups into single entry
FROM table (specify the table that we are working w/, can have multiple using join queries)
WHERE filter1 (filter1 provides the initial rows that we want to discard)
GROUPBY col (provides a structure to aggregate the data by--need to specify a function if using groupby)
	- Aggregate functions: Count, Sum, Avg, Max, Min
	- Note: aggregator functions will all ignore null values except for count * which does include NULL in its tally
HAVING filter2 (getting rid of groups that do not satisfy filter2)
ORDER BY cols (how do we want to structure the ordering of the table?--specify DESC for descending order)
LIMIT num (limit how many rows we want in our table)

Practice Questions
- Assume we have the following table: dogs w/ columns (dogid integer, ownerid, name varchar, breed varchar, age integer)
- Q1: query to get name of all dogs w/ ownerid = 3: SELECT name FROM dogs WHERE ownerid = 3
- Q2: list name & age of 5 oldest dogs: SELECT name, age FROM dogs ORDER BY age DESC, name LIMIT 5
- Q3: query to show number of dogs for each breed that has multiple dogs: SELECT count(*) FROM dogs GROUPBY breed having count(*) > 1

Note 1: Joins, Subqueries

Joins
- Cross join: cross product of 2 tables, providing all possible combinations of entries b/w 2 tables
	- Syntax: SELECT colNames FROM table1, table2
- Inner join: similar to cross join but using "ON" instead of "WHERE" to more efficiently filter
	- Syntax: SELECT colNames FROM table1 INNER JOIN table2 ON colName1 = colName2
- Left Outer Join: keep all entries from the left table, and match against entries in right table
	- Syntax: SELECT cols FROM table1 LEFT OUTER JOIN table2 ON colName1 = colName2
	- Right outer join works similarly except by preserving the entries in the right table joined against left table
- Full Outer Join: Keep all entries from either of the tables that matches the condition (condition not met --> have NULL)
	- Syntax: SELECT cols FROM t1 FULL OUTER JOIN t2 ON col1 = col2;
	- Idea: all entries that are in either table is included in the merged table (even if there is not a matching entry)
- Natural Join: performs inner join w/ all columns in the tables that have hte same name
	- In the example below, SELECT * FROM courses NATURAL JOIN enrollment is equivalent to:
	  SELECT * FROM courses as c INNER JOIN enrollment as e on  c.name = e.name

Name Conflicts
- Sample setup: courses = {num:[CS186, CS188, CS189], name:[DB, AI, ML]}, enrollment = {num: [CS186, CS188], students:[700, 800]}
	- Now, if we want to work w/ both tables, there is an issue b/c the num column is present in both tables
- Solution: provide "as [name]" syntax in order to specify the names of the tables
	- Example: SELECT * FROM courses as c INNER JOIN enrollment as e ON c.num = e.num
	- Here, we would only preserve entries where the num in courses and enrollment matches

Subqueries
- Subquery Example: SELECT num FROM enrollment WHERE students >= {SELECT AVG(students) FROM enrollment;};
	- The inner query finds the average number of students in a table, and only preserve entries in enrollment that meet that average
- Idea: we are unable to use an aggregator function in "where" clause since filtering occurs first, then we aggregate
- Correlated Subquery Example: SELECT * FROM c WHERE EXISTS (SELECT * FROM e WHERE c.num = e.num);
	- First checks to see c.num against all e.num: rows that exist in both tables are returned
	- Then, we need to check if the set of entries that gets returned is nonempty for each row from c that we plug into the subquery
	- Other potential set operators: ANY, ALL, UNION, INTERSECT, DIFFERENCE, IN
- From Subquery: SELECT * FROM (SELECT num FROM c) as a WHERE num = 'cs186';
	- "From" clause: creates a temporary table that includes ony the num column of table c, give it a name, then
	  finally apply other operation to that temp table

Practice Questions
- Setup: 1. dogs: [dogid, ownerid, name, breed, age], 2. owners: [userid, name, age]
1. Query that includes all dogs that "Josh Hug" owns using INNER JOIN
SELECT * FROM dogs as d, owners as o WHERE d.name = o.name AND o.name = "Josh Hug";
2. Same as above but w/ CROSS JOIN
SELECT * FROM dogs as d INNER JOIN owners as o ON d.name = o.name WHERE o.name = "Josh Hug";
3. Query for user & numDogs for name of user w/ the most dogs

SELECT o.name, COUNT(*) # Want to extract the name of the owner and number of entries
FROM owners as o INNER JOIN dogs as d ON d.ownerid = o.userid # Merge the 2 tables where the user & owner have the same value
	- This is going to provide all the unique combinations of dogs & their owners w/o possibility of NULLs
GROUP BY o.userid, o.name # Want to find all userID's (since we assume there can be same name)
ORDER BY COUNT(*) DESC # Sort the table by the size of each group of dogs per owner
LIMIT 1;

4. Same as above, but assume ties are possible

SELECT o.name, COUNT(*) # Want to extract the name of the owner and number of entries
FROM owners as o INNER JOIN dogs as d ON d.ownerid = o.userid # Merge the 2 tables where the user & owner have the same value
GROUP BY o.userid, o.name # Want to find all userID's (since we assume there can be same name)
HAVING COUNT(*) >= ALL(SELECT COUNT(*) FROM dogs GROUP BY d.ownerid)
	- Inner query creates a table that finds the number of dogs per owner
	- The "Having" query allows us to filter out ownerid groups that do not have a count greater than all other groups















