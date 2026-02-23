class DolphinMem:
    MEM1_START = 0x80000000
    MEM1_SIZE = 0x01800000  # 24MB
    MEM2_START = 0x90000000
    MEM2_SIZE = 0x04000000  # 64MB

    def __init__(self, pid: int):
        self.pid = pid
        self.mem1_addr = 0
        self.mem2_addr = 0
        with open(f"/proc/{self.pid}/maps") as f:
            for line in f:
                if "/dev/shm/dolphin" not in line:
                    continue

                parts = line.split()
                start_addr, end_addr = [int(x, 16) for x in parts[0].split("-")]
                offset = int(parts[2], 16)
                size = end_addr - start_addr

                # fmt: off
                if self.mem1_addr == 0 and size == 0x02000000 and offset == 0:
                    self.mem1_addr = start_addr
                elif self.mem2_addr == 0 and size == 0x04000000 and offset == 0x02040000:
                    self.mem2_addr = start_addr
                # fmt: on
                if self.mem1_addr != 0 and self.mem2_addr != 0:
                    break
        assert self.mem1_addr != 0 and self.mem2_addr != 0

    def read_byte(self, address: int) -> bytes:

        if self.MEM1_START <= address < self.MEM1_START + self.MEM1_SIZE:
            host_addr = self.mem1_addr + (address - self.MEM1_START)
        elif self.MEM2_START <= address < self.MEM2_START + self.MEM2_SIZE:
            host_addr = self.mem2_addr + (address - self.MEM2_START)
        else:
            raise ValueError("Address out of range")

        with open(f"/proc/{self.pid}/mem", "rb") as f:
            f.seek(host_addr)
            return f.read(1)

    def write_byte(self, address: int, value: bytes):

        if self.MEM1_START <= address < self.MEM1_START + self.MEM1_SIZE:
            host_addr = self.mem1_addr + (address - self.MEM1_START)
        elif self.MEM2_START <= address < self.MEM2_START + self.MEM2_SIZE:
            host_addr = self.mem2_addr + (address - self.MEM2_START)
        else:
            raise ValueError("Address out of range")

        with open(f"/proc/{self. pid}/mem", "r+b") as f:
            f.seek(host_addr)
            f.write(value)
