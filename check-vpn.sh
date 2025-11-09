#!/bin/bash

echo "=== Checking VPN Container Status ==="
echo ""

echo "1. Container Status:"
docker ps -a --filter "name=scrapsama_vpn"
echo ""

echo "2. Container Logs (last 100 lines):"
docker logs --tail 100 scrapsama_vpn
echo ""

echo "3. Container Health Status:"
docker inspect scrapsama_vpn --format='{{.State.Health.Status}}'
echo ""

echo "4. Health Check Logs:"
docker inspect scrapsama_vpn --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
echo ""

echo "5. Network Interfaces inside container:"
docker exec scrapsama_vpn ip link show 2>/dev/null || echo "Container not running or not accessible"
echo ""

echo "6. Check if tun0 exists:"
docker exec scrapsama_vpn ip link show tun0 2>/dev/null || echo "tun0 interface not found"
echo ""

echo "7. Test ping from inside container:"
docker exec scrapsama_vpn ping -c 1 -W 2 1.1.1.1 2>/dev/null || echo "Ping failed"
echo ""

