Lecture 17, 18: Recovery

Intro to Recovery
- 4 key properties of transactions: atomicity (all or nothing), consistency (DB remains consistent post-transaction),
  isolation (each Xact can pretend as though it were the only one running), Durability (commited effects persist)
  - Job of the recovery manager is primarily to ensure atomicity and durability, but also does not allow transactions that
    violate integrity constraints (and thus, are inconsistent) from changing the DB
- Atomicity property states that Xacts that get aborted should act as though no action occurred. Durability states that upon
  a system crash, committed Xacts should have their changes reflected in DB when system is back up
- Reasons transactions abort: user "kills" a transaction, it violated consistency check (does not adhere to integrity constraints,
  such as when record deleted that is referenced by a foreign key), deadlock (multiple xacts have lock conflicts), or system
  fails before a commit is realized
  - If a system aborts, then any subsequent command will be abandoned until the end of a given transaction (explicit "commit"/"abort")
- SQL semantics for starting/ending transaction: "begin" starts Xact, "commit" indicates end of Xact, "Rollback" aborts Xact
- Can also use "Savepoint <name>" to save the temporary state of a table, "Release Savepoint <name>" to erase a savepoint,
  "Rollback to Savepoint <name>" which reverts back to the state of the table saved at savepoint
- Reasons database crash: 1. Human error (executed incorrect command, used hardware incorrectly), 2. Configuration error: there is
  a misalignment b/w software/hardware specifications & user request, 3. Software Failure: security issue/operating system mistake,
  4. Hardware Failure: server actually crashed

No Steal, Force: Recovery Solution
- Assume that we are achieving concurrency control using the strict two-phase locking scheme. Also assume updates are in-place, 
  meaning that data in buffer pool write directly to the database rather than using copies of the data
- To achieve atomicity & durability w/o logging: pin dirty buffer pages in buffer pool, force any dirty pages to disk, unpin
  pages that were written to disk, then ultimately "commit"
  - Positive aspect: page locking makes it so that only 1 Xact is modifying a given page at a given point in time
  - Does not deal w/ potential issue in which buffer pool might be full and cannot accommodate more dirty pages
  - During commits, it is possible that part way through committing dirty pages to disk, DBMS crashes, so some pages have been
    written while others have not, violating the atomicity property
- This scheme is referred to as no steal, force policy
	- No Steal: frames in buffer pool cannot be replaced until Xact commits. Achieves atomicity w/o having to "undo" since there will not
	  be "faulty" commits but also is limited by the size of the buffer pool
	- Force: all updates are "forced" into disk before committing, which prevents us needing "redo" since actions go through pre-crash

Steal&No Force Policy
- This policy is the opposite of the no steal, force policy. Also is most convoluted by achieves the best performance
- No force: flush minimally, prior to ultimately committing, allowing redos to perform modifications. Intended to deal w/ issue encountered
  when system crashes before dirty buffer page of Xact that committed is flushed to disk
- Steal: if an Xact wants to flush updates but aborts or the system crashes, need a way of getting back prior values of flushed pages
- Steal, no force requires undos & redos, since and need redos 
- No force, no steal: no undo (dirty data never gets written to disk since we guarantee frames do not get replaced before committing), redo
  needed to deal w/ possibility of commits occurring prior to flushing
- Force, steal: undo (deal w/ writing dirty data pages to disk pre-commit), no redo (always force pages to DB before committing)

Write Ahead Logging
- Log: sequential list of log records that support redo/undo operations using following info: XID, pageID, offset, length, old/new data
	- Want to be able to achieve sequential writes to the log taking up as little space as possible
- Write Ahead Logging Protocol (WAL): 1. Write to log device before the database, 2. All log records must be written to log device pre-commit
	- First property helps us achieve atomicity (using undos), while the second achieves durability (using redos)
- Components of the log: ordered file that has a write buffer (aka 'tail') in RAM, and a log sequence number (LSN)
	- We write the individual log records into the log tail which exists in RAM, which gets flushed to disk
	- FlushedLSN: largest log sequence number that has been written so far to disk, but exists right before log tail in memory
	- PageLSN: pointer contained by the data page that references most recent log record for a given page
- Write ahead logging checks to see if pageLSN <= flushedLSN, checking if a given log record for a page has been written to disk
	- Condition met? Can flush a given log to the database. Condition not met? Unable to write page to disk.
	- Condition states that we need to write the log update before the page can be reflected back in the disk

Undo Logging
- Start T: begin Xact, Commit T: T committed, Abort T: T aborted, T,X, v: T updated element X from its previous value of v
- Undo logging abides by steal/force rules. 1. Xact T modifies X --> Write <T, X, v> to disk before dirty page which has new
  value of X, so we retain the original value. 2. Xact commits? Dirty pages written to disk before Xact commits so any changes
  that Xact wants to enact will be reflected pre-commit
- Fetch: put data from disk into memory. Write: clobber data in memory (disk is unaffected). Flush: force disk to take on the
  same values that were held in memory
  - Need to make sure that we write the dirty pages to disk before writing commit record to log to preserve original values for recovery
- General undo protocol: 1. Decide is Xact is completed. <Start T>... <Commit/Abort T> denotes finished, else: incomplete. Step 2:
  any modifications that are deemed incomplete need to be undone
  - Observe an update record <T, X, v> then T is incompelte so we need to write original value X = v back to disk

Redo Logging
- Redo logging uses no force, no steal, w/ the same type of log records as w/ undo. However, <T, X, v> now stores the new value
- During recovery, need to "redo" Xacts that have been committed while not touching any of the uncommitted Xacts
- Redo Rules: 1. Xact T modifies record X --> <T, X, > and COMMIT T must be written to disk prior to dirty pages
- General redo algorithm: 1. Determine if an Xact is complete or not using same mechanism as before. 2. Redo all updates of committed Xacts
- Undo logging: requires less memory b/c can write dirty pages on the fly instead of waiting for a commit, but also requires
  greater latency snce we do need to ensure all dirty buffer pages are flushed pre-commit
- Redo logging: requires greater memory since we need to wait for commit before flushing data pages but allows us to commit
  prior to flushing all the data pages

ARIES Logging
- Idea: we now want to maintain a record of all the log records for a given transaction ID. As such, we institute a linked list
  that contains the previous LSN written by a given Xact for a given record
- Potential types of log records: update, commit, abort. Other types exist but those are the main ones
	- Update: contains LSN, prevLSN (access prior records), XID (current transaction), type (what form of record is this?), along w/
	  pageLength, offset, prevData, newData (last 4 are specific to update records) allowing for redos/undos
	  - All log records must also still contain LSN, prevLSN, XID, and type
- To maintain a given log state, also need to keep track of 2 tables: transaction table, dirty page table
	- Transaction table: keeps an entry for every active Xact, only removing when an Xact commits or aborts
		- Within the table, has XID, status (run/commit/abort), along w/ lastLSN (most recent LSN an Xact has written)
	- Dirty Page Table: maintains an account of all the dirty pages in the buffer pool, corresponding to a recLSN, which is the record that
	  initially caused the dirtying of a given page. This value does not change even as page gets remodified
	  - Initially, when a record is brought into the buffer pool from memory, it is clean b/c unmodified. Then, assume some action
	    changes it, so it is now "dirty". Once this page is written to disk, it gets removed from the dirty page table
- Log maintains log records, which have a variety of fields (mainly LSN, prevLSN), database is comprised of data pages which has a pageLSN 
  (pointer to most recent updat=e by an Xact in the log) & a master record (allow for database recovery upon crash)
	- RAM: contains transaction table, dirty page table, log tail (right after flushedLSN), and buffer pool

ARIES Algorithm
- ARIES: algorithm that combines undo/redo logging that was initially developed at IBM
- Checkpoint: states of the DB that are saved periodically to avoid having to reread the entirety of a log during recovery
- General algorithm: divide work into 3 phases: analysis (reconstruct transactions table & dirty page table), redo (repeat operations
  needed to ensure durability), undo ("cancels" operations from Xacts that were executing pre-crash)

ARIES: Normal Operations
1. Update: update prevLSN in log, pageLSN in buffer pool, recLSN in dirty pages table, and lastLSN in transactions table
2. Page Flush: flush log entries <= pageLSN, remove the page from the dirty pages table & buffer pool
3. Page Fetch: add new entry in the dirty pages table/buffer pool, being sure to set recLSN to null
4. Transaction Commit: write commit to log, flush log up to & including said entry, update transactions table to indicate that
   the status of this table is committing, flush dirty pages to disk, write end record to log, ultimately update transactions
   table to complete if able to execute all the above steps
5. Transaction Abort: write abort record to log, start w/ lastLSN in transactions table for this transaction, work backward undoing
   changes alongthe way & writing CLR for undone changes to log (following prevLSN to look for other changes to undo), then change status
   in Xact table to bort, flush dirty pages to disk, write END record, update Xact table to complete

Analysis Phase
- Analysis phase: intended to reconstruct the transactions table and dirty page table prior to the crash
- Must abide by 4 rules when going through all the records in the log starting at the very beginning:
	1. Record is not an end record? Add the corresponding transaction to the transaction table if not already present. If present,
	   update the transactions table
	2. Record is abort/commit record? Change status in transaction table to reflect that
	3. Record is update record? Add page to dirty page table, setting recLSN to the LSN of this record
	4. Record is end record? Remove this transaction from the transaction table
- Upon finishing those 4 steps, insert an END record for all transactions that committed & remove that Xact from Xact table
- Also need to make a note of any record that was in the process of aborting prior to the system crash
- Checkpointing: procedure that writes contents of Xact Table and Dirty page table to log to avoid having to scan through entire log
	- Create 2 records ("Begin_checkpoint", "End_checkpoint"), which indicate when checkpoint should begin and when we are done
	  writing tables to the log
	- In between those end points, need first to flush the log to disk, then execute all the subsequent operations. Once finished
	  writing dirty page table & transactions table to disk, write "end_checkpoint" statement

Redo Phase
- Redo phase functions to ensure durability, since we want to repeat execution of Xacts that were committed to ensure durability
- Rule: start at the smallest recLSN in dirty page table, iterate through all update/change of log record Xacts unless 1 of the following met:
	1. Page not in dirty page table: means that a given page has already been witten back to disk (no need to rewrite page)
	2. recLSN > LSN: implies that initial operation recorded to "dirty" this page occurred 
	3. pageLSN(disk) >= LSN: Most recent update to given page recorded on disk has occurred after this operation --> operation
	   effect must have been reflected on disk

Undo Phase
- Undo phase is the final step of the ARIES algorithm and ensures atomicity by retracting actions that were running/aborted pre-crash
	- For every update that was running/aborting at the time, write a CLR record to the log which has the field of
	  undoNextLSN, tracking LSN of operation that needs to be undone
	- Upon undoing all the necessary operations for a given Xact, write END to terminate that transaction






