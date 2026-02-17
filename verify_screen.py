import time
import os
import mss
import mss.tools
from kart_env import KartEnv

def take_screenshot(filename="debug_screen.png"):
    os.environ["DISPLAY"] = ":7777"
    
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        output = sct.shot(mon=0, output=filename)
        print(f"스크린샷 저장 완료: {output}")

print("--- [1] 환경 접속 (채널: 7777) ---")
env = KartEnv(env_id=7777)
env.reset()

print("--- [2] 게임 로딩 대기 (10초) ---")
print("Dolphin이 켜지고 타이틀 화면이 나올 때까지 기다립니다...")
for i in range(10):
    time.sleep(1)
    print(f"{10-i}초...", end="\r")
print("\n--- [3] 화면 캡처 시도 ---")

try:
    take_screenshot("debug_screen.png")
except Exception as e:
    print(f"캡처 실패: {e}")
    print("팁: Xvfb가 켜져 있는지 확인해 보세요.")

print("--- [4] 종료 ---")
env.close()