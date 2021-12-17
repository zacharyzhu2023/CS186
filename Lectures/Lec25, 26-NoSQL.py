Lecture 25, 26: NoSQL

Organization of Database Applications
- 2 forms of relational database applications: Online Transaction Processing (OLTP), Online Analytical Processing (OLAP)
	- OLTP: queries take form of a lookup using 0/1 join, want consistency, and may need to make many updates
	- OLAP: also referred to as decision support, in which there are no updates but potential for many join/groupby operations
- Web applications like FB, Amazon needed to be able to scale to accommodate more clients --> rise of NoSQL
	- Using the OLTP model which wants to make many updates, which NoSQL is able to do but has very limited functionality
- Imagine a scenario in which there is a user, DBMS application, and a data file: consistency is automatically ensured. However,
  when we add additional clients, then the application canno tbe run by the machine for the user (user should run on their desktop)
  to be able to scale, so the server now solely contains the data file; the user just connects to the application

RDBMS Scaling
- Want to replicate the database, either through partitioning or replication, both of which create a problem w/ consistency
	- Partitioning: the datbase gets broken up across multiple machines --> allows us to inc throughput by running queries across machines
		- Write operations are cheap so long as we know which machine to write to, but reads are harder b/c need to aggregate the
		  results across all the machines now
	- Replication: make copies of each DB partition and send them to different machines, so queries spread across duplicates, increasing
	  fault tolerance (one machine goes down, still have more) & inc throughput/dec latency
	  	- Reads are cheap (data can be on a single machine b/c duplicated) but writes are expensive (need to update all the copies of data
	  	  across all the machines)
- Relational DB makes it difficult to replicate/partition since partitions may require joins and replication can result in inconsistency
- Thus, NoSQL offers the alternative that forces the user application to deal w/ joining & enforcing consistency instead
	- NoSQL has 3 key properties: 1. Basic Availability: application deals w/ partial failures, 2. Soft State: DB state can change even
	  if no new inputs introduced, 3. Eventual Consistency: DB will eventually reach a consistent state

NoSQL Data Models
- 3 forms of data models: key-value stores, extensible record stores, document stores
- Key-Value store: pair of (key, value) objects, in which key is simple datatype like string/int, value can be any arbitrary object
	- Key should uniquely identify that object, and this models ultimately supports just 2 operations: get(key), put(key, value)
	- To distribute/partition: can use a hash function. If we want replication, then use multiple hash functions w/ the same key
	  - Partition: All the key value pairs are stored on the server h(key). Replication: keys are stored on multiple servers, which means
	    that we need to at some point send change updates to other servers whenever one is updated (eventual consistency)
- Extensible Record Store: Option 1-key is a rowID, value is a record, Option 2-key is rowID and some column vlues, value is the field
- Key value model can result in a complex data type for the value, so we want to enforce some kind of structure for value

JSON
- Javascript Object Notation (JSON): text-based semistructured data to make data exchange easier & readable
- JSON objects introduce greater flexibility (often have nested tree structure), uses a text representation-not binary, which allows ease
  of message exchange but hinders performance, query operations are usually done via an API
  - JSON is made up of primitives (ints/floats/strs), objects (list of key-value pairs defining an object), & arrays (ordered list of values)
  	- Objects need not have the same keys, and the types of the vlues thta correspond to the keys can differ as well
- Can think of JSON objects in a tree structure: we have a primary object followed by the attributes that make up this object
- Big idea: JSON allows for greater flexibility, the schema can change w/ every object
- To store JSON objects in RDBMS, sometimes there is buil-in support to describe a column as being a JSON object, in which case
  we would query using SQL & JSON syntax. Otherwise, we can convet JSON objects into relations
  - Map Relation into JSON: Single relation: treat key of table as key of JSON object & provide value corresponding to that key. 2 relations: 
    one of the tables will function as the outer key of the JSON object & store corresponding objects from 2nd table in it
  - Considering a 3rd object will continue w/ this nested structure & can result in redundant records being stored in JSON object
- JSON -> Relation: Missing data? Use the null attribute. Repeated attributes? Need to use >1 table. Nested/Heterogeneous structures?
  Do not have clean way of using relational model in these cases
- Advantage of semistructured data: works well w/ data exchange b/w multiple databases. Many systems now support JSON/XML formats

MongoDB
- MongoDB: can think of it as an RDBMS that allows value to take on any type it wants (array, JSON, primitives, etc.)
- Every document contains the _id field which acts as the primary key & will allow for indexing
- MongoDB Query Language (MQL): takes in collections and spits out collections, supporting 3 queries: retrieval, aggregation, updates
  - Retrieval: similar to SQL structure, but all queries must adhere to: "Select <> Where <> Order By <> Limit <>"
  - Aggregation: think of it as a more generic form of the retrieval query, Updates: operate similarly to SQL (insert/update/delete)
- Dot notation: 'table.field1' (gets the value stored in a given field), 'table.1': gets 2nd element of an array/column
	- Queries should be in quotes & can nest dot notation: 'table.field1.1': gets 2nd element of the field1 array of table
- Dollar Notation: $ used to indicate a keyword $gt, $lte, $add (>, <, + operators), preceding the operator
	- Ex: {qty: {$gt : 30}} preserves only records w/ quantity > 30, {$add, [1, 2]} adding the inputs placed into the array

Retrieval Queries
- Syntax to use retrieve operation in MQL: db.collection.find(<predicate>, optional <projection>)
	- Examples: 1. find({status: 'D'}) keeps records w/ status = D, 2. find({qty {$gte: 50}}) keeps records w/ quantity > 50,
	  3. find({status: 'D', qty: {$gte: 50}}) keeps records that satisfy both status = 'D' AND that quantity > 50,
	  4. find({$or: [{status: 'D'}, {qty: {$lt: 30}}]}) finds records that either have status of 'D' or quantity < 30
	  - Note that the "and" is given be deafult by adding comma b/w predicates while the or needs to be the keyword
- Could also specify columns to preserve using 0 to exclude undesirable fields & 1 for fields to include
	- Ex: 1. find({}, {item: 1}) keeps only the item field, 2. find({}, {item: 1, _id: 0}) excludes the _id field but keeps item
- Also have the option to be able to include Limit(k) and Sort({}) which operates exactly the same as in SQL
	- Example syntax: db.table.find({}).limit(5), db.table.find({}).sort({'dim.0': -1, item: 1}) where the -1 indicates
	  descending order, followed by the sort order

Aggregation/Updates
- Aggregation Pipeline: by using the matching, group, and lookup operators, we essentially manipulate the existing collection in
  some way (discard records, create groups/apply operations to groups, etc.)
- Basic syntax: db.collection.aggregate([{$stage1Op: {}}, {$stage2Op: {}}...])
- Example: assume we wanted to use MQL to find sttes w/ population > 15M given city, ID, location, state, & population info
	- We know that we need to group by stte, aggregate by the sum of populations of the cities, preserve only groups that have pop
	  > 15M in the newly created groups, then can order by the population in descending order
	--> Actual syntax now becomes: db.zips.aggregate([{$group: {_id: '$state', totalPop: {$sum: "$pop"}}}, 
		{$match: {totalPop: {$gte: 15M}}}, {$sort: {totalPop: -1}}])
			- Observe: first specify the we want to group by state, then aggregate by taking the sum of the population
			  which we then filter using "match" keyword ultimately sorting by population
- Generic syntax that can be used to create groups: $group: {_id: expr <field> : {aggfunc1: expr1}}
- Array unwinding: used to create an element for each element in an array which allows us to "unnest" that specific array
	- Ex: aggregate([{$unwind: '$tags'}, {$project: {_id: 0, instock: 0}}]) where we unwind the tags array such that each new object
	  will make new "copies" based on the values contained in their tags array, & choose which columns to preserve
- Update: can now insert new records, delete records, or update. Note that we can specify quantity (insertMany([]) is valid)


MongoDB Internals
- MongoDB is a NoSQL DB whose collections are partitioned/sharded in a range-based fashion based on the field value
- Partitions are then replicated to deal w/ issue of failures. Is not much query optimization unlike w/ SQL queries
- MongoDB allows for greater flexibility, using MQL as its querying language. Serves as a basis for a NoSQL architecture


