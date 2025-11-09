#!/bin/bash
# This script is executed when the VPN connection is established

echo "=== VPN Connection Established ==="
echo "Interface: $dev"
echo "IP: $ifconfig_local"
echo "Remote: $ifconfig_remote"
echo "Gateway: ${route_vpn_gateway:-N/A}"
echo "=================================="

# Display routing table
echo "Routing table:"
ip route show
echo ""

# Display all interfaces
echo "Network interfaces:"
ip link show
echo ""

# Test connectivity
echo "Testing connectivity..."
if ping -c 1 -W 3 1.1.1.1 >/dev/null 2>&1; then
    echo "✓ Internet connectivity OK"
else
    echo "✗ Warning: Cannot ping 1.1.1.1"
fi

# Additional routing can be added here if needed
exit 0
