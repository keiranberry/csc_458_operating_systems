from Process import Process

class SegmentationMemoryManager:
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
        memoryMapCopy = self.memoryMap.copy()
        # allocate first fit for each in a row like a mini input queue
        for i, segment in enumerate(process.memoryArray):
            if self.allocateFirstFitSegment(Process(process.id, process.arrivalTime, process.timeInMemory, [segment], segment = i)) == -1:
                self.memoryMap = memoryMapCopy
                return -1
        return 0

    
    def allocateFirstFitSegment(self, segment):
        for i, block in enumerate(self.memoryMap):
            if block.id is None and (block.endMemory - block.startMemory) >= segment.totalMemory - 1:
                # allocate memory at first fit
                startMem = block.startMemory
                endMem = startMem + segment.totalMemory - 1
                self.memoryMap[i] = Process(segment.id, segment.arrivalTime, segment.timeInMemory, segment.memoryArray, startMem, endMem, segment.segmentNumber)
                
                # fill remaining memory with an empty process
                remainingMemStart = endMem + 1
                remainingMemEnd = block.endMemory
                if remainingMemStart < remainingMemEnd:
                    remainingBlock = Process(None, None, None, None, remainingMemStart, remainingMemEnd)
                    self.memoryMap.insert(i + 1, remainingBlock)

                return 0  # success
        return -1  # failure

    def allocateBestFit(self, process):
        memoryMapCopy = self.memoryMap.copy()
        # allocate best fit for each segment 
        for i, segment in enumerate(process.memoryArray):
            if self.allocateBestFitSegment(Process(process.id, process.arrivalTime, process.timeInMemory, [segment], segment = i)) == -1:
                self.memoryMap = memoryMapCopy
                return -1
        return 0
    
    def allocateBestFitSegment(self, segment):
        bestFitIndex = -1
        bestFitSize = float('inf')

        for i, block in enumerate(self.memoryMap):
            # keep track of best fit location
            if block.id is None and (block.endMemory - block.startMemory) >= segment.totalMemory - 1:
                blockSize = block.endMemory - block.startMemory + 1
                if blockSize < bestFitSize:
                    bestFitIndex = i
                    bestFitSize = blockSize

        if bestFitIndex != -1:
            # allocate memory for segment
            startMem = self.memoryMap[bestFitIndex].startMemory
            endMem = startMem + segment.totalMemory - 1
            remainingMemEnd = self.memoryMap[bestFitIndex].endMemory
            self.memoryMap[bestFitIndex] = Process(segment.id, segment.arrivalTime, segment.timeInMemory, segment.memoryArray, startMem, endMem, segment.segmentNumber)
            
            # add remaining space back in if needed
            remainingMemStart = endMem + 1
            if remainingMemStart < remainingMemEnd:
                remainingBlock = Process(None, None, None, None, remainingMemStart, remainingMemEnd)
                self.memoryMap.insert(bestFitIndex + 1, remainingBlock)

            return 0  # success

        return -1  # failure

    def allocateWorstFit(self, process):
        memoryMapCopy = self.memoryMap.copy()
        # allocate worst fit for each in a row
        for i, segment in enumerate(process.memoryArray):
            if self.allocateWorstFitSegment(Process(process.id, process.arrivalTime, process.timeInMemory, [segment], segment = i)) == -1:
                self.memoryMap = memoryMapCopy
                return -1
        return 0

    def allocateWorstFitSegment(self, segment):
        worstFitIndex = -1
        worstFitSize = -1

        for i, block in enumerate(self.memoryMap):
            # keep track of worst fit location
            if block.id is None and (block.endMemory - block.startMemory) >= segment.totalMemory - 1:
                blockSize = block.endMemory - block.startMemory + 1
                if blockSize >= worstFitSize:
                    worstFitIndex = i
                    worstFitSize = blockSize

        if worstFitIndex != -1:
            # allocate memory for segment
            startMem = self.memoryMap[worstFitIndex].startMemory
            endMem = startMem + segment.totalMemory - 1
            remainingMemEnd = self.memoryMap[worstFitIndex].endMemory
            self.memoryMap[worstFitIndex] = Process(segment.id, segment.arrivalTime, segment.timeInMemory, segment.memoryArray, startMem, endMem, segment.segmentNumber)
            
            # add back remaining empty space
            remainingMemStart = endMem + 1
            if remainingMemStart < remainingMemEnd:
                remainingBlock = Process(None, None, None, None, remainingMemStart, remainingMemEnd)
                self.memoryMap.insert(worstFitIndex + 1, remainingBlock)

            return 0  # success

        return -1  # failure

    def deallocate(self, processToDeallocate):
        processesRemoved = 0  # keep track of removed processes
        i = 0 # we need to remove all of them this time not just the first

        while i < len(self.memoryMap):
            # remove process if id matches
            if self.memoryMap[i].id == processToDeallocate.id:
                self.memoryMap[i].id = None
                processesRemoved += 1
            i += 1 

        # if it couldnt be found its an error
        if processesRemoved == 0:
            print(f"Process {processToDeallocate.id} not found.", end="\n\t")

        # collapse empty spots
        self.collapseHoles()


    
    def collapseHoles(self):
        # same collapse holes function as i wrote for contiguous
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
                print(f"\t{process.startMemory}-{process.endMemory}: Process {process.id}, Segment {process.segmentNumber}", end = "\n\t")
            else:
                print(f"\t{process.startMemory}-{process.endMemory}: Hole", end = "\n\t")

