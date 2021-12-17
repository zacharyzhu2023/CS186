Lecture 3: Disks, Files, Buffers

General Hierarchy
- The general architecture of a DBMS is as follows: Client -> Query Parsing/Optimization -> Relational Operators -> 
  File/Index Management -> Buffer Management -> Disk Space Management -> File System
  1. Client: responsible for actually executing the SQL query statement
  2. Query Parsing/Optimization: read through and check to make sure SQL statement is valid + make it into a form that is
     efficient for the relational query plan
  3. Relational Operators: actually runs a given query plan on records/files
  4. File/Index Management: structure tables/records into pages on a logical file
  5. Buffer Management: allows us to pretend as though we were operating directly in memory
  6. Disk Space Management: turn page requests into actual bytes on a physical device
- Ultimately, the design is such that each layer does not need to know how the others operator but rather just their input/output

Disks
- Originally, DBSMs were created to be used via magnetic spinning disks, but ideas permeated w/ SSDs as well
- Disk API has 2 operations: read (page data transfer: Disk -> RAM) and write (page data transfer: RAM -> disk)
	- Does not allow random read/write operations + generally a relatively slow process
- Unable to read/write individual bits directly to disk. Rather, need to bring disk page to RAM, after which we can write
  and then save back to the disk
- Reason to use magnetic disks (hard drive): cheaper memory per dollar compared to alternatives (SSD, RAM)
- Disks, at the bottom of the storage hierarchy, typically have the most storage but the slowest operations
	- Disks are used for large DBs, use RAM w/ most recently accessed data
- Disks are made up of platters, tracks, arms, and a spindle in terms of physical architecture
	- Arm assembly controls movement of head into or out of the track, under which forms a cylinder, Spindle is responsible 
	  for spinning the platters
	- Read/write time is influenced by seek time, rotational delay, transfer time
		- Seek time: time to move arm to get disk head on track which will be read (2-3 ms), rotational delay: time block takes to rotate
		  underneath head (0-4 ms), transfer time: time to move data to/out of disk surface (0.25 ms)


Flash Memory (SSDs)
- Flash memory can be thought of as a collection of SSDs organized as cells
- Allows random read/write (do not need contiguous blocks) w/ reads allowing for greater granularity compared to write operations
- Read: fast and predictable w/ little performance difference b/w random and contiguous (~500 MB/s)
- Write: much slower w/ random writes (~120MB/s), sequential writes ~480MB/s, due to the fact that write operations need to avoid 
  writing to the same region over and over, since overwriting content on a cell will eventually result in failure (move around write locations w/ wear leveling)
  - Idea: write operations are still influenced by location; farther writes are still quite expensive
  
Disk Space Management
- Vast majority of database management systems (DBMs) keep info in disks/solid state drives
	- SSD: faster than disks, slow relative to memory, and incur larger cost w/ write operations 
- Read/write operations occur w/ large chunks of contiguous bytes w/ speeds proportional to distance
	- Thus, we want to amortize cost of reads/writes of far away data using caches, buffers (keeping frequently used data nearby)
	- If we know that the data we are accessing will be costly, then want to get as much data as we can through that operation
	- Only allows for a single head to read/write at a given time, w/ a fuixed sector size based on block/page size
- Block: unit of transfer referring to read/write operations. Page: interchangeable w/ block (RAM data of size block)
- Concept of "Next": blocks w/in same track are closest, then on same cylinder, then adjacent cylinders
	- This is important b/c file pages are organized by their status of "next" disk to minimize seek/rotational delay
	- Sequential scans will transfer several blocks, reading consecutive blocks when possible
	- We want to abstract away details of file system & device. Other layers only care that next block can be accessed quickly
- Disk Space Management: lowest layer of abstraction of DBMS and is responsible for controlling disk space
	- Functions: translate pages to actual locations in disk, load page from disk to mem, save pages to disk & ensure writes
	- From there, higher level layers use the disk space management layer to read/write pages, allocate/deallocate pages
	- Implicitly, these higher levels assume that calling for next page will be a fast operation, which DSM needs to ensure

Implementation of Disk Space Management
- 2 main implementations of disk space management: can either directly communicate w/ the physical device info is being stored on
  or can instead use the file system
  - Approach 1: direct to device would be extremely quick, requires knowledge of device API, and not robust to change in devices
  - Approach 2: abstract details of OS, sequential access relatively efficient due to optimization of disk layout, allows DBMS file
    access across numerous devices potentially

Overview of Files
- Idea: on the surface level, we have a table, which gets mapped into a file that contains many pages w/in which are the actual records
	- Pages are represented as bytes in memory in actuality, which are managed on disk by disk space manager
	- Buffer manager allows these pages to be accessed, pretending that we are working directly in memory
- Database file: contains a collection of pages, which contain a collection of records
	- API calls: insert/delete/modify record, get a record based on its ID, or be able to scan through the records w/ possible WHERE clause
	- Note that it is also possible for records to be kept across multiple OS files or even w/in dif machines altogether
- Files can be stored in numerous ways: 1. Unordered heap file, 2. Clustered heap files, 3. Sorted files, 4. Index files
	1. Unordered Heap File: records are scattered w/o rhyme or reason across pages in a file
	2. Clustered Heap File: pages/records have some form of structure/grouping
	3. Sorted File: pages/records appear in the file in a strict order by some sorting
	4. Index File: disk-based file organization that allow for easier lookup, which can contain records or pointers in dif files


Heap Files
- Unordered heap file: records do not have any coherent order. Pages must be alloc/dealloc as file size changes
	- Need to be able to track: pages, free space, and the actual records
	- Implementation is as follows: we have a header page that contains a pointer to a LL of full pages and a pointer to a LL of unfull pages
	  w/ the header page ID and name of the heap file not stored w/in this file
	  	- Each page has: pointer to previous page, pointer to next page, collection of data, and potentially some free space
	  	- Limitation: diff to det where to stuff a specific sized record. Can distinguish b/w free + unfree pages but do not know how much space available
- Page directory implementation: directory made up of LL containing >= 1 header pages, which contain a pointer to a data page and num free bytes in that page
	- Keep header pages in the cache b/c they need to frequently be accessed

Page Layout
- Page contains a header: made up of info about num records, amount of free space, potentially a pointer to next/previous pointer, and sometimes bitmaps/slot table
- Considerations w/ page layout: whether records are fixed or variable length, det how to locate records based on record ID, support adding/removing records
	- Also should consider whether page will be packed (records contiguous) or unpacked (records not contiguous)

Fixed Length Records
- Fixed length, packed layout: 1. Fetch by ID: given the page ID, can easily calculate the offset by: recordSize * recordNumber + initialOffset. 2. Add:
  add record to the end of the list. 3. Delete: after deleting a record, need to reorganize the records that came after it to presrve backed nature
  	- Delete operation potentially expensive since the record IDs need to be changed, which may require altering other files as well
- Fixed length, unpacked records: this can be accomplished through a bitmap that contains 1 if location has meaningful data, 0 otherwise
	- 1. Insert: iterate through bitmap, find first empty slot. 2. fetch by ID: recordID now becomes the page + slot number in the page, which we can then easily
	  accessed. 3. Delete: simply set a given bit to 0 and we are good to go

Variable Length Records
- Considerations w/ variable length, unpacked records: need to know the start point of each record and consider what happens when records are added/deleted yet again
- General design: the footer will be located at the end of the page, and contain a pointer to free space in the record, and a collection of objects containing pointers
  to the start of a record and the length of the record stored in reverse order (earlier records are stored later in a page)
  - Fetch by ID: record ID contains the page number, and the record number w/in that page (which we can access via the slot table)
  - Delete record: set the pointer w/in the slot directory at a given position to null, which does not demand any other immediate change
  - Insert record: put a record where the free space pointer is located, add the position/lengh w/in the slot directory at first open slot, then
    change the location of the free space pointer to point to end of the new record
- This design can result in fragmentation as we do not deal w/ the null space that pops up when deleting a record. 2 approaches: either immediately reorganize
  data upon a delete or wait till we run out of space before reorganizing
  - Gneerally, favor the reorganization fo data only when running out of space

Slotted Page
- Above, there was not a clean way to whether we wanted to accommodate more slots, so we can add a variable at end of page containing number of slots
- If we want to add another slot but the slot directory is full, need to extend slot directory and increment count for number of slots
- Slotted page is typically the favored approach, regardless of whether we are working w/ variable or fixed length records

Record Layout
- Assumption: using the relational model, every record in the table has a set type (each record abides by constraints: need a certain number of fields + values those fields 
  can take on are restricted as well)
  	- System catalog stores the schema of a table, which can be treated as just another table
- We also want to be able to store the fundamental info about a table: the fields for each column, which can either be of fixed or variable legnth yet again
- Fixed length fields: can easily locate a field since each is of a fixed size and can just calculate based on offsets
- Meanwhile, variable length fields have more potential approaches: 1. can pad the length of variable length fields so they are functionally "fixed" but this requires
  knowing what the largest possible sized element in that field is. 2. Use delimiters (such as commas) but that can be a valid character that we cannot easily distinguish
  as a delimiter vs. a legitimate character, which can be solved using escape characters which wastes space & still requires scanning cost
  - Better approach: 1. organize the record such that the variable length fields are at the end of the record. 2. Store a header at the beginning of the record w/ pointers to
    the end points of variable length records
    	- W/ this format, can easily access fixed fields w/ arithmetic or the variable fields w/ pointers/ Handles nulls gracefully b/c if pointers are
    	  pointing to same location, we know we havea  null value
Summary

