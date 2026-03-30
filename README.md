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

## Prerequisites

| Machine | Requirement |
|---------|-------------|
| **Raspberry Pi** | Python 3.x |
| **Windows PC** | Python 3.x |

---

## Installation

Choose the method that fits your setup:

---

<details>
<summary><strong>Method A — Build everything on the Pi (easiest)</strong></summary>

> Best if you have direct access to the Pi and just want to get going quickly.
> Both builder scripts are run on the Pi — you only need to transfer one file to Windows at the end.

<br>

**Step 1 — Run both builders on the Pi**

```bash
python build_client.py
python build_server.py
```

`build_client.py` will auto-detect the Pi's IP — just press Enter to confirm it. Use the same port for both (default: `6000`).

| Builder | What to enter |
|---------|---------------|
| `build_client.py` | IP (auto-filled), port, script name, monitor label |
| `build_server.py` | Port (must match above) |

**Step 2 — Transfer `client.py` to the Windows machine**

```bash
# Run from the Windows machine:
scp pi@<pi-ip>:~/PiReverseShell/output/client.py .
```

Or use a USB drive, shared folder, or any other method.

**Step 3 — Open the port on the Pi (if UFW is active)**

```bash
sudo ufw allow 6000/tcp
```

**Step 4 — Start the server on the Pi**

```bash
python output/server.py
```

You should see:
```
[+] Waiting for Windows client on 0.0.0.0:6000 ...
```

**Step 5 — Run the client on Windows**

```bat
python client.py
```

A terminal window opens with the red monitoring notice. Press Enter to connect, or type `delete` to opt out.

Once connected the Pi terminal shows:
```
[+] Windows client connected: ('x.x.x.x', xxxxx)
```

Type any Windows shell command into the Pi terminal and press Enter. Press `Ctrl+C` on the Pi to close the connection.

</details>

---

<details>
<summary><strong>Method B — Build on each machine separately</strong></summary>

> Best if you want to keep the project files only on the device they belong to.
> Run `build_server.py` on the Pi and `build_client.py` on Windows.

<br>

**Step 1 — Get the Pi's IP (on the Pi)**

Run the info script to find the Pi's IP address:

```bash
bash pi_info.sh
```

> On first run, make it executable first: `chmod +x pi_info.sh`

Note down the values you need:

| Field | What to use it for |
|-------|--------------------|
| **Local IP** (`eth0` / `wlan0`) | Enter as the Pi IP in `build_client.py` for LAN use |
| **Twingate IP** (`100.x.x.x`) | Enter as the Pi IP in `build_client.py` for remote access |
| **Listening ports** | Helps you pick a free port number |
| **UFW status** | Tells you if you need to open a port |

**Step 2 — Build the server on the Pi**

```bash
python build_server.py
```

Enter a free port (default: `6000`). This outputs `output/server.py`.

If UFW is active, open the port:

```bash
sudo ufw allow 6000/tcp
```

**Step 3 — Build the client on Windows**

Copy the project files to your Windows machine, then run:

```bat
python build_client.py
```

| Prompt | What to enter |
|--------|---------------|
| **Pi IP** | The IP you noted from `pi_info.sh` in Step 1 |
| **Port** | Must match the port from Step 2 |
| **Script name** | Name for the output file (default: `client`) |
| **Monitor label** | What to show in the notice, e.g. `HomeNet` or `your school` |

This outputs `output/client.py`.

**Step 4 — Start the server on the Pi**

```bash
python output/server.py
```

You should see:
```
[+] Waiting for Windows client on 0.0.0.0:6000 ...
```

**Step 5 — Run the client on Windows**

```bat
python output/client.py
```

A terminal window opens with the red monitoring notice. Press Enter to connect, or type `delete` to opt out.

Once connected the Pi terminal shows:
```
[+] Windows client connected: ('x.x.x.x', xxxxx)
```

Type any Windows shell command into the Pi terminal and press Enter. Press `Ctrl+C` on the Pi to close the connection.

</details>

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
4. Use that IP when prompted for the Pi's IP in `build_client.py`
5. Connect Twingate on your operator machine before running `server.py`

---

## Reference Sheet

After building, run `output/setup_info.bat` on any machine for a quick reminder of your config and deployment steps.

---

## Project Structure

```
PiReverseShell/
├── build_client.py     # Generates client.py for the Windows machine
├── build_server.py     # Generates server.py for the Raspberry Pi
├── pi_info.sh          # Run on the Pi to get IP, port, and firewall info
├── windows_info.bat    # Run on Windows to get Python path and IP info
└── output/             # Created automatically when builders are run
    ├── client.py           # Deploy to the Windows machine
    ├── server.py           # Deploy to the Raspberry Pi
    └── setup_info.bat      # Quick-reference sheet for your build config
```

> **Note:** This tool is intended for use on machines you own and control, or where you have explicit permission to monitor.
