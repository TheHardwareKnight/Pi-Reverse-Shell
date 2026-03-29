#!/bin/bash

echo ""
echo " ============================================================"
echo "   Pi Reverse Shell | Raspberry Pi Information"
echo " ============================================================"
echo ""
echo " ---- SYSTEM ------------------------------------------------"
echo ""
echo "   Hostname     : $(hostname)"
echo "   User         : $(whoami)"

if [ -f /etc/os-release ]; then
    OS=$(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')
    echo "   OS           : $OS"
fi

echo "   Architecture : $(uname -m)"
echo "   Kernel       : $(uname -r)"

# Pi model if available
if [ -f /proc/device-tree/model ]; then
    MODEL=$(tr -d '\0' < /proc/device-tree/model)
    echo "   Pi Model     : $MODEL"
fi

echo ""
echo " ---- PYTHON ------------------------------------------------"
echo ""

if command -v python3 &>/dev/null; then
    echo "   $(python3 --version)"
    echo "   Path : $(which python3)"
else
    echo "   Python 3 not found."
    echo "   Install with: sudo apt install python3"
fi

echo ""
echo " ---- NETWORK -----------------------------------------------"
echo ""

# Show each interface with its IP
for iface in $(ls /sys/class/net/ | grep -v lo); do
    IP=$(ip -4 addr show "$iface" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    if [ -n "$IP" ]; then
        echo "   $iface : $IP"
    else
        echo "   $iface : (no IPv4 address)"
    fi
done

echo ""
echo " ---- TWINGATE ----------------------------------------------"
echo ""

if command -v twingate &>/dev/null; then
    echo "   Twingate     : installed ($(twingate --version 2>/dev/null || echo 'version unknown'))"
    echo ""
    twingate status 2>/dev/null && echo "" || echo "   Run 'twingate status' to check connection."

    # Try to find Twingate-assigned IP (shows up as a 100.x.x.x CGNAT address)
    TW_IP=$(ip -4 addr 2>/dev/null | grep -oP '(?<=inet\s)100\.\d+\.\d+\.\d+')
    if [ -n "$TW_IP" ]; then
        echo "   Twingate IP  : $TW_IP  <-- use this as PI_HOST in build_client.py"
    else
        echo "   Twingate IP  : not detected (connect Twingate first)"
    fi
else
    echo "   Twingate     : not installed"
    echo "   Install from : https://www.twingate.com/docs/raspberry-pi"
fi

echo ""
echo " ---- OPEN PORTS / FIREWALL --------------------------------"
echo ""

if command -v ss &>/dev/null; then
    LISTENING=$(ss -tlnp 2>/dev/null | awk 'NR>1 {print "   " $4}' | head -10)
    if [ -n "$LISTENING" ]; then
        echo "   Currently listening:"
        echo "$LISTENING"
    else
        echo "   No listening ports found."
    fi
fi

if command -v ufw &>/dev/null; then
    echo ""
    echo "   UFW status:"
    sudo ufw status 2>/dev/null | sed 's/^/   /'
fi

echo ""
echo " ============================================================"
echo ""
