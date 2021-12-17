Lecture 9, 10: Sorting, Hashing

Motivation for Sorting
- Sorting can be used for rendezvous, gathering necessary tuples in memory in one location simultaneously to be processed
	- Examples: DISTINCT (need to get all copies and keep only the unique ones), group by: cluster data, join: need to merge tables
- Also used for ordering, if the user desires the data to have a specific order in the results that get returned
- Issue: need to be able to sort large amounts of data w/ much smaller amounts of RAM. Cannot use virtual memory since it
  becomes random disk IOs --> does not understand sorting algorithm
- Out of core algorithms are what we use to process amounts of data larger than RAM. Fall into 2 primary camps: single pass streaming 
  through RAM, divide & conquer

Single Pass Streaming, Double Buffering
- Assume we want to "map": given a record, apply some function to it, then write the result, minimizing RAM & read/write calls
	- Approach: read a page into the input bufferm calling f(x) on each item w/in that bufferm which gets spit out to the output buffer
	- Under this approach, do not write the output buffer back to actual output until output buffer is full to save on IOs
- Double buffering: have 2 threads, one that performs the computation (call f(x) on input buffer) and the other for IO operations
  (read input, drain output, etc) which run in tandem w/ one another (uses parallelism)
  - First, IO thread in charge of reading in novel input & compute thread in charge of already read in data to process it
  - Next, IO thread processes data that compute thread finished processing & compute thread deals w/ newly read in data

Sorting, Hashing
- Setup: assume we are operating w/ a file, F, that contains a multiset of records, R, using N blocks of storage. Also have: 2 scratch
  disks w/ > n blocks for storage & a finite amount of space in RAM (can hold B < N blocks of disk)
  - Sorting: will produce a file, Fs, that has R stored in a specific order specified by sort key
  - Hashing: produce file, Fh, where records R are placed on disk in a way such that no 2 records w/ same hash value have a record
    w/ a different hash value sandwiched between them --> matching records are stored contiguously in the file

2 Way Sort
- Bad sorting algorithm: given an input, we read in a page, sort it, write it in block-sized chunks. Then, in the 2nd pass, we take 2
  of the sorted blocks, merge these "runs" together (using 3 buffer pages) until output buffer is full, then filling input to repeat
  - This behaves as a streaming algorithm, in which we take runs as input, merge them to create runs that are twice as large
  - First pass will sort the blocks of a page, every subsequent pass will merge the blocks together, draining/filling the buffers

External Merge Sort
- Idea: we want to improve upon 2 way sort by taking advantage of the B > 3 buffer pages that we have available to us
- Pass 0: use B buffer pages to create ceil(N/B) sorted runs that are B pages apiece. Pass 1-N: merge the B-1 runs simultaneously
	- To merge B-1 runs at the same time: take the lowest value across all B-1 runs and insert into output. Keep going until a page is empty,
	  in which case we pluck values from remaining files
- We know that each run must be of length B, merging B-1 runs simultaneously --> pass 1 yields: sorted, merged runs are of length B(B-1)
- Number of passes required: initially, we incur a cost of 1 to obtain the initial B-1 length B runs. Then, each pass afterward is going to
  merge B-1 runs together (shrinking number of runs by a factor of B-1)
	- log_b-1(numRuns) = log_b-1(ceil(N/B)) --> Total IO = (IOs/Pass)*(Num Passes) = 2N * log_b-1(ceil(N/B))
- Example: assume we have 5 buffer pages and a 108 page file
	- Pass 0: ceil(108/5) produced 22 sorted runs of 5 pages apiece (last run is truncated). Pass 1: produces 22/4 = 6 merged, sorted runs
	  of length 4 * 5 = 20, last run only has 8 pages. Pass 2: Merge ceil(6/4) = 2 sorted runs, first is 80 pages, 2nd is 28 pages. Pass 3:
	  merge those 2 pages together
- Space requirements: Pass 0 produces ceil(N/B) runs of size B, Pass 2 merges B-1 sorted runs --> can create sorted & merged
  B^2 sized data w/ just B sized space using just 2 passes

Hashing
- Idea: sometimes we just want to get rid of duplicates or create groups for our data, in which case sorting is no longer necessary
- Hashing offers this alternative, but we need some way to do it out of core (perform > RAM sized calculations in RAM)
- Hashing Algorithm comes in 2 phases: divide and conquer, offering a parallel to sort which had a conquer & merge phase
	- Divide: feed data into a hash function which gets partitioned across the B-1 buffers to be processed
		- Note: The divide phase can end up using more data pages than original input
		- Also keep in mind: divide phase will stream records through a partition into disk partitions such that the matching values
		  will be grouped w/in the same partition but they are not necessarily stored consequentively
	- Conquer: read partitions into an in-memory RAM hash table individually using a new hash function from the hash phase, creating buckets
	  w/ some distinct values. Read RAM hash tables --> write to disk, ensuring contiguity is met
	  	- Idea: starting w/ partitions generated in divide phase, read those records in applying the hash function to generate
	  	  a new hash table in-memory. Then read the buckets individually to create the final output

Cost Analysis: Hashing, Sorting
- IO of Hashing: divide phase needs to read in all the data and write them to the disk to the B-1 buckets --> 2N. Conquer phase reads in the data from
  the partitions, then write all the buckets back to disk --> 2N. Total Cost: 4N
- Memory requirement of hashing: initial partitioning plops data into B-1 buckets of size N/(B-1). During the 2nd phase (conquer), each partition
  is limited to B pages in size since we need to process B records at a time w/ our B buffers--> B(B-1) sized table can be hashed w/ B memory buffers
- IO of Sorting: conquer phase initially reads in all the data, which gets sorted & written on the block memory. During divide phase, first
  read in the sorted run, writing the merged version back to memory --> 4N
- Thus, hashing/sorting are dual algorithms w/ similar IO patterns

Recursive Partitioning
- Previously, it was assumed that after initial phase, all the partitions contained data that was <= B pages in size
- If this is not the case, we need to recursively partition the data, which we see the need for right after the 1st phase
- Recursive partitioning: upon realizing that one of the buckets is > B pages in size, apply a new hash function that is distinct from the previous
  to generate new buckets for the original bucket, then apply the conquer phase yet again
  - If there are frequent duplicates in a large dataset, difficult to uniquely partition the data. Thus, need to apply a check to see if the
    previous and current partition are the same

Parallelization
- Hashing: assume that we are operating w/ a interconnected network of disks & memory across multiple computers
- Read in data from the disk of each computer, to which we apply the hash function to determine which memory to send that chunk of data to
	- Then, on a given machine, apply traditional hashing algorithm (partition w/ hash function on disk, then conquer by applying another
	  hash function to place record in the main memory hash table to be written to the output)
- Pass 0: read in all the data in parallel, Pass 1: write data to partitions in parallel, Pass 2: read in partitions in parallel, Pass 3: generate
  final buckets & write to main memory in parallel
  - Maintains the same IO but can spread the work across multiple computers in a network
- Sorting: initially shuffle the data across machines, but the initial pass to send record to is split on value range
	- Lowest values go to lowest machine, next lowest to 2nd lowest, etc. splitting by the split value
	- Pass 0: send records to appropriate machine using the value split. Pass 1: Read in data. Pass 2: Sort & write data. Pass 3: Reread the data
	  in the sorted runs. Pass 4: merge the sorted runs
	- Challenge: want to evenly distribute the workload across machines, so need an accurate range on which to split. Else, we end up w/ data skew,
	  in which some machines have more records than others

Hashing vs. Sorting
- Hashing and sorting have the same memory requirement and same IO cost, so performance on that front will not differ
- However, hashing wins out when dealing w/ duplicate elimination (scales well w/ number of distinct values)
	- If we encounter a duplicate value in a hash table, we can get rid of it, so in 2nd pass there is only going to be unique values
	  instead of preserving all the records
- Meanwhile, sorting scales w/ number of values; does not apply any of the optimizations that hashing does. However, benefits from not
  needing to directly deal w/ the duplicates

Summary
- Hashing applies a divide & conquer algorithm. Meanwhile, sorting applies a conquer & merge algorithm
- Do not need sorting for rendezvous (grouping data together or getting rid of duplicates)
- Both of these algorithms can be improved through double buffering, in which we separate the tasks of IO and the actual computational work


