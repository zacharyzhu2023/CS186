Lecture 14: Transactions and Concurrency I

Intro to Concurrency & Control
- Consider what happens if we have multiple clients running queries simultaneously (want to ensure fault tolerance)
- Need to implement a lock manager (consistency) and have a mechanism for logging/recovery when running queries
- Concurrency Control: want correct/quick data access across many users; want the appearance of order when using data
- Recovery: database should be fault tolerant--does not collapse from disruptions in software or the system
- Want to be able to run multiple queries at the same time to inc throughput (allows instructions to be run at once)
  & latency (decrease the amount of time required to run each transaction)--do not want unrelated queries to bog down


Example of Concurrency Issues
- Example 1: 1. Update B Set m = m - 500 Where Pid = 1; 2. Update B Set M = M + 200 Where Pid = 2; 3. Select Sum(M) From B
	- Potential Issue (Ordering Issue): The first 2 queries can run together unrelated w/o affecting one another. However, 
	  query 3 depends on the results of Query 1/2, so the results clearly depend on the order in which queries are run
- Example 2: 1a. Insert into DP(a, b) Select a, b From P Where b <= 0.99, 1b. Delete P Where b <= 0.99, 2a. Select Count(*)
  From P, 2b. Select Count(*) From DP
  - User 1: takes a subset of rows from P & insert into new table DP, then delete those rows from original table P
  - User 2: get the count of all rows in either of the tables. If User 2 runs the query after 1a alone --> get an overcount
  	- This is an issue of inconsistent reads, in which they get the "before" and "after" image of a query
- Ex 3: 1. Update P Set p = p - 10 Where N = 'A', 2. Update P Set P = P*0.6 Where N = 'A'
	- Potential issue (Lost Update): user 1 can make their update but before the update gets written, user 2 gets the data of
	  N pre-change of user 1, so the results do not get compounded
- Ex 4: 1. Update A Set a = 10 Where Num = 5, 2. Select a From A Where Num = 5
	- Potential Issue (Dirty read): assume first query gets aborted, but only after query 2 fetched the data assuming the
	  update operation completed --> results in data getting read that is incorrect


Transactions
- Transactions allow users to specify the kind of behavior they want & the actual implementation to achieve said behavior
- Definition of a transaction: sequence of actions that can be chunked and run together as a single cohesive unit
	- Atomic unit means that the actions must either all occur or none do
	- Ex 1: SQL view that begins a transaction, executes a sequence of SQL statements, after which the transaction is over
	- Ex 2: booking a travel itinerary--flight, lodging, and rental car--we either get all or nothing
- Transaction ('Xact'): conceptually the high level overview of a program, which we take as instructions for reads/writes that either
  all get executed or none at all do
- Xact Manager is responsible for controlling how the transactions get executed (gets abstracted as reads/writes to the database)
- Example transaction: 1. Start, 2. Read R, 3. R = R - 100, 4. write R, 5. read S, 6. S = S + 100, 7. End
	- Here, the DBMS does not see the update operations, but rather just gets the new data to be written during each call,
	  meaning that it ignores instructions (3) and (6)

Transaction Model/Properties
- 4 key properties of transactions: atomicity, consistency, isolation, durability (ATOM)
	- Atomicity: either all actions occur or none do, Consistency: a database that starts in a consistent state will stay consistent after
	  a transaction, Isolation: each transaction is executed independently of all others, Durability: a transaction that commits a change will
	  have that effect realized by the database
- Isolation deals w/ concurrency: DBMS needs to make sure that Xacts do not intefere w/ one another. Means that if we were to run
  Xacts concurrently, should end up w/ same result as if they ran sequentially
  	- Ex: T1 (Start, Read R, R += 100, Write R, Read S, S += 100, Write S, End), T2 (Start, Read R, Read R + S). Here, we typically want
  	  T2 to run either w/ starting values of R, S or after T1 has fully updated R, S, which we achieve through isolation
- Transaction can either commit (its actions contract that caller is finished) or abort (system crash or DBMS does not want Xact to affect database)
	- Atomicity ensures either all the actions are executed or none, Durability states that any effect of committed transaction must still go through
	  even if the database were to crash/fail for whatever reason
	- Properties achieved through logging. Going through log, want to remove the consequences of failed actions & retry actions
	  of transactions that were not realized in the event of a system crash
	- Atomicity Example: assume T1 fails b/w (4) & (7) --> fail to update S, so atomicity means we should remove the write to R
	- Durability example: if the transaction is completed, then R is properly decremented, S is incremented
- Consistency: a consistent database state will stay in a state defined as consistent post-Xact
	- Achieved through integrity constraints w/ create table/assertion statements (ex: primary key/type constraints) which ensure that the database
	  adheres to a certain set of characteristics
	  	- Any Xact that does not abide by these conditions will not be exectued

Concurrency Control Definitions
- One approach might be to run Xacts sequentially, which ensures we achieve desired behavior but might be slow
- Could potentially interweave executions to obtain better performance but need some way of defining & making sure correctness is achieved
- Transaction Schedule: sequence of actions of 1+ actions (begin, read, write, commit, abort), preserving only committed Xacts
- Serial Schedule: runs transactions sequentially w/o any interruption from another Xact until it is complete
- Schedule Equivalence: includes same Xacts, Xact actions occur in same relative order, create the same DB state
- Serializable Schedule: a schedule that satisfies all 3 properties of schedule equivalence w/ the serial schedule
- Ex 1: T1 (Start, R(A), A -= 100, W(A), R(B), B += 100, W(B), Commit), T2: (Start, R(A), A *= 1.1, W(A), R(B), B *= 1.1, W(B))
	- If were run T1 then T2 sequentially --> end result becomes A = 1.1(A-100), B = 1.1(B-100)
- Ex 2: (Start, R(A), A -= 100, W(A)) -> (Start, R(A), A *= 1.1) -> (Start, R(B), B -= 100, W(B)) -> (Start, R(B), B *= 1.1)
	- Creates same end result as Ex 1: A = 1.1(A-100), B = 1.1(B+100), so these 2 schedules are considered serializable
- We still need some way of meeting the 3rd condition: transactions should leave DB in the same state
- Conflicting Operation: operations conflict if they are different Xacts on same object & there is at least 1 write
	- This correctness check captures only true positive, but has some false negatives. That is, it may incorrectly state
	  that some Xacts that leave DB in same state do not, but all transactions that pass our test are guaranteed to meet the condition
- Conflict Equivalent: same actions across all transactions & conflicting actions have the same order in both schedules
- Conflict Serializable: a given schedule is conflict equivalent to a serial schedule --> this schedule must be serializable

Examples: Conflict serializability
- Example of conflict serializability: starting schedule: 1.R(A), 1.W(A), 2.R(A), 2.W(A), 1.R(B), 1.W(B), 2.R(B), 2.W(B)
	--> 1.R(A), 1.W(A), 2.R(A), 1.R(B), 2.W(A), 1.W(B), 2.R(B), 2.W(B) since writing A and reading B occur on different objects
	--> 1.R(A), 1.W(A), 2.R(A), 1.R(B), 1.W(B), 2.W(A), 2.R(B), 2.W(B) since writing to A and writing to B occur to different objects
	--> 1.R(A), 1.W(A), 1.R(B), 2.R(A), 1.W(B), 2.W(A), 2.R(B), 2.W(B) only read operations & to different objects
	--> 1.R(A), 1.W(A), 1.R(B), 1.R(B), 2.R(A), 2.W(A), 2.R(B), 2.W(B) again to dif objects so unaffected
	- Ultimately, we end up w/ a serial sequence of (1) actions followed by a sequence of (2) actions, so the original schedule was serializable
- Ex 2: 1. R(A), 2.R(A), 2.W(A), 1.W(A) --> only possible swap is w/ first & second step (2121 sequence) so still not serialized

Conflict Dependency Graph
- Dependency Graph: construct using a node for every transaction. Include an edge b/w nodes if there is a conflicting operation
  b/w 2 transactions, drawing arrow from the node whose action appears first
- Serializable Theorem: a schedule is conflict serializable IFF dependency graph is acyclic
- Example: 1.R(A), 1.W(A), 2.R(A): need to draw an edge from T1 to T2 since there is a write operation on a single node
  --> 1.R(A), 1.W(A), 2.R(A), 2.W(A), 2.R(B), 2.W(B), 2.R(B) which creates a second edge from T2 -> T1 since W(B) occurs first
  - This creates a dependency graph w/ a cycle since we clearly cannot swap final W(B) and R(B)

View Serializability
- View Serializability: two schedules are equivalent if every initial read is the same, every dependent read provides same value,
  and same "winning" writes (writes that are proceeded by a read of said value)
  - Initial reads are the initial values of each object that get read in, dependent reads are those that occur after a write operation
  - Allows for greater flexibility in terms of blind writes--if we clobber the value that gets written, do not need all writes to be the same
- Allows for more potential schedules compared to conflict  serializability though it still excludes some schedules
- Conflict serializability is used more in reality b/c it is easier to check the conditions are met







