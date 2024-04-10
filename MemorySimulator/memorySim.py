from process import Process
from discreteEventSimulation import DiscreteEventSimulation
from discreteEventSimulation import Event

def readFile(filename):
    inputQueue = []
    with open(filename, 'r') as file:
        lines = file.readlines()[1:]  # Skip the first line
        processData = []
        for line in lines:
            if line.strip():  # Skip blank lines
                processData.append(line.strip())
            else:
                id = int(processData[0])
                arrival, timeInMem = map(int, processData[1].split())
                memArraySize, *memArrayData = map(int, processData[2].split())
                memArray = memArrayData[:memArraySize]
                inputQueue.append(Process(id, arrival, timeInMem, memArray))
                processData = []
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

    # Read workload file
    filename = input("Enter workload file name: ")
    input_queue = readFile(filename)

    for process in input_queue:
        simulation.schedule_event(Event(process.arrivalTime, 'PROCESS_ARRIVAL', process))

    # Run simulation
    simulation.run_simulation()



if __name__ == "__main__":
    main()
