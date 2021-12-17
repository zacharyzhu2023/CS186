Lecture 23, 24: Distributed Transactions

Distributed Computing
- Distributed systems rely on shared-nothing architecture to engage in parallel computations
- Distributed Copmuting: form of parallel computation that all have own memory/disk, the networks are unreliable (commonly
  loses packets or has messages reordered/delayed), clocks lack synchronicity (cannot sync up), and makes it difficult
  to determine which nodes are dead/alive
- DBMS can be understood as a unique example of distributed computing, which used Xacts to develop concurrency/parallelism
- Many distributed systems are indeed databases, both on the SQL side (Aurora, Azure) & NoSQL (DynamoDB, MongoDB)

Distributed Locking
- Setup: start w/ shared nothing DBMS that has nodes w/ partitioned, unreplicated data. One of the nodes will act as
  the coordinator of the Xact
- Locking: each node has its own lock table for its own data which it manages independently but still need coarser
  locks, which is the purpose of the "central"/master node that can lock on table/DB level
  - This architecture is more efficient, but can lead to issues w/ "global" locks w/ respect to deadlock & commit/abort

Distributed Deadlock Detection
- Potential issue: each node of the system has its own waits for graph to detect deadlock. Individually might not have a
  conflict but collectively there might be deadlock when taking all Xacts into account
  - Solution: occasionally take the union of the waits-for graph to generate the composite on the master node

Two Phase Commit (2PC)
- Potential issues: a node that is "lost" needs to figure out how to recover w/ dif conditions once it comes back online,
  messages can get delayed/interleaved, & nodes need some way to determine whether to commit/abort Xact in the end
  - Protocol: want unanimous consensus before committing since individual nodes can observe dead/constraint violations
- To implement this protocol, use 2 phase commit: first the coordinator node will indicate to the nodes to prepare for
  a vote, the participants vote, then the coordinator informs the participants about vote results (requires 100% commit
  to proceed w/ commit. Else: abort), the participants respond w/ acknowledgement message upon receiving results

2PC w/ Logging
- Phase 1 of 2PC w/ logging: 1. C indicates to P to prepare for vote, 2. P makes prepare/abort record, 3. P flushes record,
  4. P votes (send to C), 5. C creates a commit record, 6. C flushes commit record
- Phase 2 of 2PC w/ logging: 1. C sends results of vote, 2. P creates commit/abort record, 3. P flushes record, 
  4. P responds w/ acknowledgement message, 5. C creates end record, 6. C flushes the end record
  - Participants will have a  prepare/abort record & a commit/abort record. Coordinator has commit/abort log (using 
  	all the participants)

2PC Recovery
- Idea: we assume that all nodes will eventually recover and the protocol of coordinator/participant depends on timing
	- P down: no vote? C needs to abort. Else: continue w/ recovery. C down: no prepare log? Abort. Else: continue recovery
- Assume each node has a given recovery process, based on the ARIES algorithm previously used
- P recovering, no prepare: P has not started 2PC & has not voted --> abort locally, no message needs to be sent
- P recovering, has prepare record: P does not know commit decision, so asks C for that, then continues in 2PC phase 2
- C recovering, no commit: C crashed before receiving all votes --> C aborts locally & sends no messages
- C recovering, commit: know commit results but may not have given to all P --> rerun phase 2  of 2PC
- P recovering, commit record: P has done the work for committing, but needs to send acknowledgement message to C
- C recovering, end record: everyone is done (participants included) --> do nothing
- P recovering, no phase 1 abort: no presumed abort means P did not start 2PC (has not voted). Presumed abort: P chose
  to abort locally & sent no vote --> P should abort locally
- P recovering, phase 1 abort: No presumed-abort locally, cast "no" vote. Presumed: abort locally-no message needed since
  C assumes P will have aborted w/ no message
- C recovering, no abort: no presumed-C crashed before decision, presumed-possible C decided to abort --> local abort
- C recovering, abort: no presumed-rerun phase 2 (send abort message to P), presumed-abort locally (P asks C later)
- P recovering, phase 2 abort: no presumed-abort locally & send ACK, presumed-abort local

Two Phase Commit & Two Phase Locking (2PC, 2PL)
- Assume that all messages are densely ordered w/ respect to sender/receiver/transactionID. This allows receiver to
  know if anything is missing/out of order
- Commit: 2PL ensures P has sufficient locks, after which it flushes log & removes all the locks simultaneously
- Abort: can abort locally, sending appropriate logs to 2 phase commit, locally undoing & removing the locks
- If participant dies, may be issue if it holds locks others are waiting for. C takes care of "reviving" P. Meanwhile,
  if C dies, that is a source of major problem that Paxos Commit attempts to deal w/

