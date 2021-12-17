Vitamin 6

Q1: Join Costs
- R: 10,000 tuples, 10 tuples/page, 1,000 pages
- S: 2,000 tuples, 10 tuples/page, 200 pages
	- Primary key: b
- Stored as heap files w/o indices & 52 buffer pages
	1.1: 1000 *200 + 1000 = 201,000 (need to read in R, read in S, write join result --> 3 buffer pages needed)
	1.2: [R] + [R]/(B-2)*[S] = 1000 + (1000/50) * 200 = 5,000 --> need all 52 buffers
	1.3: Cost of Sort-Merge Join = Cost of sorting R + Cost of sorting S + ([R] + [S]) = 4*1000+4*200+(1000+200) = 6000


Q3: R = 60, S = 20, Have 6 buffer pages
a.
- R: (1 x 60) --> (5 x 12)
- S: (1 x 20) --> (5 x 4)
	- S gets stored in memory (which is what we care about recursively hashing)
	- Still need to hash R, S uniformly though --> that initially incurs read/write cost
	- Upon creating the partitions of each table, we just need to read in all pages across all the partitions
	- Total Cost = 80 + 80 + 80 = 240

b. Partitions: (20, 20, 10, 4, 6) AND (4, 7, 2, 5, 2)

- S: (1 x 20) -> (4, 7, 2, 5, 2)
	- 4, 2, 5, 2 all stay the same after initial partitioning
	- As such, each of those records just need to get read w/ their R counterparts
		- Cost = (20 + 4) + (10 + 2) + (4 + 5) + (6 + 2) = 53
	- 7 case: we will recursively hash the corresponding records in R, S w/ this row combined (27 pages in total) -> (5 x 6)
	  which now fits in memory
		- +27 initial read, +30 initial write, +30 final read
		- Total Cost = 87
	- Initial cost of initial parittioning = 160
	- Total = 160 + 87 + 53 = 300










