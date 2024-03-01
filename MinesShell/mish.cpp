#include "mish.h"

int main(int argc, char** argv)
{
    if(argc == 1)
    {
        runUserInput();             //run with user input
    }
    else if(argc == 2)
    {
        string fileName = argv[1];  //get file name
        ifstream input;

        input.open(fileName);       //open file

        if (!input.is_open())
        {
            cout << fileName << ": could not be found or opened" << endl;
            exit(EXIT_FAILURE);
        }

        runFileInput(input);        //run with file input
    }
    else
    {                               //dont run without correct usage
        cout << "Invalid arguments provided" << endl;
        exit(EXIT_FAILURE);
    }

    return 0;
}

void runUserInput()
{
    cout << "mish>";

    string command;
    LinkedList commandList;
    vector<string> args;

    while (getline(cin, command))   //while user input is coming in get the commands
    {
        if (command == "exit")      //exit gracefully
        {
            exit(EXIT_SUCCESS);
        }
        else if (!command.empty())
        {
            args = tokenizeCommand(command);                //tokenize the command 
            fillCommandList(args, commandList);             //fill in commandlist with line of commands
        }

        executeCommands(commandList, environ);              //execute the commands
        command = "";
        commandList.clear();                                //clear the list to start again
        cout << "mish>";                                    //await next user input
    }
}


void runFileInput(ifstream& fileIn)
{
    string command;
    LinkedList commandList;
    vector<string> args;

    while (getline(fileIn, command))
    {
        if (command == "exit")
        {
            exit(EXIT_SUCCESS); //exit gracefully
        }
        else if (!command.empty())
        {
            args = tokenizeCommand(command);                //tokenize the line of commands 
            fillCommandList(args, commandList);             //fill in the command list
        }

        executeCommands(commandList, environ);              //execute the commands
        command = "";
        commandList.clear();                                //clean up
    }
}


vector<string> tokenizeCommand(const string& command)
{
    vector<string> args;
    istringstream iss(command);
    string arg;

    while (iss >> arg)  //token read the command to fill in args
    {
        size_t pos;
        while ((pos = arg.find_first_of("&|")) != string::npos) //look for special characters
        {
            if (pos > 0)
            {
                args.push_back(arg.substr(0, pos)); //add the part before special character
            }
            args.push_back(arg.substr(pos, 1)); //add the special character
            arg.erase(0, pos + 1); //remove processed part to continue processing
        }

        if (!arg.empty())
        {
            args.push_back(arg); //add whatever is left to the vector
        }
    }

    return args;
}

void executeCommands(const LinkedList &commandList, char** envp)
{
    Node *current = commandList.head;
    int originalIn = dup(0);
    int originalOut = dup(1);
    vector<pid_t> childProcesses;
    int prevReadEnd = -1;

    while (current != nullptr)
    {

        if (current->outPipe)   //if we need to pipe out, pipe with this command's fd
        {
            if (pipe(current->pipefd) == -1)
            {
                perror("mish: pipe");   //piping failed, print info and exit
                exit(EXIT_FAILURE);
            }
        }

        if (!current->inFileName.empty())   //if we have an input file
        {
            int inFileDescriptor = open(current->inFileName.c_str(), O_RDONLY); //open the file for reading

            if (inFileDescriptor == -1) //if opening failed, output info and exit
            {
                perror(("mish: " + current->inFileName).c_str());
                exit(EXIT_FAILURE);
            }

            if (dup2(inFileDescriptor, STDIN_FILENO) == -1) //set stdin to the input file
            {
                perror("mish: dup2");   //if dup failed output info and exit
                exit(EXIT_FAILURE);
            }

            close(inFileDescriptor);
        }

        if (!current->outFileName.empty())  //if we have an output file
        {
            //open output file, or create it if it does not exist
            int outFileDescriptor = open(current->outFileName.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0666);

            if (outFileDescriptor == -1)    //if opening the output file failed, output info and exit
            {
                perror(("mish: " + current->outFileName).c_str());
                exit(EXIT_FAILURE);
            }

            if (dup2(outFileDescriptor, STDOUT_FILENO) == -1)   //set stdout to output file
            {
                perror("mish: dup2");   //if dup failed, output info and exit
                exit(EXIT_FAILURE);
            }

            close(outFileDescriptor);
        }

        //if the command is cd we need to handle it in the parent or nothing will happen
        if (current->args.size() > 0 && current->args[0] == "cd")
        {
            cd(*current);
        }
        //check if we need to set environment variable
        else if (current->args.size() > 0 && current->args[0].find('=') != string::npos)
        {
            setEnvironmentVariable(current->args, envp);
        }
        else
        {
            pid_t pid = fork();

            if (pid == 0)
            {
                char** argv = convertToCArray(current->args);   //convert to c array for exec

                if (current->outPipe)
                {   //if we need to pipe out, make sure fd is valid
                    if(current->pipefd[1] == -1)
                    {
                        perror("mish: pipe");
                        exit(EXIT_FAILURE);
                    }
                    //set stdout to the write end of the pipe
                    else if (dup2(current->pipefd[1], STDOUT_FILENO) != 1)
                    {
                        perror ("mish: dup2 out pipe");
                        exit(EXIT_FAILURE);
                    }

                }
                else
                {
                    //no need to pipe out
                    current->pipefd[1] = dup(STDOUT_FILENO);
                    if(current->pipefd[1] == -1)
                    {
                        perror("mish: dup");
                        exit(EXIT_FAILURE);
                    }
                }

                if (current->inPipe)    //if this cmd has an input pipe
                {
                    if(prevReadEnd == -1)   //check that prev read end is valid
                    {
                        perror("Failed to open read pipe\n");
                        exit(EXIT_FAILURE);
                    }
                    //set input to the previous pipe's read end
                    if (dup2(prevReadEnd, STDIN_FILENO) == -1)
                    {
                        perror ("mish: dup2 in pipe");
                        exit(EXIT_FAILURE);
                    }
                }
                else    //no need to pipe in
                {   
                    prevReadEnd = dup(STDIN_FILENO);
                    if(prevReadEnd == -1)
                    {
                        perror("Failed to duplicate stdin to read pipe\n");
                        exit(EXIT_FAILURE);
                    }
                }

                execvpe(argv[0], argv, envp);

                //if we return from exec, there has been an error
                cerr << "mish: " << current->args[0] << ": command not found" << endl;
                freeCArray(argv);
                exit(EXIT_FAILURE);
            }
            else if (pid < 0)
            {
                cerr << "Fork failed" << endl;
                exit(EXIT_FAILURE);
            }
            else
            {   
                if (!current->parallel) //if not running in parallel, we wait
                {
                    waitpid(pid, NULL, 0);
                }
                else    //if running in parallel, just put it in the list of things we need to wait for
                {
                    childProcesses.push_back(pid);
                }
            }
        }

        if (current->outPipe)   //set the read end for the next command and close the write end
        {
            prevReadEnd = current->pipefd[0];
            close(current->pipefd[1]);
        }

        dup2(originalIn, 0);    //restore stdin and stdout
        dup2(originalOut, 1);

        Node* next = current->next; //go to next command
        current = next;
    }

    for (pid_t childPid : childProcesses)   //wait for all of the child processes in parallel to finish
    {
        waitpid(childPid, NULL, 0);
    }
}


// convert vector<string> to char**
char** convertToCArray(const vector<string>& vec)
{
    char** arr = new char*[vec.size() + 1];
    for (size_t i = 0; i < vec.size(); ++i)
    {
        arr[i] = strdup(vec[i].c_str());
    }
    arr[vec.size()] = nullptr;
    
    return arr;
}

// free memory allocated by c array
void freeCArray(char** arr)
{
    for (size_t i = 0; arr[i] != nullptr; ++i)
    {
        free(arr[i]);
    }
    delete[] arr;
}

void cd(const Node& command) {
    // check if command is cd
    if (command.args.size() > 0 && command.args[0] == "cd") 
    {
        // make sure number of args is right
        if (command.args.size() != 2) 
        {
            cerr << "mish: cd: invalid number of arguments" << endl;
        } else 
        {
            // cd
            if (chdir(command.args[1].c_str()) != 0) 
            {
                perror(("mish: cd: " + command.args[1]).c_str());
            }
        }
    }
}

void setEnvironmentVariable(const vector<string> &args, char **envp)
{
    for (const string &arg : args)
    {
        size_t pos = arg.find('=');
        if (pos != string::npos)
        {
            // get variable name and value
            string varName = arg.substr(0, pos);
            string varValue = arg.substr(pos + 1);

            // set the env variable
            setenv(varName.c_str(), varValue.c_str(), 1);
        }
    }
}

void handleBothInputAndOutputRedirection(vector<string>& args, vector<string>::iterator inIndicatorLocation, 
                                         vector<string>::iterator outIndicatorLocation, LinkedList& commandList, 
                                         bool isParallel, bool pipeIn, bool pipeOut)
{
    size_t inIndex = distance(args.begin(), inIndicatorLocation);
    size_t outIndex = distance(args.begin(), outIndicatorLocation);

    //if we have both an in index and an out index and they both have proper arguments after
    if (inIndex + 1 < args.size() && inIndex + 2 == outIndex && outIndex + 1 < args.size())
    {
        string inputFile = args[inIndex + 1];   //get input file from args
        string outputFile = args[outIndex + 1]; //get output file from args
        //insert into the list with both file names
        commandList.insert(vector<string>(args.begin(), args.begin() + inIndex), inputFile, outputFile, isParallel, false, false);
    }
    else
    {
        //syntax error if the previous conditions arent met
        cerr << "mish: invalid syntax after < or > operator" << endl;
    }

    //erase what we processed to process more if needed
    args.erase(args.begin() + inIndex, args.begin() + outIndex + 2);
}

void handleInputRedirection(vector<string>& args, vector<string>::iterator inIndicatorLocation, LinkedList& commandList, 
                            bool isParallel, bool pipeIn, bool pipeOut)
{
    size_t inIndex = distance(args.begin(), inIndicatorLocation);

    if (inIndex + 1 < args.size())  //if there is an input indicator
    {
        string inputFile = args[inIndex + 1];   //get input file and add the command to the list 
        commandList.insert(vector<string>(args.begin(), args.begin() + inIndex), inputFile, "", isParallel, pipeIn, pipeOut);
    }
    else
    {
        //syntax error if there is nothing after the input indicator
        cerr << "mish: invalid syntax after < operator" << endl;
    }

    //erase processed stuff to continue on
    args.erase(args.begin() + inIndex, args.begin() + inIndex + 2);
}

void handleOutputRedirection(vector<string>& args, vector<string>::iterator outIndicatorLocation, LinkedList& commandList, 
                             bool isParallel, bool pipeIn, bool pipeOut)
{
    size_t index = distance(args.begin(), outIndicatorLocation);

    if (index + 1 < args.size() && index + 2 == args.size())
    {
        //if there is an output indicator and the output file name is the last arg of the command
        string outputFile = args[index + 1];
        //insert the command into the list
        commandList.insert(vector<string>(args.begin(), args.begin() + index), "", outputFile, isParallel, pipeIn, pipeOut);
    }
    else
    {
        //otherwise, the syntax is invalid
        cerr << "mish: invalid syntax after > operator" << endl;
    }
}

void fillCommandList(vector<string>& args, LinkedList& commandList)
{
    // find parallel indicator
    auto ampersandLocation = find(args.begin(), args.end(), "&");

    if (ampersandLocation != args.end())
    {
        // fill in command list with parallel
        vector<string> commandArgs(args.begin(), ampersandLocation);
        handleRedirection(commandArgs, commandList, true);
        
        // remove processed part
        args.erase(args.begin(), ampersandLocation + 1);

        // recursively handle remaining commands in args
        fillCommandList(args, commandList);
    }
    else
    {
        // if not parallel, handle normally
        handleRedirection(args, commandList, false);
    }
}


void handleRedirection(vector<string>& args, LinkedList& commandList, bool isParallel)
{
    auto inIndicatorLocation = find(args.begin(), args.end(), "<");
    auto outIndicatorLocation = find(args.begin(), args.end(), ">");
    auto pipeIndicatorLocation = find(args.begin(), args.end(), "|");

    bool hasInputPipe = false;

    if (pipeIndicatorLocation != args.end())
    {
        size_t pipeIndex = distance(args.begin(), pipeIndicatorLocation);

        while (pipeIndex != args.size())
        {
            vector<string> currentCommand(args.begin(), args.begin() + pipeIndex);
            inIndicatorLocation = find(currentCommand.begin(), currentCommand.end(), "<");
            outIndicatorLocation = find(currentCommand.begin(), currentCommand.end(), ">");

            //if there is an input indicator and output indicator, send it to the function to handle that
            if (inIndicatorLocation != currentCommand.end() && outIndicatorLocation != currentCommand.end())
            {
                handleBothInputAndOutputRedirection(currentCommand, inIndicatorLocation, outIndicatorLocation, commandList, isParallel, hasInputPipe, true);
            }
            //if there is just an in indicator, send it to that function
            else if (inIndicatorLocation != currentCommand.end())
            {
                handleInputRedirection(currentCommand, inIndicatorLocation, commandList, isParallel, hasInputPipe, true);
            }
            //just an out indicator, send it to that function
            else if (outIndicatorLocation != currentCommand.end())
            {
                handleOutputRedirection(currentCommand, outIndicatorLocation, commandList, isParallel, hasInputPipe, true);
            }
            else
            {
                //no input or output files so just add and say it has an out pipe
                commandList.insert(currentCommand, "", "", isParallel, hasInputPipe, true);
            }

            // remove processed part with pipe
            args.erase(args.begin(), args.begin() + pipeIndex + 1);

            // the next one will have an input pipe if the current one had an output pipe
            hasInputPipe = true;

            // find the next pipe indicator
            pipeIndex = distance(args.begin(), find(args.begin(), args.end(), "|"));
        }
    }

    //handle commands with no pipes, or the last command in a sequence of pipes
    inIndicatorLocation = find(args.begin(), args.end(), "<");
    outIndicatorLocation = find(args.begin(), args.end(), ">");

    //both input and output, send it to the corresponding function
    if (inIndicatorLocation != args.end() && outIndicatorLocation != args.end())
    {
        handleBothInputAndOutputRedirection(args, inIndicatorLocation, outIndicatorLocation, commandList, isParallel, hasInputPipe, false);
    }
    //just input
    else if (inIndicatorLocation != args.end())
    {
        handleInputRedirection(args, inIndicatorLocation, commandList, isParallel, hasInputPipe, false);
    }
    //just output
    else if (outIndicatorLocation != args.end())
    {
        handleOutputRedirection(args, outIndicatorLocation, commandList, isParallel, hasInputPipe, false);
    }
    else    //neither input nor output
    {
        commandList.insert(args, "", "", isParallel, hasInputPipe, false);
    }
}