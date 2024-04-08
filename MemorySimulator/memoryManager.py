from process import Process
import math

class ContiguousMemoryManager:
    def __init__(self, totalMemory):
        self.memorySize = totalMemory
        self.memoryMap = [Process(None, None, None, None, 0, totalMemory)]

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


class PagingMemoryManager: 
    def __init__(self, totalMemory, frameSize): 
        self.frameSize = frameSize
        self.freeFrames = int(totalMemory / frameSize)
        emptyFrame = Process(None, None, None, None)
        self.memoryMap = [emptyFrame for _ in range(self.freeFrames)]

    def allocate(self, process):
        framesNeeded = math.ceil(process.totalMemory / self.frameSize)
        if framesNeeded < self.freeFrames:  
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
        
