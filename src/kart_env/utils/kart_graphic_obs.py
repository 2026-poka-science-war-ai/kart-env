import numpy as np
from multiprocessing import shared_memory, resource_tracker
import struct
from typing import List
from PIL import Image


class KartGraphicObs:
    def __init__(self, env_id: int):
        self.shm_name = f"DolphinSharedFrameBuffer_{env_id}"
        self.HEADER_METADATA_SIZE = 40
        self.FRAME_INFO_SIZE = 32
        self.EXPECTED_MAGIC = 0x444C464E
        self.VERSION = 2

        self.shm = shared_memory.SharedMemory(name=self.shm_name)
        resource_tracker.unregister("/" + self.shm.name, "shared_memory")

        assert self.shm.buf is not None
        initial_metadata = struct.unpack(
            "IIIIQQII", self.shm.buf[: self.HEADER_METADATA_SIZE]
        )
        magic, version, num_frames, _, _, _, _, _ = initial_metadata

        assert magic == self.EXPECTED_MAGIC and version == self.VERSION

        self.num_frames = num_frames

    def get(self) -> List[np.ndarray]:
        assert self.shm.buf is not None
        buf = self.shm.buf

        ready = struct.unpack("I", buf[12:16])[0]
        while ready == 0:
            ready = struct.unpack("I", buf[12:16])[0]

        images = []
        for i in range(self.num_frames):
            offset = self.HEADER_METADATA_SIZE + (i * self.FRAME_INFO_SIZE)
            f_info = struct.unpack(
                "IIIIIIII", buf[offset : offset + self.FRAME_INFO_SIZE]
            )
            width, height, stride, fmt, data_offset, data_size, _, _ = f_info

            img_view = np.ndarray(
                shape=(height, width, 4),
                dtype=np.uint8,
                buffer=buf[data_offset : data_offset + data_size],
                strides=(stride, 4, 1),
            )
            images.append(img_view)

        return images

    def close(self):
        self.shm.close()


def save_graphic_obs(observation: List[np.ndarray]):
    for i, obs_array in enumerate(observation, start=1):
        img = Image.fromarray(obs_array)
        filename = f"image_{i}.png"
        img.save(filename)
