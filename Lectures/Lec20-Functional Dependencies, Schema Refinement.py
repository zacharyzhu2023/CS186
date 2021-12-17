Lecture 19: Functional Dependencies, Schema Refinement

Redundancies
- Redundancies in schema can lead to several issues: wasted storage b/c of repeat values + insert/delete/update anomalies
- Solution: functional dependencies, which act as integrity constraints that pinpoint redundancies & suggest refinements
	- Most common refinement is decomposition, in which columns of a table is split across 2 tables

Terminology: Functional Dependencies
- Functional Dependency: X -> Y indicates that column X "determines" column Y, meaning that given any 2 rows in a given table,
  if those rows have the same values of X, then they must also have the same values for Y
  - Alternative framing: for every tuple t1, t2 in R: if set of columns X is the same across both tables, then set of columns Y
    must also be the same for both of those rows
- Using above definition, primary keys are a special form of functional dependencies, mapping the key to the set of all attributes
- Superkey: set of columns that determine all columns of a table. Mapping: K -> {All Attributes}
- Candidate Key: smallest set of columns that determines every column of a table Mapping: K -> {All Attributes} and for any subset L
  of K: L does NOT determine all attributes, to satisfy the minimal condition
	- Primary Key: a given choice of a candidate key
- Important note: index/sort keys are unrelated to functional dependencies

Functional Dependencies & Redundancies
- Assume table HourlyEmployees contains following attributes: ssn, name, lot, rating, wage, hrs (SNLRWH)
	- SSN acts as primary key: ssn -> SNLRWH, rating -> wage (same rating -> same wage), lot -> lot (trivial dependency)
- Entries in table: [1,A,48,8,10,40], [2,B,22,8,10,30], [3,C,35,5,7,30], [4,D,35,5,7,32], [5,E,35,8,10,40]
- Issue 1: Update Anomaly-If we were to change wage of A, then R -> W would no longer hold b/c A differs from B, E
- Issue 2: Insert Anomaly-If we wanted to insert a new entry but did not know wage at their rating, then would be forced
  to create either an arbitrary value or might get it wrong
- Issue 3: Delete Anomaly-If we deleted all entries of the same R value from the table, then we would no longer have
  the reference point for that R value (want the W value that it determines)
- The above issues show that R -> W is an issue but S -> W is not since S is a primary key (unique)
	- Can address this issue by creating a new table, wages, containing R/W columns, storing only R in original table
- BookID -> (publisher, author) --> (BID->p, BID->a) since all same BookIDs have same author & publisher
- (BookID -> publisher, BookID -> author) --> (BID->p,a) using the same logic as above. If BookID determines each column
  separately, then it does the same w/ the collective
- (BookID -> author, author -> publisher) --> (BID -> p) by the transitive property
- Functional Dependency Implication: Functional dependency "g" is implied by "f" if all functional dependencies in "f" holding
  means that "g" is indeed true
- F+: notation to indicate all the functional dependencies directly stated & implied by a set of functional dependencies

Inference Rules (X, Y, Z are sets of attributes)
- Armstrong Axioms: 1. Reflexivity: X is a subset of Y means that: X -> Y, 2. Augmentation: X -> Y means XZ -> YZ for any Z, 
  3. Transitivity: X->Y and Y->Z means that X->Z
  - Other Rules: Union: X->Y, X->Z implies that X->YZ, Decomposition: X->YZ implies X->Z, X->Y
- Contracts example: we have a table contracts C such that 1. C is primary key: C -> (CSJDPQV), 2. JP->C, 3. SD->P
	- Goal: prove that SDJ is functionally a key (that is, determines all the columns) for table C
	- JP -> C, C -> (CSJDPQV) --> JP -> (CSJDPQV) by transitivity. SDJ -> JP by augmentation. SDJ -> (CSJDPQV) by the
	  transitive property yet again

Attribute Closure
- Task of finding the closure F+ on a set of functional dependencies F is a difficult task, becomes exponential in number of attributes
- Easier instead to check if a given functional dependency (X->Y) is contained by F+. Algorithm outlined below:
	1. Find attribute closure of X (X+) w/ respect to F (only care about functional dependencies w/ attributes in F).
		1. Set X+ = X. 2. Iterate through all dependencies (U -> V) contained in F, checking if U is a member of X+, checking: is U already 
		   a member of X+? Add V to the set X+. 3. Repeat step 2 until X+ stays the same
	2. Next, check if Y is contained in X+: If so, X->Y is indeed in F+
	3. To check for minimal condition, can iterate through attributes of A, removing each one individually to see if the removed
	   element set still determines the hole table
- Example: R = {ABCDE}, F = {B->CD, D->E, B->A, E->C, AD->B}
	1. Check if B->E is contained by F+: B+ contains B by default, CD by first relation, E by transitivity, A too, which ultimately
	   means that B->E is contained via transitivity
	2. Check if D is a key of R: D->E and E -> C so we know that the set of D+ = {DEC}
	3. Check if AD is key of R: D->E, E->C, AD->B which incorporates ABCDE, so it is indeed a key
	4. AD primary key: A+ = {A}, D+ = {DEC}, which is missing stuff so it is indeed a primary key
		- ADE cannot be a primary key since we can remove the attribute E and still keep all identifiable attributes

Normal Forms
- Idea: we want some way of converting the normal form to actually eliminate redundancies among functional dependencies
- Normal form acts as a property that allows us to determine decomposibility of relations more easily & avoids particular issues
- No functional dependencies hold implies there is not redundancy. However, if (A -> B) & A is NOT a key, then it is possible that multiple
  records have same A value, in which case they have the same B value --> redundancy exists
- 1st Normal Form forces all attributes to be atomic, so it does not accommodate XML/JSON model. 2nd & 3rd normal form both
  exist, but our focus will lie in Boyce-Codd Normal Form (BCNF)
- BCNF: Property in which across all (X->A) in F+: A is a subset of X OR X is a superkey of R. That is, if a functional
  dependency is non-trivial, then it must be a key constraint
  - A (right hand side) is a subset of X (left hand side), since X includes all of A attributes and possibly mores

Decomposition of Relation Scheme
- Decomposition: replacement of a relation by 2+ relations such that new relation contains subset of original attributes
  & the decomposed table collectively capture all of the original attributes of the original table
- Referencing original SNLRWH table: we have the FDs: S -> {SNLRWH} and R->W which is not in BCNF since have a non-trivial, non-key FD
	- To adhere to BCNF, could instead make a separate table for R, W and preserve only the R attribute in original table
- Run into 3 issues when dealing w/ decompositions: lossiness (loss of data may make constructing original table impossible), checking for
  dependencies may require joins (can be expensive), & queries get expensive to run
- Assume we have the following table (Cols = A, B, C): [[1,2,3],[4,5,6],[7,2,8]] w/ functional dependencies: A->B, C->B
	- As such, we can try to decompose into A,B table: [[1,2],[4,5],[7,2]] & BC table: [[2,3],[5,6],[2,8]]
	- However, when we join: AB Join BC --> [[1,2,3],[4,5,6],[7,2,8],[1,2,8],[7,2,3]] since there are multiple B keys in BC table
	  that correspond to the entry in the AB table

Lossless/Lossy Decomposition
- Lossless Join Decomposition: Decomposition of table R into X, Y is considered lossless if the join(X,Y) = R, original table
	- When decomposing into tables, R will always be a subset of join(X,Y) but need to make sure equality holds
	- In the above example, b/c the presence of extra rows corrupted the joined table, considered a "lossy" join
- Test for losslessness: decomposing R into X, Y is lossless IFF condition holds: [(X∩Y)->X OR (X∩Y)->Y]
	- That is to say, if we can decompose a table in a way such that the intersecting attributes determines one of the tables (acts as
	  as a key), then this decomposition is considered lossless
	- In the example above, ABC -> (AB, BC) is not considered lossless b/c B, the intersecting attribute, determines neither table
- Useful fact: X->Z across table R and X∩Z is an empty set implies that decompsing R into RZ and XZ would be lossless
	- Reasoning: Because there are no intersecting columns, then X uniquely determines XZ since it already determines Z
- Working w/ table: (Cols are: A, B, C): [[1,2,3],[4,5,6],[7,2,8]] w/ the functional dependencies: A->B, C->B
	- Decomposing into AC, BC: [[1,3],[4,6],[7,8]] and [[2,3],[5,6],[2,8]] --> join(AC,BC) = [[1,2,3],[4,5,6],[7,2,8]] since there
	  is no multiple C values issue
	- New problem: have no way of enforcing A -> B anymore (missing a functional dependency)

Dependency Preserving Decomposition
- Dependency Preserving Decomposition: decomposition in which decomposing R into X,Y,Z and enforcing FDs on X,Y,Z individually
  will allow FDs on R to remain true
- Projection of FDs (projection of F on X: Fx): functional dependencies (U->V) such that U, V are F+ where U, V are attributes of X
	- Alternative statement: if there exists an FD in F+ that solely uses attributes of X --> add it to the set of the ultimate projection
- Dependency Preserving Definition: (Fx U Fy)+ = F+. That is, the implied + explicit FDs of the union of the decomposed is the same
  as the FDs explicitly + implied by our original table F+
- Ex: table ABC (A->B, B->C, C->A) gets decomposed into AB, BC, and we want to check if dependency preservation condition is met
	- Step 1: find F+: F = (A->B, B->C, C->A), also had A->C, B->A, C->B through transitivity --> F+ = (A->B, B->C, C->A, A->C, B->A, C->B)
	- Step 2: find F_ab = {A->B, B->A}, F_bc: {B->C, C->B} by taking the relevant dependencies in F and restricting columns available
	- Step 3: find (F_ab U F_bc) = (A->B, B->A, B->C, C->B) --> (F_ab U F_bc)+ = (A->B, B->C, C->A, A->C, B->A, C->B) using transitivity
	- As such, we know definitively that decomposing into AB, BC tables will still allow us to keep A->C FD

Decomposition Algorithm
- Assume we are operating w/ table R w/ the functional dependencies: FD. First, we want to check if R already adheres to BCNF
	- Assume that there is some violation FD (A->B): 1. Find A+, 2. Set R1 = A+, R2 = A U (R-A+), 3. Find FDs of R1, R2 --> iterate
	- Stop only when all the broken down tables adhere to BCNF form or have 2 attributes (must be BCNF by default) since any non-trivial
	  dependency would act as a check across the entirety of the table
- Example: CSJDPQV has FDs: C -> CSJDPQV, JP->C, SD->P, J->S
	- Initial table cannot be in BCNF form since SD->P is a violation --> decompose into: 1. SD+ = SDP, 2. SD U (R-SD+) = CSJDQV
	- Now, SDP is in BCNF form, but CSJDQV needs to be fixed since it includes nontrivial dependency J->S
		- Decompose into JS, CJDQV --> ultimately have: SDP, JS, CJDQV but this is NOT a unique version of BCNF form
		- The final form (SDP, JS, CJDQV) is indeed in BCNF as desired b/c all nontrivial dependencies are indeed keys
- Ex 2: table CSZ has FDs: CS -> Z, Z -> C, in which there is no way to preserve dependencies in the conversion to BCNF
	- Cannot decompose in such a way that preserves CS -> Z since either include CS, SZ, or ZC in first table which fails to capture that dependency
- Meanwhile, our decomposition above of CSJDPQV manages to preserve losslessness but does not keep the FDs
	- Solution: keep a table JPC in addition to SDP, JS, CJDQV so that we have the JP->C dependency preserved

Summary
- BCNF is a format of storing data in which every field contains data that cannot be inferred through FDs
	- BCNF is not always the best solution: simply depends on which functional dependencies we want to keep
- In the event that BCNF is not possible to achieve through dependency-preserving decomposition, can use Third Normal Form, 
  but this results in more redundancy
