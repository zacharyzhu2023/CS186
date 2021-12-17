# Vitamin 1

1. Largest to smallest levels of organization: file -> page -> record

2. 5 full pages, 10 pages w/ free space
	a. IO cost to guarantee space w/ page for a heap file --> 11 (read header, go to end of LL reading each page sequentially)
	b. 5 full, 10 free --> 15 pointers across 2 pages since each page contains <= 8 entries --> read the 2 pages, guaranteed to
	   find a valid pointer

3. Heap vs. Sorted File
- Full scan: heap vs. sorted file does not make a difference b/w this just means reading all the pages in a file
- Range Search: sorted files (log2B + pages) * D are substantially better than heap files (B * D) since they do not have to
  go through all records individually but instead can look for the right starting point
- Equality Search (finding specific record by key): again, sorted file outperforms heapfile since it can binary search to a solution
  instead of going through the individual records in sequence
- Insert: heap files (2D) are better than sorted files (log2(B) + B) * D since they do not have to find specific location but
  rather just add onto end of a block
- Delete:heap file (B/2+1) * D does much better than sorted files (log2B + B) * D since sorted files need to shift records
  to eliminate the gaps in records

4. 64KB page --> 2^16 Bytes, footer: 10B (record count/pointer to free space), slot directory (4B/record), Int: 4B
a.
	- Schema of the inventory table: 2 integer fields, 1 text field
	- Within this page, we know that 10B must be allocated for the footer --> 2^16 - 10 bytes remain to be used
	- 2 integer fields occupy 8 bytes total per record, and need 8 bytes (4 to store pointer, 4 to store length)
	--> this results in use having a max of (2^16 - 10)/16 = 4095 records
b. Same as above, but require storing 4B for record header, 32 bit pointer for end of variable length field
	- 8B needed to store 2 integers, 4B needed to store the record headers, 
	  4B needed to store pointer to variable length field --> 16B --> 128 bits


5. Operations: a-select state w/ a where clause, b-delete, c-insert
	a. Heap file speed
		- Select statement (scan all records): B * D, Delete: (0.5B+1)*D, Insert: 2D
		- Clearly, inserts are fastest, then deletes in 2nd (b/c on average the record is 1/2 way in), and select is the
		  slowest since it requires going through every record to check the where clause
	b. Sorted file speed
		- Select: B * D, Delete: (log2B + B)*D, Insert: (log2B + B)* D
		- Same logic as above for the select statements since select uses a different field than the sort key (the primary key)
		- Delete takes advantage of the sort key and thus does not require reorganizing the pages
		- Insert also does not require reorganization since the pages are only 2/3 full
	c. Total IO (2 Integers, 1 Float, 2 Varchar of length 20)
		--> 4 * 3 + 40 = 52 w/ straightforward math











