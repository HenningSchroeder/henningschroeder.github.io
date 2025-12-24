# Lab Baseline
## Podman: Preserving Host UID/GID in Containers
To ensure that containers run with the same UID and GID as the current user (e.g., copilot), configure Podman to use user namespaces with keep-id. This avoids permission issues when mounting host directories and accessing files.

Create or edit the file:

```bash
~/.config/containers/containers.conf
```

Add the following section:

```toml
[containers]
userns = "keep-id"
```

This setting makes Podman automatically map your host UID and GID into the container, so files created by the container will be owned by your user on the host. This is especially useful for development, CI, and when sharing data between host and container.

### Group-Based Write Access for Dockge

To allow Dockge (or other containers) to write to /opt/stacks using a group:

1. **Create the group and set permissions:**
   ```sh
   sudo groupadd dockge
   sudo chown :dockge /opt/stacks
   sudo chmod 2775 /opt/stacks
   ```
   The `2` in `2775` ensures new files/folders inherit the group.

2. **Add your user to the group:**
   ```sh
   sudo usermod -aG dockge $USER
   ```
   Log out and back in, or run `newgrp dockge` to activate the group in your shell.

3. **Configure the container to use the group:**
   - Find the group ID:
     ```sh
     getent group dockge
     ```
     Example output: `dockge:x:1234:` (1234 is the GID)
   - In your compose file, set:
     ```yaml
     user: "1000:1234"  # Replace 1000 with your UID, 1234 with the dockge GID
     volumes:
       - /opt/stacks:/opt/stacks
     ```
   - Or set the GID via environment variable if supported by the container.

Now, Dockge can write to /opt/stacks as long as the container process runs with the dockge group GID.
---
title: "Lab Baseline: Automated Infrastructure with Ubuntu LTS, Docker & FastAPI"
date: 2025-12-24
description: "Step-by-step guide to setting up a reproducible lab baseline using Ubuntu LTS, Docker, Compose, and FastAPI. Includes rationale, prerequisites, and automation tips."
tags: [lab, baseline, automation, docker, fastapi, nginx, ubuntu]
---

## Lab Baseline Overview

This entry documents the process of building a reproducible lab baseline for infrastructure automation. The goal is to provide a minimal, working setup using Ubuntu LTS VMs, Podman, podman-compose, and a simple FastAPI app behind Nginx. All steps are tested on:
- **dsk-001**: Ubuntu 24.04 LTS
- **NUC-100**: Ubuntu 25.10

System information for both hosts is gathered and referenced for future automation and troubleshooting.
---

- Internet access for package installation


---

### SSH Key and Account Setup

#### 1. Generate SSH Key (Windows PowerShell)
Run the following command to create a new ed25519 key pair for copilot:
```powershell
ssh-keygen -t ed25519 -C "copilot@dsk-001" -f $env:USERPROFILE\.ssh\copilot_ed25519
scp $env:USERPROFILE\.ssh\copilot_ed25519.pub henning@dsk-001:/tmp/
scp $env:USERPROFILE\.ssh\copilot_ed25519.pub henning@nuc-100:/tmp/
```

#### 2. Create copilot User on Linux Hosts
On each host (NUC-100 and dsk-001):
```sh
sudo adduser --gecos "" copilot
sudo usermod -aG sudo copilot
sudo -u copilot mkdir -p /home/copilot/.ssh
sudo -u copilot chmod 700 /home/copilot/.ssh
sudo cp /tmp/copilot_ed25519.pub /home/copilot/.ssh/authorized_keys
sudo chown copilot:copilot /home/copilot/.ssh/authorized_keys
sudo chmod 600 /home/copilot/.ssh/authorized_keys
```


#### 3. Verify SSH Login
Test login from Windows:
```powershell
ssh -i $env:USERPROFILE\.ssh\copilot_ed25519 copilot@nuc-100
ssh -i $env:USERPROFILE\.ssh\copilot_ed25519 copilot@dsk-001
```

---
- SSH client/server

---

### Step 1: System Reference

**Command:**
```sh
python tools/gather_host_info.py
```

**Output:**
```output
Info for nuc-100 written to nuc-100_info.json
Info for dsk-001 written to dsk-001_info.json
```

System info for both hosts is collected using a Python script and stored as JSON files:
- `nuc-100_info.json`
- `dsk-001_info.json`

This ensures reproducibility and helps document the environment for future troubleshooting.

---

### Step 2: Install Prerequisites
Run the following commands on each host:

```sh
sudo apt update
sudo apt install -y podman podman-compose make git curl python3 openssh-server
```
Add `copilot` to the `podman` group (if available):
```sh
sudo usermod -aG podman copilot
```

---
### Step 3: Podman Container Registry Configuration
Podman requires explicit configuration for unqualified image names (e.g., `nginx:latest`). To avoid image pull errors, configure your registries in `/etc/containers/registries.conf` as follows:

```toml
unqualified-search-registries = ["docker.io", "quay.io", "ghcr.io", "nvcr.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry]]
prefix = "nvcr.io"
location = "nvcr.io"
# NVIDIA NGC Catalog for GPU-accelerated AI containers

[[registry]]
prefix = "quay.io"
location = "quay.io"

[[registry]]
prefix = "ghcr.io"
location = "ghcr.io"
# GitHub Container Registry
```

After editing, restart your shell or log out/in to ensure Podman uses the new configuration. This enables pulling images by short name from the most common public registries.

---
### Step 4: Compose Setup
Create `lab/podman-compose.yml` to run Nginx and a simple FastAPI app. Example:

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - fastapi
  fastapi:
    image: tiangolo/uvicorn-gunicorn-fastapi:python3.11
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
### Running Dockge on Podman

Dockge can be used as a container management UI on Podman-based systems. To run Dockge with podman-compose, use the following Compose configuration:

```yaml
version: "3.8"
services:
  dockge:
    image: docker.io/louislam/dockge:latest
    container_name: dockge
    ports:
      - "5001:5001"
    volumes:
      - /var/run/podman/podman.sock:/var/run/docker.sock
      - ./data:/app/data
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock
    restart: unless-stopped
```

**Notes:**
- Make sure Podman’s socket service is running: `systemctl --user enable --now podman.socket`
- The volume `/var/run/podman/podman.sock:/var/run/docker.sock` allows Dockge to communicate with Podman as if it were Docker.
- Some Docker-specific features may not be available on Podman, but basic container management works.

For more details, see the official Dockge documentation and Podman compatibility notes.
```

---

### Step 5: Baseline Rationale (ADR)
- VM chosen for isolation and reproducibility
- Ubuntu LTS for stability and support
- Podman/podman-compose for rootless, daemonless container orchestration
- FastAPI for a minimal, modern Python web service
- Nginx for reverse proxy and static file serving

---

### Step 6: Deliverables
- `lab/podman-compose.yml` (see above)
- `lab/app/main.py` (FastAPI app)
- `lab/nginx/nginx.conf` (Nginx config)
- `lab/Makefile` (automation commands)
- `nuc-100_info.json`, `dsk-001_info.json` (system reference)
- ADR (this document)
- Runbook (step-by-step setup)

---

### Step 7: Acceptance Criteria
- `podman-compose up -d` starts both endpoints
- Nginx serves HTTP requests and proxies to FastAPI
- Documentation lists all prerequisites and steps

---

### Step 8: AI Assist
- Use local LLM (Ollama + CodeLlama/Mistral) to draft Dockerfiles, Compose, and runbook text
- Store CLI prompt templates in `ai/prompts/lab-baseline.md`

---

## Next Steps
- Implement and test the Compose setup
- Document any issues and solutions
- Extend automation for future entries
