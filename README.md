# Pi Reverse Shell

A Python-based reverse shell that uses a Raspberry Pi as a relay and [Twingate](https://www.twingate.com/) for secure remote access — no port forwarding required.

## How It Works

```
[Windows PC] ---outbound TCP---> [Raspberry Pi] <--- operator types commands
```

1. The **Windows client** initiates an outbound TCP connection to the Pi and waits for commands.
2. The **Pi server** listens for the incoming connection and gives the operator an interactive prompt.
3. Commands typed into the Pi terminal are sent to Windows, executed, and the output is streamed back in real time.

Because the Windows machine makes the outbound connection, no inbound firewall rules or port forwarding are needed on the Windows side. Twingate provides secure, authenticated access to the Pi from anywhere on the internet.

## Features

- Persistent auto-reconnect — the client retries every 2 seconds if the connection drops
- Stateful directory tracking — `cd` commands persist across subsequent commands
- `cls` support — clears the terminal on both ends
- Threaded output — command output is received asynchronously so the server stays responsive
- Combined `stdout` + `stderr` output returned for every command

---

## Full Setup Walkthrough

### Prerequisites

- Python 3.x on both the **build machine** (Windows) and the **Raspberry Pi**
- [PyInstaller](https://pyinstaller.org/) — installed automatically by `build_client.py` if missing
- Twingate installed and configured on the Pi (or use a local IP for LAN-only use)

---

### Step 1 — Gather info from the Raspberry Pi

Before building anything, run the info script on your Pi so you have the values you'll need on hand:

```bash
bash pi_info.sh
```

> On first run, make it executable first: `chmod +x pi_info.sh`

This will show you:

| Field | Where you'll use it |
|-------|---------------------|
| **Local IP** (`eth0` / `wlan0`) | As `PI_HOST` in `build_client.py` if staying on your LAN |
| **Twingate IP** (`100.x.x.x`) | As `PI_HOST` in `build_client.py` for remote access over the internet |
| **Python version** | Confirms Python 3 is ready to run `server.py` |
| **Listening ports** | Helps you pick a free port number for the server |
| **UFW status** | Tells you if you need to open a port in the firewall |

If UFW is active and blocking connections, allow your chosen port on the Pi before continuing:

```bash
sudo ufw allow 6000/tcp
```

---

### Step 2 — Gather info from the Windows machine

Run the info script on the target Windows machine:

```bat
windows_info.bat
```

This will show you:

| Field | Where you'll use it |
|-------|---------------------|
| **Hostname / Username** | Useful to identify the machine once connected |
| **Local IP** | Use this as `PI_HOST` in `build_client.py` if the Pi and PC are on the same LAN and you want to test locally first |
| **Python path** | Confirms Python is available if you want to run the client as a `.py` instead of an `.exe` |
| **Startup folder path** | Where to drop the `.exe` for it to run on login (alternative to Task Scheduler) |

Keep this window open while you run the builders — you'll reference these values.

---

### Step 3 — Build the Pi server

On your build machine, run:

```bash
python build_server.py
```

You will be prompted for:

| Prompt | What to enter |
|--------|---------------|
| **Port** | Any free port you identified in Step 1 (default: `6000`) |

**Output:** `output/server.py`

Transfer `output/server.py` to your Raspberry Pi (via `scp`, USB, or any method you prefer).

---

### Step 4 — Build the Windows client

```bash
python build_client.py
```

You will be prompted for:

| Prompt | What to enter |
|--------|---------------|
| **Pi host** | The IP or Twingate hostname from Step 1 (e.g. `192.168.1.10` or `100.x.x.x`) |
| **Port** | Must match the port chosen in Step 3 |
| **EXE name** | A name for the output executable (default: `client`) |

**Output:**
- `output/<name>.exe` — the Windows client, ready to deploy
- `output/setup_info.bat` — a reference sheet with all your config details and deployment steps

> PyInstaller compiles the `.exe` with the IP and port baked in. If PyInstaller isn't installed, `build_client.py` will install it automatically.

---

### Step 5 — Deploy and connect

**On the Raspberry Pi**, start the server:

```bash
python server.py
```

You should see:
```
[+] Waiting for Windows client on 0.0.0.0:6000 ...
```

**On the Windows machine**, copy `client.exe` to the target machine and run it. It runs silently with no visible window and automatically connects to the Pi.

Once connected, the Pi terminal will show:
```
[+] Windows client connected: ('x.x.x.x', xxxxx)
```

---

### Step 6 — Run commands

Type any Windows shell command into the Pi terminal and press Enter:

```
C:\Users\user> whoami
desktop-abc\user

C:\Users\user> cd Documents
C:\Users\user\Documents>

C:\Users\user\Documents> dir
 Volume in drive C has no label.
 ...
```

Press `Ctrl+C` on the Pi to close the connection.

---

## Autostart on Windows (Optional)

To have the client connect automatically whenever the machine is logged into, add it to Windows Task Scheduler:

1. Open **Task Scheduler** (run `taskschd.msc`)
2. Click **Create Task**
3. **Triggers** tab → New → *At log on*
4. **Actions** tab → New → *Start a program* → browse to `client.exe`
5. Optionally check *Run whether user is logged on or not*

Alternatively, drop `client.exe` into the startup folder path shown by `windows_info.bat`.

---

## Remote Access via Twingate

To reach the Pi from anywhere on the internet without exposing a public port:

1. Install the [Twingate connector](https://www.twingate.com/docs/raspberry-pi) on the Raspberry Pi
2. Add the Pi as a **Resource** in your Twingate Admin Console
3. Connect Twingate on the Pi — `pi_info.sh` will then show a `100.x.x.x` Twingate IP
4. Use that IP as `PI_HOST` when running `build_client.py`
5. Connect Twingate on your operator machine before running `server.py`

---

## Reference Sheet

After building, run `output/setup_info.bat` on any machine for a quick reminder of your config and deployment steps.

---

## Project Structure

```
PiReverseShell/
├── build_server.py     # Generates server.py for the Pi
├── build_client.py     # Generates client.exe and setup_info.bat for Windows
├── pi_info.sh          # Run on the Pi to gather IP, port, and Python info
├── windows_info.bat    # Run on the Windows machine to gather setup info
└── output/             # Created automatically when builders are run
    ├── server.py           # Deploy to Raspberry Pi
    ├── client.exe          # Deploy to Windows machine
    └── setup_info.bat      # Quick-reference sheet for your build config
```

> **Note:** This tool is intended for use on machines you own and control.
