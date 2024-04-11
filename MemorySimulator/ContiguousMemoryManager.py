from Process import Process

class ContiguousMemoryManager:
    def __init__(self, totalMemory, algorithm):
        self.memorySize = int(totalMemory)
        self.memoryMap = [Process(None, None, None, None, 0, int(totalMemory) - 1)]
        if algorithm == "1":
            self.algorithm = "first-fit"
        elif algorithm == "2":
            self.algorithm = "best-fit"
        else:
            self.algorithm = "worst-fit"

    def allocate(self, process):
        if self.algorithm == "first-fit":
            return self.allocateFirstFit(process)
        elif self.algorithm == "best-fit":
            return self.allocateBestFit(process)
        else:
            return self.allocateWorstFit(process)

    def allocateFirstFit(self, process):
        for i, block in enumerate(self.memoryMap):
            if block.id is None and (block.endMemory - block.startMemory) >= process.totalMemory - 1:
                # Allocate memory
                startMem = block.startMemory
                endMem = startMem + process.totalMemory - 1
                self.memoryMap[i] = Process(process.id, process.arrivalTime, process.timeInMemory, process.memoryArray, startMem, endMem)
                
                # Add empty process for the remaining free memory
                remainingMemStart = endMem + 1
                remainingMemEnd = block.endMemory
                if remainingMemStart < remainingMemEnd:
                    remainingBlock = Process(None, None, None, None, remainingMemStart, remainingMemEnd)
                    self.memoryMap.insert(i + 1, remainingBlock)

                return 0  # Allocation successful
        return -1  # Not enough memory or suitable block not found

    def allocateBestFit(self, process):
        bestFitIndex = -1
        bestFitSize = float('inf')

        for i, block in enumerate(self.memoryMap):
            if block.id is None and (block.endMemory - block.startMemory) >= process.totalMemory - 1:
                blockSize = block.endMemory - block.startMemory + 1
                if blockSize < bestFitSize:
                    bestFitIndex = i
                    bestFitSize = blockSize

        if bestFitIndex != -1:
            # Allocate memory
            startMem = self.memoryMap[bestFitIndex].startMemory
            endMem = startMem + process.totalMemory - 1
            remainingMemEnd = self.memoryMap[bestFitIndex].endMemory
            self.memoryMap[bestFitIndex] = Process(process.id, process.arrivalTime, process.timeInMemory, process.memoryArray, startMem, endMem)
            
            # Adjust the block if there's remaining space
            remainingMemStart = endMem + 1
            if remainingMemStart < remainingMemEnd:
                remainingBlock = Process(None, None, None, None, remainingMemStart, remainingMemEnd)
                self.memoryMap.insert(bestFitIndex + 1, remainingBlock)

            return 0  # Allocation successful

        return -1  # Not enough memory or suitable block not found

    def allocateWorstFit(self, process):
        worstFitIndex = -1
        worstFitSize = -1

        for i, block in enumerate(self.memoryMap):
            if block.id is None and (block.endMemory - block.startMemory) >= process.totalMemory - 1:
                blockSize = block.endMemory - block.startMemory + 1
                if blockSize > worstFitSize:
                    worstFitIndex = i
                    worstFitSize = blockSize

        if worstFitIndex != -1:
            # Allocate memory
            startMem = self.memoryMap[worstFitIndex].startMemory
            endMem = startMem + process.totalMemory - 1
            remainingMemEnd = self.memoryMap[worstFitIndex].endMemory
            self.memoryMap[worstFitIndex] = Process(process.id, process.arrivalTime, process.timeInMemory, process.memoryArray, startMem, endMem)
            
            # Adjust the block if there's remaining space
            remainingMemStart = endMem + 1
            if remainingMemStart < remainingMemEnd:
                remainingBlock = Process(None, None, None, None, remainingMemStart, remainingMemEnd)
                self.memoryMap.insert(worstFitIndex + 1, remainingBlock)

            return 0  # Allocation successful

        return -1  # Not enough memory or suitable block not found

    def deallocate(self, processToDeallocate):
        # Find the process to deallocate
        processIndex = -1

        for i, process in enumerate(self.memoryMap):
            if process.id == processToDeallocate.id:
                processIndex = i
                break
        
        # If the process is not found, return
        if processIndex == -1:
            print(f"Process {processToDeallocate.id} not found.", end = "\n\t")
            return
        
        self.memoryMap[processIndex].id = None
        self.collapseHoles()

    
    def collapseHoles(self):
        consecutiveHoles = 0
        for i in range (len(self.memoryMap)):
            if self.memoryMap[i].id is None:
                firstHole = i

                while(i < len(self.memoryMap) and self.memoryMap[i].id == None):
                    consecutiveHoles += 1
                    i += 1
                i -= 1
                start = self.memoryMap[firstHole].startMemory
                end = self.memoryMap[i].endMemory
                while i > firstHole:
                    self.memoryMap.pop(i)
                    i -= 1
                self.memoryMap[i] = Process(None, None, None, None, start, end)
            if i == len(self.memoryMap) - 1:
                return
                

    def printMemoryMap(self):
        print("Memory Map:", end = "\n\t")
        for process in self.memoryMap:
            if process.id is not None:
                print(f"\t{process.startMemory}-{process.endMemory}: Process {process.id}", end = "\n\t")
            else:
                print(f"\t{process.startMemory}-{process.endMemory}: Hole", end = "\n\t")