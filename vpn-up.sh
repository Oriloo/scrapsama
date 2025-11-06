#!/bin/bash
# This script is executed when the VPN connection is established

echo "=== VPN Connection Established ==="
echo "Interface: $dev"
echo "IP: $ifconfig_local"
echo "Remote: $ifconfig_remote"
echo "=================================="

# Additional routing can be added here if needed
exit 0
