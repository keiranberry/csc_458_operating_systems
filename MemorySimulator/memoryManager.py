from process import Process
import math

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


class PagingMemoryManager: 
    def __init__(self, totalMemory, frameSize): 
        self.frameSize = int(frameSize)
        self.totalMemory = int(totalMemory)
        self.freeFrames = int(int(totalMemory) / self.frameSize)
        emptyFrame = Process(None, None, None, None)
        self.memoryMap = [emptyFrame for _ in range(self.freeFrames)]

    def allocate(self, process):
        framesNeeded = math.ceil(process.totalMemory / self.frameSize)
        if framesNeeded > self.freeFrames:  
            return -1
        else:
            framesAllocated = 0
            for i, frame in enumerate(self.memoryMap):
                if framesAllocated == framesNeeded:
                    break
                if frame.id is None:
                    self.memoryMap[i] = process
                    framesAllocated += 1
            self.freeFrames -= framesAllocated
            return framesAllocated
        
        
    def deallocate(self, process):
        for i, frame in enumerate(self.memoryMap):
            if frame.id == process.id:
                self.memoryMap[i] = Process(None, None, None, None)
                self.freeFrames += 1

    def printMemoryMap(self):
        print("Memory Map:", end = "\n\t")
        startAddress = 0
        endAddress = self.frameSize - 1
        frameCounts = {}

        i = 0
        while i < len(self.memoryMap):
            if startAddress > self.totalMemory - 1:
                        break
            frame = self.memoryMap[i]
            if frame.id is not None:
                frameCounts[frame.id] = frameCounts.get(frame.id, 0) + 1
                print(f"\t{startAddress}-{endAddress}: Process {frame.id}, Page {frameCounts[frame.id]}", end = "\n\t")
                startAddress += self.frameSize
                endAddress += self.frameSize
                i += 1
            else:
                startFreeAddress = startAddress
                endAddress = startAddress - 1
                while i < len(self.memoryMap) and self.memoryMap[i].id is None:
                    if endAddress > self.totalMemory - 1:
                        endAddress = self.totalMemory - 1
                        break
                    i += 1
                    endAddress += self.frameSize
                print(f"\t{startFreeAddress}-{endAddress}: Free Frame(s)", end = "\n\t")
                startAddress = endAddress + 1
                endAddress = startAddress + self.frameSize - 1

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

