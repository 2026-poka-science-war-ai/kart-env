import gym
from gym import spaces
import numpy as np
import time

from utils.kart_instance import KartInstance
from utils.dolphin_pipe import Button, Stick

class KartEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, env_id=0):
        super(KartEnv, self).__init__()
        
        self.kart = KartInstance(env_id=env_id)
        
        self.action_space = spaces.Discrete(5) 

        self.observation_space = spaces.Box(
            low=0, 
            high=10, 
            shape=(1,), 
            dtype=np.int32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.kart.pipe.set(Stick.MAIN, 0.5, 0.5)
        
        observation = np.array([1], dtype=np.int32)
        info = {}
        return observation, info

    def step(self, action):
        """
        AI가 행동(action)을 선택하면 실행되는 함수입니다.
        """
        self.kart.pipe.set(Stick.MAIN, 0.5, 0.5)
        self.kart.pipe.release(Button.A)
        self.kart.pipe.release(Button.B)

        if action == 0:   
            self.kart.pipe.press(Button.A)
            
        elif action == 1: 
            self.kart.pipe.press(Button.B)
            
        elif action == 2: 
            self.kart.pipe.press(Button.A)
            self.kart.pipe.set(Stick.MAIN, 0.0, 0.5) 
            
        elif action == 3: 
            self.kart.pipe.press(Button.A)
            self.kart.pipe.set(Stick.MAIN, 1.0, 0.5) 
            
        elif action == 4: 
            self.kart.click_button(Button.D_LEFT)

        observation = np.array([1], dtype=np.int32)
        reward = 0.0
        terminated = False
        truncated = False
        info = {}

        return observation, reward, terminated, truncated, info

    def close(self):
        if self.kart:
            self.kart.close()