# Docker Setup for Anime-Sama API

This project includes a Docker Compose setup with:
- **Anime-Sama API Application** (Python CLI)
- **MySQL 8.0** Database
- **phpMyAdmin** for database management

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the services:**
   - **phpMyAdmin**: http://localhost:8080
     - Username: `root`
     - Password: `rootpassword`
   - **MySQL**: localhost:3306
     - Database: `animesama_db`
     - User: `animesama_user`
     - Password: `animesama_password`

3. **Run the Anime-Sama CLI:**
   ```bash
   docker-compose run --rm app anime-sama
   ```

## Services Configuration

### MySQL Database
- **Container name**: `animesama_mysql`
- **Port**: 3306
- **Root password**: `rootpassword`
- **Database**: `animesama_db`
- **User**: `animesama_user`
- **Password**: `animesama_password`

### phpMyAdmin
- **Container name**: `animesama_phpmyadmin`
- **Port**: 8080
- **Access URL**: http://localhost:8080

### Application
- **Container name**: `animesama_app`
- **Config directory**: Mounted to persist configuration
- **Downloads directory**: `/app/downloads` (mounted as volume)

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop services and remove volumes (WARNING: This will delete your database)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f mysql
docker-compose logs -f phpmyadmin
```

### Rebuild the application image
```bash
docker-compose build app
```

### Execute a command in the running app container
```bash
docker-compose exec app bash
```

### Run the CLI interactively
```bash
docker-compose run --rm app anime-sama
```

## Volumes

The setup uses Docker volumes to persist data:
- `mysql_data`: MySQL database files
- `app_config`: Application configuration files
- `downloads`: Downloaded anime files

## Customization

### Change MySQL credentials
Edit the environment variables in `docker-compose.yml` under the `mysql` and `phpmyadmin` services.

### Change ports
Modify the `ports` section in `docker-compose.yml`:
- MySQL: Change `"3306:3306"` to `"YOUR_PORT:3306"`
- phpMyAdmin: Change `"8080:80"` to `"YOUR_PORT:80"`

## Troubleshooting

### MySQL connection issues
If you can't connect to MySQL, ensure the service is healthy:
```bash
docker-compose ps
```

### Reset the database
```bash
docker-compose down -v
docker-compose up -d
```

### Application errors
Check the logs:
```bash
docker-compose logs app
```

## Security Notes

**IMPORTANT**: The default credentials are for development purposes only. 
For production use, please:
1. Change all default passwords
2. Use environment variables or Docker secrets
3. Restrict network access appropriately
4. Use proper SSL/TLS certificates
