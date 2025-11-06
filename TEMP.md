# Configuration ProtonVPN pour Scrapsama

Ce document décrit la configuration et l'utilisation du service ProtonVPN intégré à Scrapsama. Le VPN route tout le trafic réseau du scraper Python et de FlareSolverr à travers ProtonVPN avec un kill switch strict.

## Architecture

Le service ProtonVPN est implémenté comme un conteneur Docker séparé qui fournit un tunnel VPN. Les services `app` (scraper) et `flaresolverr` utilisent le réseau du conteneur VPN via `network_mode: "service:vpn"`, garantissant que tout leur trafic passe par le tunnel VPN.

### Kill Switch

Un kill switch strict est implémenté via `iptables` dans le conteneur VPN :
- Par défaut, tout le trafic est BLOQUÉ (DROP)
- Seul le trafic via l'interface `tun` (tunnel VPN) est autorisé
- Si la connexion VPN tombe, aucun trafic ne peut sortir
- Les règles sont appliquées au démarrage du conteneur

### Partage réseau (network_mode)

Les services `app`, `flaresolverr` et `web` utilisent `network_mode: "service:vpn"`, ce qui signifie :
- Ils partagent la même interface réseau que le conteneur VPN
- Tout leur trafic passe obligatoirement par le tunnel VPN
- Ils peuvent communiquer entre eux via `localhost` (127.0.0.1)
- `FLARESOLVERR_URL` doit être configuré à `http://localhost:8191/v1` au lieu de `http://flaresolverr:8191/v1`
- Les ports sont exposés via le conteneur VPN (8191 pour FlareSolverr, 5000 pour Web)

**Important** : MySQL et PhpMyAdmin restent sur le réseau Docker normal (`scrapsama_network`) et ne passent pas par le VPN. Le scraper peut y accéder car les règles iptables autorisent les réseaux Docker locaux (172.16.0.0/12). Cette plage est intentionnellement large pour assurer la compatibilité avec toutes les configurations Docker par défaut.

**Note sur l'accessibilité des services** : Lorsque plusieurs services utilisent `network_mode: service:vpn`, ils partagent le même espace réseau et peuvent communiquer via `localhost`. C'est pourquoi `FLARESOLVERR_URL` doit être configuré à `http://localhost:8191/v1` au lieu de `http://flaresolverr:8191/v1`.

## Prérequis

### 1. Compte ProtonVPN

Vous devez avoir un compte ProtonVPN (gratuit ou payant). Récupérez vos identifiants OpenVPN/IKEv2 :

1. Connectez-vous sur [https://account.protonvpn.com](https://account.protonvpn.com)
2. Allez dans **Account** → **OpenVPN/IKEv2 username**
3. Notez votre **Username** et **Password** (différents de vos identifiants de compte)

### 2. Configuration Docker

Le système hôte doit supporter :
- Docker avec support de `NET_ADMIN` capability
- Module kernel `tun` chargé (vérifier avec `lsmod | grep tun`)

## Configuration

### Variables d'environnement

Créez un fichier `.env` à partir de `.env.example` et configurez les variables suivantes :

```bash
# Identifiants ProtonVPN (OpenVPN/IKEv2)
PROTONVPN_USERNAME=your_protonvpn_username
PROTONVPN_PASSWORD=your_protonvpn_password

# Serveur ProtonVPN
PROTONVPN_SERVER=nl-free-01.protonvpn.net

# (Optionnel) URL de configuration OpenVPN
PROTONVPN_CONFIG_URL=

# IMPORTANT: FlareSolverr est accessible via localhost quand VPN est actif
FLARESOLVERR_URL=http://localhost:8191/v1
```

#### Variables requises

| Variable | Description | Exemple |
|----------|-------------|---------|
| `PROTONVPN_USERNAME` | Username OpenVPN/IKEv2 de ProtonVPN | `user+f1` |
| `PROTONVPN_PASSWORD` | Password OpenVPN/IKEv2 de ProtonVPN | `xxxxxxxxxx` |
| `PROTONVPN_SERVER` | Serveur ProtonVPN à utiliser | `nl-free-01.protonvpn.net` |
| `CONTAINER_NAME_VPN` | Nom du conteneur VPN | `scrapsama_vpn` |

#### Variables optionnelles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `PROTONVPN_CONFIG_URL` | URL vers un fichier .ovpn personnalisé | Configuration générée automatiquement |

### Choix du serveur

Liste des serveurs ProtonVPN disponibles : [https://account.protonvpn.com/downloads](https://account.protonvpn.com/downloads)

**Serveurs gratuits** (Free tier) :
- Pays-Bas : `nl-free-01.protonvpn.net` à `nl-free-XX.protonvpn.net`
- Japon : `jp-free-01.protonvpn.net` à `jp-free-XX.protonvpn.net`
- États-Unis : `us-free-01.protonvpn.net` à `us-free-XX.protonvpn.net`

**Serveurs premium** (nécessite abonnement payant) :
- France : `fr-01.protonvpn.net`, `fr-02.protonvpn.net`, etc.
- Royaume-Uni : `uk-01.protonvpn.net`, etc.
- Suisse : `ch-01.protonvpn.net`, etc.

### Configuration OpenVPN avancée (optionnel)

Pour utiliser un fichier de configuration OpenVPN personnalisé :

1. Téléchargez votre configuration depuis [ProtonVPN Downloads](https://account.protonvpn.com/downloads)
2. Créez un dossier `vpn-config` à la racine du projet
3. Placez votre fichier `.ovpn` dans ce dossier
4. Décommentez la ligne dans `docker-compose.yml` :

```yaml
vpn:
  volumes:
    - ./vpn-config/protonvpn.ovpn:/vpn/config/protonvpn.ovpn:ro
```

## Installation

### 1. Copier le fichier d'exemple

```bash
cp .env.example .env
```

### 2. Éditer le fichier .env

Modifiez `.env` avec vos identifiants ProtonVPN :

```bash
nano .env  # ou votre éditeur préféré
```

### 3. Construire et démarrer les services

```bash
# Construire les images
docker compose build

# Démarrer le service VPN
docker compose up -d vpn

# Vérifier que le VPN est connecté (attendre ~30-60 secondes)
docker compose logs vpn

# Démarrer les autres services
docker compose up -d
```

**Note importante sur l'ordre de démarrage** : Le VPN doit être complètement connecté (status "healthy") avant que les autres services démarrent. Les services app, flaresolverr et web ont une dépendance `condition: service_healthy` sur le VPN, donc Docker Compose attendra automatiquement. 

**Healthcheck du VPN** : Le conteneur VPN utilise un healthcheck qui vérifie :
1. L'existence de l'interface tunnel `tun0`
2. La capacité à ping 1.1.1.1 à travers le VPN

Le VPN peut prendre 60-90 secondes pour être considéré "healthy" après le démarrage. Si vous voyez des erreurs de connexion ou "container is unhealthy", vérifiez :
- Les logs du VPN : `docker compose logs vpn`
- Le statut des conteneurs : `docker compose ps`
- Que vos identifiants ProtonVPN sont corrects dans `.env`

### 4. Initialiser la base de données (première utilisation)

```bash
docker compose run --rm app python scraper/init_db.py
```

## Utilisation

### Démarrage des services

```bash
# Démarrer tous les services (VPN + scraper + MySQL + FlareSolverr)
docker compose up -d

# Voir les logs du VPN
docker compose logs -f vpn

# Voir les logs du scraper
docker compose logs -f app
```

### Exécution du scraper

Les commandes scraper fonctionnent normalement, tout le trafic passe par le VPN :

```bash
# Indexer une série
docker compose run --rm app scrapsama-index

# Indexer toutes les séries
docker compose run --rm app scrapsama-index-all

# Indexer les nouveaux épisodes
docker compose run --rm app scrapsama-index-new
```

### Services avec profils optionnels

```bash
# Démarrer avec MySQL, PhpMyAdmin et interface web
docker compose --profile mysql --profile pma --profile web up -d
```

## Vérification

### Vérifier la connexion VPN

```bash
# Vérifier les logs du conteneur VPN
docker compose logs vpn

# Vous devriez voir :
# "=== VPN Connection Established ==="
# "Interface: tun0"
# "IP: xxx.xxx.xxx.xxx"
```

### Tester l'IP publique du scraper

```bash
# Exécuter une commande curl dans le conteneur app pour vérifier l'IP
docker compose exec app sh -c "apt-get update && apt-get install -y curl && curl https://ifconfig.me"

# L'IP affichée devrait être celle du serveur ProtonVPN, pas votre IP réelle
```

### Vérifier le kill switch

Pour vérifier que le kill switch fonctionne :

1. Arrêter le service VPN :
```bash
docker compose stop vpn
```

2. Essayer une requête depuis le conteneur app :
```bash
docker compose run --rm app sh -c "apt-get update && apt-get install -y curl && curl https://ifconfig.me"
# La commande devrait échouer car le VPN est arrêté
```

3. Redémarrer le VPN :
```bash
docker compose start vpn
```

## Dépannage

### Le conteneur VPN est "unhealthy"

Si vous voyez l'erreur `container scrapsama_vpn is unhealthy` ou `dependency failed to start`:

1. **Vérifier les logs du VPN** :
```bash
docker compose logs vpn
```
Recherchez des erreurs de connexion OpenVPN ou des problèmes d'authentification.

2. **Vérifier les identifiants** :
   - Les identifiants dans `.env` doivent être les identifiants OpenVPN/IKEv2 (pas vos identifiants de compte)
   - Vérifiez sur [https://account.protonvpn.com](https://account.protonvpn.com) → Account → OpenVPN/IKEv2 username

3. **Attendre le healthcheck** :
Le VPN peut prendre jusqu'à 90 secondes pour devenir "healthy". Le healthcheck vérifie que l'interface `tun0` existe et peut ping 1.1.1.1.

4. **Vérifier manuellement la connexion** :
```bash
# Vérifier si le conteneur est en cours d'exécution
docker compose ps vpn

# Vérifier l'interface tun0
docker compose exec vpn ip link show tun0

# Tester le ping
docker compose exec vpn ping -c 3 1.1.1.1
```

5. **Redémarrer le service VPN** :
```bash
docker compose down vpn
docker compose up -d vpn
# Attendre 90 secondes puis vérifier le statut
docker compose ps vpn
```

### Le VPN ne se connecte pas

1. **Vérifier les identifiants** :
   - Assurez-vous d'utiliser les identifiants OpenVPN/IKEv2, pas vos identifiants de compte ProtonVPN
   - Vérifiez sur [https://account.protonvpn.com](https://account.protonvpn.com) → Account → OpenVPN/IKEv2 username

2. **Vérifier les logs** :
```bash
docker compose logs vpn
```

3. **Essayer un autre serveur** :
   - Changez `PROTONVPN_SERVER` dans `.env`
   - Redémarrez : `docker compose restart vpn`

### Le scraper ne peut pas se connecter à Internet

1. **Vérifier que le VPN est connecté** :
```bash
docker compose ps vpn
# Status devrait être "healthy"
```

2. **Vérifier les logs du VPN** :
```bash
docker compose logs vpn | grep "VPN Connection Established"
```

3. **Redémarrer les services dans l'ordre** :
```bash
docker compose down
docker compose up -d vpn
# Attendre 30 secondes
docker compose up -d
```

### Le scraper ne peut pas se connecter à MySQL

MySQL n'utilise pas le VPN, il est sur le réseau Docker normal. Le scraper doit pouvoir y accéder même via le VPN grâce aux règles iptables qui autorisent les réseaux locaux Docker (172.16.0.0/12).

Si le problème persiste :
1. Vérifier que MySQL est démarré : `docker compose ps mysql`
2. Vérifier la configuration réseau dans `.env` : `MYSQL_HOST=mysql`

### Erreur "device tun not available"

Le module kernel `tun` n'est pas chargé :

```bash
# Sur l'hôte Docker
sudo modprobe tun

# Vérifier
lsmod | grep tun
```

Pour charger automatiquement au démarrage :
```bash
echo "tun" | sudo tee -a /etc/modules
```

### Performance lente

1. **Essayer un serveur plus proche** géographiquement
2. **Utiliser un serveur premium** si vous avez un abonnement payant
3. **Vérifier la charge du serveur** sur la page de téléchargement ProtonVPN

## Sécurité

### Kill Switch

Le kill switch est **toujours actif** et fonctionne comme suit :
- Toutes les connexions sortantes passent obligatoirement par `tun0` (tunnel VPN)
- Si le VPN se déconnecte, plus aucun trafic ne peut sortir
- Les règles iptables sont appliquées **avant** la connexion VPN

### Persistance des identifiants

Les identifiants sont stockés dans un volume Docker nommé `vpn_credentials` :
- Persistance entre les redémarrages
- Permissions restrictives (600)
- Non partagé avec d'autres conteneurs

Pour supprimer les identifiants stockés :
```bash
docker compose down
docker volume rm scrapsama_vpn_credentials
```

### Isolation réseau

- Le conteneur VPN est isolé avec `NET_ADMIN` capability uniquement
- Les autres conteneurs (app, flaresolverr) utilisent le réseau du VPN mais n'ont pas `NET_ADMIN`
- MySQL et PhpMyAdmin ne passent pas par le VPN

## Architecture réseau

```
Internet
   ↕
ProtonVPN Server
   ↕
[vpn container] ← Kill switch actif (iptables)
   ↕ (tun0)
   ├── [app container] (network_mode: service:vpn)
   └── [flaresolverr container] (network_mode: service:vpn)

[mysql container] ← Réseau Docker normal (scrapsama_network)
[phpmyadmin container] ← Réseau Docker normal (scrapsama_network)
```

### Flux réseau

1. **app** → Requête HTTP
2. **app** → **vpn** (via network_mode)
3. **vpn** → Vérification iptables (kill switch)
4. **vpn** → Tunnel OpenVPN (tun0)
5. **vpn** → ProtonVPN Server
6. **ProtonVPN Server** → Internet

Si le VPN tombe : étape 3 → **BLOCKED** (DROP)

## Fichiers du projet

| Fichier | Description |
|---------|-------------|
| `Dockerfile.vpn` | Image Docker pour le service VPN |
| `vpn-entrypoint.sh` | Script de démarrage du VPN avec kill switch |
| `vpn-up.sh` | Script exécuté quand le VPN se connecte |
| `vpn-down.sh` | Script exécuté quand le VPN se déconnecte |
| `docker-compose.yml` | Configuration des services (incluant VPN) |
| `.env.example` | Template des variables d'environnement |

## Limitations

1. **Compte gratuit ProtonVPN** :
   - Serveurs limités (NL, JP, US)
   - Vitesse potentiellement réduite
   - Un seul appareil connecté à la fois

2. **Docker** :
   - Nécessite `NET_ADMIN` capability
   - Module kernel `tun` requis

3. **Réseau** :
   - Les ports exposés (8191, 5000) le sont via le conteneur VPN
   - FlareSolverr et app partagent l'espace réseau du VPN

## Support

Pour plus d'informations :
- Documentation ProtonVPN : [https://protonvpn.com/support/](https://protonvpn.com/support/)
- Serveurs disponibles : [https://account.protonvpn.com/downloads](https://account.protonvpn.com/downloads)
- Issues GitHub : [https://github.com/Oriloo/scrapsama/issues](https://github.com/Oriloo/scrapsama/issues)
