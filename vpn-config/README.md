# Exemple de configuration OpenVPN pour ProtonVPN

Ce dossier contient un exemple de fichier de configuration OpenVPN.

## Comment obtenir votre configuration ProtonVPN

1. Connectez-vous sur [https://account.protonvpn.com](https://account.protonvpn.com)
2. Allez dans **Downloads** → **OpenVPN configuration files**
3. Sélectionnez :
   - **Platform** : Linux
   - **Protocol** : UDP ou TCP
   - **Country** : Pays de votre choix (ex: Netherlands, Japan, USA pour Free)
   - **Server** : Serveur spécifique (ex: nl-free-01)
4. Téléchargez le fichier `.ovpn`

## Utilisation

Pour utiliser votre propre configuration :

1. Placez votre fichier `.ovpn` dans ce dossier (ou créez un dossier `vpn-config` à la racine)
2. Renommez-le en `protonvpn.ovpn`
3. Dans `docker-compose.yml`, décommentez la ligne :

```yaml
vpn:
  volumes:
    - ./vpn-config/protonvpn.ovpn:/vpn/config/protonvpn.ovpn:ro
```

4. Redémarrez le service :

```bash
docker compose down vpn
docker compose up -d vpn
```

## Note importante

- Si vous ne fournissez pas de fichier `.ovpn`, une configuration basique sera générée automatiquement
- La configuration automatique utilise les variables `PROTONVPN_SERVER` et les paramètres par défaut
- Pour une configuration optimale, il est recommandé d'utiliser les fichiers officiels de ProtonVPN
