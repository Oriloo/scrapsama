#!/bin/bash

# Script de déploiement et de dépannage pour VPS OVH
# Usage: ./deploy-vpn.sh [check|restart|rebuild|logs|shell]

set -e

COMPOSE_COMMAND="docker compose --profile mysql --profile pma --profile web"

function check_vpn() {
    echo "=== Vérification du statut du VPN ==="
    echo ""

    echo "1. Statut des conteneurs:"
    docker compose ps
    echo ""

    echo "2. Logs du VPN (dernières 50 lignes):"
    docker logs --tail 50 scrapsama_vpn
    echo ""

    echo "3. État de santé du VPN:"
    docker inspect scrapsama_vpn --format='Health Status: {{.State.Health.Status}}' 2>/dev/null || echo "Conteneur non trouvé"
    echo ""

    echo "4. Logs du healthcheck:"
    docker inspect scrapsama_vpn --format='{{range .State.Health.Log}}Exit Code: {{.ExitCode}} - {{.Output}}{{end}}' 2>/dev/null
    echo ""

    echo "5. Test interface tun0:"
    docker exec scrapsama_vpn ip link show tun0 2>/dev/null && echo "✓ Interface tun0 trouvée" || echo "✗ Interface tun0 non trouvée"
    echo ""

    echo "6. Test de connectivité:"
    docker exec scrapsama_vpn ping -c 3 1.1.1.1 2>/dev/null && echo "✓ Connectivité OK" || echo "✗ Pas de connectivité"
    echo ""
}

function restart_vpn() {
    echo "=== Redémarrage du VPN ==="
    docker compose restart vpn
    echo "Attente de 30 secondes pour la connexion VPN..."
    sleep 30
    check_vpn
}

function rebuild_all() {
    echo "=== Reconstruction complète ==="
    echo "Arrêt des conteneurs..."
    $COMPOSE_COMMAND down

    echo "Reconstruction des images..."
    $COMPOSE_COMMAND build --no-cache

    echo "Démarrage des services..."
    $COMPOSE_COMMAND up -d

    echo "Attente de 60 secondes pour l'initialisation..."
    sleep 60

    check_vpn
}

function show_logs() {
    echo "=== Logs en temps réel (Ctrl+C pour quitter) ==="
    docker compose logs -f vpn
}

function vpn_shell() {
    echo "=== Accès au shell du conteneur VPN ==="
    docker exec -it scrapsama_vpn /bin/bash || docker exec -it scrapsama_vpn /bin/sh
}

function show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commandes disponibles:"
    echo "  check     - Vérifier l'état du VPN et faire des diagnostics"
    echo "  restart   - Redémarrer uniquement le conteneur VPN"
    echo "  rebuild   - Reconstruire et redémarrer tous les conteneurs"
    echo "  logs      - Afficher les logs du VPN en temps réel"
    echo "  shell     - Ouvrir un shell dans le conteneur VPN"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 check"
    echo "  $0 restart"
    echo "  $0 logs"
}

# Main
case "${1:-help}" in
    check)
        check_vpn
        ;;
    restart)
        restart_vpn
        ;;
    rebuild)
        rebuild_all
        ;;
    logs)
        show_logs
        ;;
    shell)
        vpn_shell
        ;;
    help|*)
        show_help
        ;;
esac

