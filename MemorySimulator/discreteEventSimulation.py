from queue import PriorityQueue
from Process import Process
from PagingMemoryManager import PagingMemoryManager
from ContiguousMemoryManager import ContiguousMemoryManager
from SegmentationMemoryManager import SegmentationMemoryManager

class DiscreteEventSimulation:
    def __init__(self, totalMemory, managerType, extraInfo):
        self.clock = 0
        self.event_queue = PriorityQueue()
        if managerType == "PAG":
            self.memory_manager = PagingMemoryManager(totalMemory, extraInfo)
        elif managerType == "VSP":
            self.memory_manager = ContiguousMemoryManager(totalMemory, extraInfo)
        else:
            self.memory_manager = SegmentationMemoryManager(totalMemory, extraInfo)
        self.inputQueue = []
        self.turnaroundTimes = []

    def schedule_event(self, event):
        self.event_queue.put(event)

    def run_simulation(self):
        print("t = 0: ", end = "")
        while not self.event_queue.empty():
            event = self.event_queue.get()
            
            if self.clock >= 100000:
                print("Maximum time of 100,000 reached")
                exit(1)

            if self.clock < event.time:
                self.allocate_from_queue()

                # put the event back on and get the first event again
                # this covers an edge case where a process finishes before
                # the next time stamp
                self.event_queue.put(event)
                event = self.event_queue.get()
                self.clock = event.time
                print(f"\nt = {self.clock}: ", end = "")
            if event.event_type == 'PROCESS_ARRIVAL':
                self.process_arrival(event.process)
            elif event.event_type == 'PROCESS_COMPLETION':
                self.process_completion(event.process)
            if self.event_queue.empty():
                # make sure we dont have leftover processes waiting
                self.allocate_from_queue()
        print(f"\nAverage Turnaround Time: {self.calculateAverage()}")
        print()

    def process_arrival(self, process):
        print(f"Process {process.id} arrives", end = "\n\t")
        self.inputQueue.append(process)
        self.printQueue()


    def allocate_from_queue(self):
        # make a copy so we can change our input queue and not mess up iterating
        processes = self.inputQueue.copy()

        for process in processes:
            frames_allocated = self.memory_manager.allocate(process)
            if frames_allocated == -1:
                continue
            else:
                print(f"MM moves Process {process.id} to memory", end = "\n\t")
                self.inputQueue.remove(process)
                self.printQueue()
                self.memory_manager.printMemoryMap()

                # schedule event for process completing
                completion_time = self.clock + process.timeInMemory
                self.schedule_event(Event(completion_time, 'PROCESS_COMPLETION', process))

    def process_completion(self, process):
        # deallocate memory from the completed process
        self.turnaroundTimes.append(int(self.clock - process.arrivalTime))
        self.memory_manager.deallocate(process)
        print(f"Process {process.id} completes", end = "\n\t")
        self.memory_manager.printMemoryMap()

    def printQueue(self):
        print("Input Queue:[", end = "")
        for i in range(len(self.inputQueue)):
            if i == len(self.inputQueue) - 1:
                print(self.inputQueue[i].id, end="")
            else:
                print(self.inputQueue[i].id, end = " ")
        print("]", end = "\n\t")
    
    def calculateAverage(self):
        if not self.turnaroundTimes:
            return 0.0
        
        total = sum(self.turnaroundTimes)
        average = total / len(self.turnaroundTimes)
        
        # check if the second decimal place is nonzero
        if round(average * 100) % 10 != 0:
            return round(average, 2)  # if it is, return the average rounded to 2 places
        else:
            return round(average, 1)  # otherwise round it to one place




class Event:
    def __init__(self, time, event_type, process=None):
        self.time = time
        self.event_type = event_type
        self.process = process

    def __lt__(self, other):
        if self.time == other.time:
            if self.event_type != other.event_type:
                event_order = {
                    'PROCESS_ARRIVAL': 0,
                    'PROCESS_ALLOCATION': 1,
                    'PROCESS_COMPLETION': 2
                }
                return event_order[self.event_type] < event_order[other.event_type]
            elif self.process.id != other.process.id:
                return self.process.id < other.process.id
            else:
                return False
        else:
            return self.time < other.time
    
    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.time == other.time and self.event_type == other.event_type and self.process.id == other.process.id

