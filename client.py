import socket

HOST = "your.pi.twingate.ip"  # Your Pi's Twingate IP/hostname
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello from Windows!")
