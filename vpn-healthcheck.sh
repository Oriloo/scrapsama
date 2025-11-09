#!/bin/sh
# Script de healthcheck détaillé pour le conteneur VPN

echo "=== VPN Healthcheck Debug ==="
echo "Date: $(date)"
echo ""

# 1. Vérifier l'interface tun0
echo "1. Checking tun0 interface..."
if ip link show tun0 2>/dev/null; then
    echo "✓ tun0 interface exists"
    ip addr show tun0
else
    echo "✗ tun0 interface NOT found"
    echo "Available interfaces:"
    ip link show
    exit 1
fi
echo ""

# 2. Vérifier le processus OpenVPN
echo "2. Checking OpenVPN process..."
if pgrep -x openvpn > /dev/null; then
    echo "✓ OpenVPN process is running"
    pgrep -a openvpn
else
    echo "✗ OpenVPN process NOT running"
    exit 1
fi
echo ""

# 3. Vérifier les routes
echo "3. Checking routing table..."
ip route show
echo ""

# 4. Tester la connectivité DNS
echo "4. Testing DNS resolution..."
if nslookup google.com 1.1.1.1 2>/dev/null | grep -q "Address"; then
    echo "✓ DNS resolution OK"
else
    echo "⚠ DNS resolution might have issues"
fi
echo ""

# 5. Tester la connectivité ping
echo "5. Testing ping to 1.1.1.1..."
if ping -c 1 -W 5 1.1.1.1 >/dev/null 2>&1; then
    echo "✓ Ping successful"
else
    echo "✗ Ping FAILED"
    exit 1
fi
echo ""

# 6. Tester la connectivité HTTP
echo "6. Testing HTTP connectivity..."
if wget -q --spider --timeout=5 http://www.google.com 2>/dev/null; then
    echo "✓ HTTP connectivity OK"
else
    echo "⚠ HTTP connectivity might have issues"
fi
echo ""

echo "=== Healthcheck PASSED ==="
exit 0

