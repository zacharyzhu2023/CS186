Lec21, 22: Parallel Processing

Parallel Architectures
- Idea: we want to be able to run queries in parallel in order to increase the throughput for a constant workload
  when we increase hardware and to achieve constant throughput when we increase the data that needs to be processed
  and increasing the available hardware as well
- 2 kinds of parallelism: 1.Pipeline-nests the results of processed data, 2. Partition-each function processes dif data
- We have observed the benefits of parallelism when dealing w/ divide & conquer w/ partitioning & executing batch operations
- We consider 3 different architectures: shared memory, shared disk, shared nothing
	- Shared Memory: all the hardware share the same RAM and disk
	- Shared Disk: each of the CPUs have their own independent RAM but share the disk
	- Shared Nothing: all CPUs have their own RAM and disk, can only communicate through the shared network
- Want to consider the network cost of having to communicate over the network which we measure through data that needs to be sent/received
	- Do not necessarily need to send the entire page over network, so network cost can be a single record


Types of Parallelism
- Intraquery Parallelism: increase the speed of a single query by spreading the work across multiple CPUs
	- Can be further divided into 2 subcategories: intraoperator (focus on increasing the speed of a single operator) and
	  interoperator (spreading the work of the operators of a single query across multiple machines)
	- Intraoperator parallelism increases the speed of a single query by chunking data to be processed by single operation
	  across multiple machines
- Interquery parallelism: provide different machines different queries to increase throughput to process queries
- Pipeline Parallelism: Pass on the results of parent operator to the child operator as soon as it is processed
- Bushy Tree Parallelism: form of interoperator parallelism in which different branches of the tree runs in parallel (each branch
  can run in parallel to be joined in the end)

Partitioning
- Partitioning Scheme: plan that decides which machines will receive what data to be processed. There are 3 kinds of partitioning:
  range partitioning, hash partitioning, round robin
  1. Range Partitioning: keys that are adjacent to be one another will be stored on the same machine, which allows for convenient
     lookup by key, equality search, parallel sorting/parallel sort merge join
  2. Hash Partitioning: records on the same page get distributed based on the value obtained through the hash function--works well
     for equality search but not w/ range queries. Often used w/ parallel hashing/parallel hash join
  3. Round Robin Partitioning: each adjacent record gets assigned to "next" machines, which does a good job of allocating the work
     equally but does a poor job of parallelizing the queries

Parallel Sort, Parallel Hash, Parallel Sort-Merge Join
- Parallel Sorting: range partition table, then locally sort on each machine. After, since table is guaranteed to be in sorted order,
  can easily put them together
  - Key to success is finding good values for the split range: want to spread the work out evenly which can be done via range partitioning,
    in which we sample the data to attempt to gauge the frequency of each of the values
- Parallel Hashing: hash partition table, locally hash on every machine since all "like" values will be put on the same machine
- Parallel Sort Merge Join: range partition tables using ranges on the join column, then locally execute sort merge join since we
  need to ensure that different tables w/ same join column values will end up on same machine for joining
  - Initial passes are just parallel sorting, which ultimately gets concacted at the output

Grace Hash Join
- Parallel Hash Join: hash partition tables using same hash function on join column then locally perform hash join so that matching
  records are on the same machine
- Broadcast Join: send smaller tables to all machines which gets locally joined which becomes the final result of the joins
	- Idea: the smaller table gets joined w/ the chunks of the larger table --> send the joined versions to be joined in the final output
	- Works well when one table is substantially smaller than the other in size
- Pipeline Breaker: situation in which a join cannot create an output until every record has been processed. Example: sort-merge join
  relies on output of sort to be complete before being able to join the output
  - Similarly, grace hash join requires the entirety of the has table before beginning the probing process
- Symmetric Hash Join: we stream records of R into one hashtable and stream records of S into another hashtable. Each time we stream in a
  new record from either R or S, we probe it against the table that it is not part of, which ultimately resolves in us probing each record
  once against all others
- Can potentially utilize symmetric hash join, out of core joins, and non-blocking SMJ but those are out of scope for this class

Parallelization of Aggregation Functions
- Idea: we want to be able to parallelize the aggregation functions: sum, count, average
	- Sum: we chunk out tables, take the sum of those tables, then sum up the results of the local sums w/ a global aggregator
	- Count: distribute tables, then count number of entries locally, to be summed up on the global level
	- Average: Need to find the global sum in same way we saw above, do the same w/ count--ultimately divide sum by count
- GroupBy functions can be accomplished through parallel version of hashing by combining local & global aggregation functions

Parallelism Summary
- There are 2 main forms of parallelism we use: pipline (stream output of operations into other operations) & partition (chunk out work to be done)
- 3 architectures can be used to parallelize: shared nothing, shared memory, shared disk each w/ own benefits/drawbacks
	1. Shared Memory: easiest to implement from software perspective but hardware is hard to build & thus does not scale as well
	2. Shared Nothing: scales, is cheap, but requires significantly greater design decisions/implementations
	3. Shared Disk: think of it as the goldilocks version of shared memory & shared nothing
- Also looked at parallelism in the context of intraoperation, interoperation, interquery
- Saw how we can apply parallelism logic w/ sorting (generic sort, SMJ), hashing (GHJ, SHJ)


