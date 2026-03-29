# Pi Reverse Shell

A Python-based reverse shell that uses a Raspberry Pi as a relay and [Twingate](https://www.twingate.com/) for secure remote access — no port forwarding required.

## How It Works

```
[Windows PC] ---outbound TCP---> [Raspberry Pi] <--- operator types commands
```

1. `client.py` runs on the **Windows machine**. It initiates an outbound TCP connection to the Pi on port `6000` and waits for commands.
2. `server.py` runs on the **Raspberry Pi**. It listens for the incoming connection and gives the operator an interactive prompt.
3. The operator types commands into the server terminal. They are sent to the Windows client, executed via `subprocess`, and the output is streamed back in real time.

Because the Windows machine makes the outbound connection, no inbound firewall rules or port forwarding are needed on the Windows side. Twingate provides secure, authenticated access to the Pi from anywhere on the internet.

## Features

- Persistent auto-reconnect — the client retries every 2 seconds if the connection drops
- Stateful directory tracking — `cd` commands persist across subsequent commands
- `cls` support — clears the terminal on both ends
- Threaded output — command output is received asynchronously so the server stays responsive
- Combined `stdout` + `stderr` output returned for every command

## Setup

### Prerequisites

- Python 3.x on both the Pi and the Windows machine
- Twingate installed and configured on the Pi (or use a local IP for LAN-only use)

### Raspberry Pi (server)

```bash
python server.py
```

The server will print `[+] Waiting for Windows client on 0.0.0.0:6000 ...` and block until the client connects.

### Windows Machine (client)

Edit `client.py` and set `PI_HOST` to your Pi's Twingate IP or hostname:

```python
PI_HOST = "your.pi.twingate.ip"
```

Then run:

```bash
python client.py
```

Once connected, the server terminal will show `[+] Windows client connected` and you can begin typing commands.

## Usage

Type any Windows shell command into the server terminal and press Enter:

```
C:\Users\user> whoami
desktop-abc\user

C:\Users\user> cd Documents
C:\Users\user\Documents>

C:\Users\user\Documents> dir
 Volume in drive C has no label.
 ...
```

Press `Ctrl+C` on the server to close the connection.

## Notes

- `client.py` is intended to run as a background task on startup (e.g. via Task Scheduler) on the target Windows machine.
- All commands run with the same privileges as the user who launched `client.py`.
- This tool is intended for use on machines you own and control.
