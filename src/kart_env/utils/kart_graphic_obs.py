from __future__ import annotations

import struct
from typing import Final

import numpy as np
from multiprocessing import shared_memory
from numpy.typing import NDArray
from PIL import Image

_HEADER_FMT = struct.Struct("IIIIQQII")
_FRAME_FMT = struct.Struct("IIIIIIII")


class KartGraphicObs:
    NUM_SHM_FRAMES: Final[int] = 7
    HEADER_METADATA_SIZE: Final[int] = _HEADER_FMT.size  # 40
    FRAME_INFO_SIZE: Final[int] = _FRAME_FMT.size  # 32
    TOTAL_HEADER_SIZE: Final[int] = HEADER_METADATA_SIZE + FRAME_INFO_SIZE * NUM_SHM_FRAMES
    EXPECTED_MAGIC: Final[int] = 0x444C464E
    VERSION: Final[int] = 2

    def __init__(self, env_id: int) -> None:
        self.shm_name = f"DolphinSharedFrameBuffer_{env_id}"
        self.shm = shared_memory.SharedMemory(name=self.shm_name)

    def get(self) -> list[NDArray[np.uint8]]:
        assert self.shm.buf is not None
        buf = self.shm.buf

        magic, version, _, ready, *_ = _HEADER_FMT.unpack_from(buf, 0)
        assert magic == self.EXPECTED_MAGIC and version == self.VERSION

        while ready == 0:
            ready = struct.unpack_from("I", buf, 12)[0]

        images: list[NDArray[np.uint8]] = []
        for i in range(self.NUM_SHM_FRAMES):
            offset = self.HEADER_METADATA_SIZE + i * self.FRAME_INFO_SIZE
            width, height, stride, _fmt, data_offset, data_size, _, _ = (
                _FRAME_FMT.unpack_from(buf, offset)
            )

            img_view = np.ndarray(
                shape=(height, width, 4),
                dtype=np.uint8,
                buffer=buf[data_offset : data_offset + data_size],
                strides=(stride, 4, 1),
            )
            images.append(img_view)

        return images

    def close(self) -> None:
        self.shm.close()

    def __del__(self) -> None:
        self.close()


def save_graphic_obs(observation: list[NDArray[np.uint8]]) -> None:
    for i, obs_array in enumerate(observation, start=1):
        img = Image.fromarray(obs_array)
        img.save(f"image_{i}.png")
