from dolphin import event, gui, controller
import socket
import struct

env_id = 0  # TODO support multiple envs
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", PORT))

GC_BUTTONS = ["A", "B", "X", "Y", "Z", "Start", "Up", "Down", "Left", "Right", "L", "R"]
AGENT_STRUCT = "<H6f"
AGENT_SIZE = struct.calcsize(AGENT_STRUCT)

red = 0xFFFF0000
frame_counter = 0
while True:
    data = sock.recv(1024)

    if data.startswith(b"step"):
        payload = data[4:]
        for i in range(4):
            offset = i * AGENT_SIZE
            btn_mask, sx, sy, csx, csy, tl, tr = struct.unpack_from(
                AGENT_STRUCT, payload, offset
            )

            inputs = {
                btn: bool(btn_mask & (1 << j)) for j, btn in enumerate(GC_BUTTONS)
            }
            inputs.update(
                {
                    "StickX": sx,
                    "StickY": sy,
                    "CStickX": csx,
                    "CStickY": csy,
                    "TriggerLeft": tl,
                    "TriggerRight": tr,
                }
            )
            controller.set_gc_buttons(i, inputs)

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
