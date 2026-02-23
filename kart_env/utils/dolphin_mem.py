import mmap
import os
import struct
from typing import List


class DolphinMem:
    def __init__(self, pid: int):
        self.pid = pid

        fd_dir = f"/proc/{self.pid}/fd"
        target_fd = -1
        for fd_num in os.listdir(fd_dir):
            fd_path = os.path.join(fd_dir, fd_num)
            if "/dev/shm/dolphin-emu" in os.readlink(fd_path):
                with open(fd_path, "r") as f:
                    target_fd = f.fileno()
                    # fmt: off
                    self.mm = mmap.mmap(target_fd, 0, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ)
                    # fmt: on
                    self.mv = memoryview(self.mm)
                    return

        raise ValueError()

    def get_offset(self, gcn_addr: int) -> int:
        if 0x80000000 <= gcn_addr < 0x81800000:
            return gcn_addr - 0x80000000
        elif 0x90000000 <= gcn_addr < 0x94000000:
            return (gcn_addr - 0x90000000) + 0x02040000

        raise ValueError()

    def read_u8(self, addr: int) -> int:
        return self.mv[self.get_offset(addr)]

    def read_u32(self, addr: int) -> int:
        off = self.get_offset(addr)
        return struct.unpack(">I", self.mv[off : off + 4])[0]

    def read_f32(self, addr: int) -> float:
        off = self.get_offset(addr)
        return struct.unpack(">f", self.mv[off : off + 4])[0]

    def read_ptr(self, addr: int) -> int:
        return self.read_u32(addr)

    def resolve_chain(self, base_addr: int, offsets: List[int]) -> int:
        curr = self.read_ptr(base_addr)
        for offset in offsets[:-1]:
            curr += offset
            curr = self.read_ptr(curr)
        return curr + offsets[-1]

    def read_obs(self):
        # TODO read actual obs
        return [0.0]
