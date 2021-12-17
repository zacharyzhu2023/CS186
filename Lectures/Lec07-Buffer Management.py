# Lecture 7: Buffer Management

DBMS Architecture
- File and index management has a RAM API while disk space management covers the disk memory, w/ buffer management functioning as the go-between
- Buffer manager wants to allow higher levels to pretend like they are operating in RAM
	- Does so by operating a buffer pool, which are page-sized chunks of RAM, moving pages into and out of RAM

Mapping Pages
- Scenario 1: Assume API call to read page 1 is issued. Page is not in buffer pool, so buffer manager issues call for page 1 to the
  disk space manager, who returns that page that gets mapped into a frame of RAM in the buffer manager, returned to original call
  	- Once we issue an API call to read that same page, no longer need to have buffer manager issue another call (instead can fetch
  	  directly from the buffer manager RAM space)


Handling Dirty Pages
- 2 main issues: need to handle dirty pages (updates occurred in RAM) and page replacement (RAM is full and now we need a new page)
	- Dirty page: assume that we brought a page into RAM and want to insert/delete/modify some aspect about it. We need to inform the
	  buffer manager that this page was modified w/ a dirty bit which gets written back to disk manager
	- Other potential issues: need to figure out how to deal w/ multiple actors modifying a page at the same time & what happens w/ system crash
- Dealing w/ Dirty Pages: buffer manager uses dirty bit to determine whether a page has been modified or not
	- If a page is dirty, write back to the disk using the disk manager
- Dealing w/ page replacement: use page pin count to determine if page is in use. If page should be replaced, use replacement policy


Buffer Manager State
- System starts up: mallocs a large chunk of static memory, whose frames function as the buffer frames
- Need to incoporate metadata:  a small array in memory, which is a table that includes frameID, pageID, dirty bit, and pin count, which is indexed by pageID
- Page pin count: which is number of tasks using a given page, informs buffer manager whether a page is being used or not
- Page replacement policy: dictates whether or not a given page should be replaced in the event that the buffer manager is full
- Steps taken upon issuing a request for a page: 
		1. Pick a frame that has a pinCount = 0 to do the replacing, 2. If a frame had an "on" dirty bit, write it to disk and turn dirty bit off
		3. Read request page back into the frame (overwrites pre-existing data), 4. Pin page and provide its address
- Example: Read page 7 given full buffer manager: pick page2 to replace, which was dirty so we write it back into disk memory, then read page 7 back into
  the frame, pin it before returning it --> return pointer to that page to requester
- Steps taken once the requester is done:
	- If requester modified page --> turn dirty bit on, then unpin the page ASAP once they are done so it can be re-used
	- Then, page can be requested again, which we track w/ the pin count. Page can only be replaced if pinCount = 0
	- Concurrency/recovery can perform additional IOs w/ replacement

Page Replacement: LRU Replacement Policy
- 2 common replacement policies: least recently used (LRU), clock. Also sometimes used: most recently used (MRU)
	- Importance of replacement policy: choice of policy affects number of IOs, which is affected by what gets accessed
- LRU basics: does not replace any frame w/ pinCount > 0, each frame has data about when it was last used --> choose most ancient
  frame to be replaced
  - Benefits: simple to implement, good when working w/ specific hot-spot pages, but can incur high CPU cost (need to find last used row)

Clock Policy
- Clock State: Assume the pages are laid out in a circular fashion, w/ a hand pointing toward a page we consider replacing. In addition,
  each page also has reference bits, indicating recently referenced pages
  - Represent clock w/ a clock hand in metadata indicating frame we are pointing to, and a reference bit (think of it as a "second chance")
 - Clock algorithm: clock hand starts at a given page, checking to see if it is pinned/has reference bit on. If pinned --> skip.
   If unpinned & reference bit on --> turn off reference bit but move on. Find first unpinned & reference bit off page (pin page, turn on reference bit)
- LRU/Clock Policy are good for simplicity & taking advantage of temporal locality, but only clock policy is better in CPU accesses
  since it does not need to find the absolute oldest frame to replace (Clock is constant time)

Repeated Scan Demo
- Cache hit: page request is already in buffer pool, attempt count: how many requests were initially issued
- Assume buffer pool can hold 6 pages and we want to read in pages 1-7 --> Initial 1-6 reads will fill up cache but read in 7
  requires kicking out a page (page1 gets the boot under LRU)
  - Then we need to read in page1 again which was kicked out, again w/ page2 --> this causes us never to engage in cache hits --> 0% cache hit rate
- Sequential Flooding: event of not ever having a cache hit w/ LRU w/ access pattern of repeated scans 
- Instead, clearing the most recently used page would be more efficient w/ this access pattern. Assume N pages > B frames using seuential scan & MRU
	- 1st n attempts: have 0 hits b/c they were never read in before. Next b-1 passes: have b hits eachh b/c we needed to kick out n-b pages but can read
	  [1, b-1]. Next n-b attempts: b-1 hits each, alternating b/w the 2 --> asymptotic hit rate: (B-1)/(N-1)
	  - Scan 1: Read in 1-9, kick out 456 when adding in 789 --> [123789]. Scan 2: Read in 1-9: 123 (good). 456: kick out 123. 789: good --> [456789]
	  	Scan 3: Read in 1-9: 123: kick out 789. 456: no issue. 789: kick out 456 --> [123789]. Scan 4: 123 (fine). 456: kick out 123, 789: fine --> [456789]
	  - We oscillate b/w B hits & N-B hits --> (B-1)/(N-1) hit rate

Prefetching, DBMS Access
- Idea: request that the disk space manager for a series of sequentila pages, which amortizes initial IO & CPU/Disk to perform computation alongside IO
- Clearly, LRU does better w/ random access (web access) but MRU is the favored approach for sequential access patterns (join operations)
- DBMS can provide "hints" to buffer manager. For instance, large queries can choose strategy (LRU, MRU) based on IO patterns but simple lookups typically perform better w/ LRU
	- Alternatively, there are other policies--2Q, LRU2, ARC--which have more sophisticated page replacement policies
- Hybrid policies are fairly common in the DBMS setting and ultimately depends on the need of the user
- Cannot make file system in charge of caching behavior
	Reason 1: Since operating systems utilize difference file systems, limiting predictability
	Reason 2: File systems cannot ensure that pages are written back to disk, which the DBMS ensures is the case for recovery
	Reason 3: DBMS has more info than file system to predict page behavior based on its native data structures (such as a B+ tree) which
	in turn alters performance of replacement and prefetching

Summary
- Buffer manager functions as the intermediary b/w the higher level layers and the disk space manager
- Each page that gets requested has an incremented pin count, which gets decremented by the caller once done (in RAM)
- Meanwhile, we can optimize performance, minimizing cache misses, through intelligent page replacement policy (kicking out pages we do not want to access)
  and prefetching (getting pages we know we will want)
- 3 potential page replacement policies: LRU, MRU, Clock
	- LRU: just kick out least recently accessed page based on metadata about when each page was last accessed
	- Clock: "second chance" bit used in conjunction w/ pin count to determine first available page that gets the boot
	- MRU: kick out most recently accessed page. Similar to LRU but beneficial w/ sequential access patterns







