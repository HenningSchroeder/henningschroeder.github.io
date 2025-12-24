+++
date = '2025-12-24T00:48:00+00:00'
draft = true
title = '0002 - Deployment Infrastructure: Lab Baseline'
tags = ['infrastructure', 'deployment', 'podman', 'ubuntu', 'devops']
categories = ['Infrastructure as Code']
+++

Welcome to the first entry in our Deployment Infrastructure blog series. This series explores modern deployment frameworks, Infrastructure as Code (IaC), and building scalable deployment environments from proof-of-concept to production.

## Overview

In this entry, we establish a **Lab Baseline**—a foundational development environment that serves as the starting point for exploring deployment automation, containerization, and infrastructure management. We'll set up an Ubuntu LTS virtual machine with Podman and Podman Compose, then deploy a simple multi-service stack to validate our setup.

## Objectives

- Set up an Ubuntu 24.04 LTS virtual machine (compatible with 25.10)
- Install and configure Podman and Podman Compose
- Deploy a sample multi-service application stack
- Document the process and capture key decisions
- Create reusable artifacts (Compose files, Makefiles, runbooks)

## Prerequisites

Before starting, ensure you have:

- A hypervisor installed (KVM/libvirt, VirtualBox, VMware, or similar)
- Basic familiarity with Linux command line
- Internet connection for downloading packages
- Minimum hardware requirements:
  - 2 vCPUs
  - 4GB RAM
  - 20GB disk space

## Part 1: Virtual Machine Setup

### Step 1: Create Ubuntu LTS VM

We're using **Ubuntu 24.04 LTS** as our base operating system. Ubuntu LTS (Long Term Support) provides:
- 5 years of security updates and bug fixes
- Wide community support and documentation
- Excellent OCI container ecosystem compatibility (Podman is Docker-compatible)
- Strong package availability for development tools

**VM Configuration:**
```
- OS: Ubuntu 24.04 LTS Server
- vCPUs: 2
- RAM: 4GB
- Disk: 20GB (thin-provisioned if possible)
- Network: Bridged or NAT with port forwarding
```

**Installation Steps:**

1. Download Ubuntu 24.04 LTS Server ISO from [ubuntu.com](https://ubuntu.com/download/server)
2. Create a new VM in your hypervisor with the specifications above
3. Boot from the ISO and follow the installation wizard
4. Choose "Ubuntu Server (minimized)" for a lighter footprint
5. Configure network settings (static IP recommended for lab consistency)
6. Create a user account (e.g., `deploy` or your username)
7. Install OpenSSH server when prompted (for remote access)
8. Do not install additional snaps during setup (we'll add what we need)

### Step 2: Post-Installation System Update

Once the VM is running and you're logged in (directly or via SSH):

```bash
# Update package lists and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Install essential utilities
sudo apt install -y \
    curl \
    wget \
    git \
    make \
    vim \
    htop \
    net-tools \
    ca-certificates \
    gnupg \
    lsb-release

# Reboot if kernel was updated
sudo reboot
```

## Part 2: Podman Installation

We'll install Podman and Podman Compose using the official Ubuntu repositories.

### Step 1: Install Podman and Podman Compose

```bash
# Update package index
sudo apt update

# Install Podman and Podman Compose
sudo apt install -y podman podman-compose

# Verify installation
podman --version
podman-compose --version
```

### Step 2: Post-Installation Configuration

```bash
# Enable user namespaces for rootless containers (recommended)
sudo sysctl -w user.max_user_namespaces=28633

# Add your user to the appropriate group (if needed)
sudo usermod -aG podman $USER

# Enable Podman socket for Docker compatibility (optional)
systemctl --user enable --now podman.socket

# Log out and back in for group changes to take effect
```

### Step 3: Verify Podman Installation

```bash
# Test Podman installation
podman run --rm hello-world

# Check Podman service status
systemctl --user status podman.socket
```

We'll install Docker Engine using the official Docker repository to ensure we get the latest stable version.

### Step 1: Set Up Docker Repository

```bash
# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update
```

### Step 2: Install Docker Engine and Compose

```bash
# Install Docker Engine, CLI, containerd, and Compose plugin
sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### Step 3: Post-Installation Configuration

```bash
# Add your user to the docker group (avoid using sudo for docker commands)
sudo usermod -aG docker $USER

# Enable Docker to start on boot
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

# Log out and back in for group changes to take effect
# Or run: newgrp docker
```

### Step 4: Verify Docker Installation

```bash
# Test Docker installation
docker run hello-world

# Check Docker service status
sudo systemctl status docker
```

## Part 3: Sample Application Stack

Now we'll deploy a simple multi-service stack consisting of:
- **Nginx**: Web server and reverse proxy
- **FastAPI**: Python-based REST API application

### Directory Structure

Create a project directory structure:

```bash
mkdir -p ~/lab/{app,nginx,data}
cd ~/lab
```

### FastAPI Application

Create a simple FastAPI application:

**`~/lab/app/main.py`:**
```python
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Lab Baseline API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Lab Baseline API",
        "timestamp": datetime.now().isoformat(),
        "hostname": os.getenv("HOSTNAME", "unknown")
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/info")
async def info():
    return {
        "service": "FastAPI Demo",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
```

**`~/lab/app/requirements.txt`:**
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
```

**`~/lab/app/Dockerfile`:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration

**`~/lab/nginx/nginx.conf`:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }

        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**`~/lab/nginx/index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab Baseline</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .endpoint {
            background-color: #f8f8f8;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        code {
            background-color: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Lab Baseline - Deployment Infrastructure</h1>
        <p>Welcome to the Lab Baseline environment. This is a foundational setup for exploring deployment automation and Infrastructure as Code.</p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <strong>Main Page:</strong> <code>http://localhost/</code><br>
            This page you're viewing now.
        </div>
        
        <div class="endpoint">
            <strong>API Root:</strong> <code>http://localhost/api/</code><br>
            Returns basic API information and timestamp.
        </div>
        
        <div class="endpoint">
            <strong>Health Check:</strong> <code>http://localhost/api/health</code><br>
            Returns service health status.
        </div>
        
        <div class="endpoint">
            <strong>Service Info:</strong> <code>http://localhost/api/info</code><br>
            Returns detailed service information.
        </div>

        <h2>Stack Components:</h2>
        <ul>
            <li><strong>Nginx:</strong> Reverse proxy and static file server</li>
            <li><strong>FastAPI:</strong> Python-based REST API backend</li>
        </ul>

        <h2>Quick Test:</h2>
        <p>Try these commands:</p>
        <pre><code>curl http://localhost/api/
curl http://localhost/api/health
curl http://localhost/api/info</code></pre>
    </div>
</body>
</html>
```

### Podman Compose Configuration

**`~/lab/podman-compose.yml`:**
```yaml
version: '3.9'

services:
  nginx:
    image: nginx:1.27-alpine
    container_name: lab-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/index.html:/usr/share/nginx/html/index.html:ro
    depends_on:
      - api
    networks:
      - lab-network
    restart: unless-stopped

  api:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: lab-api
    environment:
      - ENVIRONMENT=development
      - HOSTNAME=lab-api
    expose:
      - "8000"
    networks:
      - lab-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  lab-network:
    driver: bridge
```

### Makefile for Common Operations (Podman)

**`~/lab/Makefile`:**
```makefile
.PHONY: help up down restart logs ps build clean status test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

down: ## Stop all services
up: ## Start all services
  podman-compose -f podman-compose.yml up -d

down: ## Stop all services
  podman-compose -f podman-compose.yml down

restart: down up ## Restart all services

logs: ## Show logs for all services
  podman-compose -f podman-compose.yml logs -f

ps: ## Show running containers
  podman-compose -f podman-compose.yml ps

build: ## Build/rebuild all services
  podman-compose -f podman-compose.yml build

rebuild: ## Rebuild and restart services
  podman-compose -f podman-compose.yml up -d --build

clean: ## Remove all containers, networks, and volumes
  podman-compose -f podman-compose.yml down -v
  podman system prune -f

status: ## Show service status
  @echo "=== Podman Compose Services ==="
  @podman-compose -f podman-compose.yml ps
  @echo ""
  @echo "=== Podman System Info ==="
  @podman system df

test: ## Test the deployed services
  @echo "Testing Nginx..."
  @curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/
  @echo ""
  @echo "Testing API root..."
  @curl -s http://localhost/api/ | python3 -m json.tool
  @echo ""
  @echo "Testing API health..."
  @curl -s http://localhost/api/health | python3 -m json.tool
  @echo ""
  @echo "Testing API info..."
  @curl -s http://localhost/api/info | python3 -m json.tool
```

## Part 4: Deployment and Validation

### Deploy the Stack

```bash
cd ~/lab


# Build and start services
make up

# Or using podman-compose directly:
# podman-compose -f podman-compose.yml up -d --build

# Check service status
make ps

# View logs
make logs
```

### Validate Deployment

```bash
# Run automated tests
make test

# Manual testing
curl http://localhost/
curl http://localhost/api/
curl http://localhost/api/health
curl http://localhost/api/info

# Check container health
podman ps

# Inspect logs
podman logs lab-nginx
podman logs lab-api
```

Expected output:
- Nginx serving the landing page on port 80
- API endpoints responding with JSON data
- All containers showing "healthy" status
- No errors in logs

## Part 5: Architecture Decision Record (ADR)

### ADR: Lab Baseline Foundation

**Status:** Accepted  
**Date:** 2025-12-24  
**Decision Makers:** Development Team

#### Context

We need a consistent, reproducible development and testing environment for exploring deployment infrastructure, IaC frameworks, and container orchestration. The environment should:
- Be easy to set up and tear down
- Support iterative experimentation
- Provide foundation for future blog entries
- Be accessible to developers with varied experience levels

#### Decision

We will use:
1. **Ubuntu 24.04 LTS** as the base operating system
2. **KVM/libvirt** as the preferred virtualization platform
3. **Podman** with **Podman Compose** for container management (due to Docker's licensing politics)
4. **Virtual Machine** approach rather than bare metal

#### Rationale

**Ubuntu 24.04 LTS:**
- Long-term support (5 years) ensures stability
- Excellent documentation and community support
- Native compatibility with Docker and modern development tools
- Widely used in production environments

**VM vs. Bare Metal:**
- **Pros of VM:**
  - Isolation from host system
  - Easy snapshots and rollbacks
  - Multiple environments on single hardware
  - Consistent across different host OSes
- **Cons of VM:**
  - Slight performance overhead
  - Additional resource consumption
- **Decision:** VM approach provides better flexibility for a lab environment where experimentation and learning are priorities


**Podman Compose:**
- Simpler than Kubernetes for initial learning
- Declarative configuration
- Local development friendly
- Production-capable for smaller deployments
- Easy transition to Swarm or Kubernetes later
- No licensing issues (unlike Docker)

**Resource Allocation (2 vCPU, 4GB RAM, 20GB disk):**
- Sufficient for development workloads
- Allows running multiple containers
- Keeps resource requirements accessible
- Can be scaled up as needed

#### Consequences

**Positive:**
- Reproducible setup process
- Clear documentation path
- Foundation for future blog entries
- Low barrier to entry

**Negative:**
- VM overhead vs. bare metal performance
- Requires hypervisor on host system
- Initial setup time investment

**Mitigations:**
- Document VM setup thoroughly
- Provide automation scripts in future entries
- Consider cloud-based alternatives (covered in Entry 02)

#### Alternatives Considered

1. **Bare Metal:** Rejected due to lack of isolation and difficulty in providing consistent instructions across different hardware
2. **Docker Desktop:** Rejected due to licensing considerations and desire for production-similar setup. Podman is used instead to avoid Docker's licensing politics.
3. **Kubernetes from Start:** Rejected as too complex for initial baseline; will be introduced gradually
4. **Windows WSL2:** Valid alternative, will be covered in OS Support Matrix (Entry 12)

## Part 6: Runbook

### Quick Reference


**Start Services:**
```bash
cd ~/lab && make up
```


**Stop Services:**
```bash
cd ~/lab && make down
```


**View Logs:**
```bash
make logs                  # All services
podman logs lab-nginx      # Nginx only
podman logs lab-api        # API only
```


**Rebuild After Code Changes:**
```bash
make rebuild
```


**Check Status:**
```bash
make status
podman ps
podman-compose -f podman-compose.yml ps
```


**Clean Up Everything:**
```bash
make clean
```

### Troubleshooting

**Problem: Containers won't start**
```bash

# Check logs
podman-compose -f podman-compose.yml logs

# Check system resources
docker system df
free -h
df -h


# Verify Podman is running
systemctl --user status podman.socket
```

**Problem: Port already in use**
```bash
# Find what's using port 80
sudo lsof -i :80
sudo netstat -tulpn | grep :80

# Stop conflicting service or change port in docker-compose.yml
```

**Problem: Permission denied on docker commands**
```bash
# Ensure user is in docker group
groups $USER

# If not, add and relogin
sudo usermod -aG docker $USER
newgrp docker
```

**Problem: API not responding**
```bash

# Check if container is running
podman ps | grep lab-api


# Check container logs
podman logs lab-api


# Exec into container for debugging
podman exec -it lab-api sh
```

### Maintenance


**Update Images:**
```bash
podman-compose -f podman-compose.yml pull
podman-compose -f podman-compose.yml up -d
```

**Backup Configuration:**
```bash
tar -czf lab-backup-$(date +%Y%m%d).tar.gz ~/lab
```


**Clean Old Images:**
```bash
podman image prune -a
podman system prune -a
```

## Part 7: AI-Assisted Development

This lab setup was created with assistance from local LLM tools to:
- Draft initial Dockerfile and Compose configurations
- Generate boilerplate FastAPI code
- Create Nginx proxy configuration
- Write documentation templates

**AI Prompts Used:**

See `ai/prompts/lab-baseline.md` for prompt templates used during development. These can be reused with local LLMs like Ollama with CodeLlama or Mistral models.

**Workflow:**
1. Use AI to generate initial configurations
2. Review and validate all generated code
3. Test in isolation before integration
4. Document deviations from AI suggestions

## Next Steps

This lab baseline provides the foundation for:
- **Entry 02:** Terraform deployment to Hetzner Cloud
- **Entry 03:** Cloud provider comparison and packaging options
- **Entry 04:** Ansible configuration management
- **Entry 05:** Essential infrastructure services (Git, CI/CD, monitoring)

## Summary

We've successfully:
✅ Set up Ubuntu 24.04 LTS virtual machine  
✅ Installed Docker Engine and Compose  
✅ Created a multi-service application stack  
✅ Deployed and validated the services  
✅ Documented decisions and procedures  
✅ Created reusable artifacts (Compose, Makefile, runbook)  

The lab baseline is now ready for iterative development and experimentation with deployment infrastructure.

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Series Navigation:**
- Previous: _None (This is Entry 01)_
- Next: [Entry 02 — Terraform Quickstart (Hetzner)](#) _(Coming soon)_
