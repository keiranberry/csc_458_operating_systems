class Process:
    def __init__(self, process_id, arrival_time, time_in_memory, memory_array):
        self.id = process_id
        self.arrivalTime = arrival_time
        self.timeInMemory = time_in_memory
        self.memoryArray = memory_array
        self.totalMemory = sum(memory_array)

    def __str__(self):
        return f"Process {self.id}: Arrival Time - {self.arrivalTime}, Time in Memory - {self.timeInMemory}, Memory Requirement - {self.totalMemory}, Memory Array - {self.memoryArray}"