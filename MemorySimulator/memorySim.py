from Process import Process
from DiscreteEventSimulation import DiscreteEventSimulation
from DiscreteEventSimulation import Event

def readFile(filename):
    inputQueue = []
    lastBlank = False
    with open(filename, 'r') as file:
        lines = file.readlines()[1:]  # skip the first line since we dynamically size
        processData = []
        for line in lines:
            if line.strip(): 
                processData.append(line.strip())
                lastBlank = False
            else:
                # processes are separated by a new line so this is the indication to fill in a process
                # lastBlank is set up in case there are multiple newlines at the end of a file
                if lastBlank:
                    break
                id = int(processData[0])
                arrival, timeInMem = map(int, processData[1].split())
                memArraySize, *memArrayData = map(int, processData[2].split())
                memArray = memArrayData[:memArraySize]
                inputQueue.append(Process(id, arrival, timeInMem, memArray))
                processData = []
                lastBlank = True

        # this covers the edge case in which there are no new lines at eof
        if processData != []:
            id = int(processData[0])
            arrival, timeInMem = map(int, processData[1].split())
            memArraySize, *memArrayData = map(int, processData[2].split())
            memArray = memArrayData[:memArraySize]
            inputQueue.append(Process(id, arrival, timeInMem, memArray))
    return inputQueue

def main():
    memSize = input("Memory size: ")
    policy = input("Memory management policy (1 - VSP, 2 - PAG, 3 - SEG): ")

    if policy != "2":
        algorithm = input("Fit algorithm (1 - first-fit, 2 - best-fit, 3 - worst-fit): ")
        if policy == "1":
            simulation = DiscreteEventSimulation(memSize, "VSP", algorithm)
        else: 
            simulation = DiscreteEventSimulation(memSize, "SEG", algorithm)
    else:
        frameSize = input("Page size: ")
        simulation = DiscreteEventSimulation(memSize, "PAG", frameSize)

    # read file in
    filename = input("Enter workload file name: ")
    input_queue = readFile(filename)

    for process in input_queue:
        simulation.schedule_event(Event(process.arrivalTime, 'PROCESS_ARRIVAL', process))

    simulation.run_simulation()



if __name__ == "__main__":
    main()
