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
                with open(fd_path, "rb") as f:
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

    def read_u16(self, addr: int) -> int:
        off = self.get_offset(addr)
        return struct.unpack(">H", self.mv[off : off + 2])[0]

    def read_u32(self, addr: int) -> int:
        off = self.get_offset(addr)
        return struct.unpack(">I", self.mv[off : off + 4])[0]

    def read_f32(self, addr: int) -> float:
        off = self.get_offset(addr)
        return struct.unpack(">f", self.mv[off : off + 4])[0]

    def read_fff(self, addr: int) -> List[float]:
        off = self.get_offset(addr)
        return list(struct.unpack(">fff", self.mv[off : off + 12]))

    def read_ffff(self, addr: int) -> List[float]:
        off = self.get_offset(addr)
        return list(struct.unpack(">ffff", self.mv[off : off + 16]))

    def read_ptr(self, addr: int) -> int:
        return self.read_u32(addr)

    def resolve_chain(self, base_addr: int, offsets: List[int]) -> int:
        assert len(offsets) > 0
        curr = self.read_ptr(base_addr)
        for offset in offsets[:-1]:
            curr += offset
            curr = self.read_ptr(curr)
        return curr + offsets[-1]

    def read_obs(self, agent_n: int) -> dict:
        # Bind methods to locals to avoid repeated attribute lookups in hot loop
        read_ptr = self.read_ptr
        read_u8 = self.read_u8
        read_u16 = self.read_u16
        read_u32 = self.read_u32
        read_f32 = self.read_f32
        read_fff = self.read_fff
        read_ffff = self.read_ffff

        # --- Resolve shared root pointers once ---
        race_mgr = read_ptr(0x809BD730)
        player_setup = read_ptr(0x809BD728)
        kart_obj_holder = read_ptr(read_ptr(0x809C18F8) + 0x20)
        item_holder = read_ptr(read_ptr(0x809C3618) + 0x14)
        race_timer_list = read_ptr(race_mgr + 0xC)

        obs = {"RACE_INFO": {}, "PLAYER_INFO": []}

        obs["RACE_INFO"] = {
            "StageID": read_u32(race_mgr + 0x28),
            "FrameCount": read_u32(race_mgr + 0x20),
            "PlayerCount": read_u8(0x809C38B8),
            "CourseID": read_u32(player_setup + 0xB68),
            "EngineClass": read_u32(player_setup + 0xB6C),
        }

        item_node = item_holder

        for n in range(agent_n):
            # Resolve per-player base pointers once
            race_timer_n = read_ptr(race_timer_list + 0x4 * n)

            kart_obj_n = read_ptr(kart_obj_holder + 0x4 * n)
            kart_base = read_ptr(kart_obj_n + 0x0)

            kart_move = read_ptr(kart_base + 0x28)
            kart_state = read_ptr(kart_base + 0x4)
            kart_body = read_ptr(kart_base + 0x8)
            kart_collide = read_ptr(kart_base + 0x18)

            kart_phys = read_ptr(kart_body + 0x90)
            kart_dyn = read_ptr(kart_phys + 0x4)
            kart_phys_col = read_ptr(kart_phys + 0x8)
            kart_col_sub = read_ptr(kart_collide + 0x18)

            kart_drift = read_ptr(kart_obj_n + 0x44)
            kart_trick = read_ptr(kart_move + 0x258)

            p_off = 0xF0 * n

            p_info = {
                "PlayerID": n,
                "LocalPlayerNum": read_u8(player_setup + 0x2D + p_off),
                "RealControllerID": read_u8(player_setup + 0x2E + p_off),
                "KartID": read_u32(player_setup + 0x30 + p_off),
                "CharacterID": read_u32(player_setup + 0x34 + p_off),
                "CurrentRaceCompletion": read_f32(race_timer_n + 0xC),
                "MaxRaceCompletion": read_f32(race_timer_n + 0x10),
                "FirstKcpLapCompletion": read_f32(race_timer_n + 0x14),
                "NextCheckpointLapCompletion": read_f32(race_timer_n + 0x18),
                "NextCheckpointLapCompletionMax": read_f32(race_timer_n + 0x1C),
                "CurrentLap": read_u16(race_timer_n + 0x24),
                "MaxLap": read_u8(race_timer_n + 0x26),
                "currentKCP": read_u8(race_timer_n + 0x27),
                "maxKCP": read_u8(race_timer_n + 0x28),
                "StateBit": read_u8(race_timer_n + 0x3B),
                "SoftSpeedLimit": read_f32(kart_move + 0x18),
                "HardSpeedLimit": read_f32(kart_move + 0x2C),
                "Position": tuple(read_fff(kart_phys + 0x18)),
                "Velocity": tuple(read_fff(kart_dyn + 0xD4)),
                "InternalVelocity": tuple(read_fff(kart_dyn + 0x14C)),
                "ExternalVelocity": tuple(read_fff(kart_dyn + 0x74)),
                "AngularVelocity": tuple(read_fff(kart_dyn + 0xA4)),
                "Acceleration": tuple(read_fff(kart_dyn + 0x80)),
                "MainRotation": tuple(read_ffff(kart_dyn + 0xF0)),
                "Speed": read_f32(kart_move + 0x20),
                "AccelerationKartMove": read_f32(kart_move + 0x30),
                "DriftState": read_u16(kart_drift + 0xFC),
                "MiniturboCharge": read_u16(kart_drift + 0xFE),
                "SMiniturboCharge": read_u16(kart_drift + 0x100),
                "OffroadInvincibilityTimer": read_u16(kart_move + 0x148),
                "WheelieFrameCount": read_u32(kart_move + 0x2A8),
                "WheelieCooldownCount": read_u16(kart_move + 0x2B6),
                "LeanRot": read_f32(kart_move + 0x294),
                "BitField0": read_u32(kart_state + 0x4),
                "BitField1": read_u32(kart_state + 0x8),
                "BitField2": read_u32(kart_state + 0xC),
                "BitField3": read_u32(kart_state + 0x10),
                "SurfaceFlag": read_u32(kart_col_sub + 0x2C),
                "Hop": tuple(read_fff(kart_move + 0x228)),
                "MTBoostTimer": read_u16(kart_move + 0x102),
                "AllMTCharge": read_u16(kart_move + 0x10C),
                "MushroomBoostTimer": read_u16(kart_move + 0x110),
                "TrickableTimer": read_u16(kart_state + 0xA6),
                "TrickCooldown": read_u16(kart_trick + 0x38),
                "AirtimeCount": read_u32(kart_state + 0x1C),
                "RacePosition": read_u8(kart_collide + 0x3C),
                "FloorCollisionCount": read_u16(kart_collide + 0x40),
                "RespawnTimer": read_u16(kart_col_sub + 0x48),
                "WallCollideFlag": read_u32(kart_phys_col + 0x8),
                "Item": read_u32(item_node + 0x8C),
                "ItemNum": read_u32(item_node + 0x90),
                "PassiveItem": read_u32(item_node + 0xCC),
                "PassiveItemNum": read_u32(item_node + 0x104),
                "StarTimer": read_u16(kart_move + 0x18A),
                "ShockTimer": read_u16(kart_move + 0x18C),
                "BlooperInkTimer": read_u16(kart_move + 0x18E),
                "BlooperStateFlag": read_u8(kart_move + 0x190),
                "CrushTimer": read_u16(kart_move + 0x192),
                "MegaTimer": read_u16(kart_move + 0x194),
                "startBoostCharge": read_f32(kart_state + 0x9C),
                "startBoostIdx": read_u32(kart_state + 0xA0),
            }

            obs["PLAYER_INFO"].append(p_info)

            # Walk item linked list to next node
            if n < agent_n - 1:
                item_node = read_ptr(item_node + 0xBC)

        return obs

    def get_stage_id(self) -> int:
        read_ptr = self.read_ptr
        read_u32 = self.read_u32
        return read_u32(read_ptr(0x809BD730) + 0x28)
