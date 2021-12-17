Lec 06: Indices, B+ Improvements


Indexes
- When developing an index, need to consider: what kind of queries we want to be able to support, the search key,
  data entry storage, how to deal w/ keys of variable lengths, the cost of using an index vs. heap/sorted file
- In general, indexes support selection, which take the form: <key> <op> <const> where operator can be equality (=) or
  be a range selection (<, >, <=, >=, between)
  - In more sophisticated models, indexes might need to support other selections, such as 2D box (w/in boundaries),
    having nested queries, etc.

Search Key, Ordering
- We want to be able to create an index on any subset of the columns, but need to account for fact that order matters
- Keys are ordered in lexicographical order in order of the columns specified: order by 1st column, then break ties using
  the columns of the 2nd column specified, etc.
- Composite Search Key: Assume working w/ columns (k1... kn) if query is a conjunction of k1 = <val1>... k_m = <val_m>
  followed by at most 1 range clause: k_m+1 <OP> <val>
  - This is considered a "match" b/c lookup/scan occurs in lexicographic order
  - First, we perform an equality lookup for the 1st m columns to determine start of range. Then, conduct a scan on data
    entries at the leaf level to determine those that match the range predicate
 - When conducting a search, we want to find all values that are >= query conditions. For instance, query (Age = 31 & Salary = 400)
   we would look for the first row in which the data point had age >= 31 and salary >= 400, going downward in table
   - If instead we had a ">" query followed by an equality query, this causes non-lexicographic range

Data Entry Storage
- Key question: how do we want to represent the actual data in the index? Can store the raw data or a pointer to the data
	- Also need to consider the way in which data is stored on data file, whether it is clustered or unclustered
- 3 ways to store data in an index: 1. By Value, 2. By Reference, 3. By list of references
- Method 1: store contents of the record directly in the index file. Do not need to store data outside of the index file
- Method 2: at the leaf node, store the key and recordID, where recordID contains the page & position w/in that page of a record
- Method 3: leaf node contains key and a list of recordIDs that match that key, which is a compressed version of method 2
  - This works well if one key corresponds to numerous records, but can result in long lists w/in the leaves
- Need by reference index when using multiple indexes per table to avoid having to duplicating data which increases complexity

Clustered vs. Unclustered Index
- Method 2/3 can have either clustered or unclustered indexes (does not apply to method 1 which does not store by reference)
- Clustered Index: File records are stored mainly in the order specified by the search keys in the index
  - Bear in mind that the ordering need not be exact, but the general structure ensures we meet the necessary performance
- Creating a clustered index: sort heap file, leave space on every block for inserts down the line, where the index entries determine
  where to search for specific data entries
  - Clustered vs. Unclustered structure: For contiguous blocks, in clustered structure they point to fewer pages and do not "cross over"
    while the unclustered file points to many more pages on average
  - When inserting a new record, we hopefully will have room in the block that we are routed to insert a record. Otherwise, need to create
    a new block at the end in which to store the record, leading to the non-perfectly ordered property
- Benefits of clustered indexes: good w/ range searches b/c requires accessing fewer pages, good locality since records are ~ in order
- Downsides of clustered indexes: requires maintaining the heap file ordering, which may require periodic reorganization of the data

B+ Tree: Variable Length Keys/Records
- Assume instead of an integer key, we instead use a string, which is of a variable length
- Under this scenario, amount of data held in an entry is no longer a fixed value since size of each key varies w/in each node
- As such, we instead measure the memory in bytes to determine whether or not a node is half full or not, for the occupancy invariant

Prefix/Suffix Key Compression
- Want: increase fanout to decrease IOs for search when dealing w/ variable length keys
  - Assume we have the following keys: Dan Ha, Danielle Yogurt, Davey Jones, David Yu, Diana Murthy when routing the search
  - Idea: we can compress keys by solely including characters up to when adjacent entries first differ. 1. (Dan, Dani) since 4th character
    distinguishes the two. 2. (Dani, Dav) since 3rd character is where they differ, 4. (Dav, Davi), 5. (Davi, Di)
      - Although this minimizes how many characters we need to route searches, we also may potentially end up inserting in different
        locations. Ex: David Jones --> Would fall right after Davey Jones ordinarily, but after Davi under new key regime
- Ex 2: Assume we have the keys: [Sarah Manning, Sarah Zhu, Sarita Adve, Saruman The White]. Want to insert: Sarah Lee
  - We know that this insert will cause a split at the leaf level, so Sarah Zhu will be copied up to route searches, but only want the minimal
    components needed. "Sarah Z" would be sufficient characters to copy up to distinguish b/w Sarah M & Sarah Zhu on the margin
- One alternative to prefix key compression is suffix key compression, in which we retain the common prefix as a header, then
  using remaining characters to route the searches using prefix key compression
  - Start: [Sarah L, Sarah M, Sarah Z, Sarita, Saruman] --> Common prefix: Sar, Prefix compression: [ah L, ah M, ah Z, i, u]. Can recreate
    the whole key by concating the header w/ the routing key. Sar + ah L = Sarah L, etc.

B+ Tree: Cost Analysis
- B = number of data blocks, R = number of records on a block, D = time to read/write from a block, F = average internal node fanout,
  E = average number of data entries on a leaf
- We assume that data is stored by reference, the heap files are 2/3 full, the heap file is initially sorted, large fanout
- Scan: 3/2BD. Scan the heap file directly (no need to go through the index). Since the heap files are 2/3 full, we need to scan 3/2 as many
  blocks that we would compared to the completely compact heap file/sorted file. (3/2B) blocks * D read/block = 3/2BD
- Equality Search: (logF(BR/E)+2)*D. First, need to search the index to route the search, walking through the intermediary nodes depending
  on how they route the search. Need to add +1 to account for cost of accessing the initial root node
    - BR = total number of records, E = records per leaf --> BR/E = number of leaf pages. Thus, logF(BR/E) directs us to the correct leaf page
    - The other +1 comes from the IO of having to lookup the record in the heap file using its recordID
- Range Search: (logF(BR/E)+3*pages)*. 1. Incur a cost of logF(BR/E) to initially find the right location in which to start searching at heap file level.
  2. Need to read through 3/2 * NumPages given property of being 2/3 full across the heap file. 3. Cost of 3/2 * NumPages in order to
  perform a scan at the leaf level in the worst case (assumes each heap page corresponds to a different leaf)
- Insert: (logF(BR/E)+4)*D. 1. Incur cost of logF(BR/E) to find right location, 2. +1 to account for root node read, +1 to get right page
  to modify, +2 to write to the leaf in the index & heap file page
- Delete: (logF(BR/E)+4)*D--cost analysis is the same as w/ insert

Summary
- Need to understand how to "match" queries using the lexicographic ordering (pay attention to equality & other operands--order matters)
- Can use prefixes to increase the fanout to decrease IOs w/ variable length keys
- Data can be stored either as direct records (method 1), by reference (method 2), or as a list of records (method 3)
  - Clustered indexes, records stored mainly in sorted order by the search keys, can be utilized w/ by reference data storage (method 2, 3)
- B+ tree model has good runtime analysis compared to heap/sorted files but need to account for constant factors during IOs


