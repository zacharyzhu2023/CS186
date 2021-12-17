Vitamin 12


To Phase Commit (2PC) Protocol
- Phase 1 (Preparation): C sends "prepare" message to vote ether to commit or abort, Ps create prepare or abort
  record then flushes to disk, Ps send either "yes" or "no" vote to C, C generates commit or abort record & flushes
- Phase 2 (Commit/Abort): C broadcast results of vote to Ps (either commit or abort), Ps generate commit/abort
  record based on verdict & flush corresponding record to disk, Ps send ACK to C, C makes end record & flushes to disk

Question 1
- When is it NOT possible for the coordinator to abort an Xact?
	1. If coordinator wrote abort to its log, that means some participant voted abort --> will abort the Xact
	2. C received 6 "yes", waiting on 1: if the last one ultimately votes to abort --> C will abort
	3. C sent commit to all & got 6 ACKs, waiting on 7th: the fact that C sent a commit verdict means that it
	   must have received unanimous consent verdict --> impossible for it to proceed with abort
	4. P wrote abort in log --> it voted to "abort", meaning that C will abort overall
	5. P wrote commit in log --> P received "commit" verdict from C --> it must have received all commit votes
	6. P voted yes --> other P might have voted no (which would allow for overall "abort" verdict)
- When is it NOT possible for coordinator to commit an Xact?
	- With the above scenarios, 1 and 4 are valid answers since if C has an abort record in it log, C must have
	  received a "abort" vote in the 1st phase. Meanwhile, if participant has "abort" in its logs, P received a
	  "no" verdict from the C, which must have received a "no" vote from a participant


Question 3
- 3 Participant nodes (P1, P2, P3) and 1 coordinator node: C
- C takes 40s to send a message (broadcast @ same time), P1 takes 6s, P2 takes 12s, P3 takes 15s, 6s to flush

a. Best case if we want to commit the transaction & complete it
- Phase 1: C will broadcast the "prepare" message to tell the participant nodes that they should vote
	- Upon receiving this message, each of the Xacts will flush this record, then vote "yes" since they want to commit
	- Once all the participants cast their vote & coordinator receives it, flush "commit" log record to indicate
	  that the verdict was to commit
	--> Cost = Cost of Broadcast + Cost of participant prepare flush + Cost of voting + Cost of Coordinator Flush 
	    = 40 + 6 + max(6, 12, 15) + 6 = 67
- Phase 2: during phase 2, this is when the coordinator will send out the verdict to the participants, so the
  participants will flush the verdict record & send an acknowledgement of the verdict back to the coordinator
  	- Cost of Phase 2 = Cost of Broadcast Commit + Cost of Participant Flush Verdict + Cost of sending acknowledgement
  	  = 40 + 6 + max(6, 12, 15) = 61
- Finally, after phase 1 and phase 2, coordinator flushes the end record
- Total Cost = Phase 1 Cost + Phase 2 Cost + Final Flush Cost = 134

b. Best case if we have presumed abort w/ all participants voting to commit
- Results in the same cost as above since the presumed abort only matters if there are any "abort" votes
- Presumed abort is a form of an optimization that applies during "abort" operation

c. Best case if they want to vote the following P2 commits, P1 aborts, P3 aborts
- Phase 1: first, the coordinator will broadcast the prepare message to each of the nodes. While P2 is going to
  flush the prepare log, P1/P3 will instead add "abort" records. Using the presumed abort optimization means that
  P1/P3 need not flush the abort records. P2 send "yes", P1&P3 vote "no", sending results to coordinator. When coordinator
  receives the votes, it adds abort record (but no flush needed)
  - Cost = Cost of broadcast prepare message + max(Cost of Abort Records (cost of sending a message), Cost of Commit
  	Records (cost of send & flush)) = 40 + max(6, 12+6, 15) = 58
- Phase 2: the coordinator knows that we want to abort, so C send the messages to participants to tell them to abort.
  P2 is the only participant that needs to add an abort record, since P1/P3 already have an abort record. Using presumed
  abort means that even though we created new abort records --> no need to send acknowledgement since since the coordinator
  will assume that they aborted given no response
	- Total Cost = 40
- Cost across both phases = 58 + 40 = 98


