# Browsing the Galaxy

Requirements
 - A compiler, we used GCC 10.1.0 (uses C++20 and some builtins)
 - gtk3 for wxWidgets (the latter being included as submodule)

```
# Yes, recursive submodules
git submodule init --recursive
mkdir build
cd build
# Definately needs -O3, but still want assertions to be active
cmake .. -DCMAKE_BUILD_TYPE -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-O3 -g"
export API_KEY=...
# Must be executed so that it reaches ../resources/galaxy.txt
./galaxy 
```

# Our journey / ordeal

We didn't prepare a lot, especially since we were all working remotely this time.
We did test the submission system in advance and followed the preface (joining way too late unfortuantely).

## Day 0.5

When we crawled through the messages, reading the messages and following the discovery took us a long time.

From the messages, we assumed the worst about the structure of rules.
Thus we started by implementing a very generic pattern matching engine and fed it the messages.
There was a variant with a breadth first search ordered by expression size to deal with recursion while remaining generic.
It was able to evaluate `pwr2` so we though that we are onto something.

## Day 1.5

The first fundamental optimization effort was to split the rules into strict simplifications and expansions.
One step in the search for a evaluated term was then a single expansion followed by a full tree simplification.
The BFS was still far too slow and the video 2 about recursion suggested that a leftmost evaluation should always be fine to do.
So we switched the focus to a linear evaluation - still with the expansion & simplification steps.

Now video 3 highlighted the importance of handling copied subtress efficiently.
At this point we used immutable trees.
This enabled efficient lookup for expression through cached hashes.
Using a `@lru_cache` was speeding things up, but still far away from necessary performance for galaxy.
It went on and on with optimizations, by hardcoding *all* primitives, assuming only `op = expr` expansion instead of pattern matching.
While we did see improvements in evaluation speed, still galaxy interaction was impossible.
We had another attempt with mutable trees that didn't allow for the BFS any longer at all.
Again it was much faster and it could get us to the entry screen, but it was far away from rendering the far from rendering the full galaxy.

Only after the Pseudocode Evaluator was published, we could get it working - first by adapting the current code then by a much simpler reimplementation of the pseudocode.
By the end of day 2 we had a reasonable Python implementation with a basic tcod interface.
We started to look a bit into the "tutorial", but it was still slow enough to be difficult to use.

## Day 2.5

While we started off Sunday with some more optimization imporvement, we did hit a wall with Python for the implementation speed and tcod as an interface.
So we built another evaluator in C++ from Pseudocode that finally went fairly well with respect of performance.
Oddly enough the further performance optimization attempts didn't yield any progress.
For instance we tried caching *all* expressions.
That way we could just compare pointers and never evaluate the same expression twice.
Still, this was way slower, likely due to > 80 % miss rate on ap (i.e. surprisingly most expressions seemed to be unique).
So that approach was scrapped, but performance was sufficient.

The evaluator got a wxWidgets UI that allowed much better rendering.
Especially it gave us a numbers overlay that we felt was necessary to fully understand the tutorial.

We also followed attempted to write a transpiler from `galaxy` to haskell, but it remained an attempt.

More of us started to shift towards space battles, but unfortunately not with good information base from the galaxy experience. 

## Day 3

On Monday, most of us worked on getting some reasonable submission, unfortunately with little measurable success.

Also the C++ Galaxy evaluator improved a lot with several useful features:

 - Evaluating every possible click in the visible bounding box to create cluster maps where to click.
   This doesn't work for large screens due to time and memory requirements.
   Unfortunately C++ made it very painful to properly cluster these trees of recursive variants.
   Later there was a strided version for the "numbers game".
 - Undo function - surprisingly simple but very effective
 - Save and load traces of evaluation (clicks, not state) - also very simple and effective
 - Brute force hard-coded evaluator for the 3x3 "Tic-Tac-Toe" puzzle

# Impressions

We did have a lot of fun in this contest even without placing highly (as usual).
There were a lot of ups, but also downs for us.
This is a typical for us in the ICFP contest, but seemed even more true this year.

First, the story was glorious.
The messages and their discussion on Discord were amazing to follow.
My only regret is to not having noticed it earlier on.
There really should be persistent communication path *across the years*
that is used for an initial announcement, to hint towards the communication medium of the year and as a reminder when the hints/preface starts.

I really enjoyed exploring the galaxy and learning rules and interacting on discord.
The galaxy felt like a very consistent place full of surprises and layers of discovery.  
But it was a bit frustrating to spend the first day on an evaluator only to have it replaced by a couple lines of Pseudocode.
I suspect the Pseudocode Evluator only works efficiently because it is not generic, i.e., it exploits undocumented properties of `galaxy`, it's input.
We always suspected that you just had to know enough about functional programming (which we certainly did not) to easily write a fast evaluator.
Now I'm not complaining that being successful at the **I**CFP programming contest requires knowledge of functional programming.
But it did feel that this time you needed more specific knowledge to even make some progress.
I appreciate that the organizers did help out with hints throughout the contest,
but it would have felt better if there was enough information to do it on our own.
If the lightning round scores are any indications, a vast majority of teams struggled evaluating the galaxy. 

I was lucky to be in a team of five and it felt like we needed all the manpower we got.
While there was plenty of stuff to do or just try out in parallel, there were also dependencies that created a nice dynamic.

A highlight for me was the communication on discord and especially the live videos.
The technical side, git/docker submissions and simple API worked well.

We thank all the organizers for this year's contest.
Thank you for the very challenging and deep experience.
