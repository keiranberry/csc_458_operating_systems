from queue import PriorityQueue
from process import Process
from memoryManager import PagingMemoryManager
from memoryManager import ContiguousMemoryManager
import math

class DiscreteEventSimulation:
    def __init__(self, total_memory, frame_size):
        self.clock = 0
        self.event_queue = PriorityQueue()
        self.memory_manager = PagingMemoryManager(total_memory, frame_size)

    def schedule_event(self, event):
        self.event_queue.put(event)

    def run_simulation(self, input_queue):
        while not self.event_queue.empty():
            event = self.event_queue.get()
            if self.clock < event.time:
                self.clock = event.time
            if event.event_type == 'PROCESS_ARRIVAL':
                self.process_arrival(event.process)
            elif event.event_type == 'PROCESS_COMPLETION':
                self.process_completion(event.process)
            elif event.event_type == 'MEMORY_DEALLOCATION':
                self.memory_deallocation(event.process)

    def process_arrival(self, process):
        frames_allocated = self.memory_manager.allocate(process)
        if frames_allocated == -1:
            print(f"Not enough memory to allocate for Process {process.id} at time {self.clock}")
        else:
            print(f"Process {process.id} allocated {frames_allocated} frames at time {self.clock}")

        # Schedule process completion event
        completion_time = self.clock + process.timeInMemory
        self.schedule_event(Event(completion_time, 'PROCESS_COMPLETION', process))

    def process_completion(self, process):
        # Deallocate memory occupied by the completed process
        self.memory_manager.deallocate(process)
        print(f"Process {process.id} completed at time {self.clock}")


    def memory_deallocation(self, process):
        self.memory_manager.deallocate(process)
        print(f"Memory deallocated for Process {process.id} at time {self.clock}")


class Event:
    def __init__(self, time, event_type, process=None):
        self.time = time
        self.event_type = event_type
        self.process = process

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time

    def __eq__(self, other):
        return self.time == other.time
