Lecture 1: Intro, SQL 1

Reasons to take CS186
- Will learn about databases & data processing, which is critical in all applications + in computing
- 2000s: pivot from using programs to a model that utilizes data services. Now, data management is a critical
  job in many firms
- Clearly, databases are relevant, as we have seen in the news from data leaks. The NSA to the data that
  Google has collected on ppl both highlight the importance of understanding data
  - Now, misinformation has become a pressing data issue. Need to figure out new data integrity paradigm
- Data is now the foundation of how society operates: continues to grow and has greater relevance
- Growth of data will (human and non-human generated) inevitably grow faster than our computing capabilities
	- Non-human data: one example would be scientific data, which is on the scale of 10^21 bytes
- Data growth is driven by greater use of sensors/reporting, scientific projects, & general philosophy across
  companies that collecting more data is valuable

Intro to CS186
- Rolodex can be thought of as an early predecessor to the modern database: has alphabetically ordered cards w/
  indexes for efficient access and is at its core a collection of organized info
  - Other databases: airline reservation systems (organize flight transactions) , Tinder (collection of ppl/profiles)
- Database: large collection of organized data
- Database Management System (DBMS): software responsible for storing, managing, and accessing the data
- DBMSs typically refer to the relational version of them (RDBMS)
	- Properties of RDBMS: use SQL to access/manipulate data, have durable writes, have been around for quite some time
	- Oracle and MySQL are most popular DBMS, Microsoft SQL and PostgreSQL are other examples of DBMSs
- Scale of DBMS market: RDBMS capture vast majority of it, but Hadoop + NoSQL are recent disruptors
- Change in database markets: cloud DBMS, more data tools have (ML + data science), non-RDBMS systems have popularized
- Main topics: SQL (declarative language), designing data systems, transactions, data modeling (representation of info)

SQL: History
- SQL came about in 1970s from IBM but gained popularity in 1980s when Oracle came to the market
- Originally focused on objected-oriented DBMS, then came XML, now NoSQL and MapReduce are how SQL is used
- SQL is a declarative language (meaning we state the info we want but do not specify how to get it), is widely used,
  is quite limited in what it can do, and has many features/use cases

SQL: Terminology
- Database: set of relations
- Relation (also referred to as a table): contains a schema (specification for the format of the data) and an instance,
  which is the data that obeys the schema
  - Schema must be fixed (names are set in stone, types are atomic, meaning they are the simplest data types possible)
    while the instance can change (can add or delete rows)
- Attribute: also called a column or field is the collection of data for a single
- Tuple: also referred to as a record or row, which is a the collection of info for a specific individual data point
- Illegal relations: If there is a row that does not obey the schema, then it is not a schema. Also cannot have duplicate column names. 
  Cannot have "complex" data types in a column either, such as a list or a tuple
- Data Definition Language (DDL): used to define/change the schema of a table
- Data Manipulation Language (DML): used to write queries
- From there, the RDBMS evaluates the SQL query and chooses an algorithm to efficiently run a query


Creating a Table
1. Create table Sailors (sid integer, sname char(20), rating integer, age float primary key (sid));
	- We can specify integer type, a char of a max length, floats. Note that we also specified one field to
	  act as the primary key, meaning that all entries must have a unique sid
	- Primary key will be used for lookup which is why we cannot have duplicates of it w/in a table
2. Create table Boats (bid integer, bname char(20), color char(10), primary key (bid));
3. Create table reserves (sid integer, bid integer, day date, primary key (sid, bid, day) foreign key (sid) reference Sailors
   foreign key (bid) references Boats);
	- In this table, we used multiple columns for the primary key. As such, we just need a unique combination of
	  the collective of those 3 columns when coming up w/ a row
	- Also, we specified foreign keys w/ a column name and the table that they correspond to. Foreign keys can be thought of
	  as pointers to another table (w/ the column name matching the other table it references)

Sample Queries/Syntax
1. SELECT: Select * from Sailors as s where S.age = 27: query will provide sailors that are 27 years old
	- Syntax of a basic SQL query: Select [COLS] from <TABLE> where <predicate> 
2. DISTINCT: Select distinct S.name, S.gpa from students S where S.dept = 'CS':
	- This will gives all non-duplicate entries upon preserving only CS students (using only their name + GPA). 
	  Also uses an alias to refer to the original table
	- Distinct can be used in 2 different places: select count(distinct s.name) AND select distinct count(s.name)
		- In the first instance, we first get rid of any duplicate names (have 1 of each), then count them
		- In 2nd instance, we get the count of a specified column w/ the aggregate function, then that would be boiled
		  down to a single row so then there is no effect specifying distinct
3. ORDER BY: Select S.name, S.gpa, S.age*2 as a2 from Students S where [predicate] order by S.gpa, S.name, a2;
	- Here, we show how to specify a new column based off of a prior column, and can order the data by column(s)
	  lexicographically, breaking ties w/ the next column specified
	- By default, data is sorted in ascending order but can use DESC keyword to get the reverse
4. LIMIT: Select S.name from Students s where [predicate] order by [ordering] limit 3;
	- Only preserve the first N rows in the output. Usually used in conjunction w/ order by other results are indeterminant
5. AGGREGATES: Select [distinct] AVG (S.gpa) from Students S where [pred]
	- Sum, Count, Max, Min, Avg are all examples of aggregate functions, which produce a single row of output by computing
	  something about the columns of the data
6. GROUP BY: Select Avg(S.gpa), S.dept from Students S group by S.dept
	- In this query, we first place the data into groupings, and aggregate results w/in a group, yielding number of results
	  correpsonding to number of groups
7. HAVING: Select Avg(S.Gpa), S.dept from Students S group by S.dept having (count*) > 2
	- Here, we can filter out groups that do not obey the aggregating condition specified in HAVING statement (applied post-grouping)
8. Ex 1: Select S.name, Avg(S.gpa) from Students S group by S.dept;
	- Get the name of a student and the average GPA for the students w/in a department. This is illegal b/c it has a value
	  that gets aggregated (Avg) and non-aggreagte (S.name)
9. SUMMARY: Select [distinct] <cols> from <table> where <pred> group by <cols> having <pred> order by <cols> limit <integer>;










