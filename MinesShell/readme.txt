This is a functioning shell that supports piping, parallelization, 
and file input and output redirection. It has the ability to run 
commands, and has three built-in supported commands as well: 

- exit , which takes no arguments, and exits the program. If arguments 
    are entered, the shell will tell the user that the command was not 
    found and allow them to try again.

- cd , which takes an argument for the directory that is to be changed to.
    This utilizes the chdir() call.

- <var>= , which allows the user to change the value of an environment 
    variable. Either the value of the environment variable will be changed 
    or the environment variable will be created with the given value.

This program should be compiled as follows: 

g++ -o mish  -Wall -Werror -O mish.cpp

This treats all warnings as errors as well, so it can be ensured that there 
are no warnings or errors in the code. 

There are two ways to run the executable: 

./mish and ./mish fileName

Running mish without an input file puts the shell in interactive mode, in which 
the user can type in their own commands and continue until they decide to "exit".

Running mish with an input file will run the commands in the file line by line, and 
then return. No control will be given to the user in this case, but it will run the 
specified commands in the file. 