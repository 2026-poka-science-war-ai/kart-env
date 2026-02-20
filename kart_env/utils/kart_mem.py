from .dolphin_mem import DolphinMem


class KartMem(DolphinMem):
    def read_obs(self):
        # TODO read actual obs
        return [0.0]
