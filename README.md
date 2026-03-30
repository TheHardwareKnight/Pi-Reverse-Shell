# Pi Reverse Shell

A Python-based remote monitoring tool that uses a Raspberry Pi as the control server and a Windows PC as the monitored client. Optionally uses [Twingate](https://www.twingate.com/) for secure remote access over the internet — no port forwarding required.

## How It Works

```
[Windows PC] ---outbound TCP---> [Raspberry Pi] <--- operator types commands
```

1. The **Windows client** shows a monitoring notice, then initiates an outbound TCP connection to the Pi and waits for commands.
2. The **Pi server** listens for the incoming connection and gives the operator an interactive prompt.
3. Commands typed into the Pi terminal are sent to Windows, executed, and the output is streamed back in real time.

Because the Windows machine makes the outbound connection, no inbound firewall rules or port forwarding are needed on the Windows side.

## Features

- Visible monitoring notice — the user on the Windows machine always sees a red banner and can opt out by typing `delete`
- Persistent auto-reconnect — the client retries every 2 seconds if the connection drops
- Stateful directory tracking — `cd` commands persist across subsequent commands
- `cls` support — clears the terminal on both ends
- Threaded output — command output is received asynchronously so the server stays responsive
- Combined `stdout` + `stderr` output returned for every command

---

## Full Setup Walkthrough

### Prerequisites

| Machine | Requirement |
|---------|-------------|
| **Raspberry Pi** | Python 3.x |
| **Windows PC** | Python 3.x |

---

### Step 1 — Build the client (run on the Raspberry Pi)

Run this **on your Pi**. It auto-detects the Pi's own IP so you don't have to look it up manually:

```bash
python build_client.py
```

You will be prompted for:

| Prompt | What to enter |
|--------|---------------|
| **Pi IP** | Auto-filled from the Pi's detected IP — just press Enter to confirm, or type a Twingate IP for remote access |
| **Port** | Any free port (default: `6000`) |
| **Script name** | Name for the output file (default: `client`) |
| **Monitor label** | What to show in the notice, e.g. `HomeNet` or `your school` |

**Output:** `output/client.py` — transfer this file to the Windows machine.

> To transfer the file, you can use `scp`, a USB drive, or any file sharing method:
> ```bash
> # Example from the Windows machine (replace the IP and path as needed):
> scp pi@192.168.1.10:~/PiReverseShell/output/client.py .
> ```

---

### Step 2 — Build the server (run on Windows)

Run this **on your Windows machine**:

```bat
python build_server.py
```

You will be prompted for:

| Prompt | What to enter |
|--------|---------------|
| **Port** | Must match the port chosen in Step 1 (default: `6000`) |

**Output:** `output/server.py` — transfer this file to the Raspberry Pi.

> Example transfer to the Pi:
> ```bat
> scp output\server.py pi@192.168.1.10:~/
> ```

---

### Step 3 — Start the server on the Pi

On the Raspberry Pi, run:

```bash
python server.py
```

You should see:
```
[+] Waiting for Windows client on 0.0.0.0:6000 ...
```

If UFW is active on the Pi and blocking connections, allow the port first:

```bash
sudo ufw allow 6000/tcp
```

---

### Step 4 — Run the client on Windows

On the Windows machine, run:

```bat
python client.py
```

A terminal window will appear with a red monitoring notice:

```
============================================================
  MONITORING NOTICE
============================================================

  This device is being monitored by HomeNet.
  Activity on this device may be recorded and reviewed.

  If you DO NOT wish to be monitored, type  delete  and
  press Enter to stop this program.

============================================================
```

- Press **Enter** to continue — the client connects to the Pi.
- Type **`delete`** and press Enter to opt out and exit.

Once connected, the Pi terminal will show:
```
[+] Windows client connected: ('x.x.x.x', xxxxx)
```

---

### Step 5 — Run commands

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

To have the client run automatically when the machine is logged into:

1. Open **Task Scheduler** (run `taskschd.msc`)
2. Click **Create Task**
3. **Triggers** tab → New → *At log on*
4. **Actions** tab → New → *Start a program* → `python` with argument `C:\path\to\client.py`
5. Optionally check *Run whether user is logged on or not*

---

## Remote Access via Twingate

To reach the Pi from anywhere on the internet without exposing a public port:

1. Install the [Twingate connector](https://www.twingate.com/docs/raspberry-pi) on the Raspberry Pi
2. Add the Pi as a **Resource** in your Twingate Admin Console
3. Connect Twingate on the Pi — it will get a `100.x.x.x` IP
4. Use that IP when `build_client.py` asks for the Pi's IP
5. Connect Twingate on your operator machine before running `server.py`

---

## Reference Sheet

After building, run `output/setup_info.bat` on any machine for a quick reminder of your config and deployment steps.

---

## Project Structure

```
PiReverseShell/
├── build_client.py     # Run on the Pi — generates client.py for Windows
├── build_server.py     # Run on Windows — generates server.py for the Pi
├── pi_info.sh          # Optional: run on the Pi to check IPs, ports, firewall
├── windows_info.bat    # Optional: run on Windows to check Python path, IPs
└── output/             # Created automatically when builders are run
    ├── client.py           # Deploy to the Windows machine
    ├── server.py           # Deploy to the Raspberry Pi
    └── setup_info.bat      # Quick-reference sheet for your build config
```

> **Note:** This tool is intended for use on machines you own and control, or where you have explicit permission to monitor.
