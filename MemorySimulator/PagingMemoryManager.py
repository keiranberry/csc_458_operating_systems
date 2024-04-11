from Process import Process
import math

class PagingMemoryManager: 
    def __init__(self, totalMemory, frameSize): 
        self.frameSize = int(frameSize)
        self.totalMemory = int(totalMemory)
        self.freeFrames = int(int(totalMemory) / self.frameSize)
        emptyFrame = Process(None, None, None, None)
        self.memoryMap = [emptyFrame for _ in range(self.freeFrames)]

    def allocate(self, process):
        # we will be using full frames 
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
        # set all frames to empty processes
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
            # printing filled frames, keeping track of frame number also
            if frame.id is not None:
                frameCounts[frame.id] = frameCounts.get(frame.id, 0) + 1
                print(f"\t{startAddress}-{endAddress}: Process {frame.id}, Page {frameCounts[frame.id]}", end = "\n\t")
                startAddress += self.frameSize
                endAddress += self.frameSize
                i += 1
            else:
                # printing free frames (want to collapse consecutive ones)
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
