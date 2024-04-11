class Process:
    def __init__(self, process_id, arrival_time, time_in_memory, memory_array, start_memory = -1, end_memory = -1, segment = None):
        self.id = process_id
        self.arrivalTime = arrival_time
        self.timeInMemory = time_in_memory
        self.memoryArray = memory_array
        if self.memoryArray is not None:
            self.totalMemory = sum(memory_array)
        else: self.totalMemory = None
        self.startMemory = int(start_memory)
        self.endMemory = int(end_memory)
        self.segmentNumber = segment

    def __str__(self):
        return f"Process {self.id}: Arrival Time - {self.arrivalTime}, Time in Memory - {self.timeInMemory}, Memory Requirement - {self.totalMemory}, Memory Array - {self.memoryArray}"