from __future__ import annotations

import mmap
import os
import struct
from typing import Sequence, TypedDict

# Pre-compiled struct formats for hot-path reads
_U16 = struct.Struct(">H")
_U32 = struct.Struct(">I")
_F32 = struct.Struct(">f")
_FFF = struct.Struct(">fff")
_FFFF = struct.Struct(">ffff")

Vec3 = tuple[float, float, float]
Quat = tuple[float, float, float, float]


class RaceInfoDict(TypedDict):
    StageID: int
    FrameCount: int
    PlayerCount: int
    CourseID: int
    EngineClass: int


class PlayerInfoDict(TypedDict):
    PlayerID: int
    LocalPlayerNum: int
    RealControllerID: int
    KartID: int
    CharacterID: int
    CurrentRaceCompletion: float
    MaxRaceCompletion: float
    FirstKcpLapCompletion: float
    NextCheckpointLapCompletion: float
    NextCheckpointLapCompletionMax: float
    CurrentLap: int
    MaxLap: int
    currentKCP: int
    maxKCP: int
    StateBit: int
    SoftSpeedLimit: float
    HardSpeedLimit: float
    Position: Vec3
    Velocity: Vec3
    InternalVelocity: Vec3
    ExternalVelocity: Vec3
    AngularVelocity: Vec3
    Acceleration: Vec3
    MainRotation: Quat
    Speed: float
    AccelerationKartMove: float
    DriftState: int
    MiniturboCharge: int
    SMiniturboCharge: int
    OffroadInvincibilityTimer: int
    WheelieFrameCount: int
    WheelieCooldownCount: int
    LeanRot: float
    BitField0: int
    BitField1: int
    BitField2: int
    BitField3: int
    SurfaceFlag: int
    Hop: Vec3
    MTBoostTimer: int
    AllMTCharge: int
    MushroomBoostTimer: int
    TrickableTimer: int
    TrickCooldown: int
    AirtimeCount: int
    RacePosition: int
    FloorCollisionCount: int
    RespawnTimer: int
    WallCollideFlag: int
    Item: int
    ItemNum: int
    PassiveItem: int
    PassiveItemNum: int
    StarTimer: int
    ShockTimer: int
    BlooperInkTimer: int
    BlooperStateFlag: int
    CrushTimer: int
    MegaTimer: int
    startBoostCharge: float
    startBoostIdx: int


class ObservationDict(TypedDict):
    RACE_INFO: RaceInfoDict
    PLAYER_INFO: list[PlayerInfoDict]


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
        return _U16.unpack_from(self.mv, off)[0]

    def read_u32(self, addr: int) -> int:
        off = self.get_offset(addr)
        return _U32.unpack_from(self.mv, off)[0]

    def read_f32(self, addr: int) -> float:
        off = self.get_offset(addr)
        return _F32.unpack_from(self.mv, off)[0]

    def read_fff(self, addr: int) -> Vec3:
        off = self.get_offset(addr)
        x, y, z = _FFF.unpack_from(self.mv, off)
        return (x, y, z)

    def read_ffff(self, addr: int) -> Quat:
        off = self.get_offset(addr)
        x, y, z, w = _FFFF.unpack_from(self.mv, off)
        return (x, y, z, w)

    def read_ptr(self, addr: int) -> int:
        return self.read_u32(addr)

    def resolve_chain(self, base_addr: int, offsets: Sequence[int]) -> int:
        assert len(offsets) > 0
        curr = self.read_ptr(base_addr)
        for offset in offsets[:-1]:
            curr = self.read_ptr(curr + offset)
        return curr + offsets[-1]

    def read_obs(self) -> ObservationDict:
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

        race_info: RaceInfoDict = {
            "StageID": read_u32(race_mgr + 0x28),
            "FrameCount": read_u32(race_mgr + 0x20),
            "PlayerCount": read_u8(0x809C38B8),
            "CourseID": read_u32(player_setup + 0xB68),
            "EngineClass": read_u32(player_setup + 0xB6C),
        }

        player_infos: list[PlayerInfoDict] = []
        item_node = item_holder

        for n in range(4):
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

            p_info: PlayerInfoDict = {
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
                "Position": read_fff(kart_phys + 0x18),
                "Velocity": read_fff(kart_dyn + 0xD4),
                "InternalVelocity": read_fff(kart_dyn + 0x14C),
                "ExternalVelocity": read_fff(kart_dyn + 0x74),
                "AngularVelocity": read_fff(kart_dyn + 0xA4),
                "Acceleration": read_fff(kart_dyn + 0x80),
                "MainRotation": read_ffff(kart_dyn + 0xF0),
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
                "Hop": read_fff(kart_move + 0x228),
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
            player_infos.append(p_info)

            # Walk item linked list to next node
            if n < 3:
                item_node = read_ptr(item_node + 0xBC)

        return {"RACE_INFO": race_info, "PLAYER_INFO": player_infos}
