Lecture 18: Database Design-Relational Models

Database Design: Intro
- Idea: when designing the actual database, there are several design considerations that we want to keep in mind
- Database design steps: requirements analysis-consider needs of the database, conceptual design-broad overview
  of what we want our DB to accomplish through entity-relationship model, logical design-convert ER (more conceptual) 
  into DBMS (holds relational representation), schema refinement-ensure consistency & normalization, physical design-think of 
  whether indexes are used & how data is spread across disks, security design-who should be able to access (R/W) of DB?
- Data model: concepts used to describe the data. Schema: describes collection of data. Relational model of data: relates
  the rows and columns of the table--relations abide by a schema which provides number of cols & their names/constraints
- 3 levels of abstraction: 1. Users have access to views which represent subsets of the data, 2. Conceptual Schema: logical structure
  of the info of the database, 3. Physical Schema: describes how data is partitioned, laid out, and any data structures used
  - Example: university database might have a conceptual schema of: Table S (sid text, name text, age int), Table C (cid text, cname text,
  	credits integer), physical schema: rows stored in ordered files w/ a single index on SID for students, external schema: course_info (
  	cid text, age int) which is a view that the end user has access to

Data Independence
- Idea: we want to ensure that applications do not need to know how the data is actually stored through logical & physical data independence
	- Logical data independence: tracks views even if the schema of the database changes (ex: if add a new column--> views are still valid)
	- Physical data independence: if logical structure changes (ex: add new index), then again the views should not be affected
- Logical data independence comes in handy at the level of abstraction between views & conceptual schema since we do not want the schema change
  to affect the views
- Meanwhile, physical data independence separates the physical and conceptual schema, since organizing physical schema should not force us to
  change the conceptual schema
- We want data independence since one of the key qualities of a DB is persistence (want permanence of effects)
- Hellerstein Inequality: when the rate of change of applications is slower than the rate of change of the environment, data independence is
  vital since we want to be able to resilient to environment changes

Entity-Relationship Model
- Will be operating w/ the relational model & entity relationship model (very simple) b/c it can be converted easily to relational model
- Entity-Relationship Model: visual, graph-based model that acts as a graph, or a flexible representation of rows in a table
	- Corresponds to object-relationship mapping (Django, Ruby on Rails, etc.--translates well for dif programming languages)

Conceptual Design
- Conceptual design answers the following questions: understand entities & relationships in a database, integrity constraints: facts that must
  hold in a database (can we have null entries? Is there a specific data type?)
- Meanwhile, entity-relationship model is a visual schema, as a starting point of the conceptual design process
- Entity: object that we want to represent that can be described through a set of attributes
- Entity Set: collection of entities that share the same attributes constrained by a domain & have a key
- Relationship: how 2+ entities are actually related (can also have attributes), Relationship Set: collection of similar relationships

Constraints: Key, Participation
- Key Constraint: provides a 1 to many relationship which constraints the number of relations that obey a relationship b/w entities
	- Ex: assume we have employees, departments, works_in, manages table. We might impose a key constraint stating that each relation in
	  department has <= 1 manager in the manages entity set (represented by an arrow: departments -> manages)
- Participation Constraint: ensures that every entity in an entity set participates in a particular relationship
	- Ex: might want all employees to work in a department. works_in acts as the relationship (the go-between employees & departments)
- Weak Entity: entity that needs the primary key of a different entity set (the owner) to actually be identified
	- Owner & Weak Entity Set are in 1-many relation (w/ owner acting as the 1) & weak entity set must obey participation constraint
	- Ex: Assume we are operating w/ kids entity set, who are on their parents (employees) insurance policy. Each employee has 1+ kids,
	  but each kid corresponds to 1 parent/employee
	- Weak entity set is represented by a bolding around weak entity set & relationship model, w/ bold arrow as go-between
	- Weak entities have partial keys (dashed underline) since the keys can have duplicates and are instead defined by owner set

Crow Foot Notation
- Crow Foot notation (alternate way of expressing entity-relationship model): o: 0+, |: 1+, |o: 0/1, ||: 1, ─∈: many 
- No constraints: normal-line, crowfoot-o∈, Key constraint: arrow, crowfoot: |o, Participation constraint: normal:bold line, crowfoot:-∈, 
  Participation & key constraint: normal:bold arrow, Crowfoot: ||
- Can translate this into math terms as partial functions, total functions, surjection, injection, bijection

Binary/Ternary Relationships
- Operating w/ previous example: dependents is a weak entity set that has a relationship to employees. Assume that we now have policies entity
  set that relates employees & dependents
  - Initially, impose key constraint on policies w/ the "covers" relationship to ensure that each policy participates only a single time. However,
  	since dependents and employees are related, this forces each policy to have (employee, dependent) pairing
  - Impovement: connect dependents to beneficiary relationship, so that each dependent has only 1 policy, which connects to employees through
    "purchaser" relationship: each policy is purchased by 1 employee (employees can purchase multiple policies)

Aggregation
- With entity-relationship diagrams, relationships should not connect relationships but instead work w/ entity sets, but this
  is not always the desired behavior
- Aggregation: take a subgraph of the existing ER diagram (represented by a dotted box) which then corresponds to another entity set
  via the relationship

Design Considerations
- We have various operations to choose from: binary, ternary, aggregation, which just depends on the design needs
- Other considerations: need to consider entity vs. attribute, entity vs. relationship, & the form of the relationship
- Entity vs. Attribute: assume we are dealing w/ address, which could be an attribute of the employees table or it could be
  its very own entity. If desired behavior is to allow 1 employee to have >1 address, need an entity since cannot have a set 
  of values as an attribute in ER model. 
	- If we want structure (set format for the entities) --> must be entity as well since we need atomic types for the attributes

Converting ER Diagram into Relational Schema
- Step 1: convert entity set into a table using the key of the entity set as the primary key
- Step 2: translate many-to-many relationship set into a new table, in which the columns include the keys of all the original entities which
  act as the foreign keys & also include the attributes of the original entity set that we want to include
- Step 3: convert key constraints in the original diagram as the primary keys of the new table under relational paradigm
- Step 4: participation constraints typically captured as "Not Null" to ensure that there is a presence since it is binary relationship
- Step 5: translating weak entity set by including the weak entity partial key and the owner entity set key as primary key
	- Should include a "delete cascade" phrase in the foreign key to ensure that referenced table is removed if what it references is deleted too

Conceptual Design Summary
- The initial phase of designing a database requires taking inventory of what functionality we actually want to achieve
- ER model is used w/ conceptual design, providing graphical representation of entities, relationships, & attributes
- Also are interested in integrity constraints, such as key constraints and participation constraints, in which we require a
  1 to many or presence of all in relationships b/w entity sets
- Ultimately, need to realize that entity-relationship design is a human decision, considering multiple options w/
  how to represent w/ entities, attributes, or relationships
  - If using a relatinoship, can use binary, n-ary, or aggregation models


Example From Vitamin: Baseline: BTSPDCHRA
- Functional Dependencies: R->SP, SP->DCH, B->SCT, DH->A, TS->R, SPR->B, S->P
R+ = [R, SP, DCH, A, B, T] --> R is a candidate key
SP+ = [SP, DCH, A] --> Not candidate key
B+ = [B, SCT, P, DCH, A, R] --> Candidate key
DH+ = [DH, A] --> Not candidate key
SPR+ = [SPR, B, SCT, DCH] --> Candidate Key
TS+ = [TS, R, P, DCH, B, A] --> Candidate key
S = [S, P, DCH, A] --> Not a candidate Key


