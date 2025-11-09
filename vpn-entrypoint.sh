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

# Create credentials file with atomic write
CRED_TEMP=$(mktemp)
echo "$PROTONVPN_USERNAME" > "$CRED_TEMP"
echo "$PROTONVPN_PASSWORD" >> "$CRED_TEMP"
chmod 600 "$CRED_TEMP"
mv "$CRED_TEMP" /vpn/credentials/auth.txt

echo "Credentials file created"

# Download ProtonVPN OpenVPN configuration if not provided
if [ ! -f "/vpn/config/protonvpn.ovpn" ]; then
    echo "Downloading ProtonVPN configuration for $PROTONVPN_SERVER..."
    
    # Set default config URL pattern - users should provide the full config file via volume mount
    # or we use a basic template
    if [ -n "$PROTONVPN_CONFIG_URL" ]; then
        # Validate URL format (basic check for http/https)
        if [[ "$PROTONVPN_CONFIG_URL" =~ ^https?:// ]]; then
            # Download with SSL verification enabled
            wget --secure-protocol=auto --https-only -O /vpn/config/protonvpn.ovpn "$PROTONVPN_CONFIG_URL" || \
            wget -O /vpn/config/protonvpn.ovpn "$PROTONVPN_CONFIG_URL"
        else
            echo "ERROR: PROTONVPN_CONFIG_URL must be a valid http/https URL"
            exit 1
        fi
    else
        # Validate server hostname format (alphanumeric, dots, dashes)
        if [[ ! "$PROTONVPN_SERVER" =~ ^[a-zA-Z0-9.-]+$ ]]; then
            echo "ERROR: PROTONVPN_SERVER contains invalid characters"
            exit 1
        fi
        
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
        echo "======================================================================="
        echo "WARNING: Basic configuration template created WITHOUT certificates!"
        echo "This configuration WILL FAIL to connect to ProtonVPN."
        echo ""
        echo "To fix this, you MUST provide a complete OpenVPN configuration file:"
        echo "1. Download your .ovpn file from https://account.protonvpn.com/downloads"
        echo "2. Create a 'vpn-config' directory in the project root"
        echo "3. Copy your .ovpn file to vpn-config/protonvpn.ovpn"
        echo "4. Uncomment the volume mount in docker-compose.yml:"
        echo "   - ./vpn-config/protonvpn.ovpn:/vpn/config/protonvpn.ovpn:ro"
        echo "5. Restart the VPN service: docker compose restart vpn"
        echo ""
        echo "OR set PROTONVPN_CONFIG_URL to download a config automatically"
        echo "======================================================================="
        
        # Give user time to see the warning
        sleep 5
    fi
fi

# Validate that the config file has certificates (basic check)
if ! grep -q "BEGIN CERTIFICATE" /vpn/config/protonvpn.ovpn 2>/dev/null && \
   ! grep -q "<ca>" /vpn/config/protonvpn.ovpn 2>/dev/null; then
    echo "======================================================================="
    echo "ERROR: OpenVPN configuration file is missing required certificates!"
    echo ""
    echo "The configuration at /vpn/config/protonvpn.ovpn does not contain"
    echo "the necessary CA certificate to connect to ProtonVPN."
    echo ""
    echo "Please provide a complete .ovpn file from ProtonVPN:"
    echo "https://account.protonvpn.com/downloads"
    echo ""
    echo "The container will continue to retry every 10 seconds..."
    echo "======================================================================="
    sleep 10
    exit 1
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

# Allow ICMP (ping) for healthcheck
iptables -A OUTPUT -p icmp -j ACCEPT
iptables -A INPUT -p icmp -j ACCEPT

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
echo "Username: [REDACTED]"
echo "========================="

# Display system information
echo "=== System Information ==="
echo "Kernel: $(uname -r)"
echo "Available network interfaces:"
ip link show
echo "TUN device status:"
ls -la /dev/net/tun || echo "TUN device not found!"
echo "========================="

# Start OpenVPN with the configuration
echo "Starting OpenVPN connection..."
echo "OpenVPN will now attempt to connect..."
exec openvpn --config /vpn/config/protonvpn.ovpn \
    --auth-user-pass /vpn/credentials/auth.txt \
    --script-security 2 \
    --up /vpn/up.sh \
    --down /vpn/down.sh \
    --verb 3
