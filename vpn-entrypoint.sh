#!/bin/bash

set -e

echo "=== ProtonVPN Docker Container ==="

# Check if required environment variables are set
if [ -z "$PROTONVPN_USERNAME" ] || [ -z "$PROTONVPN_PASSWORD" ]; then
    echo "ERROR: PROTONVPN_USERNAME and PROTONVPN_PASSWORD must be set"
    exit 1
fi

if [ -z "$PROTONVPN_SERVER" ]; then
    echo "ERROR: PROTONVPN_SERVER must be set (e.g., nl-free-01.protonvpn.net)"
    exit 1
fi

# Create credentials file
echo "$PROTONVPN_USERNAME" > /vpn/credentials/auth.txt
echo "$PROTONVPN_PASSWORD" >> /vpn/credentials/auth.txt
chmod 600 /vpn/credentials/auth.txt

echo "Credentials file created"

# Download ProtonVPN OpenVPN configuration if not provided
if [ ! -f "/vpn/config/protonvpn.ovpn" ]; then
    echo "Downloading ProtonVPN configuration for $PROTONVPN_SERVER..."
    
    # Set default config URL pattern - users should provide the full config file via volume mount
    # or we use a basic template
    if [ -n "$PROTONVPN_CONFIG_URL" ]; then
        wget -O /vpn/config/protonvpn.ovpn "$PROTONVPN_CONFIG_URL"
    else
        # Create basic OpenVPN configuration template
        cat > /vpn/config/protonvpn.ovpn <<EOF
client
dev tun
proto udp
remote $PROTONVPN_SERVER 1194
remote-random
resolv-retry infinite
nobind
persist-key
persist-tun
cipher AES-256-CBC
auth SHA512
verb 3
auth-user-pass /vpn/credentials/auth.txt
tun-mtu 1500
mssfix 0
reneg-sec 0

# Certificate and keys - must be provided via volume mount or config
# Users should mount their ProtonVPN config file to /vpn/config/protonvpn.ovpn
EOF
        echo "WARNING: Basic configuration template created. Please provide full ProtonVPN OpenVPN config file."
        echo "Mount your .ovpn file to /vpn/config/protonvpn.ovpn"
    fi
fi

# Set up iptables for kill switch
echo "Setting up firewall kill switch..."

# Default policy to DROP all traffic
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow DNS (for VPN setup)
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# Allow VPN connection to ProtonVPN servers
iptables -A OUTPUT -p udp --dport 1194 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 1194 -j ACCEPT
iptables -A OUTPUT -p udp --dport 443 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT

# Allow traffic on TUN interface (VPN tunnel)
iptables -A INPUT -i tun+ -j ACCEPT
iptables -A OUTPUT -o tun+ -j ACCEPT
iptables -A FORWARD -i tun+ -j ACCEPT
iptables -A FORWARD -o tun+ -j ACCEPT

# Allow local network communication (for Docker networking)
iptables -A INPUT -s 172.16.0.0/12 -j ACCEPT
iptables -A OUTPUT -d 172.16.0.0/12 -j ACCEPT

echo "Firewall rules applied - kill switch active"

# Display configuration info
echo "=== VPN Configuration ==="
echo "Server: $PROTONVPN_SERVER"
echo "Username: $PROTONVPN_USERNAME"
echo "========================="

# Start OpenVPN with the configuration
echo "Starting OpenVPN connection..."
exec openvpn --config /vpn/config/protonvpn.ovpn \
    --auth-user-pass /vpn/credentials/auth.txt \
    --script-security 2 \
    --up /vpn/up.sh \
    --down /vpn/down.sh
