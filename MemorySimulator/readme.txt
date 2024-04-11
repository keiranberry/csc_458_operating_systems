Memory Simulator in Python written by Keiran Berry

This memory simulator implements Variable Size Partitioning (first-fit, best-fit, and worst-fit), 
Paging, and Segmentation (first-fit, best-fit, and worst-fit).

Usage for this program is as follows: 

From the directory of the program, type "Python3 MemorySim.py" into the console. The user 
will be prompted for information regarding the simulation, and then the simulation will be 
run. Important information about the simulation will be output to the console, and it has 
been checked for consistency (except for very minor whitespace) with the provided test files.

I implemented a Priority Queue for this program, so that I could specify the order of precedence in 
the queue simply. I could differentiate between the types of Events (an object which I implemented), 
the process id's, and the arrival time to make a consistent ordering of events at each time. I run a 
simulation which utilizes a memory manager, of which there are three to choose from, one for each of the 
memory management policies. Whichever the user chooses is the memory manager for that run of the simulation. 
Then, it is as simple as calling each one's allocate and deallocate function, so the same code is very 
reusable. 