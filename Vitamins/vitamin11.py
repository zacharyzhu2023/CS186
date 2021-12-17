Vitamin 11

Question 1
- Parallel hash join constitutes a single query, which is why parallelizing it results in intraquery parallelism
- If running >1 query, then we are working w/ interquery parallelism
- Context: 8 machines, 3 page buffers, 96 pages of data
	- Number of sort passes: 1 pass used to partition data across 8 machines (each machine now has 12 pages). On each of
	  those machines, we have: 4 x 3 -> 2 x 6 -> 1 x 12
	- Number of hash passes: First pass will distribute data to 8 machines (each now has hash table w/ 12 pages: 1 x 12).
	  Then, 1 x 12 -> 2 x 6 -> 4 x 3 which requires 2 partition phases & 1 conquer phase

1.4
- Context: R, S have 32 pages, range parititon over 2 machines w/ 4 buffer pages each
- Want: disk IO cost of sort-merge join
- Each of the machines have 16 pages each, each w/ 4 buffer pages
	- 1 x 16 -> 4 x 4 -> 1 x 16 (3 passes, need a read/write in each of these passes)
	- Before the passes, need to read in data. Afterward, also want to read each of the relations 1 more time each to join
	- Total = 16 * (2 * 3) + 16*2 = 256

1.5
- See problem above, but we want to get network cost of worst case scenario w/ parallel SMJ
	- Yields a cost of 256 likewise since network cost is at its worst when all data is sent via machines & processed
	  there instead of locally

Question 2
- Context: m1 has 45 pages w/ values 1-50, m2 has 10 pages w/ values 51-100, m3 has 50 pages w/ values 101-150
	- Assume each machine has 1k pages of memory & data is not stored in sorted order
- When finding max(age) of this table, only need to check m3 directly given the range values (50 IOs)
- Select Count(age) From Students: will result in 105 IOs since need to read m1, m2, and m3

2.5-2.8
- Context: Table T has 90,000 pages, Table C has 90 pages, 3 machines, pages are 1 KB in size
	- When executing the parallelized versions of operations, need to distribute the pages of tables evenly. That means
	  that 60k pages in table T need to be moved and 60 pages in C need to be moved
	- In addition, 180 KB need to be sent to new machines to be sent to all the different tables beyond the original


