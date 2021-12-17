Vitamin 4: Buffer Management, Relational Algebra

Question 5: Relational Algebra
- 1. Users: uid, uname, country; 2. Artists: aid, aname; 3. Albums: albumid, albumname, genre, aid, 4. Ratings: uid, aid, rating
  4. Follows: uid, fuid
  - Albums: foreign key aid references artists aid, Ratings: foreign key uid references users(uid) and foreign key (aid) references
    artists (aid), follows references users (uid, fuid)

1. Want: every instance of artist rated by a user: give name of user/artist & the rating
    1. π_uname,aname,rating (Users CJ Ratings CJ Artists)
    	- Correct: Obtain all tuples such that there the user ID in ratings and users match and within that row, the
    	  artist ID matches w/ the artists table --> provides exactly what we want
    	  - Selected the 3 relevant columns above
    2. π_uname,aname,rating (Users CJ Artists)
    	- Incorrect: tries to select the rating column, but the ratings table was not included
    3. π_uname,aname,rating (Users CJ Ratings CJ σ(aid!=Ratings.aid) (Artists))
    	- Only preserve artists such that the ratings & artist have the same ID w/ the neste query. However, initial aid
    	  query could refer to the artists or the ratings table (leading to ambiguity) --> incorrect

2. Want: artist names who have albums in genre TTS and MPFM
	a. π(Artists.aname σ((Albums.genre= "TTS" (Albums))) intersect π(Artists.aname σ((Albums.genre= "MPFM" (Albums)))
		- We first only select rows that have the genre "TTS" in Albums, doing the same w/ genre "MPFM". Never obtained the actual
		  artist names from the artists table --> invalid choice
	b. π(Artists.aname σ((Albums.genre= "TTS"(Albums) CJ Artists))) intersect
	   π(Artists.aname σ((Albums.genre= "MPFM"(Albums) CJ Artists)))
	    - First query finds the artist names that have an album that is TTS by cross joining rows of that genre against artists
	      matching on artist ID against artists table. Match those artists against those w/ the genre "MPFM"
	    - This provides the correct behavior that we want
	c. π(Artists.aname σ((Albums.genre= "TTS"(Albums) and Albums.genre = "MPFM" (Albums)) CJ Artists
		- Keep only genres that are simultaneosuly TTS and MPFM --> yields no results even before attempting to cross join w/ artists
			- The issue is that this prematurely filters out columns from the albums table
	d. π(Artists.aname σ((Albums.genre= "TTS"(Albums)))) U π(Artists.aname σ((Albums.genre= "TTS"(Albums))))
		- Keeps only the artists that have a TTS genre, keep only those in MPFM --> take the union of both which provides artists
		  that have a genre in either genre --> incorrect

3. Want: names of artists that have not been rated
	a. π_aname(π_aid, aname(Artists) - π_aid, aname(Artists CJ Users)))
		- First has the artists, the second has the artist ID and names for artists matching against users,
		  but there is no way to directly match users and artists --> incorrect behavior
	b. π_aname(π_aid, aname(Artists) - π_aid, aname(Artists CJ Ratings))
		- Get the artist ID and names, subtracting away artists that have a rating that have matching artist ID & name
	c. π_aname(π_aid, aname(Artists) - π_aid, aname(Artists CJ Ratings CJ Users))
		- Add in joining the users, which does not provide any added info against the intersection of aritsts & ratings
			- The idea here is that since ratings references both the original users and ratings so it ends up being the same
			 table w/ a username & country column before ignoring those columns anyway
	d. π_aname(Ratings - π_aid, aname(Artists CJ Ratings CJ Users))
		- Tries to remove artists w/ ratings from all ratings --> Also cannot take set dfiference b/w 2 tables w/different schemas,
		  such as the ratings table vs. one w/ artist ID and name

# Code for LRU, MRU, Clock policies

def lru(size, s):
	cache = []
	hits = 0
	for i in range(size):
		cache.append(s[i])
	for i in range(size, len(s)):
		if s[i] in cache:
			cache.remove(s[i])
			cache.append(s[i])
			hits += 1
		else:
			cache.pop(0)
			cache.append(s[i])
	return (cache, hits)

def mru(size, s):
	cache = []
	hits = 0
	for i in range(size):
		cache.append(s[i])
	for i in range(size, len(s)):
		if s[i] in cache:
			cache.remove(s[i])
			cache.append(s[i])
			hits += 1
		else:
			cache.pop()
			cache.append(s[i])
	return (cache, hits)

def clock(size, s):
	cache = []
	hits = 0
	for i in range(size):
		cache.append([s[i], True]) # Current element, second chance bit, pinned bit
	pointer = 0
	for i in range(size, len(s)):
		exists = False
		for j in range(size):
			# print(cache, j)
			if cache[j][0] == s[i]:
				cache[j] = [s[i], True]
				# pointer = (j + 1) % 4
				hits += 1
				exists = True
				break
		if not exists:
			toRemove = False
			while not toRemove:
				testRemove = cache[pointer]
				if testRemove[1] == False:
					cache[pointer] = [s[i], True]
					toRemove = True
				else:
					cache[pointer][1] = False
				pointer = (pointer + 1) % 4
	return (cache, hits)
