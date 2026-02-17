from kart_env import KartEnv
import time

print("--- [1] 환경 생성을 시작합니다 ---")

env = KartEnv(env_id=7777) 

print("--- [2] 환경 생성 완료! 리셋합니다 ---")
obs, _ = env.reset()

print("--- [3] 리셋 완료! 10번 연속 스텝 테스트 ---")

for i in range(10):
    action = 0 
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {i+1}: Action={action} 성공!")
    time.sleep(0.1) 

print("--- [4] 테스트 완료! 환경을 안전하게 종료합니다 ---")

env.close()