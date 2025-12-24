# Lab Environment - Deployment Infrastructure

This directory contains the code and configuration files for the Lab Baseline environment described in blog post [0002 - Deployment Infrastructure: Lab Baseline](../content/posts/0002-deployment-infrastructure-lab-baseline/index.md).

## Purpose

The Lab Baseline provides a foundational development environment for exploring:
- Infrastructure as Code (IaC)
- Container orchestration with Docker Compose
- Deployment automation
- Service architecture patterns

## Prerequisites

- Docker Engine (20.10+)
- Docker Compose (2.0+)
- Make (optional, for convenience commands)

## Quick Start

```bash
# Navigate to lab directory
cd lab

# Start all services
make up

# Or using docker compose directly
docker compose up -d

# Verify services are running
make status

# Test endpoints
make test

# View logs
make logs

# Stop services
make down
```

## Services

### Nginx (Port 80)
- **Purpose**: Reverse proxy and static file server
- **Endpoint**: http://localhost/
- **Features**:
  - Serves landing page on root path
  - Proxies API requests to backend
  - Production-ready configuration

### FastAPI Backend (Internal Port 8000)
- **Purpose**: REST API demonstration
- **Endpoints**:
  - `GET /` - Service information and timestamp
  - `GET /health` - Health check
  - `GET /info` - Detailed service metadata
- **Access**: Via Nginx at http://localhost/api/

## Directory Structure

```
lab/
├── app/                      # FastAPI application
│   ├── Dockerfile           # Container image definition
│   ├── main.py              # Application code
│   └── requirements.txt     # Python dependencies
├── nginx/                    # Nginx configuration
│   ├── nginx.conf           # Reverse proxy config
│   └── index.html           # Landing page
├── docker-compose.yml        # Service orchestration
├── Makefile                  # Convenience commands
└── README.md                 # This file
```

## Makefile Targets

Run `make help` to see all available targets:

- `make up` - Start all services in detached mode
- `make down` - Stop all services
- `make restart` - Restart all services
- `make logs` - Show logs (follows)
- `make ps` - Show running containers
- `make build` - Build/rebuild images
- `make rebuild` - Rebuild and restart
- `make clean` - Remove containers, networks, volumes
- `make status` - Show detailed service and system status
- `make test` - Test all service endpoints

## Testing

### Automated Testing

```bash
make test
```

### Manual Testing

```bash
# Test landing page
curl http://localhost/

# Test API endpoints
curl http://localhost/api/
curl http://localhost/api/health
curl http://localhost/api/info

# Pretty print JSON responses
curl -s http://localhost/api/ | python3 -m json.tool
```

## Troubleshooting

### Port Conflict

If port 80 is already in use:

```bash
# Find what's using port 80
sudo lsof -i :80

# Either stop the conflicting service or edit docker-compose.yml
# to use a different port, e.g., "8080:80"
```

### Permission Denied

Ensure your user is in the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Containers Not Starting

Check logs for errors:

```bash
docker compose logs
docker logs lab-nginx
docker logs lab-api
```

### Resource Issues

Check available resources:

```bash
docker system df
free -h
df -h
```

## Customization

### Change Ports

Edit `docker-compose.yml`:

```yaml
services:
  nginx:
    ports:
      - "8080:80"  # Change host port from 80 to 8080
```

### Modify API

1. Edit `app/main.py`
2. Rebuild and restart:
   ```bash
   make rebuild
   ```

### Update Nginx Configuration

1. Edit `nginx/nginx.conf` or `nginx/index.html`
2. Restart services:
   ```bash
   make restart
   ```

## Development Workflow

1. **Make Changes**: Edit files in `app/` or `nginx/`
2. **Rebuild**: Run `make rebuild`
3. **Test**: Run `make test` or test manually
4. **View Logs**: Run `make logs` if issues occur
5. **Iterate**: Repeat as needed

## Maintenance

### Update Images

```bash
docker compose pull
docker compose up -d
```

### Clean Up

```bash
# Remove containers and networks
make down

# Full cleanup including volumes and unused images
make clean
```

### Backup Configuration

```bash
tar -czf lab-backup-$(date +%Y%m%d).tar.gz .
```

## Next Steps

This baseline environment is the foundation for:
- Terraform deployment to cloud providers (Blog Entry 02)
- Ansible configuration management (Blog Entry 04)
- Essential infrastructure services (Blog Entry 05)
- Monitoring and observability (Blog Entries 07-08)

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Blog Series](../content/posts/) - Full deployment infrastructure series

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the full blog post for detailed explanations
3. Check Docker and service logs
4. Consult the official documentation links

---

**Part of the Deployment Infrastructure Blog Series**  
See [Blog Entry 0002](../content/posts/0002-deployment-infrastructure-lab-baseline/index.md) for complete documentation.
