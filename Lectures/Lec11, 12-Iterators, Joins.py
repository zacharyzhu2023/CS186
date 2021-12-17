Lecture 11, 12: Iterators, Joins

Iterators
- Can think of a query as a series of nested relational algebra operators that take in and spit out a relation
- Query optimizer is responsible for choosing operators, each of which implements iterator iterface & actually
  runs efficiently the operation to be forwarded into the net operator
- Iterface interface includes the following: setup(), init(args), next(), close();
	- Setup: makes the dataflow graph (who are the children), init:  sets up the state, next: return a tuple in the
	  graph, close: close the iterator
	- This is a pull-based model: calling init/next call can get passed onto the children to be returned
- Init/next can be either streaming or blocking: streaming will only perform exactly the calculation that is needed in
  the moment and nothing more ('on the fly'). Meanwhile, blocking performs all the work in 1 single go ('batch')
- Encasulation: do not require subclass info --> iterators can be the input to other iterators. State: iterators contain 
  info about a state (might have hash tables, counts, sorted files, etc.)
- Query plan occurs on a single thread, and we can start to understand how the calls could potentially be nested
- The result of one query (Select, Sort, Groupby, etc.) occurs on call stack (do not need to use disk for memory)
	- Can recurisvely call init & next which recurse down chain of various iterators. Tuples get passed w/ next() operation

Select: On the Fly
1. Init(predicate): 
	child.init(); // Initializes the child and all the subtrees as needed
	pred = predicate; // Create the predicate parameter specified
	current = null; // Functions as a local cursor
2. next(): 
while (current != EOF and !pred(current) { // While not at end of file and current tuple does not satisfy predicate
	current = child.next(); // Try the next child
}
return current; // Return the child that first satisfies the given condition
3. close: child.close(); // Close the iterator

Heap Scan
1. init(predicate):
	heap = openHeapFile(); // From memory, we need to pull up the heap with which we are operating
	curPage = heap.firstPage(); // This holds the current page that we are in the heap
	curSlot = curPage.firstSlot(); // Get the slot in which we are operating for a given page
	# Notice that a heap has no children, so no recursive calls were needed
2. next():
	if (curPage == NULL) return EOF; // We have exhausted the entirety of the heap--end of story
	current = [curPage, curSlot]; // Get info to access record at a given page & slot
	curSlot = curSlot.next(); // Get the next slot on the page
	if (currSlot == NULL) { // We do not have any more room on the given page
		curPage = curPage.next(); // Try obtaining the next available page in the heap
		if (curPage != NULL) curSlot = curPage.firstSlot(); // If there is a page, get the slot in that page
	}
3. close: heap.close(); // All we need to do is close the iterator

Two-Pass Sort
1. init(keys): // Intended to perform the entirety of Pass 0 (generate sorted runs), making it a "batch" call
	child.init(); // Recurisvely call initialization on its children 
	while (child != EOF) { // So long that we are not at the end of the file--meaning we have not consumed entire input
		child.next(); // Fetch the next child
		Generate sorted runs on disk; // Fill the B buffers in sorted order on the disk
	}
	Open every sorted run file & load into input buffer; // Reached here--we have consumed entire input & can merge
	// We have read the pages from the sorted runs in prepareation for pass 1 calls (smallest tuple is in memory)
2. next():
	output = Smallest tuple across all the buffers // Get the smallest tuple across all the buffers in memory
	If minimum tuple is last in buffer --> fill that buffer w/ a new page
	Return the output or EOF if empty // Tuple is the minimum across all the data--iteratively returning min tuple seen so far
3. Close(): deallocate runs files; child.close(); // Recursively call close on the child

Aggregation Functions
- 4 aggregation functions--count, sum, avg, min--each of which have an initialization, merge mechanism, state, & value to return
1. Count: maintains a count, init: 0, merge by incrementing count, ultimately returns the count
2. Sum: maintains running sum, init: 0, merge by adding current element to the sum, ultimately returning sum variable
3. Avg: maintain sum & count, init: (0, 0), merge by incrementing count and adding current element to sum, returning sum/count
4. Min: maintain min variable, init: +inf, merge by taking smaller of current element and min variable, returning min variable

Group By: Sorted Input
1. init(groupKeys, aggs): // aggs: aggregation function
	child.init(); // Again, we choose to recursively call init on the children
	curGroup = NULL; // Set the current group to null
2. next(): // Idea: we need to fetching the next element so long as we are operating w/in the same group
	result = NULL; // Want this variable to hold the end result of the aggregation functions of a given group
	do { 
		tuple = child.next(); // Obtain the next tuple
		if (group(tuple) != curGroup) { // Case in which we have reached the end of a given group (sorted order, remember?) & did not newly start
			if (curGroup != NULL) { // This refers to the case in which we are not operating w/ the very first group
				result = [curGroup, result of aggregation]; // Get the group and what happens when we apply aggregation function to that group
			}
		curGroup = group(tuple); // Establish the new group using the new tuple of the new group
		Initialize all aggregation functions; // See the initial values of aggregation function to prepare for new tuples of group
		}
		merge(tuple) w/ aggregation functions; // Keep only 1 tuple in memory at a time; Maintain results of the aggregation functions
	} while (!result); // A result exists? Have gone through entirety of a group
	return result;
3. close(): child.close(); // Recusively call close on the


Simple Nested Loop Theta Join, Page Nested Loop Join
- Joins will use the following notation: [R] = numPages, p_R: records/page, |R|: numRecords. Assume that the following
  stats: Reserves table: [R]=1000, p_R=100, |R|=100,000; Sailors table: [S]=500, p_S=80, |S| = 40,000
- Syntax of a nested loop theta-join:
	for record r in R: // Go through all the individual records in R
		for record s in S: // At a given record in R, we need to scan through all the pages in S
			if (theta(r,s) resultBuffer.add(<r,s>);
- Cost analysis w/ R on outside, S on inside: [R] + |R|[S] = 1000 + 500*100,000 = 50,000,100
	- We need to scan all the records once in R once (meaning we go through all the pages), then need to go through each
	  record in S on the page level across every record in R
- Cost w/ S on outside, R on inside: [S] + |S|[R] = 500 + 40,000*1000 = 40,000,500 using same logic as above
- Page Nested Loop Join: can improve upon previous algorithm by going on a page by page basis
	for page rPage in R:
		for page sPage in S:
			for tuple rTuple in rPage:
				for tuple sTuple in sPage:
					if theta(rTuple, sTuple): resultBuffer.add((rTuple, sTuple));
- Cost analysis of page nested loop join: need to scan in pages of R, then for every page in R we read in a page in S
  --> Cost = [R] + [S]*[R] = 1000 + 1000 * 500 = 501,000

Block Nested Loop Join
- Idea: read S pages at a time (think of it as a block/chunk) in contrast to page nested loop join, which goes a page at a time
for each rChunk of size B-2 pages in R: // Need to save 1 page for input, 1 page for output
	for sPage in S: // Still operating on a page level in S
		if (theta(sPageTuple, rChunkTuple)): resultBuffer.add((rTuple, sTuple)) // Go through records for the chunk/page combo
- Cost analysis: [R] + [R/(B-2)]*[S] since we still need to read the record in R, but then when we perform the cross sections
  there are only R/(B-2) iterations on R-front & [S] on the S-front (since we are reading that on the page level)
  --> Cost = 1000 + (1000/(B-2)) * 500 which can see massive savings for large B

Index Nested Loops Join
for tuple r in R:
	for tuple s in S where r_i == s_j: result.add((r, s)) // Performing an equijoin on r_i = s_j
		- The advantage of the inner loop is that we only need to llok at entries in S such that a match is made:
		  does so by utilizing an index that looks up r_i in S
- Cost of evaluation: [R] + |R| * MatchingCost. Still need to read in all the records of R, then try to match those tuples
  against those in S, but the cost depends on the index that we are using
  	- Alternative 1 index: MatchingCost = cost to get from root to leaf (usualy ~2-4 IOs)
  	- Alternative 2/3 index: MatchingCost = Cost to look up RID (~2-4 IOs) + Cost of retrieve RID
  		- Clustered index: 1 IO per page of matches, Unclustered index: 1 IO/matching tuple
- Assume we are working w/ Reserves, Sailors table above given that sid is the primary key in sailors (matched against SID in reserves)
  and that the height of the tree is 2 (takes 3 IOs to traverse from the root to the leaf)
	1. Unclustered Cost = [R] + |R| * (numMatchingTuples) * (Cost/Tuple) = 1000 + (100,000) * 1 * (3+1)
		- Cost/Tuple = 4 IOs since we need to get to the leaf node then read it. numMatchingTuples = 100,000 since there
		  is precisely a single match across every record in R (corresponds to a single SID)
	2. Clustered Cost = [R] + |R| * (numMatchingPages) * (Cost/Page) = 1000 * (100,000) * 1 * (3+1)
		- Same logic as w/ the unclustered cost, since each matching tuple will be on its own page
		- If there are multiple matching tuples --> clustered cost is vastly reduced


Sort-Merge Join
- Sort-Merge join only applies to equijoin, natural joins since they have an equality predicate
- Idea: first, sort 2 tables R, S by the join key if the tuples are not already on csorted order
- Then, perform a merge-scan of the sorted partitions, adding the tuples w/ matching equality predicate to the result
- Algorithm of Sort-Merge Join is outlined below:
	if (!mark):
		while (r < s) r.next(); // As long that the record in r is smaller --> check next record in R
		while (r > s) s.next(); // Advance s to get the next higher element in the S table (since s record too small)
		mark = s; // Indicates which record we are operating w/ in the S table --> we have found a match
	if (r == s): // Want to keep reading S records until there is a non-match against r_i
		result = [r, s]; // Start off w/ the match obtained in the prior step
		s.next(); // Get the next record in S to check against the given result
		return result; // Returns the result obtained via the initial match
	else: // Case where after a series of matches, we have found a non-match in S
		s = mark; // Start back at the last point at which we knew there was a match w/ R, S
		r.next(); // Move onto the next element in R to match against S records
		mark = None; // Reset mark variable to attempt to find next matching element

Cost of Sort-Merge Join, Refinement:
- Cost of sort-merge join = Cost of sorting R + Cost of sorting S + ([R] + [S]) since we need to sort each of the tables initially,
  then generate the merged runs based off of the join key
  	- In the worst case, there are [R] * [S] possible records if we need to join all the records in R w/ all the records in S
  	- In the R, S example, cost becomes:  4 * 1000 + 4 * 500 + (1000 + 500) = 7500 since we need to sort in 2 phases (read/write in each),
  	  then generate merged tuples via streaming
  	- Cost of Join, Sort: Join = [S] + ([S]/(B-2)) * [R] = 5500, Sort = 4 * [R] = 4000 since to join on block level need to read through
  	  all pages of S, and for every chunk in S need to read a page in R (asuming 102 buffers). Sort involves 2 passes using larger of 2 tables
  	  	- Clearly, join -> sort is less efficient compared to sort-merge join

Sort-Merge Join Improvement
- Improvement be made by combining final sort phase w/ the merge phase, given sufficient memory to hold page of run in [R] & [S]
	1. Read R & write sorted runs to memory. Read S & write sorted runs to memory
	2. As we merge the runs from R, S in memory--> find the crossjoin matches b/w the 2 (we know min value of R, S in memory)
- Can call next() just like w/ merge-join, but now we call next on the final merge of R & final merge of S (do not need to write out final
  Pass of R, S during the sorting)
	- Allows us to avoid having to perform the final pass in R, S --> new cost = 3[R] + 3[S]
- This requires that we have a page from the runs generated by R, S in memory which allows us to know which page to read from when merging
	- Requirement stated in a different way: number of runs in last merge phase R + number runs in last merge phase S <= B-1

Memory Hash Join
- In-memory hash join: occurs in memory, assuming that R is the smaller relation. This algorithm requires R to fit in memory
	- Algorithm: load R into hash table. Then, scan S and match against the records in R
	- This requires R < (B-2) * hashFillFactor given B buffers, since we need an input and an output buffer, adjusting for space of the hash table
	- Meanwhile, S can be an arbitrary size since we are streaming it in age by page
- Sample query: σ(sid=4 U sid=6) (R CJ S on SID) = σ(sid=4) (R CJ S on SID) U σ(sid=6) (R CJ S on SID)
	- Essentially, we have decomposed the initially selection clause into 2 different joins that we union, w/ 2 different sid values
	- Can extend this to all the potential SID values (decompose join of R, S into selection of hash values of sid) --> hash buckets need to fit in memory

Grace Hash Join
- Grace hash join can only be used w/ equijoins or natural joins which have an equality predicate
- 2 stages: 1. Partition records of R, S using join key and store on disk (if they have same key, they are in same partition). 2. Build/Probe
  a hash table across all the possible partitions assuming smaller relation partition fits in memory
- Step 1: divide the relation into partitions using hash function. Step 2: take the partitions of step 1 to place into hash table, but be sure
  to probing relation, that uses same hash function as the initial divide phase to spit out records to form the entire record included building & probing relation
  using naive hash join

Grace Join Pseudocode
for cur in (R, S): // Looking at each of the relations in R, S
	for page in cur: // Within that relation, go through all the pages
		read page into input buffer; // Load that into the input buffer
		for tuple in page: // Go through individual records in that page
			Add tuple into output buffer hash_p(tuple.joinkey) // Place into bucket based off of its join key
			if (outputBuffer.isFull()) --> flush to disk partition // If buffer is full, we expel the results to memory
	Flush output bufer to disk partitions; // Anything remaining on the output buffers should go to disk
for i in range(0, B-1): // Look at each of the partitions that were generated
	for page in R_i: // Across every page in the building relation
		for tuple in page: // Pick out a specific record w/in that page
			Build tuple into memory hash_r(tuple.joinkey); // Using the join key, add that tuple into the hash table
	for page in S_i: // Looking at all the pages in the probing relation
		Read Page into input buffer; // Load that page into input to be matched against records of R
			Probe memory hash_r(tuple.joinkey) for matches; // We already have a fully formed hash table of R --> find all matches
			Send matches to output buffer; // Of those matches, want to write them to output
			Flush output buffer when full; // Again, only spit out to memory if full

Grace Hash Join Intuitive Process 
- First, we partition in S using the hash function, reading it a page at a time. Tuples that match should be in the same partition
	- Generate new buffers as needed, flushing the B-1 buffers to output once they are full
	- Perform the same process w/ R, dividing the records in R, S into partitions to which we will perform naive hash join
- Next, we build on relation R, reading in a relation to the hash table. We read in relation S to the input buffer, obtaining all matches against
  the hash table we read in for R, writing each of the matches to output, knowing that we flush when full
  	- This process involves us streaming table 
- Cost of Hash Join: partition phase involves reading & writing both relations --> 2*([R]+[S]) IOs & the matching phase involves
  reading both relations & stream data to the output --> [R] + [S] ---> Total Cost = 3([R] + [S])
- Memory Requirements of Grace Hash Join: need to build table R using uniform partitioning into B-1 Runs of size [R]/(B-1)
	- Then, during matching, we need to ensure that [R]/(B-1) < B-2 since we need to be able to fit each of the partitions in memory
	--> R < (B-1)*(B-2), though there is no constraint on S

Conclusion
- Naive hash join requires that [R] < B so that we can fit the smaller of the two relations in memory as a hash table --> cuts the IO cost by a factor of 3 
- Grace Hash Join reuiqres that [R] < B^2 (looser requirement) & performs the hash-joining in 2 phase: the partition phase & probing phase 
- Sorting Benefits: useful if input is already sorted or if the output needs to be sorted. Also, not vulnerable to data skew/poor hash functions
- Hashing Benefits: if joining, number of passes only deends on size of the smaller relation (obviously good for hashing specifically)
- Nested Loop Join: universally works, regardless of what kind of predicate we are working w/. Can operate on chunk level to improve performance
- Index Nested Loops: used w/ equijoins (equality predicate) given that we have the index for one of the relations
- Sort/Hash: used w/ equijoins, does not need a relation, performance very good when one relation is much smaller than the other


