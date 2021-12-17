Lecture 16: Transactions, Concurrency II

Two Phase Locking
- Motivation: want to ensure the property of isolation is met, in that each Xact can pretend as though it were operating alone
- In reality, want to interweave actions b/w Xacts in order to increase the efficiency of runtime
- Lock: mechanism that allows transaction to read/write data w/o worrying about another Xact modifying said resource
	- 2 types of locks: Shared (S) lock-used for reads (can have multiple Xacts), Exclusive (X)-use for writes so only 1 Xact can hold this lock
- 2 Phase Locking Scheme: Xacts must get S lock before reading, get an X-lock before writing, banned from getting new locks after releasing
  any lock (regardless of type fo lock)
  - Two Phase Locking is a subset of conflict serializable schedules that is "conservative" in that it rejects potentially viable schedules
  - Downside: this scheme does not ensure that cascading aborts do not occur (situation in which T1 has lock_A, releases lock, T2 reads A,
  	T1 aborts --> T2 forced to abort b/c it read a value of A that was not ultimately committed)
  - TPL conflict serializability guarantee: after a transaction has all thelocks it needs, any conflicting transaction is guaranteed to have
    either completed all their use of resources beforehand or are forced to wait for the current Xact to finish


Strict 2 Phase Locking
- Cascading aborts example: (1: R_A, W_A), (2: R_A, W_A), (1: Abort) --> When T2 reads/writes to A, it will have read a faulty value
- Strict 2PL improvement: all locks that an Xact are only released after every final commit or Xact is aborted


Example of 2 Phase Locking
- (1:L_X(A),R(A))->(2:L_S(A))->(1:A-=50,W(A),UL(A))->(2:R(A),UL(A),L_S(B))->(1:L_X(B))->(2:R(B),UL(B),P(A),P(B),P(A+B)),
  ->(1:R(B),B+=50,W(B),UL(B))
  - Step 1: T1 obtains an exclusive lock on A, and reads in the value 1000. T2 gets in line for a shared lock on A, needs to wait for T1
  - Step 2: T1 updates A to 950, writes change to disk, releases lock. T2 gets its shared lock on A, reads 950, releases lock, obtains shared
    lock on B
  - Step 3: T1 requests an exclusive lock on B but needs to wait for T2 to finish. T2 reads the value of B (2000) and releases its lock.
    Then T2 prints values that it has read in (A = 950, B = 2000, A+B = 2950)
  - Step 4: T1 obtains exclusive lock on B, reading in the 2000 value, updating it to 2050, commit changes, release lock on B
 - Hierarchy of schedules (most to least inclusive): serializable -> view serializable -> conflict serializable -> serial

Lock Management
- Convention: if a transaction has a lock --> transaction that requests a conflicting lock joins queue to wait for lock
- Behind the hood, this is maintained by a hashtable, tracking the object resources that locks are being requested for, w/
  information about who has been granted a lock, the type of lock (shared vs. exclusive), as well as Xacts that are in the queue
  - Ex: Resource A might have granted a shared (S) lock to T1, T2. Its wait queue contains {T3(X), T4(S)}--can have dif request types
- Lock request is processed by: if Xact does not conflict w/ current granted set --> put request in granted set. Otherwise,
  add the request to the wait queue
  - Might have to deal w/ lock upgrades: situation in which one transaction that current has a shared lock wants exclusive access
- Lock Manager Example: (1:L_X(A))->(2:L_S(B),R(B),L_S(A))->(1:R(A),A-=50,W(A),L_X(B))
	- Initially, T1 granted exclusive lock to A. T2 granted shared lock to B & gets in line for a shared lock on A. Then, T1
	  requests an exclusive lock on B --> Catch 22 since both Xacts have a lock they need & one they currently have but do need, waiting on other


Deadlock
- Deadlock: condition of a cycle of transactions waiting for the release of each other
- Deadlock situations can occur as the result of: unavoidable conflicts, poor implementation of lock upgrades, multiple lock upgrades
	1. Unavoidable conflicts: T1 has L_X(A) but wants L_X(B), T2 has L_X(B) but wants L_X(A) --> neither can relent
	2. Bad lock upgrades: T1, T2 have L_S(A) but T_2 is at back of queue waiting for L_X(A), but cannot be granted before releasing L_S(A)
	   which we know is not allowed. Can be fixed by placing lock ugprades at front of the queue
	3. Multiple lock upgrades: T1, T2 have L_S(A). T1, T2 both want L_X(A) --> need to kill one of the transactions
- Deadlock can be dealt w/ using prevention, avoidance, or detection & resolution
1. Deadlock Avoidance: assume that Ti wants some lock that Tj currently holds, can use 2 options: wait-die, wound-wait
	- Strategy 1-Wait Die: Ti has higher priority? Wait until Tj is done then gets lock. Lower Priority?: Ti aborts
	- Strategy 2-Wound Wait: Ti has higher priority? Tj aborts & Ti gets the lock. Ti has lower priority?: Ti waits
	- Both strategies ensure that the deadlock situation is avoided but can result in an excess of abortions
2. Deadlock Prevention: typically order the resources cleverly such that we do not encounter a deadlock scenario to begin w/, but this
  is not always possible w/ DBMS setup
3. Deadlock Detection: maintain a waits-for graph, which maintains a node for every transaction drawing an edge from
   Ti to Tj when Tj has a lock for some resource that Ti is trying to access
  - Example setup: (1:S_A, S_D), (2:X_B), (1:S_B), (3:S_D, S_C), (2:X_C), (4:X_B), (3:X_A)
  - Initially, T1 requests shared lock on A, D --> no conflicts. T2 wants exclusive lock on B --> no conflict. T1 wants shared lock on B
    --> conflict so we draw an edge from T1 -> T2, indicating that T1 wants a lock that T2 has
  - Then, T3 wants shared lock on D, which it is granted along w/ T1. T3 also requests & gets shared lock on C. Then, T2 reqiests
    an exclusive lock on C, which conflicts --> draw edge from T2 -> T3
  - T4 wants exclusive lock on B --> conflicts w/ T2 Xlock on that resource, so draw edge from T4 -> T2 (no cycles yet still)
 	- Finally, T3 wants an Xlock on A, which T1 currently has an Slock for, so draw edge from T3 -> T1, creating a cycle
 	- Idea: typically, we will run this deadlock detection program and "kill" Xacts involved in the deadlock situation
 	  which works since deadlocks do not usually involve too many transactions anyway

Lock Granularity
- Idea: we face a tradeoff when implementing locks at a given scope. Too fine? Resources will be freed up for use, but requires 
  us to track too many locks. Too coarse? Do not need to track that many locks but resources will be unnecessarily blocked off from usage
  - When resources are blocked off from usage, this prevents us from taking advantage of concurrency since Xacts might have
    to wait in line for a resource to be freed up
- To solve this problem, we need some way of developing a pyramid of granularities, to decide how we grant locks for various resources on
  the record, page, and table level (record the smallest unit, table the largest)
  - Can think of a database as a "container" of tables, which consists of pages that are made up of records
  - Each time a higher up resource obtains a lock, all the downstream resources that it contains are also locked
- Solution: use intent to share (IS), intent to exclusive lock (IX), and intent to share/exclusively lock (SIX) locks
	- SIX locks are useful in the context of SQL queries, in which we might run "Select * From A Where b = 100" in which we first want to scan
	  the entirety of the table (shared lock for reading), but then obtain exclusive lock to update a subset of those rows
- Granularity protocol: assume we are starting at the largest resource. In order to gain access to an S or IS lock on a resource contained w/in 
  a lower level, then an Xact needs to either have either an IS or IX lock on the parent node
  - To obtain X, IX, or SIX lock on a lower node: need to have IX or SIX lock on the parent node
  - When releasing locks, start it from the bottom and work the way up the hierarchy 

Compatibility Matrix
- Given that 2 Xacts want to obtain a lock (IS, IX, S, SIX, X) simultaneously, what lock is the other Xact allowed to have?
	1. T1 has SLock -> T2 can hold SLock or ISLock since any other lock would corrupt the read w/ the potential for modification
	2. T1 has XLock -> T2 is not allowed to hold any lock since T1 is hogging the resource all to themself
	3. T1 has ISLock -> T2 can hold any but XLock since T2 is not quite reading any data yet and does not plan on modifying it
	4. T1 has IXLock -> T1 can hold ISLock or IXLock since it cannot actually read/modify data that T2 plans on manipulating
	5. T1 has SIXLock -> T2 can only have a IS lock since this gums up access to downstream resources

Summary
- We want some way to meet the criteria of isolation, in which each of the Xacts can pretend as though they were operating independently
  even though we might be running them at the same time
  - To achieve this, we first used the idea of conflict serializability, which does not capture all serializable schedules
    but ensures any schedule that is conflict serializable will indeed by a serializable schedule
- TPL/Strict 2PL: schemes that use locks in order to prevent conflicts from occurring. Need to deal w/ deadlocks
  in these schemes using either detection or prevention
- Need to consider the scope of the resource we need w/ locking, balancing the overhead and concurrency tradeoffs


