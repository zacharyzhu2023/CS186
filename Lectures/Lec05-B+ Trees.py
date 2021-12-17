Lecture 5: B+ Trees

Indexes 
- With heap files, we could either fetch a record by its recordID or by scanning the entirety of a page to look for a record
- Instead, want to build an index to avoid having to go through the entirety of the page to look for records
	- Examples of data structures w/ indexes: search tables, hash tables. Want: a paginated index data structure (made of data pages)
- Index: data strcuture allowing for quick lookup, modification of data entries using a search key
	- Lookup: want to determine which entries meet a criteria (match equality, or fall w/in a range)
	- Search Key: subset of columns of a table that need not provide unique entries in the end
	- Data Entry: stuff that is stored in the index; assume we store a pair of keys & recordIDs (a heap file pointer to records)
	- Modification: want efficient insertion and deletion of data from the DB
- Examples of forms of indexes: B+ Tree, Hash table, R-Tree, GiST

High Fan-out Search Tree: Build
- Assume that we have input heap file, which contains individual values: [3,4,5], [1,2,7], [8,6,9], [10,_,_]
	1. Sort file & leave space: [1,2,_], [3,4,_], [5,6,_], [7,8,_], [9,10,_]
		- Note that the page is sorte in logical order for access sake so pointers to next pointers not needed
	2. Create index structure over this sorted file on top of the original file
		- Do not use binary search over the heap file since a binary tree will create a log2(size) structure --> many IOs
- Improvement 1: Create a search file for the file w/ the data of sorted (key, pageIDs) pairs where key points to the first
  entry in each page. This file is substantially smaller than original file b/c do not need to store record info, so binary
  search can be conducted more efficiently
  - Improvement 2: make a search file for the first search file --> keep recursing until we are left w/ a single page in search key
- Key invariant: guarantee that at a given node [...(K_L, P_L), (K_R, P_R)...] all values in range of [K_L, K_R]are in tree P_L
	- All values less than the upper key of two adjacent nodes and >= lower key is contained in the left subtree

High Fan-out Search Tree: Search
- When searching for a key, start at the uppermost level, searching for adjacent nodes that the key falls between. Then, follow pointer
  to the next layer of the tree until we ultimatel reach the data pages themselves
  - Results in a complexity of: O(log_F(NumPages)) where F = fanout factor since that will be the height of the tree
- Optimization 1: drop leftmost key of each search file since they encode redundant info about the fact that value < node immediately to the right
- To create the search tree, have the data pages stored in the file first, followed by the index pages
	- Under this structure, scans will be efficient since data is contained at the beginning of the indexed file
	- Achieve high fanout since index pages allow for many pointers to the data pages
- This data structure is referred to as ISAM, w/ the primary drawback being the insert operations
	- Difficulty arises when a page does not contain enough room to insert a record at its proper location, which results in us needing
	  overflow pages that we need a pointer to

ISAM
- ISAM contains data entries in a sorted heap file, followed by a high fanout static tree index
	- Enables quick search through the index & locality (since sorted values are next to one another) but requires
	  insertions to potentially go into overflow pages, which are not efficient
- ISAM is essentially a simpler version of the B+ tree, but w/o some of the benefits

B+ Tree
- Similarities w/ ISAM: interior nodes made up of (key, pointer) pairs, contains key invariant guarantee, uses a similar search mechanism as ISAM
	- However, no longer contains the overflow pages that plagued the ISAM structure (more efficient insertions)
- Properties of B+ tree: has a balanced tree index, supports efficient insertion/deletion by growing at room and not leaves
- Contains an occupancy invariant: guarantee that all interior nodes are at least half full: d <= num entries <= d where d = order of a tree
- Example B+ Tree: 1. [17,*,*,*], 2. [5,13,*,*], [24,30,*,*], 3. [2,3,*,*], [5,7,8,*], [14,16,*,*], [19,20,22,*], [24,27,29,*],[33,34,38,39]
	- This tree has: d = 2 since each node contains at most 5 pointers (fanout factor) --> 2d+1 = F --> d = 2
	- Root is exempt from being half full since this still allows us to adhere to asymptotic bounds for our tree
- Node that the values are not packed in the B+ tree structure since we want to be able to insert & still have room
- Height 1 tree scale: fanout 5 --> each pointer points to page w/ at most 4 records --> 20 records
- Height 3 scale: fanout = 5, so root -> 5 L1 pointers -> 25 L2 pointers -> points to 125 data pages, each w/ <= 4 records --> 4*5^3 records 

B+ Tree: Search
- TREE: 1. [13,17,24,30], 2. [[2,3,5,7],[14,16,**],[19,20,**],[24,27,29,*],[33,34,38,39]]
- When searching for a record, operates sme way as ISAM, in which we start at the root node and conduct binary search to find
  the next search page via the pointer to next node until we reach the ultimate (pageID, recordID) pair
  	- This pointer allows us to access the actual record via the corresponding page & record ID if we want to fetch the actual data

B+ Tree: Insertion
- TREE: 1. [13,17,24,30], 2. [[2,3,5,7],[14,16,**],[19,20,**],[24,27,29,*],[33,34,38,39]]
- Insert 25: first, follow the search algorithm to find the proper location in the leaf layer in which to insert the value.
  Insert at the end of the page if room permits. Sort that leaf as needed
- Insert 8: when we follow initial pointer, it is the pointer before 13, leading us to the [2,3,5,7] node which is full
	1. Split the original leaf in half + insert the new value such that the leaf w/ greater values has 1 more value, adjusting the next & previous
	   pointers such that they point to the new next/previous nodes
	   - Try inserting 8 into [2,3,5,7] --> [2,3], [5,7,8]. Make note of the middle key among all values: 5
	2. Create a new parent for the newly create node upon the node split, copying up the value of the lowest value of the upper node
	   - Create parent [5], which we try to insert into original layer above [13,17,24,30] to get [5,13,17,24,30]
	3. If the original parent is full that we want to insert the step 2 parent into, then we need to split the original parent node, moving
	   rightmost d+1 keys into newnode, and the original node will contain d keys
	   - Need to split to get: [5,13],[17,24,30], but we know that this was originally the root layer so more actions needed
	4. Bubble up the smallest value of the RHS node into the upper node, w/ pointers to the LHS and the RHS of the previous level
	   - Among new middle layer, know that 17 is middle value that gets bubbled up --> [17] -> [5. 13], [24,30]
- General behavior of insertion: most of the time, insertion will simply cause the layers to grow wider. However, sometimes as the root node is full,
  then the height of the overall tree grows
- Importantly, insertion strictly obeys the properties of occupancy invariant and key invariant

Copying vs. Pushing
- Splitting a leaf vs. internal node: if we split at the leaf level, then the entry needs to be copied up into the next layer. If split at the
  internal node, then we just copy that value
  - Split leaf (COPY): end up w/ [size d leaf], [size d+1 leaf] and upper level node w/ [middle leaf value] since that key is needed to direct searches
    to a specific leaf in the final level
  - Split internal (PUSH): split nodes into [d entry node], [d-entry node], pushing middle key up to parent. Do not need the routing key in the below
    level unlike w/ leaf in which that value is a fundamental part of the data

B+ Tree General Insert Algorithm
1. Find the correct leaf in which to insert a data entry using the binary search across the search files
2. Insert data D into that leaf. If space, finished. Else, go to step 3.
3. Split the given node, redistributing entries evenly. If middle node, push up middle key. If leaf, copy up middle key.
4. Repeat step 3 as needed until reaching the root layer

B+ Tree: Deletion
- Generally, not concerned w/ deletion when dealing w/ B+ trees
- This results in occupancy invariant not being enforced, since nodes can potentially become underfull through deletion
	- Can leave space for space for new entries in a leaf. If page is completely empty, can delete the page, so its parent
	  may be underfull as well
- Nevertheless, we still have a guarantee about runtime of deletes/inserts: logF(maximum tree size)

B+ Tree: Bulk Loading
- Idea: assume we wanted to create index from a large table. One potential solution would be to repeatedly insert, which is not
  efficient since it requires constantly starting from root to search & does not take advantage of the cache
- Smarter implementation: first sort the input records by their key, filling the leaf pages according to the full factor. Afterward,
  create the parent index until that fills up, making a sibling as needed, which will now contain some of the original values in the parent
  - If a sibling is created, then the LHS sibling & corresponding lower layers remain untouched afterward
- This smarter implementation utilizes cache more effectively since intermediary node takes advantage of cached leaf values AND
  the leaf pages are well-ordered

Summary
- Issue w/ ISAM structure: need to allocate overflow pages since the pages that are fixed upon creation
- Instead, we prefer using a B+ tree, which is dynamic in nature (algorithm for insertion outlined above)
	- Helpful properties of B+ tree include: height balanced upon insertion/deletion, insert/delete cost logF(n),
	  the depth usually hovers ~3-4, 67% occupancy on average (nodes are 2/3 full), can scale better
- Bulk-loading is a technique allowing for repeat inserts in a more efficient manner w/ large datasets
- Generally, B+ trees are commonly used for their efficiency as discussed above




