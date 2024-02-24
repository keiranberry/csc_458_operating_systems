#pragma once

#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstring>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <algorithm>

using namespace std;

struct Node 
{
    vector<string> args;   // args
    string inFileName;     // input file
    string outFileName;    // output file
    bool parallel;         // parallel flag
    bool inPipe;           // in pipe flag
    bool outPipe;          // out pipe flag
    int pipefd[2] = {};

    Node* next;

    Node(const vector<string>& arguments, const string& fin, 
        const string& fout, bool para, bool pin, bool pout)
        : args(arguments), inFileName(fin), outFileName(fout), parallel(para), 
        inPipe(pin), outPipe(pout), next(nullptr) {}
};

class LinkedList 
{
public:

    Node* head;

    LinkedList() : head(nullptr) {}

    //insert a new node at the end of the list
    void insert(const vector<string>& arguments, const string& fin, 
        const string& fout, bool para, bool pin, bool pout) 
    {
        Node* newNode = new Node(arguments, fin, fout, para, pin, pout);

        if (head == nullptr) 
        {
            head = newNode;
        } 
        else 
        {
            Node* current = head;
            while (current->next != nullptr) 
            {
                current = current->next;
            }
            current->next = newNode;
        }
    }

    void clear() 
    {
        while (head != nullptr) 
        {
            Node* temp = head;
            head = head->next;
            delete temp; 
        }
    }

    void print() const              //function to print linked list for debug purposes
    {
        Node* current = head;

        while (current != nullptr) 
        {
            cout << "Arguments: ";
            for (const auto& arg : current->args) 
            {
                cout << arg << " ";
            }
            cout << "\nInput File: " << current->inFileName
                      << "\nOutput File: " << current->outFileName
                      << "\nParallel: " << (current->parallel ? "true" : "false")
                      << "\nIn Pipe: " << (current->inPipe ? "true" : "false")
                      << "\nOut Pipe: " << (current->outPipe ? "true" : "false")
                      << "\n\n";

            current = current->next;
        }
    }
};
//environment variables
extern char **environ;

void runUserInput();
void runFileInput(ifstream& fileIn);
vector<string> tokenizeCommand(const string& command);
void executeCommands(const LinkedList& commandList, char** envp);
char** convertToCArray(const vector<string>& vec);
void freeCArray(char** arr);
void cd(const Node& command);
void setEnvironmentVariable(const vector<string> &args, char **envp);
void handleBothInputAndOutputRedirection(vector<string>& args, 
                                         vector<string>::iterator inIndicatorLocation, 
                                         vector<string>::iterator outIndicatorLocation, 
                                         LinkedList& commandList, 
                                         bool isParallel, 
                                         bool pipeIn, 
                                         bool pipeOut);
void handleInputRedirection(vector<string>& args, 
                            vector<string>::iterator inIndicatorLocation, 
                            LinkedList& commandList, 
                            bool isParallel, 
                            bool pipeIn, 
                            bool pipeOut);
void handleOutputRedirection(vector<string>& args, 
                             vector<string>::iterator outIndicatorLocation, 
                             LinkedList& commandList, 
                             bool isParallel, 
                             bool pipeIn, 
                             bool pipeOut);
void fillCommandList(vector<string>& args, LinkedList& commandList);
void handleRedirection(vector<string>& args, LinkedList& commandList, bool isParallel);