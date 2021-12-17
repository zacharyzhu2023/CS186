Lecture 27, 28: Map Reduce, Spark

Parallelism
- Interquery parallelism: parallelizing the execution by assigning each query to a different machine (good for OLTP)
- Interoperator parallelism: each operation w/in same query gets sent to a different machine (good for OLAP)
- Intraoperator parallelism: distribute the work of a single operato on the data to different machines (scales best)
- Partitioned Hash Join setup: assume that we have R(K1, A, B) and S(K2, B, C) where K1, K2 are the primary keys
	- Query to execute: R(K1, A, B) TJ S(K2, B, C). Plan: first, chunk R, S into (R1... Rn), (S1... Sn) based on each of their primary
	  keys, respectively. Then, reshuffle such that the data is organized by B column for each table --> join locally
	  against all other tables
- Broadcast join: same setup, but this time each of R partitions are sent the entirety of S to be joined, which is better
  when S is much smaller than R to avoid incurring the IO cost of having to partition S

Distributed File Systems/Map Reduce
- Distributed File Systems: used w/ TBs/PBs worth of data, which get chunked into pieces, replicated, and sent to different machines
- MapReduce: model that allows for parallel data processing (supposed to deal w/ the DFS scale of data)
	- Map: gets info from each record in the data, which gets shuffled & sorted, Reduce: performs some sort of aggregation/filtering
	  to the data to "summarize" the results
- Execution of MapReduce: takes in (inputKey, value) pairs and ultimately produces (outputKey, value) pairs (outputkey is optional since
  for results like "count" we do not need to know the key)
- Map phase: takes in (inputKey, value), applies map function in parallel to produce (intermediateKey, value)
- Reduce phase: takes (intermediateKey, values) to produce values at the output
- Example: assume we took in a collection of documents and wanted to find the count of each unique word in those documents
	- map(key, value): for word in value: emit(word, 1). This allows us to create a collection of words in each doc assigned value of 1
	- reduce(key, values): sum += v for v in values; emit (key, sum). During the shuffle phase, each word, value pair gets combined into
	  a word followed by a list of values --> reduce simply takes the sum of the values list to produce the actual count
- Worker: process that executes a task (can be part of the mapping, shuffling, or reducing phase)
- Fault Tolerance: map reduce is able to achieve fault tolerance by writing intermediate files to disk so if any worker is unable
  to complete its task, it gets reassigned to a different worker
- Leader Node Model: a leader is in charge of partitioning initial input by key to assign workers to the mapping tasks. Each worker
  writes output locally into R regions, after which the leader assigns workers to the "reduce" tasks
- Sometimes, there is a straggler, a machine that takes longer to complete its task. To deal w/ this potential bottleneck, the leader node
  can assign early task finishers the task of the straggler node, killing whichever processes do not finish first along the way

MapReduce Implementation: Relational Operator
- Selection_(A = 100) R: 1. map(Tuple t): if t.A = 100: Emit(t.A, t), 2. reduce(String A, values): for v in values: emit(v);
	- In the map phase, we only keep tuples that adhere to the selection clause. Afterward, we have a collection of records that adhere
	  to the format desired, so reduce is unnecessary but included to maintain the standard MapReduce format
- GroupBy(A, sum(B) R): 1. map(Tuple t): emit(t.A, t.B), 2. reduce(String A, values): s += v for v in values; emit(A, s);
	- Idea: first, we know we need to track the A to group, and B to sum by. During the shuffle phase, we have the "A" keys followed by
	  a list of B values. Finally, during reduce: we want to actually take the sum of those B columns we clumped together
- Partitioned Hash Join(R(A,B) TJ_(b,c) S(C, D)): 1. map(Tuple t): if R: emit(t.B, t). else: emit(t.C, t). 2. reduce(String k, values):
  R = [], S = []; for v in values: if R: R.append(v); else: S.append(v); for v1 in R, v2 in S: emit(v1, v2);
  - Map phase will produce the tuple, w/ key depending on which relation it is part of, which is used for joining. During shuffle
    phase, want to clump together all records of same key. In reduce phase, go through all the key & value lists to determine which list
    they belong in (building an R list & S list). Use that newly minted list to create a joined list of tuples
- Broadcast join(same relations): map(String v): hashTable = new HashTable(S); for w in S: hashTable.insert(w.C, w); for v in value:
  for w in hashTable.find(v.B): emit(v, w);
  	- Intuition: need to first build a hash table on S. Then, go through all the records in value (corresponding to R) to match against the hash
  	  table, emitting records that contain the same key value
 - MapReduce is simple, has fault tolerance, and can achieve scalability, but suffers from bottleneck if one task takes much longer
 	- The intermediate writes to disk are needed for fault tolerance but can be rather slow. This can be improved upon w/ Spark

Spark
- Spark built on MapReduce, but includes iterative steps, stores intermediate results in main memory instead of disk, & adheres closely to relation algebra
	- Can also be implemented w/ actual programming languages such as Java/Python, w/ a querying interface as well
- RDD Model (resilient distributed datasets): an unchanging, distributed dataset that has a lineage, which provides a plan
  that states how dataset was "computed". Used in Spark, which stores intermediate results as RDD
  - Key insight: server crashes results in loss of the RDD in main memory. However, using lineage allows us to easily refind missing RDD bits
- Spark also is made up of transformations (map, reduceByKey, join) & actions (count, reduce, save) where transformations are lazy, only computed
  if necessary, but actions are "eager", meaning they are executed right away
- Also now have 2 forms of collections: 1. RDD<T> which are partitioned, recoverable, not nested & 2. Seq<T>: a sequence local to server that can be nested
- Similarity to MpReduce: spark has col.map(f) that allows for parallel mapping of a function to a collection to produce new collection
- Also has a .persist() operator that allows for the saving of intermediate results (but we can choose which results to save)

Dataframes
- Dataframes are unchanging, distributed collections of data organized by "named" columns instead of objects. Elements in dataframes are rows
- Datasets, meanwhile, are dataframes whose elements have a specific type, which allows for error detection during compilation
	- Dataset API: aggregation(exprs): aggregate on entire dataset, groupby(cols), join(Dataset R), orderBy (Cols), Select(cols)

