from dolphin import event, gui
import socket

env_id = 0  # TODO support multiple envs
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", PORT))

red = 0xFFFF0000
frame_counter = 0
while True:
    data = sock.recv(1024)
    if data.startswith(b"step"):
        await event.frameadvance()
        sock.sendall(b"step_done")
    elif data.startswith(b"reset"):
        await event.frameadvance()
        sock.sendall(b"reset_done")
    elif data.startswith(b"close"):
        sock.close()
        break
    frame_counter += 1
    # draw on screen
    gui.draw_text((10, 10), red, f"Frame: {frame_counter}")
