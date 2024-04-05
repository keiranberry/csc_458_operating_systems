from process import Process

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
    else:
        frameSize = input("Page size: ")

    # Read workload file
    filename = input("Enter workload file name: ")
    input_queue = readFile(filename)
    print("Processes loaded into input queue:")
    for process in input_queue:
        print(process)



if __name__ == "__main__":
    main()
