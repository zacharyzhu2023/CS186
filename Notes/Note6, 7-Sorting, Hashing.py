Vitamin 6


Question 1: Context--150 pages, 23 pages of RAM (buffer pages)
a. Sorted runs in Pass 0: ceil(150/23) = 7
	- Formula: ceil(File Size in Pages/Num Pages of RAM)
b. Maximum pages in a run: 23
	- This is exactly the same as number of pages of RAM, since we fill up all the runs w/ RAM capacity, w/
	  the possible exception of the final page
c. Number of Input Buffers in Pass 1: 22
	- Number of input buffers used = Number of buffer pages - 1 since we need to retain one buffer to hold output
d. Number of Output Buffers in Pass 1: 1
	- Only need a single output buffer since we are trying to stream the merged version of the data anyhow
e. Number of sorted runs after Pass 1: 
	- We know after Pass 0, we have produced 7 pages w/ ~23 pages, so we since numPages < numBufferPages --> can
	  merge them into a single run w/in the first Pass
f. Number of pages post-sorted run: 150
	- After Pass 1, all the pages are now glommed into 1 single run w/ 150 pages
g. IO Cost
	- Pass 0: Read 150 pages, write 150 sorted pages into memory
	- Pass 1: Read 150 sorted pages, write the 150 sorted pages to disk


Question 2: Setup is that there are B pages of RAM available and B(B-1) pages to parse
	a. Number of input buffers = 1 since we want to divide our data into as many partitions as we can, leaving us w/ 1 frame to take in input
	b. Number of partitions = 22 since we want to divide data into as small as possible while still leaving 1 buffer to take in initial input
	c. Pages per partition: Given B-1 partitions --> Insert B pages of data into each partition
	d. 10 buffer pages: number of pages to hash that guarantees no recursive partitioning
		- Idea: we know that we need to recursively partition if we end up with a partition that contains > our number of buffer frames. Thus,
		  in the worst case our hash function sticks everything into the same buffer frame, but we can still handle all that data in that single
		  frame so long as that frme is 10 pages or fewer (the original number of buffer frames)
	e. 20 buffer pages: how many pages can we hash and force us to use recursively partition?
		- Given a perfect hash function, all the pages will be evenly distributed across all frames. As such, we saw previously that
		  we will be able to use 20 - 1 = 19 partitions that contain 20 pages apiece --> 19 * 20 = 380 pages w/o needing to recursively
		  partition --> 381 forces the hand at recursive partitioning
	f. 15 pages, do not want to recursively partition: 210 (see logic above)
	g. 72 KB memory, 4 KB pages, Cost of IOs of 128 page file: 606
		- We have 18 pages of RAM, which can hold 4 KB apiece
		- 18 buffer pages in total: divide into 17 buckets (128 reads)
			- Afterward, 1 bucket has 20 pages, remaining 16 have ceil(128/17) = 7 pages apiece (20 + 16 * 7 = 132 writes)
			- Need to recursively partition the 20 (read 20, split into across 17 buckets --> 2 pages each) --> +20 reads, +34 writes
		- Total pages: 132 - 20 + 34 = 146
			- Need to read/write these back to memory --> 146 * 2 = 292
		- Total Cost = 128 + 132 + 146 *2 = 606

1 x 1000 -> 100 x 10 -> 12 x [90, 10] -> 2 x  [810, 190] -> 1 x [1000]
