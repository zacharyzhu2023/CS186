Lecture 5: File Organization

File Organization Overview
- We are interested in the following operations: insert, delete, modify, scan all records, fetch recod by recod ID
- Heap Files: unordered collection of records, use when access pattern requires full scan
- Sorted Files: files w/ a specific ordering; useful when records are retrieved in order or a range of records is needed
- Clustered Files/Index Files: pages/records have systematic grouping; organizes data in blocks to expedite lookups/modifications
- Across each of these formats, we are interested in how inserts/deletes/modifications/fetch/scan operations occur &
  cost of these operations
  - Need to consider tradeoffs b/w these forms of organization to try to judge have the "best" access patterns are

Cost Model/Analysis
- Setup: B = num blocks in a file, R = num records in a block, D = average read/write time to a disk block
	- This model assumes that every block holds the same number of records
- Assume that we ignore the differences b/w sequential vs. random IO (assume uniformity), time savings of prefetching (the time
	saving optimizations such as caching do not occur in hypothetical model), in-memory costs (calculating offsets & other operations
	are not accounted for)
- Also assume that each insert/delete operation occurs w/ a single record, equality search will give 1 match, heap file inserts to the last 
  block in a file, sorted files repack upon deletion & sort by a search key
- Ultimately, need to determine the runtime analysis in order to later optimize running queries

Cost of Full Scan (Go through all records)
- Cost for heap file: BD, Cost for a sorted file: BD
- Scanning all records involves going through each block individually in a file. The organization of the file does not
  affect the behavior, since we have to touch each block through this operation
  	- Cost per block: B, Number of blocks: D --> B*D cost in total

Cost of Equality Search (Look for a key)
- Cost for a heap file: 0.5BD, Cost for a sorted file: (log2B)*D
	- Heap file analysis: when searching for a key, the worst case scenario would be to go through the entire file (scan all B blocks)
	  but on average only requires going through 1/2B of the blocks before finding desired result --> 1/2B scans * D cost/scan = 1/2*BD
	- Sorted File Analysis: worst case scenario is log2B cost. With binary search, probability of getting right block in first attempt
	  is 1/B. Probability of getting it in 2 IOs is 2/B (account for LHS, RHS). 3 IOs: 4/B. Carry onward: 
	  Expected cost = sum [0, log2B] (i * 2^(i-1))/B = log2B - (B-1)/B where (B-1)/B ~ 1 --> log2(B) reads --> Expected cost = log2(B) * D

Cost of Range Search
- Cost for a heap file: BD, Cost for a sorted file: (log2B+pages)*D
	- Heap File Analysis: to find all the values that are within a range, then we need to scan through all the records since there
	  is no coherent ordering to the data
	- Sorted File Analysis: first, need to find the location of a given value, which previous shown as cost of log2(B) to find a given location.
	  From that location, keep going through the file till we encounter a data value that falls outside of that range

Cost of Insert
- Cost for a heap file: 2D, Cost for a sorted file: (log2B+B)*D
	- Heap File Analysis: Assume that we can precalculate the end location at which we want to insert the record. We need to read a page
	  into memory, write the new record to it, which is then saved back into memory
	  	- We never write directly to memory, so modifying a page/file requires 2 IO operations each time
	- Sorted File Analysis: First, need to locate where to insert the new record, which is a log2(B) operation. Then need to shift over
	  remaining records to the right of current location (which on average is B/2 records, each of which require a read + write)
	  	- Shifting (modifying existing records): 2*B/2*D = BD, Finding right location: log2B * D--> total: (B+log2B)*D


Cost of Delete
- Cost for a heap file: (0.5B + 1)*D, Cost for a sorted file: (log2B+B)*D
	- Heap File Analysis: On average, takes 0.5B to find the right record. Upon finding the right location, incur one more write operation
	  to modify a given page to get rid of that reocrd --> (0.5B+1)*D
	- Sorted File Analysis: find record to delete--> log2B. Create hole in page + repack w/ records to the right, which average cost
	  becomes B/2*2 (1 read, 1 write w/ the average location being in the middle of the file) --> Total Cost = (B+log2B)*D






