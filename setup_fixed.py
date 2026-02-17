import os
import shutil

BASE_DIR = os.path.abspath("./users/fixed_player")
CONFIG_DIR = os.path.join(BASE_DIR, "Config")
PIPES_DIR = os.path.join(BASE_DIR, "Pipes")

print(f"[Setup] 환경 설정을 시작합니다... (경로: {BASE_DIR})")

if os.path.exists(BASE_DIR):
    try:
        shutil.rmtree(BASE_DIR)
        print("[Setup] 기존 폴더 삭제 완료")
    except Exception as e:
        print(f"[Setup] 기존 폴더 삭제 실패 (권한 문제 등): {e}")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(PIPES_DIR, exist_ok=True)
print("[Setup] 새 폴더 구조 생성 완료 (Config, Pipes)")

with open(os.path.join(CONFIG_DIR, "Dolphin.ini"), "w") as f:
    f.write("""
[Analytics]
ID = 11111111111111111111111111111111
PermissionAsked = True
Enabled = False
[Interface]
ConfirmStop = False
UsePanicHandlers = False
OnScreenDisplayMessages = False
[General]
ISOPaths = 1
ISOPath0 = ./
""")

with open(os.path.join(CONFIG_DIR, "GCPadNew.ini"), "w") as f:
    f.write("""
[GCPad1]
Device = Pipe/0/pipe
Buttons/A = Button A
Buttons/B = Button B
Buttons/X = Button X
Buttons/Y = Button Y
Buttons/Z = Button Z
Buttons/Start = Button Start
Main Stick/Up = Axis UP
Main Stick/Down = Axis DOWN
Main Stick/Left = Axis LEFT
Main Stick/Right = Axis RIGHT
Triggers/L = Button L
Triggers/R = Button R
D-Pad/Up = Button D_UP
D-Pad/Down = Button D_DOWN
D-Pad/Left = Button D_LEFT
D-Pad/Right = Button D_RIGHT
""")

print("[Setup] 설정 파일(Dolphin.ini, GCPadNew.ini) 생성 완료!")
print("이제 'python3 test_run.py'를 실행하면 됩니다.")