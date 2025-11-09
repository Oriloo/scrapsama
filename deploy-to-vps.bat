@echo off
REM Script de déploiement depuis Windows vers VPS OVH
REM Usage: deploy-to-vps.bat [VPS_IP]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: deploy-to-vps.bat [VPS_IP]
    echo Example: deploy-to-vps.bat 123.456.789.012
    exit /b 1
)

set VPS_IP=%1
set VPS_USER=ubuntu
set VPS_PATH=/home/ubuntu/dev/scrapsama

echo ========================================
echo Deploiement vers VPS OVH
echo ========================================
echo VPS: %VPS_IP%
echo User: %VPS_USER%
echo Path: %VPS_PATH%
echo ========================================
echo.

echo [1/5] Test de connexion SSH...
ssh %VPS_USER%@%VPS_IP% "echo 'Connexion OK'"
if errorlevel 1 (
    echo ERREUR: Impossible de se connecter au VPS
    echo Verifiez l'IP et que SSH est accessible
    exit /b 1
)
echo OK
echo.

echo [2/5] Creation du repertoire sur le VPS si necessaire...
ssh %VPS_USER%@%VPS_IP% "mkdir -p %VPS_PATH%"
echo OK
echo.

echo [3/5] Copie des fichiers de configuration...
scp docker-compose.yml %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp Dockerfile %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp Dockerfile.vpn %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp Dockerfile.web %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp .env %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp requirements.txt %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp pyproject.toml %VPS_USER%@%VPS_IP%:%VPS_PATH%/
echo OK
echo.

echo [4/5] Copie des scripts...
scp vpn-entrypoint.sh %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp vpn-up.sh %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp vpn-down.sh %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp vpn-healthcheck.sh %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp deploy-vpn.sh %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp check-vpn.sh %VPS_USER%@%VPS_IP%:%VPS_PATH%/
echo OK
echo.

echo [5/5] Copie des dossiers...
scp -r scraper %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp -r webapp %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp -r vpn-config %VPS_USER%@%VPS_IP%:%VPS_PATH%/
echo OK
echo.

echo [6/6] Copie de la documentation...
scp README.md %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp LICENSE %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp FIX-VPN-UNHEALTHY.md %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp VPN-TROUBLESHOOTING.md %VPS_USER%@%VPS_IP%:%VPS_PATH%/
scp DEPLOYMENT-VPS.md %VPS_USER%@%VPS_IP%:%VPS_PATH%/
echo OK
echo.

echo ========================================
echo Deploiement termine !
echo ========================================
echo.
echo Prochaines etapes sur le VPS:
echo.
echo 1. Se connecter au VPS:
echo    ssh %VPS_USER%@%VPS_IP%
echo.
echo 2. Aller dans le repertoire:
echo    cd %VPS_PATH%
echo.
echo 3. Rendre les scripts executables:
echo    chmod +x *.sh
echo.
echo 4. Verifier le module TUN:
echo    lsmod ^| grep tun
echo    sudo modprobe tun  # si necessaire
echo.
echo 5. Demarrer les services:
echo    docker compose --profile mysql --profile pma --profile web up -d --build
echo.
echo 6. Verifier le statut:
echo    ./deploy-vpn.sh check
echo.
echo ========================================
echo.

set /p CONNECT="Voulez-vous vous connecter au VPS maintenant ? (O/N): "
if /i "%CONNECT%"=="O" (
    ssh %VPS_USER%@%VPS_IP%
)

endlocal

