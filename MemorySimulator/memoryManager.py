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
            return self.allocate_first_fit(process)
        elif self.algorithm == "best-fit":
            return self.allocate_best_fit(process)
        else:
            return self.allocate_worst_fit(process)

    def allocate_first_fit(self, process):
        for i, block in enumerate(self.memoryMap):
            if block.id is None and (block.endMemory - block.startMemory) >= process.totalMemory - 1:
                # Allocate memory
                start_memory = block.startMemory
                end_memory = start_memory + process.totalMemory - 1
                self.memoryMap[i] = Process(process.id, process.arrivalTime, process.timeInMemory, process.memoryArray, start_memory, end_memory)
                
                # Add empty process for the remaining free memory
                remaining_memory_start = end_memory + 1
                remaining_memory_end = block.endMemory
                if remaining_memory_start < remaining_memory_end:
                    remaining_block = Process(None, None, None, None, remaining_memory_start, remaining_memory_end)
                    self.memoryMap.insert(i + 1, remaining_block)

                return 0  # Allocation successful
        return -1  # Not enough memory or suitable block not found

    def allocate_best_fit(self, process):
        best_fit_index = -1
        min_free_memory = float('inf')
        for i, block in enumerate(self.memoryMap):
            if block.id is None and block.totalMemory >= process.totalMemory:
                if block.totalMemory - process.totalMemory < min_free_memory:
                    best_fit_index = i
                    min_free_memory = block.totalMemory - process.totalMemory
        if best_fit_index != -1:
            # Allocate memory
            start_memory = self.memoryMap[best_fit_index].startMemory
            end_memory = start_memory + process.totalMemory
            self.memoryMap[best_fit_index] = Process(process.id, process.arrivalTime, process.timeInMemory, process.memoryArray, start_memory, end_memory)
            return 0  # Allocation successful
        else:
            return -1  # Not enough memory or suitable block not found

    def allocate_worst_fit(self, process):
        worst_fit_index = -1
        max_free_memory = -1
        for i, block in enumerate(self.memoryMap):
            if block.id is None and block.totalMemory >= process.totalMemory:
                if block.totalMemory - process.totalMemory > max_free_memory:
                    worst_fit_index = i
                    max_free_memory = block.totalMemory - process.totalMemory
        if worst_fit_index != -1:
            # Allocate memory
            start_memory = self.memoryMap[worst_fit_index].startMemory
            end_memory = start_memory + process.totalMemory
            self.memoryMap[worst_fit_index] = Process(process.id, process.arrivalTime, process.timeInMemory, process.memoryArray, start_memory, end_memory)
            return 0  # Allocation successful
        else:
            return -1 

    def deallocate(self, processToDeallocate):
        # Find the process to deallocate
        process_index = -1

        for i, process in enumerate(self.memoryMap):
            if process.id == processToDeallocate.id:
                process_index = i
                break
        
        # If the process is not found, return
        if process_index == -1:
            print(f"Process {processToDeallocate.id} not found.")
            return
        
        self.memoryMap[process_index].id = None
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
        print("\tMemory map:")
        for process in self.memoryMap:
            if process.id is not None:
                print(f"\t\t{process.startMemory} - {process.endMemory}: Process {process.id}")
            else:
                print(f"\t\t{process.startMemory} - {process.endMemory}: Hole")


class PagingMemoryManager: 
    def __init__(self, totalMemory, frameSize): 
        self.frameSize = int(frameSize)
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
        print("Memory Map:")
        start_address = 0
        end_address = self.frameSize - 1

        for i, frame in enumerate(self.memoryMap):
            if frame.id is not None:
                print(f"\t{start_address}-{end_address}: Process {frame.id}, Page {i + 1}")
            else:
                print(f"\t{start_address}-{end_address}: Free Frame(s)")
            start_address += self.frameSize
            end_address += self.frameSize

class SegmentationMemoryManager:
    def __init__(self, totalMemory, algorithm):
        self.memorySize = totalMemory
        self.memoryMap = [Process(None, None, None, None, 0, totalMemory)]
        if algorithm == "1":
            self.algorithm = "first-fit"
        elif algorithm == "2":
            self.algorithm = "best-fit"
        else:
            self.algorithm = "worst-fit"

    def allocate(self, process):
        # Implement allocation algorithm based on user's choice
        pass

    def deallocate(self, processId):
        # Find the process to deallocate
        process_index = -1
        for i, process in enumerate(self.memoryMap):
            if process.id == processId:
                process_index = i
                break
        
        # If the process is not found, return
        if process_index == -1:
            print(f"Process with id {processId} not found.")
            return

        # Update start and end memory addresses
        start_memory = self.memoryMap[process_index].startMemory
        end_memory = self.memoryMap[process_index].endMemory

        # Check memory block before the deallocated process
        if process_index > 0 and self.memoryMap[process_index - 1].id is None:
            start_memory = self.memoryMap[process_index - 1].startMemory
            del self.memoryMap[process_index - 1]

        # Check memory block after the deallocated process
        if process_index < len(self.memoryMap) - 1 and self.memoryMap[process_index + 1].id is None:
            end_memory = self.memoryMap[process_index + 1].endMemory
            del self.memoryMap[process_index + 1]

        # Replace deallocated process with new empty process
        self.memoryMap[process_index] = Process(None, None, None, None, start_memory, end_memory)

    def printMemoryMap(self):
        for process in self.memoryMap:
            print(process)